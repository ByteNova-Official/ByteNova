# File: app/job_matcher.py
from app.models.inference_job import InferenceJob
from app.models.worker import Worker
from collections import deque
from app import app

def match_jobs(dry_run=False):
    job_queue = _get_job_queue()
    idle_worker_queue = _get_idle_workers()
    matched_jobs = []
    
    unable_to_match = []

    while job_queue:
        job = job_queue.pop(0)
        matched = False
        
        # Use a loop to go through the deque and try to find a matching worker for the job
        for _ in range(len(idle_worker_queue)):  # This loop guarantees we check each worker once
            worker = idle_worker_queue.popleft()
            if worker.available_gpu >= job[1]:  # job[1] contains model_required_gpu
                if not dry_run:
                    worker.working_on = job[0]  # job[0] contains job.id
                    worker.save()  # Save the worker's state
                matched_jobs.append([worker.id, job[0]])  # job[0] contains job.id, worker.id contains worker.id
                matched = True
                break
            else:
                idle_worker_queue.append(worker)  # Re-add the worker to the right side of the deque
            
        if not matched:
            unable_to_match.append(job[0])

        if not idle_worker_queue:
            # print("No more idle workers")
            break
    
    if app.debug:
        app.logger.info(f'{len(matched_jobs)} Jobs that were matched: {matched_jobs}')
        app.logger.info(f'{len(unable_to_match)} Jobs that could not be matched: {unable_to_match}')
        app.logger.info(f'{len(idle_worker_queue)} Remaining idle workers: {list(idle_worker_queue)}')
    return matched_jobs


def _get_job_queue():
    jobs = InferenceJob.get_jobs_to_match()
    queue = []
    for job in jobs:
        N = job.desired_workers - job.get_activate_worker_count()
        if N > 0:
            queue.extend([[job.id, job.model_required_gpu] for _ in range(N)])
    # Sorting the queue based on the model_required_gpu (index 1 of the sublist) in descending order
    queue = sorted(queue, key=lambda x: x[1], reverse=True)
    return queue

def _get_idle_workers():
    sorted_idle_workers = sorted(Worker.get_workers_waiting_for_a_job(), key=lambda worker: worker.available_gpu, reverse=True)
    # Convert the sorted list to a deque
    return deque(sorted_idle_workers)
