from utils.celery_app import celery
from services.automl_service import _run_job

@celery.task(name="tasks.run_training_job")
def run_training_job(job_id, dataset, target, problem_type, test_size, random_state):
    _run_job(job_id, dataset, target, problem_type, test_size, random_state)