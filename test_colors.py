
from PIL import Image
from color_extractor import extract_colors


# Create a simple red image for testing
image = Image.new(
    "RGB",
    (100, 100),
    (255, 0, 0)
)

# Extract dominant colors
colors = extract_colors(image, n_colors=5)

# Print results
print("Extracted Colors:")

for color in colors:
    print("RGB:", color["rgb"])
    print("HEX:", color["hex"])
    print("Percentage:", color["percentage"], "%")
    print("------------------------")


# Check whether the algorithm is correct
assert len(colors) == 1
assert colors[0]["hex"] == "#FF0000"
assert colors[0]["percentage"] == 100.0

print("All tests passed!")
