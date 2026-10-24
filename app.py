from flask import Flask, request, jsonify, render_template, session
from flask_cors import CORS 
from utils.secure_filename import secure_filename 
from models import db, Image, User
from utils.authentication import auth_bp
from functools import wraps
from flask import send_from_directory



import os 


app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get(
    "FLASK_SECRET_KEY",
    "change-this-to-a-long-random-secret"
)


app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:A123456s@localhost/image_gallery'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()

# connect authtentication.py  

app.register_blueprint(auth_bp)


def login_required(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return jsonify({"error": "Please log in first"}), 401

        return function(*args, **kwargs)

    return wrapper


UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route('/') 
def index(): 
    return render_template('index.html') 


@app.route('/images', methods=['GET'])
@login_required
def get_images():
    images = Image.query.filter_by(
        user_id=session["user_id"]
    ).order_by(Image.uploaded_at.desc()).all()

    return jsonify([
        {
            "id": image.id,
            "filename": image.filename,
            "uploaded_at": image.uploaded_at.strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        }
        for image in images
    ])

@app.route("/api/registered-emails", methods=["GET"])
def registered_emails():
    users = User.query.with_entities(User.email).order_by(
        User.email.asc()
    ).all()

    return jsonify({
        "emails": [user.email for user in users]
    })




@app.route('/images', methods=['POST'])
@login_required
def upload_images():
    file = request.files.get('image')

    if not file or not file.filename:
        return jsonify({"message": "No image selected"}), 400

    filename = secure_filename(file.filename)

    if not filename:
        return jsonify({"message": "Invalid filename"}), 400

    allowed_extensions = {"png", "jpg", "jpeg", "gif", "webp"}

    if "." not in filename or filename.rsplit(".", 1)[1].lower() not in allowed_extensions:
        return jsonify({"message": "Unsupported image format"}), 400

    existing = Image.query.filter_by(
        filename=filename,
        user_id=session["user_id"]
    ).first()

    if existing:
        return jsonify({
            "message": f"{filename} has already been uploaded"
        }), 409

    file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)

    try:
        file.save(file_path)

        new_image = Image(
            filename=filename,
            mime_type=file.mimetype or "application/octet-stream",
            user_id=session["user_id"]
        )

        db.session.add(new_image)
        db.session.commit()

        return jsonify({
            "message": "Image uploaded successfully",
            "id": new_image.id,
            "filename": new_image.filename
        }), 201

    except Exception:
        db.session.rollback()

        if os.path.isfile(file_path):
            os.remove(file_path)

        app.logger.exception("Image upload failed")

        return jsonify({
            "message": "Upload failed because of a server or database error"
        }), 500


@app.route('/images/search', methods=['GET'])
@login_required
def search_images_route():

    name = request.args.get('name', '')

    images = Image.query.filter(Image.filename.ilike(f"%{name}%")).order_by(Image.uploaded_at.desc()).all()
    return jsonify([
        {
            "id": image.id,
            "filename": image.filename,
            "uploaded_at": image.uploaded_at.strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        }
        for image in images
    ])



@app.route('/images/<int:image_id>', methods=['DELETE'])
@login_required
def delete_image_route(image_id):
    
    image = Image.query.filter_by(
        id=image_id,
        user_id=session["user_id"]
    ).first()
    
    if not image:
        return jsonify({
            "error": "Image not found"
        }), 404

    db.session.delete(image)
    db.session.commit()

    return jsonify({
        "message": "Image deleted successfully"
    }), 200




@app.route('/image/<int:image_id>')
@login_required
def get_image(image_id):
    image = Image.query.filter_by(
        id=image_id,
        user_id=session["user_id"]
    ).first_or_404()

    return send_from_directory(
        app.config["UPLOAD_FOLDER"],
        image.filename
    )

if __name__ == '__main__':
    app.run(debug=True, port=5000) 

