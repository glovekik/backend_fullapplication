import os
from flask import Flask, request, jsonify, send_from_directory
import yt_dlp
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

DOWNLOAD_DIR = 'downloads'  # Directory where files will be saved

def download_media(link, media_type='video'):
    try:
        os.makedirs(DOWNLOAD_DIR, exist_ok=True)

        if media_type == 'video':
            ydl_opts = {
                'format': 'bestvideo[height>=720]+bestaudio/best',  # Video quality at least 720p
                'outtmpl': os.path.join(DOWNLOAD_DIR, '%(title)s.%(ext)s'),
                'merge_output_format': 'mp4',
                'noplaylist': True,
            }
        elif media_type == 'audio':
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': os.path.join(DOWNLOAD_DIR, '%(title)s.%(ext)s'),
                'noplaylist': True,
                'postprocessors': [{
                    'key': 'FFmpegAudioConvertor',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            }
        else:
            return None, "Invalid media type"

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(link, download=True)
            filename = ydl.prepare_filename(info_dict)
            return os.path.basename(filename), None

    except Exception as e:
        return None, str(e)

@app.route('/download', methods=['POST'])
def download():
    data = request.json
    link = data.get('link')
    media_type = data.get('media_type', 'video')

    if not link:
        return jsonify({"error": "No link provided"}), 400

    filename, error = download_media(link, media_type)
    if filename:
        return jsonify({"filename": filename}), 200
    else:
        return jsonify({"error": error}), 500

@app.route('/downloads/<filename>', methods=['GET'])
def serve_file(filename):
    return send_from_directory(DOWNLOAD_DIR, filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
