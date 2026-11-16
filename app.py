from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import requests
import json
import os
from functools import wraps

app = Flask(__name__)
app.secret_key = "yasin_bhai_emote_secret_key_2026"

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

EMOTE_CDN = "https://cdn.jsdelivr.net/gh/ShahGCreator/icon@main/PNG/{item_id}.png"

def load_json(filename, default):
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path):
        with open(path, "w") as f:
            json.dump(default, f, indent=2)
        return default
    with open(path, "r") as f:
        return json.load(f)

def save_json(filename, data):
    path = os.path.join(DATA_DIR, filename)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

DEFAULT_SETTINGS = {
    "admin_password": "admin123",
    "user_password": "123456",
    "youtube_link": "https://youtube.com",
    "telegram_link": "https://t.me",
    "discord_link": "https://discord.gg",
    "get_password_link": "https://youtube.com",
    "site_title": "YASIN BHAI EMOTE"
}

DEFAULT_SERVERS = [
    {"id": 1, "name": "INDIA", "api_server": "ID", "api_url": "https://ob55-emote-api.onrender.com", "order": 1},
    {"id": 2, "name": "BD", "api_server": "BD", "api_url": "https://ob55-emote-api.onrender.com", "order": 2}
]

DEFAULT_EMOTES = [
    {"id": 1, "emote_id": "909000063", "name": "AK47", "category": "Funny"},
    {"id": 2, "emote_id": "909000001", "name": "Laugh", "category": "Funny"},
    {"id": 3, "emote_id": "909000010", "name": "Wave", "category": "Greeting"}
]

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("admin_logged_in"):
            return redirect(url_for("admin_login"))
        return f(*args, **kwargs)
    return decorated

def user_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("user_logged_in"):
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated

@app.route("/")
def home():
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    settings = load_json("settings.json", DEFAULT_SETTINGS)
    if request.method == "POST":
        if request.form.get("password") == settings.get("user_password"):
            session["user_logged_in"] = True
            return redirect(url_for("dashboard"))
        return render_template("login.html", settings=settings, error="Wrong password")
    return render_template("login.html", settings=settings)

@app.route("/logout")
def logout():
    session.pop("user_logged_in", None)
    return redirect(url_for("login"))

@app.route("/dashboard")
@user_required
def dashboard():
    settings = load_json("settings.json", DEFAULT_SETTINGS)
    servers = load_json("servers.json", DEFAULT_SERVERS)
    emotes = load_json("emotes.json", DEFAULT_EMOTES)
    # Auto attach image URL
    for e in emotes:
        e["image"] = EMOTE_CDN.format(item_id=e["emote_id"])
    return render_template("dashboard.html", settings=settings, servers=servers, emotes=emotes)

@app.route("/api/send", methods=["POST"])
@user_required
def send_emote():
    data = request.json
    team_code = data.get("team_code", "").strip()
    emote_id = data.get("emote_id", "").strip()
    server_name = data.get("server_name", "BD").strip().upper()
    uids = [uid.strip() for uid in data.get("uids", []) if uid.strip()]

    if not team_code or not emote_id:
        return jsonify({"success": False, "error": "Team Code and Emote ID are required"}), 400

    servers = load_json("servers.json", DEFAULT_SERVERS)
    server = next((s for s in servers if s["name"].upper() == server_name), None)
    
    # Use api_server if available, otherwise use the name
    api_server_name = server.get("api_server", server_name) if server else server_name
    api_base = (server["api_url"] if server else "https://ob55-emote-api.onrender.com") + "/emote"

    params = {
        "team_code": team_code,
        "emote_id": emote_id,
        "server_name": api_server_name
    }
    if uids:
        params["uid"] = uids[0]
        for i, uid in enumerate(uids[1:4], start=2):
            params[f"uid{i}"] = uid

    try:
        resp = requests.get(api_base, params=params, timeout=15)
        return jsonify(resp.json())
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# ========== ADMIN ==========
@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        settings = load_json("settings.json", DEFAULT_SETTINGS)
        if request.form.get("password") == settings.get("admin_password"):
            session["admin_logged_in"] = True
            return redirect(url_for("admin_dashboard"))
        return render_template("admin_login.html", error="Wrong password")
    return render_template("admin_login.html")

@app.route("/admin/logout")
def admin_logout():
    session.pop("admin_logged_in", None)
    return redirect(url_for("admin_login"))

@app.route("/admin")
@admin_required
def admin_dashboard():
    settings = load_json("settings.json", DEFAULT_SETTINGS)
    servers = load_json("servers.json", DEFAULT_SERVERS)
    emotes = load_json("emotes.json", DEFAULT_EMOTES)
    for e in emotes:
        e["image"] = EMOTE_CDN.format(item_id=e["emote_id"])
    return render_template("admin.html", settings=settings, servers=servers, emotes=emotes)

@app.route("/admin/settings", methods=["POST"])
@admin_required
def update_settings():
    settings = load_json("settings.json", DEFAULT_SETTINGS)
    settings["youtube_link"] = request.form.get("youtube_link", "")
    settings["telegram_link"] = request.form.get("telegram_link", "")
    settings["discord_link"] = request.form.get("discord_link", "")
    settings["get_password_link"] = request.form.get("get_password_link", "")
    settings["site_title"] = request.form.get("site_title", "YASIN BHAI EMOTE")
    if request.form.get("new_admin_password"):
        settings["admin_password"] = request.form.get("new_admin_password")
    if request.form.get("new_user_password"):
        settings["user_password"] = request.form.get("new_user_password")
    save_json("settings.json", settings)
    return redirect(url_for("admin_dashboard"))

@app.route("/admin/server/add", methods=["POST"])
@admin_required
def add_server():
    servers = load_json("servers.json", DEFAULT_SERVERS)
    new_id = max([s["id"] for s in servers], default=0) + 1
    servers.append({
        "id": new_id,
        "name": request.form.get("name", "").upper().strip(),
        "api_server": request.form.get("api_server", "").upper().strip() or request.form.get("name", "").upper().strip(),
        "api_url": request.form.get("api_url", "").rstrip("/"),
        "order": int(request.form.get("order", 0) or 0)
    })
    save_json("servers.json", servers)
    return redirect(url_for("admin_dashboard"))

@app.route("/admin/server/delete/<int:sid>")
@admin_required
def delete_server(sid):
    servers = load_json("servers.json", DEFAULT_SERVERS)
    servers = [s for s in servers if s["id"] != sid]
    save_json("servers.json", servers)
    return redirect(url_for("admin_dashboard"))

@app.route("/admin/emote/add", methods=["POST"])
@admin_required
def add_emote():
    emotes = load_json("emotes.json", DEFAULT_EMOTES)
    new_id = max([e["id"] for e in emotes], default=0) + 1
    emotes.append({
        "id": new_id,
        "emote_id": request.form.get("emote_id", "").strip(),
        "name": request.form.get("name", "").strip(),
        "category": request.form.get("category", "Funny").strip() or "Funny"
    })
    save_json("emotes.json", emotes)
    return redirect(url_for("admin_dashboard"))

@app.route("/admin/emote/edit/<int:eid>", methods=["POST"])
@admin_required
def edit_emote(eid):
    emotes = load_json("emotes.json", DEFAULT_EMOTES)
    for e in emotes:
        if e["id"] == eid:
            e["name"] = request.form.get("name", e["name"]).strip()
            e["category"] = request.form.get("category", e["category"]).strip() or "Funny"
            break
    save_json("emotes.json", emotes)
    return redirect(url_for("admin_dashboard"))
    emotes = load_json("emotes.json", DEFAULT_EMOTES)
    emotes = [e for e in emotes if e["id"] != eid]
    save_json("emotes.json", emotes)
    return redirect(url_for("admin_dashboard"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
