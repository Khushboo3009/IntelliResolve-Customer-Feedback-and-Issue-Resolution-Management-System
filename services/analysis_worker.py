from concurrent.futures import ThreadPoolExecutor

from services.analysis_service import (
    process_pending_feedback,
)


executor = ThreadPoolExecutor(
    max_workers=2
)


def start_analysis(
    limit=100,
):

    return executor.submit(
        process_pending_feedback,
        limit,
    )