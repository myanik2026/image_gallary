from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from werkzeug.utils import secure_filename
from datetime import datetime, timezone
from uuid import uuid4
import os
import json
from utils.extension_allow import allowed_file
from utils.delete_image import delete_image
from utils.search_image import search_image

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

JSON_FILE = "images.json"

# Load existing images, keyed by their id (as a string, since JSON object keys are strings)
if os.path.exists(JSON_FILE):
    try:
        with open(JSON_FILE, "r") as file:
            images = json.load(file)
    except (json.JSONDecodeError, FileNotFoundError):
        images = {}
else:
    images = {}


def save_images():
    with open(JSON_FILE, "w") as file:
        json.dump(images, file, indent=4)


def next_image_id():
    if not images:
        return 1
    return max(int(image_id) for image_id in images) + 1


def serialize_image(image):
    return {
        "id": image["id"],
        "original_filename": image["original_filename"],
        "file_type": image["file_type"],
        "size": image["size"],
        "uploaded_at": image["uploaded_at"],
        "url": f"/static/uploads/{image['stored_filename']}",
    }


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/images', methods=['GET'])
def get_images():
    ordered = sorted(images.values(), key=lambda image: image["id"], reverse=True)
    return jsonify([serialize_image(image) for image in ordered])


@app.route('/images', methods=['POST'])
def upload_image():

    if 'file' not in request.files:
        return jsonify({"error": "No image selected"}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "No image selected"}), 400

    original_filename = secure_filename(file.filename)

    if not original_filename:
        return jsonify({"error": "Invalid filename"}), 400

    if not allowed_file(original_filename):
        return jsonify({"error": "File type not allowed"}), 400

    extension = original_filename.rsplit(".", 1)[1].lower()
    stored_filename = f"{uuid4().hex}.{extension}"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], stored_filename)

    file.save(filepath)

    size = os.path.getsize(filepath)
    if size == 0:
        os.remove(filepath)
        return jsonify({"error": "Uploaded file is empty"}), 400

    image = {
        "id": next_image_id(),
        "original_filename": original_filename,
        "stored_filename": stored_filename,
        "file_type": file.mimetype or "application/octet-stream",
        "size": size,
        "uploaded_at": datetime.now(timezone.utc).isoformat(),
    }

    images[str(image["id"])] = image
    save_images()

    return jsonify(serialize_image(image)), 201


@app.route('/images/search', methods=['GET'])
def search_images():

    search_name = request.args.get("q", "").strip()

    if not search_name:
        return jsonify({"error": "Please provide a search term"}), 400

    results = sorted(
        search_image(search_name, images),
        key=lambda image: image["id"],
        reverse=True,
    )
    return jsonify([serialize_image(image) for image in results]), 200


@app.route('/images/<int:image_id>', methods=['DELETE'])
def delete_image_route(image_id):

    deleted = delete_image(
        image_id,
        images,
        app.config['UPLOAD_FOLDER']
    )

    if not deleted:
        return jsonify({
            "error": "Image not found"
        }), 404

    save_images()

    return jsonify({
        "message": "Image deleted successfully"
    }), 200


if __name__ == '__main__':
    app.run(debug=True, port=5000)
