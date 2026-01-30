# GitHub Webhook Receiver

Simple Flask app to receive GitHub webhook events and store them in MongoDB.

## Setup

1. Create a virtual environment and activate it (optional but recommended):

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Copy `.env.example` to `.env` and fill in `MONGO_URL`:

```bash
copy .env.example .env   # Windows
cp .env.example .env     # macOS / Linux
```

4. Run the app:

```bash
python app.py
```

The server will listen on port 5000 by default. The app reads `MONGO_URL` from environment (via `python-dotenv`).

## Notes

- Ensure `.env` is not committed; `.gitignore` already excludes it.
- For production, provide `MONGO_URL` via environment variables or a secrets manager rather than committing credentials.
