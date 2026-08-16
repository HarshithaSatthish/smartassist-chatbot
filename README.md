# SmartAssist AI Chatbot

A clean, internship-ready web chatbot built with **React** and **FastAPI**. SmartAssist answers common greetings and FAQs from saved replies, then falls back to an AI API for everything else. Users can register, log in, and reopen past chats.

---

## Project description

SmartAssist is a beginner-friendly full-stack chatbot. The frontend is a professional chat UI with a login screen and a chat-history sidebar. The backend decides whether to use a predefined answer or call an AI provider, then saves each conversation for the logged-in user.

Users and chats are stored as local JSON files (`backend/data/users.json` and `backend/data/conversations.json`). This is demo storage, not a database — easy to swap later. No MongoDB is required.

This project is designed for internships, portfolio demos, and GitHub.

---

## Features

- Register and log in with username + password
- JWT session (token stored in the browser)
- Chat history sidebar: open, start new, or delete a conversation
- Clean, responsive chat interface for desktop and mobile
- Airbnb-inspired UI (Rausch accent, pill composer, rounded cards)
- Predefined answers for greetings, help, thanks, and FAQs
- AI API fallback for questions that are not saved
- Loading (typing) indicator and clear error messages
- API key stored only on the backend in `.env`
- Easy to switch AI providers later (OpenAI-compatible API)

---

## Technology stack

| Layer | Tools |
| --- | --- |
| Frontend | React, Vite, JavaScript, CSS, Fetch API |
| Backend | Python, FastAPI, Pydantic, Uvicorn, PyJWT, passlib (bcrypt) |
| Storage | JSON files under `backend/data/` (demo persist layer) |
| AI | OpenAI-compatible Chat Completions API (OpenAI, Groq, or similar) |
| Config | `.env` with `python-dotenv` |

---

## Architecture

```text
                    SMARTASSIST
                         │
                         ▼
                 React Frontend
                    (login + chat)
                         │
                         │ JWT + POST /chat
                         ▼
                  FastAPI Backend
                         │
          ┌──────────────┼──────────────┐
          ▼              ▼              ▼
        Auth        Chatbot         JSON files
     (register /    Processing     users.json
      login)             │         conversations.json
               ┌─────────┴─────────┐
               ▼                   ▼
       Predefined Response       AI API
               │                   │
               └─────────┬─────────┘
                         ▼
                    Bot Response
                         │
                         ▼
              Saved chat history
```

The React app never talks to the AI provider directly. Only FastAPI uses the secret API key. Passwords are hashed; tokens are signed with `SECRET_KEY`.

---

## Project structure

```text
smartassist-chatbot/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ChatWindow.jsx
│   │   │   ├── ConversationList.jsx
│   │   │   ├── LoginPage.jsx
│   │   │   ├── Message.jsx
│   │   │   ├── MessageInput.jsx
│   │   │   └── Header.jsx
│   │   ├── services/
│   │   │   └── chatbotApi.js
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── index.css
│   ├── index.html
│   ├── vite.config.js
│   ├── vercel.json
│   └── package.json
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── chatbot.py
│   │   ├── responses.py
│   │   ├── models.py
│   │   ├── auth.py
│   │   └── storage.py
│   ├── data/
│   │   └── .gitkeep          (users.json / conversations.json are gitignored)
│   ├── requirements.txt
│   └── .env
├── DESIGN.md
├── render.yaml
├── README.md
└── .gitignore
```

A few extra files exist for Vite (`index.html`, `vite.config.js`) and Python packaging (`app/__init__.py`). `.env.example` files are included so others know which variables to set, without real secrets.

---

## Installation

You need these tools installed first:

1. **Python 3.10+** — [https://www.python.org/downloads/](https://www.python.org/downloads/)
   - During setup on Windows, tick **Add python.exe to PATH**.
2. **Node.js 18+** (includes npm) — [https://nodejs.org/](https://nodejs.org/)
3. **Git** — [https://git-scm.com/downloads](https://git-scm.com/downloads)
4. **VS Code** (optional, recommended)

Open **PowerShell** and check:

```powershell
python --version
node --version
npm --version
git --version
```

If a command is not found, install that tool and open a new PowerShell window.

Then go to the project folder:

```powershell
cd C:\Users\harsh\Desktop\CHATBOT\smartassist-chatbot
```

---

## Backend setup

Run these commands in PowerShell from the project root.

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

If PowerShell blocks the virtual environment, run this once, then try again:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Copy the example environment file if `.env` is missing:

```powershell
copy .env.example .env
```

---

## Frontend setup

Open a **second** PowerShell window.

```powershell
cd C:\Users\harsh\Desktop\CHATBOT\smartassist-chatbot\frontend
npm install
```

The frontend reads the backend URL from `frontend/.env`:

```text
VITE_API_URL=http://localhost:8000
```

---

## Environment variables

### Backend (`backend/.env`)

| Variable | Meaning | Example |
| --- | --- | --- |
| `AI_API_KEY` | Secret key for the AI provider. Never put this in React. | `sk-...` |
| `AI_BASE_URL` | OpenAI-compatible API base URL | `https://api.openai.com/v1` |
| `AI_MODEL` | Model name | `gpt-4o-mini` |
| `AI_TIMEOUT` | Request timeout in seconds | `30` |
| `SECRET_KEY` | Random string used to sign login tokens | a long random value |

**OpenAI**

1. Create an account at [https://platform.openai.com](https://platform.openai.com)
2. Create an API key
3. Paste it into `backend/.env`:

```text
AI_API_KEY=your_openai_key_here
AI_BASE_URL=https://api.openai.com/v1
AI_MODEL=gpt-4o-mini
```

**Free alternative: Groq**

1. Create an account at [https://console.groq.com](https://console.groq.com)
2. Create an API key
3. Use:

```text
AI_API_KEY=your_groq_key_here
AI_BASE_URL=https://api.groq.com/openai/v1
AI_MODEL=llama-3.1-8b-instant
```

If `AI_API_KEY` is empty, greetings and FAQs still work. Unmatched questions get a friendly “AI is not configured” message.

Generate a random `SECRET_KEY` (do not copy a real secret into GitHub or this README):

```powershell
python -c "import secrets; print(secrets.token_hex(32))"
```

Paste the result into `backend/.env` as `SECRET_KEY=...`. `.env.example` only has a placeholder.

### Frontend (`frontend/.env`)

```text
VITE_API_URL=http://localhost:8000
```

Do not put `AI_API_KEY` in any frontend file.

---

## Running the application

You need **two terminals**.

### Terminal 1 — backend

```powershell
cd C:\Users\harsh\Desktop\CHATBOT\smartassist-chatbot\backend
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --port 8000
```

Leave this window open. The API is at `http://localhost:8000`.

Check health in a browser: `http://localhost:8000/health`

### Terminal 2 — frontend

```powershell
cd C:\Users\harsh\Desktop\CHATBOT\smartassist-chatbot\frontend
npm run dev
```

Open the URL Vite prints, usually `http://localhost:5173`.

### Register, log in, and chat history

1. Create an account (username + password, at least 6 characters).
2. You are logged in automatically. The token is saved in `localStorage`, so a browser refresh keeps you signed in.
3. Send a message. The first message becomes the conversation title in the sidebar.
4. Click **New chat** to start another conversation.
5. Click a past chat to reload its messages. **Delete** removes that chat.
6. **Logout** (header) returns you to the login screen.

User accounts live in `backend/data/users.json`. Conversations live in `backend/data/conversations.json`. These files are local demo storage and are gitignored.

---

## API endpoints

| Method | Path | Auth | Purpose |
| --- | --- | --- | --- |
| `GET` | `/health` | No | Health check |
| `POST` | `/auth/register` | No | Create an account |
| `POST` | `/auth/login` | No | Log in and receive a token |
| `GET` | `/auth/me` | Bearer | Current user |
| `GET` | `/conversations` | Bearer | List this user's chats |
| `POST` | `/conversations` | Bearer | Create an empty chat |
| `GET` | `/conversations/{id}` | Bearer | Load messages |
| `DELETE` | `/conversations/{id}` | Bearer | Delete a chat |
| `POST` | `/chat` | Bearer | Send a message (optional `conversation_id`) |

Health response:

```json
{
  "status": "ok",
  "service": "SmartAssist API"
}
```

Chat request:

```json
{
  "message": "Hello",
  "conversation_id": null
}
```

Send `Authorization: Bearer <access_token>`. If `conversation_id` is omitted, a new conversation is created.

Chat response:

```json
{
  "reply": "Hello! I'm SmartAssist, your AI assistant. Ask me about our services, working hours, or any general question.",
  "source": "predefined",
  "conversation_id": "uuid-here"
}
```

Login / register request:

```json
{
  "username": "harsh",
  "password": "secret1"
}
```

Login / register response:

```json
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "username": "harsh"
}
```

`source` is `"predefined"` or `"ai"`.

---

## Screenshots

Add screenshots here after you run the app:

1. Login / register screen
2. Chat home screen with the history sidebar
3. A greeting reply
4. An FAQ reply (working hours / contact / services)
5. An AI fallback answer
6. Mobile layout (Chats button opens history)

Suggested files: `docs/home.png`, `docs/faq.png`, `docs/ai-reply.png`

---

## Testing

### Greetings

| Input | Expected |
| --- | --- |
| `Hello` | Predefined greeting |
| `Hi` | Predefined greeting |
| `Hey there` | Predefined greeting |
| `Good morning` | Predefined greeting |

### FAQ

| Input | Expected |
| --- | --- |
| `What are your working hours?` | Hours reply, `source: predefined` |
| `How can I contact you?` | Contact reply |
| `What services do you provide?` | Services reply |

### General

| Input | Expected |
| --- | --- |
| `Thank you` | Thanks reply |
| `Bye` | Goodbye reply |
| `Help` | Help reply |

### AI fallback

These should **not** match saved FAQs. They go to the AI API if a key is set:

| Input | Expected |
| --- | --- |
| `What is machine learning?` | AI explanation, `source: ai` |
| `Explain neural networks.` | AI explanation |
| `What is computer vision?` | AI explanation |

If the key is missing, you still get a friendly fallback. Greetings and FAQs continue to work.

`Hi, can you explain machine learning?` should go to AI, not the short greeting reply.

### Error cases

| Case | Expected |
| --- | --- |
| Empty input | Send button stays disabled. Backend also rejects blank messages with `Please enter a message.` |
| Missing / invalid login token | `POST /chat` and history routes return `401` and the UI shows the login screen |
| Backend offline | Frontend shows: `Unable to connect to SmartAssist. Please check whether the backend server is running.` |
| AI API unavailable | Friendly fallback: `Sorry, I couldn't process that question right now. Please try again later.` |

---

## Future improvements

- Save conversations in MongoDB (replace the JSON files in `storage.py`)
- Streaming AI replies
- Voice input
- Dark mode
- Stronger password rules / email verification

The chatbot functions and `storage.py` are already separated so a database can be added later without rewriting the UI.

---

## Learning outcomes

- Building a React + Vite frontend
- Creating a FastAPI backend with Pydantic validation
- Separating UI, API calls, and chatbot logic
- Using `.env` files so secrets stay off GitHub
- Simple login with hashed passwords and JWT
- File-based persistence you can swap for a database later
- Keyword matching vs AI fallback
- CORS, error handling, and a simple production-ready layout

---

## Deployment

Deploy the **backend first**, then the **frontend**. The React app needs the live API URL at build time.

### 1. Push the project to GitHub

```powershell
cd C:\Users\harsh\Desktop\CHATBOT\smartassist-chatbot
git init
git add .
git commit -m "Add Airbnb-inspired UI and deployment config"
git branch -M main
git remote add origin <GITHUB_REPOSITORY_URL>
git push -u origin main
```

Never commit `.env`. Your Groq/OpenAI key must stay on the hosting dashboard only.

### 2. Deploy the backend on Render

1. Go to [https://render.com](https://render.com) and sign in with GitHub.
2. Click **New +** → **Web Service**.
3. Select the `smartassist-chatbot` repository.
4. Use these settings:

| Setting | Value |
| --- | --- |
| Root Directory | `backend` |
| Runtime | Python 3 |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |

5. Add environment variables (do not type a real key into GitHub):

```text
AI_API_KEY=your_groq_or_openai_key
AI_BASE_URL=https://api.groq.com/openai/v1
AI_MODEL=llama-3.1-8b-instant
AI_TIMEOUT=30
SECRET_KEY=your_long_random_string
CORS_ORIGINS=https://your-frontend.vercel.app
```

Leave `CORS_ORIGINS` as a placeholder until Vercel gives you a URL, then come back and update it.

Generate `SECRET_KEY` locally and paste it into the Render dashboard. Do not commit it.

**Demo storage on Render:** `users.json` and `conversations.json` live on the server disk. On Render's free plan those files are **ephemeral** — they reset when the service sleeps, redeploys, or moves to another instance. Accounts and chat history will not persist unless you add a persistent disk (or later swap `storage.py` for a database).

6. Click **Deploy**. When it finishes, copy the backend URL, for example:

```text
https://smartassist-api.onrender.com
```

7. Open this in a browser to confirm:

```text
https://smartassist-api.onrender.com/health
```

You should see `{"status":"ok","service":"SmartAssist API"}`.

The first request on Render's free plan can take 30–60 seconds while the service wakes up.

### 3. Deploy the frontend on Vercel

1. Go to [https://vercel.com](https://vercel.com) and sign in with GitHub.
2. Click **Add New** → **Project** and import `smartassist-chatbot`.
3. Use these settings:

| Setting | Value |
| --- | --- |
| Root Directory | `frontend` |
| Framework Preset | Vite |
| Build Command | `npm run build` |
| Output Directory | `dist` |

4. Add one environment variable:

```text
VITE_API_URL=https://smartassist-api.onrender.com
```

Use your real Render URL. Do **not** add `AI_API_KEY` here.

5. Click **Deploy**. Copy the frontend URL, for example:

```text
https://smartassist-chatbot.vercel.app
```

### 4. Connect frontend and backend

1. In Render, edit `CORS_ORIGINS` to your Vercel URL (no trailing slash):

```text
CORS_ORIGINS=https://smartassist-chatbot.vercel.app
```

2. Redeploy the Render service (or wait for it to pick up the env change).
3. Open the Vercel URL and send `Hello`, then `What is machine learning?`.

### 5. Local production build check (optional)

```powershell
cd C:\Users\harsh\Desktop\CHATBOT\smartassist-chatbot\frontend
npm run build
npm run preview
```

### Hosting alternatives

- Frontend: Netlify (same `frontend` folder, build `npm run build`, publish `dist`, env `VITE_API_URL`)
- Backend: Railway (start command same as Render)

---

## GitHub preparation

Never push `.env`. It is listed in `.gitignore` because it can contain your API key.

```powershell
cd C:\Users\harsh\Desktop\CHATBOT\smartassist-chatbot
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin <GITHUB_REPOSITORY_URL>
git push -u origin main
```

Replace `<GITHUB_REPOSITORY_URL>` with your real repo URL, for example:

```text
https://github.com/your-username/smartassist-chatbot.git
```

Suggested GitHub repository description:

> Internship-ready AI chatbot with React, FastAPI, login, chat history, FAQ replies, and OpenAI-compatible API fallback.

Suggested topics: `react`, `fastapi`, `chatbot`, `openai`, `internship-project`
Deployed link:https://vercel.com/harshithas-projects-270046d5/smartassist-chatbot-4s4x

---

## Author

**Harsh**

SmartAssist AI Chatbot — internship / portfolio project.

Update this section with your full name, GitHub profile, and LinkedIn if you want.
