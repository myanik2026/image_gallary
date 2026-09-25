import os
from utils.search_images import search_images
from utils.secure_filename import secure_filename
from utils.extension_allow import allowed_file


def upload_image(file, images, upload_folder):

    if file is None:
        return {
            "error": "No image selected"
        }, 400


    if file.filename == "":
        return {
            "error": "No image selected"
        }, 400


    filename = secure_filename(file.filename)


    # Check valid filename
    if not filename:
        return {
            "error": "Invalid filename"
        }, 400

    # Check file extension
    if not allowed_file(filename):
        return {
            "error": "File type not allowed"
        }, 400


    # Check if file already exists
    existing_images = search_images(filename, images)
    if existing_images:
        return {
            "error": "File already exists"
        }, 400


    # Create file path
    filepath = os.path.join(
        upload_folder,
        filename
    )


    # Save image
    file.save(filepath)


    # Add image information
    images[filename] = {
        "filename": filename,
        "size": os.path.getsize(filepath)
    }


    return {
        "message": "Image uploaded!",
        "images": {
            "filename": filename,
            "size": os.path.getsize(filepath)
        }
    }, 201

