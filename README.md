# LaunchPad AI

An AI-powered startup analysis tool. Enter your startup's name, description, target audience, and business model — it returns a viability score, innovation score, SWOT report, and growth recommendations using Google Gemini 1.5 Flash.

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
