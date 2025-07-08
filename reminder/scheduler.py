from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta

scheduler = BackgroundScheduler()
scheduler.start()

def schedule_reminder(info, start_date, start_time, callback):
    dt = datetime.combine(start_date, start_time)
    freq = info["frequency_per_day"]
    duration = info["duration_days"]

    for dose in range(duration * freq):
        run_time = dt + timedelta(hours=(24 / freq) * dose)
        job_id = f"{info['medicine']}_{run_time.strftime('%Y%m%d%H%M')}"

        scheduler.add_job(
            callback,
            'date',
            run_date=run_time,
            args=[info],
            id=job_id
        )
        print(f"⏰ Scheduled: {info['medicine']} at {run_time}")
