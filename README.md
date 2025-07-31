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
3. (Recommended) Start Celery beat for scheduled jobs:
```bash
celery -A application.tasks worker --loglevel=info --pool=solo
```
This will run:
- **Daily reminders** at 19:00 IST
- **Monthly activity reports** on the 1st at 08:00 IST

Emails are written to `backend/application/outbox/` as `.eml` files for local demo. Configure SMTP later if desired.

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Default Admin
- username: `admin@gmail.com`
- password: `987`

