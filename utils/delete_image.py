import os


<<<<<<< HEAD
def delete_image(filename, images, upload_folder):

    if filename in images:
=======
def delete_image(image_id, images, upload_folder):

    entry = images.pop(str(image_id), None)

    if entry is None:
        return False
>>>>>>> 43378e8b93f763e0f6fbbc99971fbbdaf4c0a1d7

    filepath = os.path.join(upload_folder, entry["stored_filename"])

    if os.path.exists(filepath):
        os.remove(filepath)

<<<<<<< HEAD
            # Remove image from list
            del images[filename]

            return True

    return False




=======
    return True
>>>>>>> 43378e8b93f763e0f6fbbc99971fbbdaf4c0a1d7
