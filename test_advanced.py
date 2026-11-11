
from PIL import Image
from color_extractor import extract_colors, rgb_to_hex


# TEST 1: Check RGB to HEX conversion

print("TEST 1: RGB to HEX")

assert rgb_to_hex((255, 0, 0)) == "#FF0000"
assert rgb_to_hex((0, 255, 0)) == "#00FF00"
assert rgb_to_hex((0, 0, 255)) == "#0000FF"

print("Test 1 passed!")


# TEST 2: Check a three-color image

print("\nTEST 2: Three-color image")

image = Image.new("RGB", (100, 100))

for x in range(100):
    for y in range(100):

        if x < 50:
            color = (255, 0, 0)

        elif x < 80:
            color = (0, 0, 255)

        else:
            color = (0, 255, 0)

        image.putpixel((x, y), color)

colors = extract_colors(image, n_colors=3)

for color in colors:
    print(color)

assert len(colors) == 3

actual_colors = {
    color["hex"]: color["percentage"]
    for color in colors
}

assert abs(actual_colors["#FF0000"] - 50) < 0.1
assert abs(actual_colors["#0000FF"] - 30) < 0.1
assert abs(actual_colors["#00FF00"] - 20) < 0.1

print("Test 2 passed!")


# TEST 3: Check percentages

print("\nTEST 3: Total percentage")

total = sum(
    color["percentage"]
    for color in colors
)

assert abs(total - 100) < 0.1

print("Test 3 passed!")


print("\nAll advanced tests passed!")
