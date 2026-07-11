import sqlite3
from datetime import date
from pathlib import Path

from flask import Flask, g, redirect, render_template, request, url_for

DATABASE = Path(__file__).parent / "todo.db"

app = Flask(__name__)


def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db


@app.teardown_appcontext
def close_db(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()


def init_db():
    with sqlite3.connect(DATABASE) as db:
        db.row_factory = sqlite3.Row
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS todo (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                is_complete INTEGER NOT NULL DEFAULT 0,
                due_date TEXT
            )
            """
        )
        columns = {row["name"] for row in db.execute("PRAGMA table_info(todo)")}
        if "due_date" not in columns:
            db.execute("ALTER TABLE todo ADD COLUMN due_date TEXT")


init_db()


@app.route("/")
def index():
    db = get_db()
    todos = db.execute(
        "SELECT * FROM todo ORDER BY (due_date IS NULL), due_date, id"
    ).fetchall()
    return render_template(
        "index.html", todos=todos, today=date.today().isoformat(), editing_id=None
    )


@app.route("/add", methods=["POST"])
def add():
    title = request.form.get("title", "").strip()
    due_date = request.form.get("due_date", "").strip() or None
    if title:
        db = get_db()
        db.execute(
            "INSERT INTO todo (title, due_date) VALUES (?, ?)", (title, due_date)
        )
        db.commit()
    return redirect(url_for("index"))


@app.route("/toggle/<int:todo_id>", methods=["POST"])
def toggle(todo_id):
    db = get_db()
    db.execute(
        "UPDATE todo SET is_complete = 1 - is_complete WHERE id = ?", (todo_id,)
    )
    db.commit()
    return redirect(url_for("index"))


@app.route("/edit/<int:todo_id>", methods=["GET", "POST"])
def edit(todo_id):
    db = get_db()
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        if title:
            db.execute("UPDATE todo SET title = ? WHERE id = ?", (title, todo_id))
            db.commit()
        return redirect(url_for("index"))

    todos = db.execute(
        "SELECT * FROM todo ORDER BY (due_date IS NULL), due_date, id"
    ).fetchall()
    return render_template(
        "index.html", todos=todos, today=date.today().isoformat(), editing_id=todo_id
    )


@app.route("/delete/<int:todo_id>", methods=["POST"])
def delete(todo_id):
    db = get_db()
    db.execute("DELETE FROM todo WHERE id = ?", (todo_id,))
    db.commit()
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
