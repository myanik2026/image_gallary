import os
def delete_image(filename, images, upload_folder):
    if filename in images:
        filepath = os.path.join(
            upload_folder,
            filename)

        if os.path.exists(filepath):
            os.remove(filepath)
            del images[filename]
            return True

        return False




