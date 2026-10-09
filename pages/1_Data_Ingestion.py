import os
import tempfile

import streamlit as st
from sqlalchemy import select

from db.engine import SessionLocal
from db.models import Dataset, IngestionJob

from services.data_reader import read_preview
from services.ingestion_service import process_dataset

from styles.theme import apply_theme


# ============================================================
# PAGE CONFIGURATION
# ============================================================

apply_theme()

st.title("📥 Data Ingestion Engine")
st.caption(
    "Upload and process customer feedback datasets "
    "from multiple file formats."
)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def safe_int(value, default=0):
    """
    Safely convert a database value to an integer.
    """
    try:
        if value is None:
            return default

        return int(value)

    except (TypeError, ValueError):
        return default


def mark_job_failed(job_id):
    """
    Safely mark an ingestion job as failed.
    """
    if not job_id:
        return

    try:
        with SessionLocal() as db:

            job = db.get(
                IngestionJob,
                job_id,
            )

            if job:

                job.status = "failed"

                if hasattr(job, "processing_status"):
                    job.processing_status = "failed"

                db.commit()

    except Exception:
        # Do not allow failure handling to crash Streamlit.
        pass


# ============================================================
# DATASET UPLOAD
# ============================================================

uploaded = st.file_uploader(
    "Upload Customer Feedback Dataset",
    type=[
        "csv",
        "xlsx",
        "xls",
        "json",
    ],
    help=(
        "Supported formats: CSV, Excel and JSON. "
        "The dataset can contain different column names; "
        "the ingestion service should determine which fields "
        "are available."
    ),
)


# ============================================================
# PROCESS UPLOADED DATASET
# ============================================================

if uploaded:

    temp_path = None
    dataset_id = None
    job_id = None

    # --------------------------------------------------------
    # SAVE UPLOADED FILE TEMPORARILY
    # --------------------------------------------------------

    suffix = os.path.splitext(
        uploaded.name
    )[1].lower()

    try:

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=suffix,
        ) as tmp:

            tmp.write(
                uploaded.getbuffer()
            )

            temp_path = tmp.name

    except Exception as exc:

        st.error(
            f"Unable to save the uploaded file: {exc}"
        )

        st.stop()

    st.success(
        f"Dataset uploaded: {uploaded.name}"
    )


    # ========================================================
    # DATASET PREVIEW
    # ========================================================

    st.subheader("Dataset Preview")

    try:

        preview = read_preview(
            temp_path
        )

        if preview is None:

            st.warning(
                "The dataset could not be previewed."
            )

        elif hasattr(preview, "empty") and preview.empty:

            st.warning(
                "The uploaded dataset contains no rows."
            )

        else:

            st.dataframe(
                preview,
                use_container_width=True,
                hide_index=True,
            )

            # ------------------------------------------------
            # DISPLAY BASIC DATASET INFORMATION
            # ------------------------------------------------

            try:

                row_count = len(preview)
                column_count = len(preview.columns)

                st.caption(
                    f"Preview: {row_count:,} rows × "
                    f"{column_count:,} columns"
                )

            except Exception:
                pass

    except Exception as exc:

        st.error(
            "Unable to read the uploaded dataset."
        )

        st.code(
            str(exc)
        )

        st.info(
            "Please verify that the file is a valid "
            "CSV, Excel, or JSON file."
        )

        # Cleanup temporary file.
        try:

            if temp_path and os.path.exists(
                temp_path
            ):
                os.remove(temp_path)

        except Exception:
            pass

        st.stop()


    # ========================================================
    # START INGESTION
    # ========================================================

    st.divider()

    if st.button(
        "🚀 Start Ingestion",
        type="primary",
        use_container_width=True,
    ):

        try:

            # =================================================
            # CREATE DATASET RECORD
            # =================================================

            with SessionLocal() as db:

                dataset = Dataset(
                    # Required by the existing MySQL schema.
                    name=uploaded.name,

                    file_name=uploaded.name,

                    source="Employee Upload",

                    row_count=0,

                    processed_rows=0,

                    duplicate_rows=0,

                    failed_rows=0,

                    status="uploaded",

                    processing_status="pending",
                )

                db.add(dataset)

                db.commit()

                db.refresh(dataset)

                dataset_id = dataset.id


                # =============================================
                # CREATE INGESTION JOB
                # =============================================

                job = IngestionJob(
                    dataset_id=dataset.id,
                )

                db.add(job)

                db.commit()

                db.refresh(job)

                job_id = job.id


            # =================================================
            # PROCESS DATASET
            # =================================================

            with st.spinner(
                "Processing dataset. Please wait..."
            ):

                result = process_dataset(
                    dataset_id,
                    temp_path,
                    job_id,
                )


            # =================================================
            # PROCESSING COMPLETED
            # =================================================

            st.success(
                f"✅ Dataset '{uploaded.name}' "
                "processed successfully."
            )


            # -------------------------------------------------
            # SHOW PROCESSING RESULT IF SERVICE RETURNS ONE
            # -------------------------------------------------

            if isinstance(result, dict):

                processed = safe_int(
                    result.get(
                        "processed_rows",
                        result.get(
                            "processed",
                            0,
                        ),
                    )
                )

                inserted = safe_int(
                    result.get(
                        "successful_rows",
                        result.get(
                            "inserted",
                            0,
                        ),
                    )
                )

                duplicates = safe_int(
                    result.get(
                        "duplicate_rows",
                        result.get(
                            "duplicates",
                            0,
                        ),
                    )
                )

                failed = safe_int(
                    result.get(
                        "failed_rows",
                        result.get(
                            "failed",
                            0,
                        ),
                    )
                )

                c1, c2, c3, c4 = st.columns(4)

                c1.metric(
                    "Processed",
                    processed,
                )

                c2.metric(
                    "Inserted",
                    inserted,
                )

                c3.metric(
                    "Duplicates",
                    duplicates,
                )

                c4.metric(
                    "Failed",
                    failed,
                )


            # -------------------------------------------------
            # REMOVE TEMPORARY FILE
            # -------------------------------------------------

            try:

                if temp_path and os.path.exists(
                    temp_path
                ):
                    os.remove(temp_path)

            except Exception:
                pass


            # -------------------------------------------------
            # REFRESH PAGE
            # -------------------------------------------------

            st.rerun()


        except Exception as exc:

            # ================================================
            # DATABASE ROLLBACK
            # ================================================

            try:

                with SessionLocal() as db:
                    db.rollback()

            except Exception:
                pass


            # ================================================
            # MARK JOB AS FAILED
            # ================================================

            mark_job_failed(
                job_id
            )


            # ================================================
            # SHOW ERROR
            # ================================================

            st.error(
                "⚠️ Dataset ingestion could not be completed."
            )

            st.warning(
                "The application kept running, but this "
                "dataset could not be processed."
            )

            with st.expander(
                "Technical details"
            ):

                st.code(
                    str(exc)
                )


            # ================================================
            # CLEAN TEMPORARY FILE
            # ================================================

            try:

                if temp_path and os.path.exists(
                    temp_path
                ):
                    os.remove(temp_path)

            except Exception:
                pass


# ============================================================
# PROCESSING JOBS
# ============================================================

st.divider()

st.subheader("📊 Processing Jobs")


try:

    with SessionLocal() as db:

        jobs = db.scalars(
            select(
                IngestionJob
            ).order_by(
                IngestionJob.id.desc()
            )
        ).all()


        if jobs:

            for job in jobs:

                with st.container(
                    border=True
                ):

                    # ----------------------------------------
                    # JOB METRICS
                    # ----------------------------------------

                    c1, c2, c3, c4 = st.columns(4)


                    c1.metric(
                        "Job ID",
                        job.id,
                    )


                    c2.metric(
                        "Processed",
                        safe_int(
                            getattr(
                                job,
                                "processed_rows",
                                0,
                            )
                        ),
                    )


                    c3.metric(
                        "Inserted",
                        safe_int(
                            getattr(
                                job,
                                "successful_rows",
                                0,
                            )
                        ),
                    )


                    status = getattr(
                        job,
                        "status",
                        None,
                    )

                    c4.metric(
                        "Status",
                        status or "Unknown",
                    )


                    # ----------------------------------------
                    # ADDITIONAL INFORMATION
                    # ----------------------------------------

                    duplicates = safe_int(
                        getattr(
                            job,
                            "duplicate_rows",
                            0,
                        )
                    )

                    failed = safe_int(
                        getattr(
                            job,
                            "failed_rows",
                            0,
                        )
                    )


                    st.write(
                        f"**Duplicates:** {duplicates}"
                    )

                    st.write(
                        f"**Failed:** {failed}"
                    )


        else:

            st.info(
                "No ingestion jobs available."
            )


except Exception as exc:

    st.warning(
        "Unable to load ingestion history."
    )

    with st.expander(
        "Technical details"
    ):

        st.code(
            str(exc)
        )