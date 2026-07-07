import uuid
from typing import Any, Dict, Optional

# In-memory store for import jobs.
# In a real enterprise app, this would be Redis or a database table.
_jobs: Dict[str, Dict[str, Any]] = {}


def create_job() -> str:
    job_id = str(uuid.uuid4())
    _jobs[job_id] = {"id": job_id, "status": "pending"}
    return job_id


def get_job(job_id: str) -> Optional[Dict[str, Any]]:
    return _jobs.get(job_id)


def update_job(job_id: str, data: Dict[str, Any]) -> None:
    if job_id in _jobs:
        _jobs[job_id].update(data)
