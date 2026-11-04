# LearnMate — AI-Powered Personalized Learning Assistant

> A complete full-stack web application with 10 Gang-of-Four design patterns, an AI chatbot, adaptive quizzes, personalized study plans, and real-time progress tracking.

![LearnMate](https://img.shields.io/badge/LearnMate-1.0.0-2D6A4F?style=for-the-badge)
![Next.js](https://img.shields.io/badge/Next.js-14-black?style=for-the-badge&logo=next.js)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?style=for-the-badge&logo=fastapi)
![Supabase](https://img.shields.io/badge/Supabase-PostgreSQL-3ECF8E?style=for-the-badge&logo=supabase)
![Gemini](https://img.shields.io/badge/Google-Gemini_AI-4285F4?style=for-the-badge&logo=google)

---

## Design Patterns Implemented

| Pattern | Category | File | Used By |
|---------|----------|------|---------|
| Factory Method | Creational | `backend/app/patterns/creational/resource_factory.py` | Resource creation, quiz generation |
| Builder | Creational | `backend/app/patterns/creational/study_plan_builder.py` | Study plan wizard |
| Singleton | Creational | `backend/app/patterns/creational/singletons.py` | Auth, notifications, AI engine |
| Facade | Structural | `backend/app/patterns/structural/learning_facade.py` | Dashboard, recommendations |
| Adapter | Structural | `backend/app/patterns/structural/external_adapters.py` | Gemini AI, external resources |
| Decorator | Structural | `backend/app/patterns/structural/module_decorators.py` | Topic content enhancement |
| Observer | Behavioral | `backend/app/patterns/behavioral/notification_observer.py` | Notifications on user events |
| Strategy | Behavioral | `backend/app/patterns/behavioral/recommendation_strategy.py` | Personalized recommendations |
| State | Behavioral | `backend/app/patterns/behavioral/topic_state.py` | Topic progress states |
| Command | Behavioral | `backend/app/patterns/behavioral/commands.py` | Quiz generation, plan creation, progress updates |

---

## Tech Stack

- **Frontend**: Next.js 14 (App Router), TypeScript, Tailwind CSS, shadcn/ui, Recharts
- **Backend**: FastAPI (Python 3.11+), Pydantic v2, Uvicorn
- **Database & Auth**: Supabase (PostgreSQL + Row Level Security + Supabase Auth)
- **AI**: Google Gemini API (`gemini-2.0-flash`)
- **Deployment**: Vercel (frontend) + Render (backend) + Supabase Cloud

---

## Project Structure

```
learnmate/
├── frontend/                     # Next.js 14 App Router
│   ├── app/                      # Pages and layouts
│   ├── components/               # Reusable UI components
│   ├── lib/                      # API client, Supabase client, utilities
│   └── .env.example
├── backend/                      # FastAPI backend
│   ├── app/
│   │   ├── patterns/             # All 10 design pattern implementations
│   │   │   ├── creational/       # Factory Method, Builder, Singleton
│   │   │   ├── structural/       # Facade, Adapter, Decorator
│   │   │   └── behavioral/       # Observer, Strategy, State, Command
│   │   ├── models/               # Pydantic schemas
│   │   ├── routers/              # API endpoints (12 routers)
│   │   ├── services/             # Database service layer
│   │   └── main.py               # App entry point
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── supabase/
│   ├── schema.sql                # Full DDL + RLS policies
│   └── seed.sql                  # Demo data (3 users, 5 courses, 45 topics)
├── render.yaml                   # Render.com deployment config
├── vercel.json                   # Vercel deployment config
└── README.md
```

---

## Local Development Setup

### Prerequisites

- Node.js 18+
- Python 3.11+
- A [Supabase](https://supabase.com) project (free tier)
- A [Google AI Studio](https://aistudio.google.com) API key for Gemini

### Step 1: Supabase Setup

1. Create a new Supabase project at [supabase.com](https://supabase.com)
2. Go to **Settings → API** and copy:
   - **Project URL** → `SUPABASE_URL`
   - **anon/public key** → `SUPABASE_ANON_KEY`
   - **service_role key** → `SUPABASE_SERVICE_ROLE_KEY`

3. Go to **SQL Editor** and run `supabase/schema.sql` (paste the entire file and click Run)

4. Enable Google Provider in Supabase:
   - Go to **Authentication → Providers → Google**
   - Toggle **Enable Google provider**
   - Input your **Google Client ID** & **Google Client Secret** (from Google Cloud Console OAuth 2.0 Client IDs)
   - Add `http://localhost:3000/auth/callback` to **URL Configuration → Redirect URLs**

5. Create 3 demo users in **Authentication → Users → Add user**:
   ```
   alex@learnmate.demo  / LearnMate2024!
   priya@learnmate.demo / LearnMate2024!
   sam@learnmate.demo   / LearnMate2024!
   ```

6. Copy the UUID of each user from the Auth dashboard. Open `supabase/seed.sql` and replace:
   ```sql
   user_alex  UUID := '11111111-1111-1111-1111-111111111111';  -- replace with Alex's UUID
   user_priya UUID := '22222222-2222-2222-2222-222222222222';  -- replace with Priya's UUID
   user_sam   UUID := '33333333-3333-3333-3333-333333333333';  -- replace with Sam's UUID
   ```

7. Run `supabase/seed.sql` in the SQL editor.

### Step 2: Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your actual values:
#   SUPABASE_URL=https://your-project.supabase.co
#   SUPABASE_ANON_KEY=your-anon-key
#   SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
#   GEMINI_API_KEY=your-gemini-api-key
#   JWT_SECRET=any-long-random-string

# Start backend
uvicorn app.main:app --reload --port 8000
```

Backend will be available at: http://localhost:8000  
API docs at: http://localhost:8000/docs

### Step 3: Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Install shadcn/ui components
npx shadcn@latest init  # follow prompts
npx shadcn@latest add button card dialog tabs input label badge progress

# Configure environment
cp .env.example .env.local
# Edit .env.local:
#   NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
#   NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
#   NEXT_PUBLIC_API_URL=http://localhost:8000

# Start frontend
npm run dev
```

Frontend will be available at: http://localhost:3000

### Demo Login

Once seed data is loaded, log in with:
- **Email**: `alex@learnmate.demo`
- **Password**: `LearnMate2024!`

---

## Deployment

### Frontend → Vercel

1. Push to GitHub
2. Import project at [vercel.com](https://vercel.com)
3. Set environment variables in Vercel dashboard:
   ```
   NEXT_PUBLIC_SUPABASE_URL=
   NEXT_PUBLIC_SUPABASE_ANON_KEY=
   NEXT_PUBLIC_API_URL=https://learnmate-backend.onrender.com
   ```
4. Deploy. Vercel auto-detects Next.js.

### Backend → Render

1. Push backend to GitHub (or use monorepo)
2. Create a new **Web Service** at [render.com](https://render.com)
3. Connect your GitHub repo, set root directory to `backend`
4. Set environment variables:
   ```
   SUPABASE_URL=
   SUPABASE_ANON_KEY=
   SUPABASE_SERVICE_ROLE_KEY=
   GEMINI_API_KEY=
   JWT_SECRET=
   FRONTEND_URL=https://your-app.vercel.app
   ```
5. Build command: `pip install -r requirements.txt`
6. Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

Alternatively, use the included `render.yaml` for one-click deployment.

### Backend → Docker (alternative)

```bash
cd backend
docker build -t learnmate-backend .
docker run -p 8000:8000 --env-file .env learnmate-backend
```

---

## Features

| Feature | Description |
|---------|-------------|
| 🔐 **Auth** | Supabase email/password signup + login + profile onboarding |
| 📊 **Dashboard** | Recharts progress overview, streaks, quiz score trends |
| 🤖 **AI Chatbot** | Persistent chat with Gemini, grounded in your actual progress |
| 🎯 **Adaptive Quizzes** | AI-generated quizzes matched to your mastery level |
| 📅 **Study Plans** | Wizard UI + calendar view with checkable items |
| ✨ **Recommendations** | Strategy-pattern recommendations with "why" explanations |
| 📈 **Progress Tracking** | Visual topic state trail (Not Started → Mastered) |
| 🔮 **Predictions** | AI-powered performance predictions per topic |
| 🔔 **Notifications** | Bell icon, unread count, mark as read |
| 👥 **Groups** | Create/join study groups, shared leaderboard |
| 🏆 **Achievements** | Badge system tied to Gamification decorator |

---

## API Documentation

Full interactive documentation available at `http://localhost:8000/docs` (Swagger UI).

Key endpoints:
- `GET  /health` — System health + AI availability
- `POST /auth/signup` — Create account
- `POST /auth/login` — Login
- `GET  /dashboard?user_id=...` — Dashboard data (Facade pattern)
- `GET  /courses` — List all courses
- `GET  /topics/course/{id}?user_id=...` — Topics with progress
- `POST /quizzes/generate?user_id=...` — Generate AI quiz (Command pattern)
- `POST /quizzes/attempt?user_id=...` — Submit quiz attempt
- `GET  /recommendations?user_id=...` — Personalized recs (Strategy pattern)
- `POST /study-plans?user_id=...` — Create plan (Builder pattern)
- `POST /chat/send?user_id=...` — Chat with AI
- `GET  /notifications?user_id=...` — Get notifications

---

## License

MIT © LearnMate 2024
