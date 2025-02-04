# File: run.py
import os
from app import app, db, socketio
from app.load_jobs import load_invocations_to_redis

from flask_apscheduler import APScheduler
from app.job_matcher import match_jobs
from app.auto_scaler import auto_scale

if __name__ == '__main__':
    # Initialize and configure scheduler
    scheduler = APScheduler()
    scheduler.init_app(app)
    scheduler.start()


    @scheduler.task('interval', id='do_job_matching', seconds=5, misfire_grace_time=900)
    def scheduled_match_jobs():
        # print("Starting job matching...")
        with app.app_context():
            match_jobs()


    @scheduler.task('interval', id='auto_scaling', seconds=10, misfire_grace_time=900)
    def scheduled_match_jobs():
        with app.app_context():
            auto_scale()

            # This is only used when running locally


    with app.app_context():
        db.create_all()
        try:
            load_invocations_to_redis()
        except:
            pass

    socketio.run(app, host='0.0.0.0', port=os.getenv("PORT", 5000), allow_unsafe_werkzeug=True)
