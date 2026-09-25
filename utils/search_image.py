def search_image(search_name, images):

    term = search_name.lower()

    return [
        image for image in images.values()
        if term in image["original_filename"].lower()
    ]
