import hashlib
import json
from datetime import datetime

from sqlalchemy import select

from db.engine import SessionLocal

from db.models import (
    Dataset,
    Feedback,
    IngestionJob,
)

from services.schema_detector import detect_schema
from services.data_reader import read_chunks


# ============================================================
# CONSTANTS
# ============================================================

DEFAULT_SOURCE = "Employee Upload"


# ============================================================
# BASIC HELPERS
# ============================================================

def clean(value):
    """
    Convert a dataset value into a safe string.

    Empty values, NaN and common textual representations
    of missing values are converted to None.
    """

    if value is None:
        return None

    try:
        if value != value:
            return None
    except Exception:
        pass

    try:
        text = str(value).strip()
    except Exception:
        return None

    if not text:
        return None

    if text.lower() in {
        "nan",
        "none",
        "null",
        "n/a",
        "na",
        "nil",
        "unknown",
    }:
        return None

    return text


def create_hash(customer, text, source):
    """
    Create a stable SHA-256 hash used for duplicate detection.
    """

    customer = clean(customer) or ""
    text = clean(text) or ""
    source = clean(source) or ""

    raw = f"{customer}|{text}|{source}"

    return hashlib.sha256(
        raw.encode("utf-8")
    ).hexdigest()


def safe_json(value):
    """
    Safely serialize a value for raw_payload.
    """

    try:
        return json.dumps(
            value,
            default=str,
            ensure_ascii=False,
        )
    except Exception:
        return "{}"


def safe_mapping_get(mapping, key):
    """
    Safely retrieve a column name from the detected mapping.
    """

    if not isinstance(mapping, dict):
        return None

    value = mapping.get(key)

    if value is None:
        return None

    return clean(value)


def get_row_value(row, column_name):
    """
    Safely retrieve a value from a pandas Series.
    """

    if not column_name:
        return None

    try:
        return clean(
            row.get(column_name)
        )
    except Exception:
        return None


def get_error_text(exc):
    """
    Convert an exception into a useful diagnostic message.

    SQLAlchemy errors can contain a large amount of SQL text.
    We preserve the actual exception because it is important
    for diagnosing database/model mismatches.
    """

    try:
        text = str(exc).strip()
    except Exception:
        text = repr(exc)

    if not text:
        text = repr(exc)

    return text


# ============================================================
# JOB / DATASET STATE HELPERS
# ============================================================

def _set_processing_state(dataset, job):
    """
    Set initial processing state.
    """

    if dataset is not None:

        dataset.status = "processing"

        if hasattr(dataset, "processing_status"):
            dataset.processing_status = "processing"

    if job is not None:

        job.status = "running"

        if hasattr(job, "started_at"):
            job.started_at = datetime.utcnow()

        if hasattr(job, "error_message"):
            job.error_message = None


def _set_completed_state(dataset, job):
    """
    Set completely successful state.
    """

    now = datetime.utcnow()

    if dataset is not None:

        dataset.status = "ready"

        if hasattr(dataset, "processing_status"):
            dataset.processing_status = "completed"

        if hasattr(dataset, "processed_at"):
            dataset.processed_at = now

    if job is not None:

        job.status = "completed"

        if hasattr(job, "completed_at"):
            job.completed_at = now


def _set_completed_with_warnings_state(
    dataset,
    job,
    message,
):
    """
    Set state when ingestion completed but had
    duplicates or other non-fatal warnings.
    """

    now = datetime.utcnow()

    if dataset is not None:

        dataset.status = "ready"

        if hasattr(dataset, "processing_status"):
            dataset.processing_status = (
                "completed_with_warnings"
            )

        if hasattr(dataset, "processed_at"):
            dataset.processed_at = now

    if job is not None:

        job.status = "completed"

        if hasattr(job, "error_message"):
            job.error_message = message

        if hasattr(job, "completed_at"):
            job.completed_at = now


def _set_completed_with_errors_state(
    dataset,
    job,
    message,
):
    """
    Set state when the file was processed but one or more
    database/row-level errors occurred.
    """

    now = datetime.utcnow()

    if dataset is not None:

        dataset.status = "ready"

        if hasattr(dataset, "processing_status"):
            dataset.processing_status = (
                "completed_with_errors"
            )

        if hasattr(dataset, "processed_at"):
            dataset.processed_at = now

    if job is not None:

        # Keep the distinction visible.
        job.status = "completed_with_errors"

        if hasattr(job, "error_message"):
            job.error_message = message

        if hasattr(job, "completed_at"):
            job.completed_at = now


def _set_failed_state(dataset, job, error):
    """
    Set complete job failure state.
    """

    now = datetime.utcnow()

    error_text = get_error_text(error)

    if dataset is not None:

        dataset.status = "failed"

        if hasattr(dataset, "processing_status"):
            dataset.processing_status = "failed"

        if hasattr(dataset, "processed_at"):
            dataset.processed_at = now

    if job is not None:

        job.status = "failed"

        if hasattr(job, "error_message"):
            job.error_message = error_text

        if hasattr(job, "completed_at"):
            job.completed_at = now


# ============================================================
# COUNTER HELPERS
# ============================================================

def _increment_dataset_failed(dataset, count=1):

    current = getattr(
        dataset,
        "failed_rows",
        0,
    ) or 0

    dataset.failed_rows = current + count


def _increment_job_failed(job, count=1):

    current = getattr(
        job,
        "failed_rows",
        0,
    ) or 0

    job.failed_rows = current + count


def _increment_dataset_duplicate(dataset, count=1):

    current = getattr(
        dataset,
        "duplicate_rows",
        0,
    ) or 0

    dataset.duplicate_rows = current + count


def _increment_job_duplicate(job, count=1):

    current = getattr(
        job,
        "duplicate_rows",
        0,
    ) or 0

    job.duplicate_rows = current + count


def _increment_processed(dataset, count=1):

    current = getattr(
        dataset,
        "processed_rows",
        0,
    ) or 0

    dataset.processed_rows = current + count


def _increment_successful(job, count=1):

    current = getattr(
        job,
        "successful_rows",
        0,
    ) or 0

    job.successful_rows = current + count


def _increment_job_processed(job, count=1):

    current = getattr(
        job,
        "processed_rows",
        0,
    ) or 0

    job.processed_rows = current + count


# ============================================================
# FEEDBACK TEXT DETECTION
# ============================================================

def _get_feedback_text(row, mapping):
    """
    Get feedback text using detected schema.

    The schema detector is used first, followed by common
    fallback column names.
    """

    column = safe_mapping_get(
        mapping,
        "feedback_text",
    )

    if column:

        value = get_row_value(
            row,
            column,
        )

        if value:
            return value

    fallback_columns = [
        "feedback",
        "feedback_text",
        "review",
        "review_text",
        "comment",
        "comments",
        "customer_feedback",
        "customer_comment",
        "complaint",
        "description",
        "message",
        "text",
        "remarks",
        "issue",
        "problem",
        "response",
    ]

    # --------------------------------------------------------
    # Exact column-name matching
    # --------------------------------------------------------

    try:

        available_columns = {
            str(column).strip().lower(): column
            for column in row.index
        }

    except Exception:

        available_columns = {}

    for column_name in fallback_columns:

        actual_column = available_columns.get(
            column_name.lower()
        )

        if actual_column is None:
            continue

        value = get_row_value(
            row,
            actual_column,
        )

        if value:
            return value

    # --------------------------------------------------------
    # Last-resort fallback:
    # If the detector failed and there is exactly one
    # textual column, use it as feedback.
    # --------------------------------------------------------

    try:

        for column in row.index:

            value = get_row_value(
                row,
                column,
            )

            if value and len(value) >= 5:

                # Avoid treating obvious ID/number columns
                # as feedback when possible.
                column_name = str(
                    column
                ).strip().lower()

                if any(
                    token in column_name
                    for token in [
                        "id",
                        "date",
                        "time",
                        "rating",
                        "score",
                    ]
                ):
                    continue

                return value

    except Exception:
        pass

    return None


# ============================================================
# SCHEMA DETECTION
# ============================================================

def _detect_mapping(columns):
    """
    Detect dataset schema safely.
    """

    try:

        schema = detect_schema(
            list(columns)
        )

    except Exception:

        schema = {
            "mapping": {},
            "columns": list(columns),
        }

    if not isinstance(schema, dict):
        schema = {
            "mapping": {},
            "columns": list(columns),
        }

    mapping = schema.get(
        "mapping",
        {},
    )

    if not isinstance(mapping, dict):
        mapping = {}

    return schema, mapping


# ============================================================
# MAIN DATASET PROCESSOR
# ============================================================

def process_dataset(
    dataset_id,
    file_path,
    job_id,
):
    """
    Process an uploaded customer-feedback dataset.

    Important behavior:

    1. Reads the file in chunks.
    2. Detects the schema from the first non-empty chunk.
    3. Inserts valid feedback records.
    4. Detects duplicates.
    5. Handles bad rows individually.
    6. Uses a SAVEPOINT for each row so one failed row does
       not rollback successful rows from the same chunk.
    7. Records the first actual database error.
    8. Distinguishes successful, warning and error completion.
    """

    with SessionLocal() as db:

        dataset = db.get(
            Dataset,
            dataset_id,
        )

        job = db.get(
            IngestionJob,
            job_id,
        )

        if dataset is None:
            raise ValueError(
                f"Dataset {dataset_id} was not found."
            )

        if job is None:
            raise ValueError(
                f"Ingestion job {job_id} was not found."
            )

        # ----------------------------------------------------
        # INITIAL STATE
        # ----------------------------------------------------

        _set_processing_state(
            dataset,
            job,
        )

        db.commit()

        mapping = {}

        first_chunk = True
        any_chunk = False

        total_rows_seen = 0
        row_number = 0

        first_error = None
        first_error_row = None

        schema_error = None

        try:

            # =================================================
            # READ DATASET
            # =================================================

            chunks = read_chunks(
                file_path
            )

            if chunks is None:
                raise ValueError(
                    "The uploaded dataset could not be read."
                )

            # =================================================
            # PROCESS CHUNKS
            # =================================================

            for chunk in chunks:

                any_chunk = True

                if chunk is None:
                    continue

                try:
                    chunk_length = len(chunk)
                except Exception:
                    chunk_length = 0

                if chunk_length == 0:
                    continue

                total_rows_seen += chunk_length

                # =================================================
                # DETECT SCHEMA
                # =================================================

                if first_chunk:

                    try:

                        schema, mapping = _detect_mapping(
                            chunk.columns
                        )

                        if not mapping:

                            schema_error = (
                                "No column mapping was detected."
                            )

                    except Exception as exc:

                        schema_error = get_error_text(
                            exc
                        )

                        mapping = {}

                    first_chunk = False

                # =================================================
                # PROCESS EACH ROW
                # =================================================

                for _, row in chunk.iterrows():

                    row_number += 1

                    # ------------------------------------------------
                    # FEEDBACK TEXT
                    # ------------------------------------------------

                    try:

                        text = _get_feedback_text(
                            row,
                            mapping,
                        )

                    except Exception as exc:

                        text = None

                        if first_error is None:

                            first_error = (
                                "Feedback text extraction failed: "
                                f"{get_error_text(exc)}"
                            )

                            first_error_row = row_number

                    # ------------------------------------------------
                    # OPTIONAL FIELDS
                    # ------------------------------------------------

                    try:

                        customer_column = safe_mapping_get(
                            mapping,
                            "customer_id",
                        )

                        category_column = safe_mapping_get(
                            mapping,
                            "category",
                        )

                        source_column = safe_mapping_get(
                            mapping,
                            "source",
                        )

                        customer = get_row_value(
                            row,
                            customer_column,
                        )

                        category = get_row_value(
                            row,
                            category_column,
                        )

                        source = get_row_value(
                            row,
                            source_column,
                        )

                    except Exception as exc:

                        customer = None
                        category = None
                        source = None

                        if first_error is None:

                            first_error = (
                                "Optional column processing failed: "
                                f"{get_error_text(exc)}"
                            )

                            first_error_row = row_number

                    # ------------------------------------------------
                    # DEFAULT SOURCE
                    # ------------------------------------------------

                    if not source:
                        source = DEFAULT_SOURCE

                    # ------------------------------------------------
                    # INVALID / EMPTY ROW
                    # ------------------------------------------------

                    if not text:

                        _increment_dataset_failed(
                            dataset
                        )

                        _increment_job_failed(
                            job
                        )

                        if first_error is None:

                            if schema_error:

                                first_error = (
                                    "No usable feedback text was "
                                    "found. Schema mapping problem: "
                                    f"{schema_error}"
                                )

                            else:

                                first_error = (
                                    "No usable feedback text "
                                    "was found in this row."
                                )

                            first_error_row = row_number

                        continue

                    # ------------------------------------------------
                    # DUPLICATE DETECTION
                    # ------------------------------------------------

                    try:

                        record_hash = create_hash(
                            customer,
                            text,
                            source,
                        )

                        exists = db.scalar(
                            select(Feedback).where(
                                Feedback.record_hash
                                == record_hash
                            )
                        )

                    except Exception as exc:

                        _increment_dataset_failed(
                            dataset
                        )

                        _increment_job_failed(
                            job
                        )

                        if first_error is None:

                            first_error = (
                                "Duplicate check failed: "
                                f"{get_error_text(exc)}"
                            )

                            first_error_row = row_number

                        continue

                    if exists:

                        _increment_dataset_duplicate(
                            dataset
                        )

                        _increment_job_duplicate(
                            job
                        )

                        continue

                    # ------------------------------------------------
                    # RAW DATA
                    # ------------------------------------------------

                    try:

                        raw_data = (
                            row.to_dict()
                            if hasattr(row, "to_dict")
                            else {}
                        )

                    except Exception:

                        raw_data = {}

                    # ------------------------------------------------
                    # CREATE FEEDBACK
                    # ------------------------------------------------

                    feedback = Feedback(
                        dataset_id=dataset.id,
                        customer_id=customer,
                        feedback_text=text,
                        category=category,
                        source=source,
                        record_hash=record_hash,
                        raw_payload=safe_json(
                            raw_data
                        ),
                        status="new",
                        processing_status="pending",
                    )

                    # =================================================
                    # SAVE INDIVIDUAL RECORD
                    # =================================================
                    #
                    # IMPORTANT:
                    #
                    # begin_nested() creates a SAVEPOINT.
                    #
                    # If this particular row fails, only this row
                    # is rolled back. Previously successful rows in
                    # the same chunk remain intact.
                    #
                    # =================================================

                    try:

                        with db.begin_nested():

                            db.add(
                                feedback
                            )

                            db.flush()

                        # ------------------------------------------------
                        # Only update success counters after the SAVEPOINT
                        # has succeeded.
                        # ------------------------------------------------

                        _increment_processed(
                            dataset
                        )

                        _increment_successful(
                            job
                        )

                    except Exception as exc:

                        error_text = get_error_text(
                            exc
                        )

                        _increment_dataset_failed(
                            dataset
                        )

                        _increment_job_failed(
                            job
                        )

                        # ------------------------------------------------
                        # Store ONLY the first error.
                        #
                        # This is important because if 38,444 rows fail,
                        # we don't want a 38,444-line error message.
                        # ------------------------------------------------

                        if first_error is None:

                            first_error = (
                                error_text
                            )

                            first_error_row = (
                                row_number
                            )

                        continue

                # =================================================
                # UPDATE JOB PROGRESS
                # =================================================

                _increment_job_processed(
                    job,
                    chunk_length,
                )

                dataset.row_count = (
                    total_rows_seen
                )

                # ------------------------------------------------
                # Commit this completed chunk.
                # ------------------------------------------------

                db.commit()

                # ------------------------------------------------
                # Re-fetch after commit so the next chunk always
                # works with current database state.
                # ------------------------------------------------

                dataset = db.get(
                    Dataset,
                    dataset_id,
                )

                job = db.get(
                    IngestionJob,
                    job_id,
                )

            # =================================================
            # EMPTY DATASET
            # =================================================

            if not any_chunk:

                dataset.row_count = 0

                _set_completed_state(
                    dataset,
                    job,
                )

                db.commit()

                return {
                    "success": True,
                    "warning": False,
                    "processed_rows": 0,
                    "successful_rows": 0,
                    "duplicate_rows": 0,
                    "failed_rows": 0,
                    "first_error": None,
                    "first_error_row": None,
                    "message": "Dataset was empty.",
                }

            # =================================================
            # FINAL COUNTERS
            # =================================================

            successful_rows = getattr(
                job,
                "successful_rows",
                0,
            ) or 0

            failed_rows = getattr(
                job,
                "failed_rows",
                0,
            ) or 0

            duplicate_rows = getattr(
                job,
                "duplicate_rows",
                0,
            ) or 0

            processed_rows = getattr(
                job,
                "processed_rows",
                0,
            ) or 0

            # =================================================
            # ZERO SUCCESSFUL RECORDS
            # =================================================

            if successful_rows == 0:

                dataset.row_count = (
                    total_rows_seen
                )

                # ------------------------------------------------
                # If rows failed, this is a real ingestion error.
                # ------------------------------------------------

                if failed_rows > 0:

                    if first_error:

                        message = (
                            f"First ingestion error "
                            f"(row {first_error_row}): "
                            f"{first_error}"
                        )

                    else:

                        message = (
                            f"{failed_rows} rows failed "
                            "during ingestion."
                        )

                    _set_completed_with_errors_state(
                        dataset,
                        job,
                        message,
                    )

                    db.commit()

                    return {
                        "success": False,
                        "warning": True,
                        "processed_rows": processed_rows,
                        "successful_rows": successful_rows,
                        "duplicate_rows": duplicate_rows,
                        "failed_rows": failed_rows,
                        "first_error": first_error,
                        "first_error_row": first_error_row,
                        "message": message,
                    }

                # ------------------------------------------------
                # No failures but all records were duplicates.
                # ------------------------------------------------

                if duplicate_rows > 0:

                    message = (
                        "No new feedback records were inserted. "
                        f"{duplicate_rows} rows were duplicates."
                    )

                    _set_completed_with_warnings_state(
                        dataset,
                        job,
                        message,
                    )

                    db.commit()

                    return {
                        "success": True,
                        "warning": True,
                        "processed_rows": processed_rows,
                        "successful_rows": successful_rows,
                        "duplicate_rows": duplicate_rows,
                        "failed_rows": failed_rows,
                        "first_error": None,
                        "first_error_row": None,
                        "message": message,
                    }

                # ------------------------------------------------
                # No usable feedback.
                # ------------------------------------------------

                message = (
                    "No usable feedback records "
                    "were found in the dataset."
                )

                _set_completed_with_warnings_state(
                    dataset,
                    job,
                    message,
                )

                db.commit()

                return {
                    "success": True,
                    "warning": True,
                    "processed_rows": processed_rows,
                    "successful_rows": successful_rows,
                    "duplicate_rows": duplicate_rows,
                    "failed_rows": failed_rows,
                    "first_error": first_error,
                    "first_error_row": first_error_row,
                    "message": message,
                }

            # =================================================
            # SUCCESSFUL RECORDS EXIST
            # =================================================

            dataset.row_count = (
                total_rows_seen
            )

            # ------------------------------------------------
            # Some records failed.
            # ------------------------------------------------

            if failed_rows > 0:

                if first_error:

                    message = (
                        "Completed with errors. "
                        f"Inserted: {successful_rows}; "
                        f"Failed: {failed_rows}; "
                        f"Duplicates: {duplicate_rows}. "
                        f"First error (row "
                        f"{first_error_row}): "
                        f"{first_error}"
                    )

                else:

                    message = (
                        "Completed with errors. "
                        f"Inserted: {successful_rows}; "
                        f"Failed: {failed_rows}; "
                        f"Duplicates: {duplicate_rows}."
                    )

                _set_completed_with_errors_state(
                    dataset,
                    job,
                    message,
                )

                db.commit()

                return {
                    "success": True,
                    "warning": True,
                    "processed_rows": processed_rows,
                    "successful_rows": successful_rows,
                    "duplicate_rows": duplicate_rows,
                    "failed_rows": failed_rows,
                    "first_error": first_error,
                    "first_error_row": first_error_row,
                    "message": message,
                }

            # ------------------------------------------------
            # Only duplicates in addition to successful rows.
            # ------------------------------------------------

            if duplicate_rows > 0:

                message = (
                    "Dataset processed successfully with "
                    f"{duplicate_rows} duplicate rows skipped."
                )

                _set_completed_with_warnings_state(
                    dataset,
                    job,
                    message,
                )

                db.commit()

                return {
                    "success": True,
                    "warning": True,
                    "processed_rows": processed_rows,
                    "successful_rows": successful_rows,
                    "duplicate_rows": duplicate_rows,
                    "failed_rows": failed_rows,
                    "first_error": None,
                    "first_error_row": None,
                    "message": message,
                }

            # =================================================
            # COMPLETE SUCCESS
            # =================================================

            _set_completed_state(
                dataset,
                job,
            )

            db.commit()

            return {
                "success": True,
                "warning": False,
                "processed_rows": processed_rows,
                "successful_rows": successful_rows,
                "duplicate_rows": duplicate_rows,
                "failed_rows": failed_rows,
                "first_error": None,
                "first_error_row": None,
                "message": (
                    "Dataset processed successfully."
                ),
            }

        # =====================================================
        # COMPLETE DATASET FAILURE
        # =====================================================

        except Exception as exc:

            error_text = get_error_text(
                exc
            )

            try:
                db.rollback()
            except Exception:
                pass

            try:

                dataset = db.get(
                    Dataset,
                    dataset_id,
                )

                job = db.get(
                    IngestionJob,
                    job_id,
                )

                _set_failed_state(
                    dataset,
                    job,
                    error_text,
                )

                db.commit()

            except Exception:
                pass

            raise