# Flask Todo App

A minimal full-stack todo app: Flask + Jinja2 templates + SQLite.

## Run

```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
Create a .env file in the project directory:
SECRET_KEY="your-secret-key"
python app.py
```

Open http://127.0.0.1:5000. Todos persist in `todo.db` (created automatically, gitignored).
