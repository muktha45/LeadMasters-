# Frontend (React + Vite)

### Quick start
```bash
cd frontend
npm install
npm run dev
```
- The app assumes the backend runs at `http://localhost:8000`.
- To change API base, set `VITE_API` env var, e.g. `VITE_API=http://127.0.0.1:8000 npm run dev`.


# Backend (FastAPI)

### Quick start (SQLite for demo)
```bash
cd backend
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

### Use PostgreSQL
- Start Postgres and create a DB `leadmasters`
- Set `DATABASE_URL` in `.env` like:
```
DATABASE_URL=postgresql+psycopg2://postgres:password@localhost:5432/leadmasters
```
- Run the server again.

### Seed questions
```
POST http://localhost:8000/dev/seed
```

### Auth
- Register: `POST /auth/register` with JSON `{ "email": "...", "password": "..." }`
- Login: `POST /auth/login` form fields `username` and `password`
- Copy the returned token and use `Authorization: Bearer <token>`

### Exam Flow
- `GET /exam/start?limit=10` -> returns `session_id` and randomized questions (no correct answers)
- Client shows countdown (default 30 min). If time ends, auto-submit.
- `POST /exam/submit` with `{ "session_id": X, "answers": { "qid": "a" } }`
- `GET /exam/result/{session_id}` returns score and total

### Curl examples
```bash
curl -X POST http://localhost:8000/auth/register -H "Content-Type: application/json" -d '{"email":"a@a.com","password":"pass"}'
curl -X POST http://localhost:8000/auth/login -H "Content-Type: application/x-www-form-urlencoded" -d 'username=a@a.com&password=pass'

TOKEN=...

curl -X POST http://localhost:8000/dev/seed
curl -H "Authorization: Bearer $TOKEN" "http://localhost:8000/exam/start?limit=5"
curl -X POST http://localhost:8000/exam/submit -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d '{"session_id":1,"answers":{"1":"b","2":"c"}}'
curl -H "Authorization: Bearer $TOKEN" "http://localhost:8000/exam/result/1"
```

### Notes
- Beginner-style, simple table design: options stored as columns and correct option as a single letter.
- JWT implementation uses `python-jose` and `passlib`.
- For production, remove `/dev/seed` and lock CORS origins.



# LeadMasters-
Fresher Selection Assessment. Developed a functional exam-taking interface (student-side only), which tests their skills in React.js, backend APIs, and database integration for Frontend: React.js, Backend: Python with Fast API, Database: PostgreSQL .
