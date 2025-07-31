# quiz-master-v2
It is a multi-user app (one requires an administrator and other users) that acts as an exam preparation site for multiple courses. (Version 2)


## Quick Setup (Updated 2025-07-30)

### Backend
```bash
cd backend
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
# Start Flask API
python app.py
```

### Celery & Redis (for batch jobs)
1. Start Redis locally (default `redis://localhost:6379/0`).
2. In a new terminal, start a Celery worker:
```bash
cd backend
source .venv/bin/activate
celery -A application.celery_app.celery worker --loglevel=info
```
3. (Recommended) Start Celery beat for scheduled jobs:
```bash
celery -A application.celery_app.celery beat --loglevel=info
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

---

## What was fixed
- **422 UNPROCESSABLE ENTITY** on `/api/dashboard`, `/api/admin/add_subject`, `/api/admin/show_users` was caused by JWT `sub` claim not being a string (PyJWT >= 2.8 enforces string). Fixed by:
  - issuing tokens with `create_access_token(identity=str(user.id))`;
  - casting back to `int` in `user_lookup_loader`.
- Added **Redis caching** for `/api/dashboard` and `/api/search`.
- Implemented **Celery tasks**:
  - Daily reminders
  - Monthly activity reports (HTML/text)
  - User/Admin CSV exports with `/api/user/export_csv`, `/api/admin/export_csv` and `/api/task_status/<id>`.
- Added `/api/exports` to list generated CSV files.

### Default Admin
- username: `admin@gmail.com`
- password: `987`

