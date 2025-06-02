from flask import Flask, render_template, request, send_file
from yt_dlp import YoutubeDL
import os
import uuid

app = Flask(__name__)
DOWNLOAD_FOLDER = "downloads"

if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        url = request.form.get("url")
        if not url:
            return render_template("index.html", error="Please provide a tweet URL")

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
            return render_template("index.html", error=str(e))

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=False)
