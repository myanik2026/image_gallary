def find_image(new_filename,Image_list):
    for i, image in enumerate(Image_list):
        image_name = image.get("filename")
        if image_name == new_filename:
            return i
    return -1


    
    