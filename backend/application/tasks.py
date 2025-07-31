import os, csv, io
from datetime import datetime, date
from celery.schedules import crontab
from celery.utils.log import get_task_logger
from celery import shared_task
from .celery_app import celery, create_app_context
from .database import db
from .models import User, Quiz, Score, Subject, Chapter

logger = get_task_logger(__name__)

OUTBOX_DIR = os.path.join(os.path.dirname(__file__), "outbox")
EXPORTS_DIR = os.path.join(os.path.dirname(__file__), "exports")
os.makedirs(OUTBOX_DIR, exist_ok=True)
os.makedirs(EXPORTS_DIR, exist_ok=True)

def write_mail(to, subject, body):
    fname = f"{datetime.now().strftime('%Y%m%d-%H%M%S')}-{to.replace(
        '@','_')}.eml"
    path = os.path.join(OUTBOX_DIR, fname)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(f"To: {to}\nSubject: {subject}\n\n{body}")
    logger.info("Wrote email to %s", path)
    return path

@celery.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    # Daily reminders at 7:00 PM IST
    sender.add_periodic_task(
        crontab(hour=13, minute=30), 
        send_daily_reminders.s(),
        name="daily-reminders-1900IST",
    )
    # Monthly report on 1st day at 08:00 AM IST
    sender.add_periodic_task(
        crontab(hour=2, minute=30, day_of_month=1),
        send_monthly_reports.s(),
        name="monthly-reports-0800IST",
    )

@celery.task
def send_daily_reminders():
    app = create_app_context()
    today = date.today()
    users = User.query.filter(User.role == 'user').all()
    for u in users:
        upcoming = Quiz.query.filter(Quiz.date_of_quiz >= today).count()
        body = f"Hello {u.full_name or u.username}, you have {upcoming} upcoming quizzes. Visit the app to practice!"
        write_mail(u.username, "Daily Quiz Reminder", body)
    return {"status": "ok", "count": len(users)}

@celery.task
def send_monthly_reports():
    app = create_app_context()
    users = User.query.filter(User.role == 'user').all()
    for u in users:
        scores = Score.query.filter_by(user_id=u.id).all()
        total = len(scores)
        avg = sum(s.total_score for s in scores)/total if total else 0
        body_lines = [f"Monthly Activity Report for {u.full_name or u.username}", "", f"Quizzes taken: {total}", f"Average score: {avg:.2f}"]
        write_mail(u.username, "Monthly Activity Report", "\n".join(body_lines))
    return {"status": "ok", "users": len(users)}

@celery.task
def export_user_quizzes_csv(user_id):
    app = create_app_context()
    user = User.query.get(user_id)
    if not user:
        return {"error": "user not found"}
    scores = db.session.query(Score, Quiz, Chapter).join(Quiz, Score.quiz_id==Quiz.id).join(Chapter, Quiz.chapter_id==Chapter.id).filter(Score.user_id==user_id).all()
    file_path = os.path.join(EXPORTS_DIR, f"user-{user_id}-quizzes-{datetime.now().strftime('%Y%m%d-%H%M%S')}.csv")
    with open(file_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["quiz_id","chapter_id","date_of_quiz","score","remarks"])  
        for s,q,c in scores:
            writer.writerow([q.id, c.id, q.date_of_quiz, s.total_score, ""])
    logger.info("Exported %s", file_path)
    return {"file": file_path}

@celery.task
def export_admin_overview_csv():
    app = create_app_context()
    users = User.query.filter(User.role=='user').all()
    file_path = os.path.join(EXPORTS_DIR, f"admin-overview-{datetime.now().strftime('%Y%m%d-%H%M%S')}.csv")
    with open(file_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["user_id","username","quizzes_taken","avg_score"]) 
        for u in users:
            scores = Score.query.filter_by(user_id=u.id).all()
            total = len(scores)
            avg = sum(s.total_score for s in scores)/total if total else 0
            writer.writerow([u.id, u.username, total, f"{avg:.2f}"])
    logger.info("Exported %s", file_path)
    return {"file": file_path}