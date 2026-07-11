import sqlite3
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
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS todo (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                is_complete INTEGER NOT NULL DEFAULT 0
            )
            """
        )


init_db()


@app.route("/")
def index():
    db = get_db()
    todos = db.execute("SELECT * FROM todo ORDER BY id").fetchall()
    return render_template("index.html", todos=todos)


@app.route("/add", methods=["POST"])
def add():
    title = request.form.get("title", "").strip()
    if title:
        db = get_db()
        db.execute("INSERT INTO todo (title) VALUES (?)", (title,))
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


@app.route("/delete/<int:todo_id>", methods=["POST"])
def delete(todo_id):
    db = get_db()
    db.execute("DELETE FROM todo WHERE id = ?", (todo_id,))
    db.commit()
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
