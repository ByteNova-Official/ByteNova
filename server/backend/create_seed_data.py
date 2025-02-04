from app import db, app
from app.models.inference_job import InferenceJob
from app.models.worker import Worker
from app.models.api_key import ApiKey
from app.models.user import User
from app.models.model import Model

def create_seed_data():
    if User.query.filter_by(email="demo@example.com").first():
        demo_user = User.query.filter_by(email="demo@example.com").first()
        api_key = demo_user.api_keys[0]
        model1 = demo_user.models[0]
        model2 = demo_user.models[1]
        inference_job1 = demo_user.inference_jobs[0]
        inference_job2 = demo_user.inference_jobs[1]
        worker1 = demo_user.workers[0]
        worker2 = demo_user.workers[1]

    else:
        # Create a user named "demo" with password "demoAdmin@1234"
        demo_user = User(
            name="demo",
            email="demo@example.com",
            password="demoAdmin@1234"
            # Add other user details here
        )
        db.session.add(demo_user)
        db.session.commit()

        # Create an API key for the user
        api_key = ApiKey(
            user_id=demo_user.id
        )
        db.session.add(api_key)
        db.session.commit()

        # Create two models belonging to the user
        model1 = Model(
            name="llama7b",
            version="1.0",
            user_id=demo_user.id,
            model_type="text_to_text",
            artifact="https://huggingface.co/tiiuae/falcon-7b"
            # Add other model details here
        )
        db.session.add(model1)

        model2 = Model(
            name="stablediffusion",
            version="2.1",
            user_id=demo_user.id,
            model_type="text_to_image",
            artifact="https://huggingface.co/stabilityai/stable-diffusion-2-1"
            # Add other model details here
        )
        db.session.add(model2)
        db.session.commit()

        # Create two inference jobs, one for each model
        inference_job1 = InferenceJob(
            job_name="inference_job_1_falcon7b",
            status="pending",
            enabled=True,
            model_id=model1.id,
            user_id=demo_user.id
            # Add other inference job details here
        )
        db.session.add(inference_job1)

        inference_job2 = InferenceJob(
            job_name="inference_job_2_sd",
            status="pending",
            enabled=True,
            model_id=model2.id,
            user_id=demo_user.id
            # Add other inference job details here
        )
        db.session.add(inference_job2)
        db.session.commit()

        # Create two workers, one for each inference job
        worker1 = Worker(
            name="worker_1_llm",
            status="active",
            connected=True,
            working_on=inference_job1.id,
            user_id=demo_user.id
            # Add other worker details here
        )
        db.session.add(worker1)

        worker2 = Worker(
            name="worker_2_llm",
            status="active",
            connected=True,
            working_on=inference_job1.id,
            user_id=demo_user.id
            # Add other worker details here
        )
        db.session.add(worker2)
        db.session.commit()

        worker3 = Worker(
            name="worker_3_sd",
            status="active",
            connected=True,
            working_on=inference_job2.id,
            user_id=demo_user.id
            # Add other worker details here
        )
        db.session.add(worker3)
        db.session.commit()

    # Print the objects with generated UUID values
    print("User UUID:", demo_user.id)
    print("API Key UUID:", api_key.key)
    print("")
    print("Model 1 UUID:", model1.id)
    print("Inference Job 1 UUID:", inference_job1.id)
    print("Worker 1 UUID:", worker1.id)
    print("")
    print("Model 2 UUID:", model2.id)
    print("Inference Job 2 UUID:", inference_job2.id)
    print("Worker 2 UUID:", worker2.id)
    print("")

with app.app_context():
    create_seed_data()
