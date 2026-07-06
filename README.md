# LaunchPad AI

An AI-powered startup analysis tool. Enter your startup's name, description, target audience, and business model — it returns a viability score, innovation score, SWOT report, and growth recommendations using Google Gemini 1.5 Flash.

#  LaunchPad AI


**AI-Powered Startup Viability & Strategy Engine**

LaunchPad AI turns a short description of your startup idea into a structured, data-backed analysis — a Viability Score, an Innovation Score, a full SWOT report, and actionable growth recommendations — powered by Google's Gemini API.

---

##  Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Architecture](#-architecture)
- [Project Structure](#-project-structure)
- [Getting Started](#-getting-started)
- [Environment Variables](#-environment-variables)
- [Running the App](#-running-the-app)
- [Public Deployment via Ngrok](#-public-deployment-via-ngrok)
- [API Reference](#-api-reference)
- [Database Schema](#-database-schema)
- [Screenshots](#-screenshots)
- [Team](#-team)
- [Acknowledgements](#-acknowledgements)
- [License](#-license)

---

##  Overview

Founders often struggle to get honest, structured feedback on a new idea before investing real time and money into it. **LaunchPad AI** solves this by acting as an on-demand startup analyst: describe your startup name, target audience, description, and business model, and the platform returns:

- A **Viability Score** (0–100)
- An **Innovation Score** (0–100)
- A complete **SWOT Report** (Strengths, Weaknesses, Opportunities, Threats)
- **Market Insights** — a narrative read on the target market
- A **Growth Strategy** — concrete, actionable next steps

Every analysis is saved automatically so you can revisit past reports at any time.

---

##  Features

-  **Instant AI Analysis** — structured startup evaluation in seconds via Gemini's `gemini model
-  **Viability & Innovation Scoring** — quantified, comparable scores across ideas
-  **SWOT Report Generation** — four-quadrant breakdown tailored to your specific idea
- **Market Insights & Growth Strategy** — practical, idea-specific recommendations, not generic advice
-  **Report History** — every analysis is persisted to a local database and viewable under "Recent Reports"
-  **Secure API Key Management** — credentials never touch source control, managed via `.env`
-  **One-Command Public Deployment** — auto-launches an Ngrok tunnel so anyone can access your local instance
-  **Strict Input Validation** — every field is required and capped at 2,000 characters to keep requests clean and abuse-resistant

---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3, Flask |
| Database | SQLite via Flask-SQLAlchemy |
| AI Engine | Google Gemini API (`gemini-3.5-flash`) |
| Frontend | HTML, CSS, JavaScript (Fetch API) |
| Public Tunneling | Ngrok (via `pyngrok`) |
| Config Management | `python-dotenv` |

---

##  Architecture

```
                ┌────────────────────┐
      Renders   │                    │  Sends structured   ┌───────────────────────┐
   ┌───────────▶│   User Input       │      prompt          │   Gemini API           │
   │            │  (Startup Form)    │──────────────────────▶│  (gemini model)   │
   │            └────────────────────┘                       └──────────┬────────────┘
┌──┴──────────────┐                                                     │ Generates
│  LaunchPad AI    │   Persists report     ┌────────────────────┐        ▼
│  (Flask Backend) │───────────────────────▶│  SQLite Database   │  Viability & Innovation Scores
│                  │   Loads key via        │ (via SQLAlchemy)   │  SWOT Report
│                  │───────────────────────▶│  Secure .env keys  │  Market Insights & Growth Strategy
│                  │   Exposed via
└──────────────────┘───────────────────────▶ Ngrok Public Tunnel
```

The Flask backend validates all incoming requests, builds a strict JSON-only prompt, calls Gemini, validates the response shape, persists it to SQLite, and returns it to the frontend for rendering.

---

##  Project Structure

```
launchpad-ai/
├── app.py                  # Main Flask entry point — routes, DB models, Ngrok tunnel
├── services/
│   └── ai_engine.py        # Gemini API orchestration, prompt construction, JSON validation
├── templates/
│   └── index.html          # Main dashboard — input form + results UI
├── static/
│   ├── css/
│   │   └── style.css       # Styling
│   └── js/
│       └── main.js         # Fetch API logic, dynamic result rendering
├── instance/
│   └── launchpad.db        # Auto-generated SQLite database (not committed)
├── requirements.txt        # Python dependencies
├── .env.example            # Template for required environment variables
├── .gitignore
└── README.md
```

---

##  Getting Started

### Prerequisites

- Python 3.9+
- A [Google Gemini API key](https://aistudio.google.com/)
- A free [Ngrok account](https://ngrok.com/) and authtoken (only needed for public deployment)

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/shilpasingh89q69-dottie/Launchpad-ai.git
cd Launchpad-ai

# 2. Create and activate a virtual environment
python -m venv env

# Windows
env\Scripts\activate

# macOS/Linux
source env/bin/activate

# 3. Install dependencies
pip install -r requirements.txt
```

---

##  Environment Variables

Create a `.env` file in the project root (use `.env.example` as a template):

```env
GEMINI_API_KEY=your_gemini_api_key_here
NGROK_AUTHTOKEN=your_ngrok_authtoken_here
PORT=5000
```

##  Running the App

```bash
python app.py
```

The app will:
1. Ensure database tables exist
2. Start the Flask server locally at `http://127.0.0.1:5000`
3. Automatically open a public Ngrok tunnel (if `NGROK_AUTHTOKEN` is configured)

Open `http://127.0.0.1:5000` in your browser and submit a startup idea to see it in action.

---

##  Public Deployment via Ngrok

If a valid `NGROK_AUTHTOKEN` is set in `.env`, `app.py` automatically opens a public tunnel on startup and prints it to the terminal:

```
============================================================
 LaunchPad AI is LIVE
 Local:  http://127.0.0.1:5000
 Public: https://your-generated-url.ngrok-free.dev
============================================================
```

Share the **Public** URL with anyone to let them access your running instance directly from their browser — no installation required.

> On the free Ngrok tier, this URL changes every time the app restarts.

---

## API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Renders the main dashboard |
| `POST` | `/api/analyze` | Accepts startup details as JSON, returns the AI-generated analysis |
| `GET` | `/api/history` | Returns the 20 most recent saved reports |
| `DELETE` | `/api/history/<id>` | Deletes a single saved report by ID |

### `POST /api/analyze` — Request Body

```json
{
  "startup_name": "Diet Plan Ai",
  "target_audience": "students, elderly people, busy professionals",
  "description": "AI-powered platform that generates personalized daily nutrition plans.",
  "business_model": "Freemium — free basic plans, paid pro features."
}
```

### `POST /api/analyze` — Response

```json
{
  "success": true,
  "data": {
    "id": 1,
    "startup_name": "Diet Plan Ai",
    "viability_score": 55,
    "innovation_score": 42,
    "swot": {
      "strengths": ["..."],
      "weaknesses": ["..."],
      "opportunities": ["..."],
      "threats": ["..."]
    },
    "market_insights": "...",
    "growth_strategy": "...",
    "created_at": "2026-07-06T18:34:30"
  }
}
```

---

## Database Schema

Single-table schema (`startup_reports`):

| Column | Type | Description |
|---|---|---|
| `id` | Integer (PK) | Auto-incrementing primary key |
| `startup_name` | String(200) | Name of the startup being analyzed |
| `description` | Text | User-provided startup description |
| `target_audience` | Text | User-provided target audience |
| `business_model` | Text | User-provided business model |
| `viability_score` | Integer | AI-generated viability score (0–100) |
| `innovation_score` | Integer | AI-generated innovation score (0–100) |
| `swot_json` | Text | SWOT report, stored as a serialized JSON string |
| `market_insights` | Text | AI-generated market analysis |
| `growth_strategy` | Text | AI-generated growth recommendations |
| `created_at` | DateTime | Timestamp the report was generated |

---

## 🖼 Screenshots

**Startup Input Form**

![Input Form](docs/screenshots/input-form.jpg)

**Results Dashboard — Viability, Innovation & SWOT**

![Results Dashboard](docs/screenshots/results-dashboard.jpg)

**Recommendations — Market Insights & Growth Strategy**

![Recommendations](docs/screenshots/recommendations.jpg)

---

## 👥 Team

| Name | Role | GitHub |
|---|---|---|
| **Shilpa Kumari** | Team Lead — - Project concept and planning
- Frontend and backend development
- API integration
- Testing and debugging
- GitHub repository management
- Demo video creation
- Final project integration | [@shilpasingh89q69-dottie](https://github.com/shilpasingh89q69-dottie) |
| **Chanchal Patani** | - Co-prepared the project documentation.
- Created and organized approximately half of the project PDF reports.
- Assisted in compiling project documentation.- Co-prepared the project documentation.
- Created and organized approximately half of the project PDF reports.
- Assisted in compiling project documentation. | [@Chanchalpatni302-bit](https://github.com/Chanchalpatni302-bit) |

---

##  Acknowledgements

- Built as part of the **SmartBridge / SkillWallet AI-Specialist-Track** internship program
- Powered by [Google Gemini API](https://ai.google.dev/)
- Public tunneling by [Ngrok](https://ngrok.com/)

---

## 📄 License

This project was developed for educational purposes as part of an internship submission. Add a license of your choice here (e.g. MIT) if you plan to open-source it.

```
MIT License

Copyright (c) 2026 Shilpa Kumari, Chanchal Patani

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.
```


<!-- ## Project Structure
```
launchpad-ai/
├── app.py                  # Main Flask app: routes, database, ngrok tunnel
├── requirements.txt        # Python dependencies
├── .env                    # Your real API keys go here (edit this)
├── .env.example            # Template reference (do not edit/use directly)
├── services/
│   └── ai_engine.py         # Gemini API logic, prompt, JSON validation
├── templates/
│   └── index.html           # Main dashboard page
├── static/
│   ├── css/style.css        # Styling
│   └── js/main.js           # Fetch API logic, dynamic rendering
└── instance/
    └── launchpad.db         # SQLite database (auto-created on first run)
```

## Setup

**1. Create and activate a virtual environment**
```bash
python3.11 -m venv env
```
Windows:
```bash
env\Scripts\activate
```
macOS/Linux:
```bash
source env/bin/activate
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Add your API keys**

Open `.env` and replace the placeholders:
```
GEMINI_API_KEY=your_gemini_api_key_here
NGROK_AUTHTOKEN=your_ngrok_authtoken_here
```
- Gemini key: https://aistudio.google.com/app/apikey
- Ngrok token: https://dashboard.ngrok.com/get-started/your-authtoken

**4. Run the app**
```bash
python app.py
```

You'll see output like:
```
Local:  http://127.0.0.1:5000
Public: https://xxxx-xx-xx-xxx-xx.ngrok-free.app
```

Open either URL in your browser.

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| "something went wrong" in browser | Backend error, check terminal | Read the actual terminal output, not the browser message |
| 502 error on analyze | Bad/expired Gemini key | Check `.env`, get a fresh key |
| No public URL printed | Missing/invalid ngrok token | App still works locally at 127.0.0.1:5000 |
| `pip install` fails | Python version mismatch | Use Python 3.10–3.12 (3.11 recommended) |
| Port already in use | Another app on port 5000 | Change `PORT` in `.env` | -->
