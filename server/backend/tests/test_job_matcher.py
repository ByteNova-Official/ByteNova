import pytest
from app.job_matcher import match_jobs
import app.job_matcher as job_matcher

# Mock classes
class InferenceJob:
    _mock_jobs = []
    def __init__(self, job_id, model_required_gpu, desired_workers, activated_workers):
        self.id = job_id
        self.model_required_gpu = model_required_gpu
        self.desired_workers = desired_workers
        self.activated_workers = activated_workers

    @classmethod
    def mock_jobs(cls, job_params_list):
        cls._mock_jobs = [cls(*params) for params in job_params_list]

    @classmethod
    def get_jobs_to_match(cls):
        return cls._mock_jobs

    def get_activate_worker_count(self):
        return self.activated_workers
    
class Worker:
    _mock_workers = []

    def __init__(self, worker_id, available_gpu):
        self.id = worker_id
        self.available_gpu = available_gpu
        self.working_on = None

    def save(self):
        # Do nothing for the mock version
        pass

    @classmethod
    def mock_workers(cls, worker_params_list):
        cls._mock_workers = [cls(*params) for params in worker_params_list]

    @classmethod
    def get_workers_waiting_for_a_job(cls):
        return cls._mock_workers

@pytest.fixture
def setup_mock_data():
    job_matcher.InferenceJob = InferenceJob
    job_matcher.Worker = Worker
    InferenceJob._mock_jobs = []
    Worker._mock_workers = []
    yield
    # Teardown logic after the test finishes can be added here

def test_match_jobs_1(setup_mock_data):
    # Set mock jobs and workers data for test 1
    # job_id, model_required_gpu, desired_workers, activated_workers
    job_params = [
        (1, 2, 3, 2),
        (2, 10, 4, 0)
    ]
    worker_params = [
        (1, 4),
        (2, 12)
    ]

    InferenceJob.mock_jobs(job_params)
    Worker.mock_workers(worker_params)

    matched_jobs = match_jobs()
    # Assertions or checks specific to test 1
    assert matched_jobs == [[2, 2], [1, 1]]

def test_match_jobs_2(setup_mock_data):
    # job_id, model_required_gpu, desired_workers, activated_workers
    job_params = [
        (1, 2, 3, 2),
        (2, 10, 4, 0)
    ]
    worker_params = [
        (1, 12),
        (2, 12)
    ]
    # Both workers should be matched to job 2
    InferenceJob.mock_jobs(job_params)
    Worker.mock_workers(worker_params)

    matched_jobs = match_jobs()

    assert matched_jobs == [[1, 2], [2, 2]]

def test_match_jobs_3(setup_mock_data):
    # job_id, model_required_gpu, desired_workers, activated_workers
    job_params = [
        (1, 2, 3, 2),
        (2, 10, 4, 0)
    ]
    worker_params = [
        (1, 4),
        (2, 3)
    ]
    # Both workers should be matched to job 2
    InferenceJob.mock_jobs(job_params)
    Worker.mock_workers(worker_params)

    matched_jobs = match_jobs()

    assert matched_jobs == [[1, 1]]

def test_match_jobs_4(setup_mock_data):
    # job_id, model_required_gpu, desired_workers, activated_workers
    job_params = [
        (1, 2, 3, 1),
        (2, 10, 4, 0)
    ]
    worker_params = [
        (1, 4),
        (2, 3)
    ]
    # Both workers should be matched to job 2
    InferenceJob.mock_jobs(job_params)
    Worker.mock_workers(worker_params)

    matched_jobs = match_jobs()

    assert matched_jobs == [[1, 1], [2, 1]]

def test_match_jobs_5(setup_mock_data):
    # job_id, model_required_gpu, desired_workers, activated_workers
    job_params = [
        (1, 2, 3, 1),
        (2, 20, 4, 0)
    ]
    worker_params = [
        (1, 10),
        (2, 10),
        (3, 23),
        (4, 23),
        (5, 23),
        (6, 23),
    ]
    # Both workers should be matched to job 2
    InferenceJob.mock_jobs(job_params)
    Worker.mock_workers(worker_params)

    matched_jobs = match_jobs()

    assert matched_jobs == [[3, 2], [4, 2], [5,2], [6,2], [1, 1], [2, 1]]

def test_match_jobs_6(setup_mock_data):
    # job_id, model_required_gpu, desired_workers, activated_workers
    job_params = [
        (1, 2, 3, 2),
        (2, 20, 4, 0)
    ]
    worker_params = [
        (1, 10),
        (2, 10),
        (3, 23),
        (4, 23),
        (5, 23),
        (6, 23),
    ]
    # Both workers should be matched to job 2
    InferenceJob.mock_jobs(job_params)
    Worker.mock_workers(worker_params)

    matched_jobs = match_jobs()

    assert matched_jobs == [[3, 2], [4, 2], [5,2], [6,2], [1, 1]]

def test_match_jobs_7(setup_mock_data):
    # job_id, model_required_gpu, desired_workers, activated_workers
    job_params = [
        (1, 2, 3, 3),
        (2, 24, 4, 0)
    ]
    worker_params = [
        (1, 10),
        (2, 10),
        (3, 23),
        (4, 23),
        (5, 23),
        (6, 23),
    ]
    # Both workers should be matched to job 2
    InferenceJob.mock_jobs(job_params)
    Worker.mock_workers(worker_params)

    matched_jobs = match_jobs()

    assert matched_jobs == []