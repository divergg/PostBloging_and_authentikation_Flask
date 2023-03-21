import os
import secrets

from PIL import Image

from main_code import app


def save_picture(image):
    random_num = secrets.token_hex(8)
    ext = os.path.splitext(image.filename)[1]
    filename = random_num + ext
    path = os.path.join(app.root_path, 'static/user_pics', filename)
    size = (125, 125)
    resized_image = Image.open(image)
    resized_image.thumbnail(size)
    resized_image.save(path)
    return filename
