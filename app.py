from flask import Flask, request, jsonify, render_template 
from flask_cors import CORS 
from utils.secure_filename import secure_filename 
from utils.find_image import find_image
import os 
import json
from utils.delete_image import delete_image
from utils.search_images import search_images
from utils.upload_image import upload_image
 
app = Flask(__name__) 
CORS(app) 
 
UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'uploads') 
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER 
os.makedirs(UPLOAD_FOLDER, exist_ok=True) 
 
JSON_FILE= "images.json"

# Load existing images
if os.path.exists(JSON_FILE):
    try:
        with open(JSON_FILE, "r") as file:
            loaded_images = json.load(file)
            if isinstance(loaded_images, dict):
                images = loaded_images
            else:
                images = {
                    image.get("filename"): image
                    for image in loaded_images
                    if image.get("filename")
                }
    except (json.JSONDecodeError, FileNotFoundError):
        images = {}
else:
    images = {}


def save_images():
    with open(JSON_FILE, "w") as file:
        json.dump(images, file, indent=4)
 
@app.route('/') 
def index(): 
    return render_template('index.html') 
 
@app.route('/images', methods=['GET']) 
def get_images(): 
    return jsonify(images) 
 
@app.route('/images', methods=['POST']) 
def upload_images(): 
    result, status_code = upload_image(
        request.files.get('image'),
        images,
        app.config['UPLOAD_FOLDER']
    )
    if status_code == 201:
        save_images()
    return result, status_code

@app.route('/images/search', methods=['GET'])
def search_images_route():
    return search_images(
        request.args.get('name'),
        images
    )

@app.route('/images/<filename>', methods=['DELETE'])
def delete_image_route(filename):

    filename = secure_filename(filename)

    deleted = delete_image(
        filename,
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
