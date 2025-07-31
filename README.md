# quiz-master-v2
It is a multi-user app (one requires an administrator and other users) that acts as an exam preparation site for multiple courses. (Version 2)

## Quick Setup

### Backend
```bash
cd backend
python -m venv venv 
venv\\Scripts\\activate
pip install -r requirements.txt
# Start Flask API
python app.py
```

### Celery & Redis (for batch jobs)
1. Start Redis locally (default `redis://localhost:6379/0`).
2. In a new terminal, start a Celery worker:
```bash
cd backend
venv/Scripts/activate
celery -A application.tasks worker --loglevel=info --pool=solo
```

This will run:
- **Daily reminders** at 19:00 IST
- **Monthly activity reports** on the 1st at 08:00 IST

Emails are written to `backend/application/outbox/` as `.eml` files for local demo. Configure SMTP later if desired.

3. (Recommended) Scheduled/User or Admin triggered jobs:
In your original terminal, run:
```bash
flask shell
```
1. Daily Email Reminder
from application.tasks import send_daily_reminders
send_daily_reminders.delay()

📍 Check the outbox/ folder — .eml files should be created for each user.

2.Monthly Activity Report
from application.tasks import send_monthly_reports
send_monthly_reports.delay()

📍 Check the outbox/ folder again — .eml files should contain summary per user.

3.Export CSV of a User’s Quizzes
from application.tasks import export_user_quizzes_csv
export_user_quizzes_csv.delay(USER_ID)  # Replace USER_ID with an actual user ID

📍 Check exports/ folder — CSV file should appear with quiz data.

4.Export Admin Overview CSV
from application.tasks import export_admin_overview_csv
export_admin_overview_csv.delay()

📍 Check exports/ — File should show all users' quiz count and average scores.


### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Default Admin
- username: `admin@gmail.com`
- password: `987`

