from flask import Flask, render_template, request, send_file
from yt_dlp import YoutubeDL
import os
import uuid
import datetime

app = Flask(__name__)
DOWNLOAD_FOLDER = "downloads"
VISIT_LOG = "visit_log.txt"
UNIQUE_IPS_LOG = "unique_ips.txt"

os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)
open(VISIT_LOG, 'a').close()
open(UNIQUE_IPS_LOG, 'a').close()

@app.before_request
def log_visit():
    ip = request.remote_addr
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(VISIT_LOG, "a") as v:
        v.write(f"{timestamp} - {ip} - {request.path}\n")

    
    with open(UNIQUE_IPS_LOG, "r+") as u:
        ips = set(line.strip() for line in u.readlines())
        if ip not in ips:
            u.write(f"{ip}\n")

@app.route("/", methods=["GET", "POST"])
def index():
    try:
        with open(VISIT_LOG, "r") as v:
            total_visits = len(v.readlines())
    except FileNotFoundError:
        total_visits = 0

    if request.method == "POST":
        url = request.form.get("url")
        if not url:
            return render_template("index.html", error="Please provide a tweet URL", visits=total_visits)

        video_id = str(uuid.uuid4())
        output_path = os.path.join(DOWNLOAD_FOLDER, f"{video_id}.mp4")

        ydl_opts = {
            "format": "best[ext=mp4]",
            "outtmpl": output_path
        }

        try:
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            return send_file(output_path, as_attachment=True)
        except Exception as e:
            return render_template("index.html", error=str(e), visits=total_visits)

    return render_template("index.html", visits=total_visits)


@app.route("/stats")
def stats():
    try:
        with open(VISIT_LOG, "r") as v:
            total_visits = len(v.readlines())
    except FileNotFoundError:
        total_visits = 0

    try:
        with open(UNIQUE_IPS_LOG, "r") as u:
            unique_visits = len(u.readlines())
    except FileNotFoundError:
        unique_visits = 0

    return f"""
    <h2>Site Analytics</h2>
    <p>Total Visits: {total_visits}</p>
    <p>Unique Visitors: {unique_visits}</p>
    """

if __name__ == "__main__":
    app.run(debug=False)
