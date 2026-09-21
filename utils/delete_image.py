import os


def delete_image(image_id, images, upload_folder):

    entry = images.pop(str(image_id), None)

    if entry is None:
        return False

    filepath = os.path.join(upload_folder, entry["stored_filename"])

    if os.path.exists(filepath):
        os.remove(filepath)

    return True
