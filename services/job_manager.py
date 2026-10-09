from concurrent.futures import ThreadPoolExecutor

from sqlalchemy import select

from db.engine import SessionLocal

from db.models import (
    Dataset,
    IngestionJob,
)

from services.ingestion_service import (
    process_dataset,
)


executor = ThreadPoolExecutor(
    max_workers=2
)


def create_ingestion_job(
    dataset_id,
):

    with SessionLocal() as db:

        dataset = db.get(
            Dataset,
            dataset_id,
        )

        if not dataset:

            raise ValueError(
                "Dataset not found."
            )

        job = IngestionJob(
            dataset_id=dataset_id,
            job_type="ingestion",
            status="queued",
        )

        db.add(job)

        db.commit()

        db.refresh(job)

        return job.id


def start_ingestion_job(
    job_id,
    dataset_id,
    file_path,
):

    future = executor.submit(
        process_dataset,
        dataset_id,
        file_path,
        job_id,
    )

    return future


def get_job_status(job_id):

    with SessionLocal() as db:

        job = db.get(
            IngestionJob,
            job_id,
        )

        if not job:

            return None

        return {
            "id": job.id,
            "dataset_id": job.dataset_id,
            "status": job.status,
            "total_rows": job.total_rows,
            "processed_rows": job.processed_rows,
            "successful_rows": job.successful_rows,
            "duplicate_rows": job.duplicate_rows,
            "failed_rows": job.failed_rows,
            "error_message": job.error_message,
            "started_at": job.started_at,
            "completed_at": job.completed_at,
        }


def list_jobs(limit=50):

    with SessionLocal() as db:

        jobs = db.scalars(
            select(IngestionJob)
            .order_by(
                IngestionJob.created_at.desc()
            )
            .limit(limit)
        ).all()

        return jobs