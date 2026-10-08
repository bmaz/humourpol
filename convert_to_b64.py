import argparse
import base64
from io import BytesIO

import casanova
from PIL import Image, UnidentifiedImageError

# Max dimensions for processing
MAX_IMAGE_SIZE = 1000  # pixels


# Resize image while maintaining aspect ratio
def resize_image(image, max_size=MAX_IMAGE_SIZE):
    width, height = image.size
    if width <= max_size and height <= max_size:
        return image

    if width > height:
        new_width = max_size
        new_height = int(height * (max_size / width))
    else:
        new_height = max_size
        new_width = int(width * (max_size / height))

    return image.resize((new_width, new_height), Image.LANCZOS)


parser = argparse.ArgumentParser(
    prog="b64 conversion",
)
parser.add_argument("input_path")
parser.add_argument("output_path")

args = parser.parse_args()


def convert_to_b64(image_path):
    with open(image_path, "rb") as f:
        image_bytes = f.read()
        try:
            image = Image.open(BytesIO(image_bytes))
        except UnidentifiedImageError:
            print(image_path)
            return ""
        resized = resize_image(image)
        buff = BytesIO()
        resized.save(buff, format="JPEG")
        img_str = base64.b64encode(buff.getvalue()).decode("utf-8")
    return img_str


with open(args.input_path) as input, open(args.output_path, "w") as output:
    enricher = casanova.enricher(input, output, add=["b64_image"])
    for row in enricher:
        if "image" in row[enricher.headers.mimetype]:
            path = row[enricher.headers.full_path]
            img_b64 = convert_to_b64(path)
        else:
            img_b64 = ""
        enricher.writerow(row, add=[img_b64])
