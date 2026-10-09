from pathlib import Path

import pandas as pd


# ============================================================
# CONSTANTS
# ============================================================

SUPPORTED_EXTENSIONS = {
    ".csv",
    ".xlsx",
    ".xls",
    ".json",
}

DEFAULT_PREVIEW_ROWS = 10
DEFAULT_CHUNK_SIZE = 5000


# ============================================================
# GENERAL HELPERS
# ============================================================

def _get_extension(file_path):
    """
    Return the lowercase file extension.
    """

    return Path(file_path).suffix.lower()


def _validate_file(file_path):
    """
    Validate that the uploaded file exists and has a
    supported extension.
    """

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Dataset file was not found: {file_path}"
        )

    if not path.is_file():
        raise ValueError(
            f"The supplied path is not a file: {file_path}"
        )

    extension = path.suffix.lower()

    if extension not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            "Unsupported file format. "
            "Supported formats are CSV, XLSX, XLS and JSON."
        )

    return extension


def _clean_dataframe(df):
    """
    Apply safe basic normalization to a DataFrame.

    This function does not try to determine the meaning of
    columns. Schema detection is handled separately.
    """

    if df is None:
        return pd.DataFrame()

    if not isinstance(df, pd.DataFrame):
        df = pd.DataFrame(df)

    # --------------------------------------------------------
    # Remove completely empty rows.
    # --------------------------------------------------------

    df = df.dropna(
        how="all"
    )

    # --------------------------------------------------------
    # Remove completely empty columns.
    # --------------------------------------------------------

    df = df.dropna(
        axis=1,
        how="all",
    )

    # --------------------------------------------------------
    # Make column names safe strings.
    # --------------------------------------------------------

    cleaned_columns = []

    for index, column in enumerate(df.columns):

        try:
            name = str(column).strip()
        except Exception:
            name = ""

        if not name:
            name = f"column_{index + 1}"

        cleaned_columns.append(name)

    df.columns = cleaned_columns

    return df


# ============================================================
# CSV READER
# ============================================================

def _read_csv(file_path, nrows=None):
    """
    Read CSV with multiple encoding/separator fallbacks.

    This helps with datasets created by different systems,
    Excel exports and regional applications.
    """

    encodings = [
        "utf-8",
        "utf-8-sig",
        "cp1252",
        "latin1",
    ]

    last_error = None

    for encoding in encodings:

        # ----------------------------------------------------
        # First attempt: normal CSV parsing.
        # ----------------------------------------------------

        try:

            return pd.read_csv(
                file_path,
                nrows=nrows,
                encoding=encoding,
                encoding_errors="replace",
                low_memory=False,
            )

        except Exception as exc:

            last_error = exc

        # ----------------------------------------------------
        # Second attempt: automatically detect separator.
        # ----------------------------------------------------

        try:

            return pd.read_csv(
                file_path,
                nrows=nrows,
                encoding=encoding,
                encoding_errors="replace",
                sep=None,
                engine="python",
            )

        except Exception as exc:

            last_error = exc

    raise ValueError(
        "Unable to read the CSV file. "
        f"Last error: {last_error}"
    )


# ============================================================
# EXCEL READER
# ============================================================

def _read_excel(file_path, nrows=None):
    """
    Safely read Excel files.

    The first non-empty sheet is used.
    """

    try:

        workbook = pd.ExcelFile(
            file_path
        )

    except Exception as exc:

        raise ValueError(
            f"Unable to open the Excel file: {exc}"
        ) from exc

    if not workbook.sheet_names:

        raise ValueError(
            "The Excel workbook does not contain any sheets."
        )

    last_error = None

    for sheet_name in workbook.sheet_names:

        try:

            df = pd.read_excel(
                file_path,
                sheet_name=sheet_name,
                nrows=nrows,
            )

            df = _clean_dataframe(
                df
            )

            if not df.empty:
                return df

        except Exception as exc:

            last_error = exc
            continue

    if last_error:

        raise ValueError(
            "The Excel workbook could not be read. "
            f"Last error: {last_error}"
        )

    return pd.DataFrame()


# ============================================================
# JSON READER
# ============================================================

def _read_json(file_path):
    """
    Read common JSON dataset structures.

    Supports normal tabular JSON and JSON Lines.
    """

    last_error = None

    # --------------------------------------------------------
    # Normal JSON
    # --------------------------------------------------------

    try:

        df = pd.read_json(
            file_path
        )

        if isinstance(
            df,
            pd.DataFrame,
        ):

            return _clean_dataframe(
                df
            )

    except Exception as exc:

        last_error = exc

    # --------------------------------------------------------
    # JSON Lines
    # --------------------------------------------------------

    try:

        df = pd.read_json(
            file_path,
            lines=True,
        )

        if isinstance(
            df,
            pd.DataFrame,
        ):

            return _clean_dataframe(
                df
            )

    except Exception as exc:

        last_error = exc

    # --------------------------------------------------------
    # Generic JSON fallback.
    # --------------------------------------------------------

    try:

        import json

        with open(
            file_path,
            "r",
            encoding="utf-8",
            errors="replace",
        ) as file:

            data = json.load(file)

        # List of records.
        if isinstance(data, list):

            return _clean_dataframe(
                pd.json_normalize(data)
            )

        # Single dictionary.
        if isinstance(data, dict):

            # Common API structure:
            # {"data": [...]}
            for key in (
                "data",
                "records",
                "results",
                "items",
                "rows",
            ):

                value = data.get(key)

                if isinstance(
                    value,
                    list,
                ):

                    return _clean_dataframe(
                        pd.json_normalize(
                            value
                        )
                    )

            # Single object.
            return _clean_dataframe(
                pd.json_normalize(
                    data
                )
            )

    except Exception as exc:

        last_error = exc

    raise ValueError(
        "Unable to read the JSON dataset. "
        f"Last error: {last_error}"
    )


# ============================================================
# GENERIC DATAFRAME READER
# ============================================================

def _read_dataframe(
    file_path,
    nrows=None,
):
    """
    Read any supported file into a DataFrame.
    """

    extension = _validate_file(
        file_path
    )

    if extension == ".csv":

        return _clean_dataframe(
            _read_csv(
                file_path,
                nrows=nrows,
            )
        )

    if extension in {
        ".xlsx",
        ".xls",
    }:

        return _clean_dataframe(
            _read_excel(
                file_path,
                nrows=nrows,
            )
        )

    if extension == ".json":

        df = _read_json(
            file_path
        )

        if nrows is not None:
            df = df.head(
                nrows
            )

        return _clean_dataframe(
            df
        )

    raise ValueError(
        "Unsupported file format."
    )


# ============================================================
# PREVIEW
# ============================================================

def read_preview(
    file_path,
    rows=DEFAULT_PREVIEW_ROWS,
):
    """
    Read a safe preview of an uploaded dataset.

    Returns:
        pandas.DataFrame
    """

    try:

        rows = int(rows)

    except (
        TypeError,
        ValueError,
    ):

        rows = DEFAULT_PREVIEW_ROWS

    rows = max(
        1,
        rows,
    )

    df = _read_dataframe(
        file_path,
        nrows=rows,
    )

    return df.head(
        rows
    )


# ============================================================
# CHUNK READING
# ============================================================

def read_chunks(
    file_path,
    chunksize=DEFAULT_CHUNK_SIZE,
):
    """
    Yield dataset chunks.

    CSV files are streamed in chunks.

    Excel and JSON files are loaded into memory and then
    divided into chunks because pandas does not provide
    the same chunked interface for normal Excel/JSON reads.
    """

    extension = _validate_file(
        file_path
    )

    try:

        chunksize = int(
            chunksize
        )

    except (
        TypeError,
        ValueError,
    ):

        chunksize = DEFAULT_CHUNK_SIZE

    chunksize = max(
        1,
        chunksize,
    )


    # ========================================================
    # CSV
    # ========================================================

    if extension == ".csv":

        encodings = [
            "utf-8",
            "utf-8-sig",
            "cp1252",
            "latin1",
        ]

        last_error = None

        for encoding in encodings:

            try:

                reader = pd.read_csv(
                    file_path,
                    chunksize=chunksize,
                    encoding=encoding,
                    encoding_errors="replace",
                    low_memory=False,
                )

                for chunk in reader:

                    chunk = _clean_dataframe(
                        chunk
                    )

                    if not chunk.empty:

                        yield chunk

                return

            except Exception as exc:

                last_error = exc

        # ----------------------------------------------------
        # CSV separator fallback
        # ----------------------------------------------------

        for encoding in encodings:

            try:

                reader = pd.read_csv(
                    file_path,
                    chunksize=chunksize,
                    encoding=encoding,
                    encoding_errors="replace",
                    sep=None,
                    engine="python",
                )

                for chunk in reader:

                    chunk = _clean_dataframe(
                        chunk
                    )

                    if not chunk.empty:

                        yield chunk

                return

            except Exception as exc:

                last_error = exc

        raise ValueError(
            "Unable to process the CSV dataset. "
            f"Last error: {last_error}"
        )


    # ========================================================
    # EXCEL
    # ========================================================

    if extension in {
        ".xlsx",
        ".xls",
    }:

        df = _read_excel(
            file_path
        )

        df = _clean_dataframe(
            df
        )

        for start in range(
            0,
            len(df),
            chunksize,
        ):

            chunk = df.iloc[
                start:start + chunksize
            ].copy()

            if not chunk.empty:

                yield chunk

        return


    # ========================================================
    # JSON
    # ========================================================

    if extension == ".json":

        df = _read_json(
            file_path
        )

        df = _clean_dataframe(
            df
        )

        for start in range(
            0,
            len(df),
            chunksize,
        ):

            chunk = df.iloc[
                start:start + chunksize
            ].copy()

            if not chunk.empty:

                yield chunk

        return


    raise ValueError(
        "Unsupported dataset format."
    )