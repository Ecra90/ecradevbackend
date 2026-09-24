from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)

CORS(app)

DATABASE = "/tmp/database.db"

ADMIN_TOKEN = "EcraDev2026Admin"


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "success",
        "message": "EcraDev API is running"
    })


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({
        "status": "success",
        "message": "EcraDev backend is running"
    })


@app.route("/api/contact", methods=["POST"])
def contact():
    data = request.get_json()

    if not data:
        return jsonify({
            "status": "error",
            "message": "No data provided"
        }), 400

    name = data.get("name", "").strip()
    email = data.get("email", "").strip()
    message = data.get("message", "").strip()

    if not name or not email or not message:
        return jsonify({
            "status": "error",
            "message": "All fields are required"
        }), 400

    conn = get_db()

    conn.execute(
        """
        INSERT INTO messages (name, email, message, created_at)
        VALUES (?, ?, ?, ?)
        """,
        (
            name,
            email,
            message,
            datetime.now().isoformat()
        )
    )

    conn.commit()
    conn.close()

    return jsonify({
        "status": "success",
        "message": "Your message has been received!"
    }), 201


@app.route("/api/projects", methods=["GET"])
def get_projects():
    projects = [
        {
            "id": 1,
            "title": "Eclix",
            "description": "A marketplace web application for browsing and managing online listings.",
            "technologies": ["React", "Flask", "SQLite", "REST API"],
            "github": "#",
            "demo": "#"
        },
        {
            "id": 2,
            "title": "Anniversary Project",
            "description": "A personalized web experience for showcasing memories, messages and special moments.",
            "technologies": ["React", "CSS", "JavaScript"],
            "github": "#",
            "demo": "#"
        },
        {
            "id": 3,
            "title": "Tennis Project",
            "description": "A tennis-focused web application providing tennis-related information and features.",
            "technologies": ["React", "Flask", "API"],
            "github": "#",
            "demo": "#"
        }
    ]

    return jsonify({
        "status": "success",
        "projects": projects
    })


@app.route("/api/messages", methods=["GET"])
def get_messages():
    authorization = request.headers.get("Authorization", "")

    if not authorization:
        return jsonify({
            "message": "Admin token is required."
        }), 401

    if not authorization.startswith("Bearer "):
        return jsonify({
            "message": "Invalid authorization format."
        }), 401

    token = authorization[7:]

    if token != ADMIN_TOKEN:
        return jsonify({
            "message": "Invalid token."
        }), 401

    conn = get_db()

    messages = conn.execute("""
        SELECT id, name, email, message, created_at
        FROM messages
        ORDER BY id DESC
    """).fetchall()

    conn.close()

    return jsonify({
        "status": "success",
        "messages": [dict(message) for message in messages]
    }), 200


@app.route("/api/messages/<int:message_id>", methods=["DELETE"])
def delete_message(message_id):
    authorization = request.headers.get("Authorization", "")

    if not authorization.startswith("Bearer "):
        return jsonify({
            "message": "Unauthorized."
        }), 401

    token = authorization[7:]

    if token != ADMIN_TOKEN:
        return jsonify({
            "message": "Invalid token."
        }), 401

    conn = get_db()

    message = conn.execute(
        "SELECT id FROM messages WHERE id = ?",
        (message_id,)
    ).fetchone()

    if not message:
        conn.close()

        return jsonify({
            "message": "Message not found."
        }), 404

    conn.execute(
        "DELETE FROM messages WHERE id = ?",
        (message_id,)
    )

    conn.commit()
    conn.close()

    return jsonify({
        "status": "success",
        "message": "Message deleted successfully."
    }), 200


init_db()


if __name__ == "__main__":
    app.run(
        debug=True,
        port=5000
    )