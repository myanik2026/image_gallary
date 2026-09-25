def search_images(search_name, images):
    search_name = (search_name or "").strip()
    if not search_name:
        return {"error": "Please enter image name"}, 400

    image_values = images.values() if isinstance(images, dict) else images
    return [
        image
        for image in image_values
        if search_name.lower() in image.get("filename", image.get("title", "")).lower()
    ]
