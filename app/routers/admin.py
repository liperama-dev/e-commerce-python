from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.database import SessionLocal, get_db
from app.dependencies.auth import verify_admin_key
from app.models.product import Product
from app.schemas.import_job import ImportJobResponse
from app.services.csv_import import process_csv
from app.services.import_jobs import create_job, get_job, update_job

router = APIRouter(
    prefix="/api/products", 
    tags=["admin"], 
    dependencies=[Depends(verify_admin_key)]
)


def _run_import_task(job_id: str, decoded_content: str):
    db = SessionLocal()
    try:
        result = process_csv(decoded_content, db)
        update_job(job_id, {
            "status": "completed",
            "imported_count": result.get("imported_count"),
            "discarded_count": result.get("discarded_count"),
            "discard_reasons": result.get("discard_reasons"),
        })
    except Exception as e:
        update_job(job_id, {"status": "failed", "error": str(e)})
    finally:
        db.close()


@router.post("/import", status_code=202)
async def import_csv(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    """
    Upload a CSV file and process it in the background.
    Returns 202 Accepted with a job_id for polling status.
    """
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="File must be a CSV")

    content = await file.read()
    try:
        decoded_content = content.decode("utf-8")
    except UnicodeDecodeError:
        decoded_content = content.decode("iso-8859-1")

    job_id = create_job()
    background_tasks.add_task(_run_import_task, job_id, decoded_content)
    
    return {"message": "Import started", "job_id": job_id}


@router.get("/import/{job_id}", response_model=ImportJobResponse)
def get_import_status(job_id: str):
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.post("/flush")
def flush_database(db: Session = Depends(get_db)):
    """
    Delete all products from the database.
    """
    db.query(Product).delete()
    db.commit()
    return {"message": "Database flushed successfully"}
