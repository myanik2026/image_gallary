def search_image(search_name, images):

    term = search_name.lower()

    return [
        (image_id, image) for image_id, image in images.items()
        if term in image["filename"].lower()
    ]
