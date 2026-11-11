
from PIL import Image
from color_extractor import extract_colors

image = Image.open("sample.jpg")

colors = extract_colors(image, n_colors=5)

print("Dominant colors in your image:")

for color in colors:
    print(
        color["hex"],
        "-",
        color["percentage"],
        "%"
    )
