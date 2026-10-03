from flask import Flask, request, jsonify, render_template 
from flask_cors import CORS 
from utils.secure_filename import secure_filename 
from models import db, Image



import os 


app = Flask(__name__)
CORS(app)


app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:A123456s@localhost/image_gallery'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()


UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)



@app.route('/') 
def index(): 
    return render_template('index.html') 


@app.route('/images', methods=['GET'])
def get_images():

    images = Image.query.order_by(
        Image.uploaded_at.desc()
    ).all()

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


@app.route('/images', methods=['POST'])
def upload_images():

    file = request.files.get('image')

    if file is None or file.filename == "":
        return jsonify({
            "error": "No image selected"
        }), 400

    filename = secure_filename(file.filename)

    # Check if file already exists
    existing_image = Image.query.filter_by(
        filename=filename
    ).first()

    if existing_image:
        return jsonify({
            "error": "File already uploaded"
        }), 409

    # Read the actual image
    image_data = file.read()

    # Store image in database
    new_image = Image(
        filename=filename,
        image_data=image_data,
        mime_type=file.mimetype
    )

    db.session.add(new_image)
    db.session.commit()

    return jsonify({
        "message": "Image uploaded successfully",
        "id": new_image.id,
        "filename": new_image.filename,
        "uploaded_at": new_image.uploaded_at.strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    }), 201



@app.route('/images/search', methods=['GET'])
def search_images_route():

    name = request.args.get('name', '')

    images = Image.query.filter(
        Image.filename.ilike(f"%{name}%")
    ).order_by(
        Image.uploaded_at.desc()
    ).all()

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



@app.route('/images/<filename>', methods=['DELETE'])
def delete_image_route(filename):

    filename = secure_filename(filename)

    image = Image.query.filter_by(
        filename=filename
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
def get_image(image_id):

    image = Image.query.get_or_404(image_id)

    return image.image_data, 200, {
        'Content-Type': image.mime_type

    }


if __name__ == '__main__':
    app.run(debug=True, port=5000) 