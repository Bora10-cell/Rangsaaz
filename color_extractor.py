
import numpy as np
from PIL import Image
from sklearn.cluster import KMeans


def rgb_to_hex(rgb):
    """Convert RGB values into a HEX color code."""

    r, g, b = [int(value) for value in rgb]

    return f"#{r:02X}{g:02X}{b:02X}"


def extract_colors(image, n_colors=5):
    """Extract dominant colors from an image."""

    # STEP 1: Validate the number of colors
    if not isinstance(n_colors, int) or n_colors < 1:
        raise ValueError(
            "Number of colors must be a positive integer."
        )

    # STEP 2: Convert the image to RGB
    image = image.convert("RGB")

    # STEP 3: Resize the image to speed up processing
    image.thumbnail((250, 250))

    # STEP 4: Convert image pixels into a NumPy array
    pixels = np.array(image)

    # STEP 5: Convert the 3D array into a 2D array
    pixels = pixels.reshape(-1, 3)

    # STEP 6: Count unique colors
    unique_colors = np.unique(pixels, axis=0)

    # Avoid requesting more clusters than unique colors
    k = min(n_colors, len(unique_colors))

    # STEP 7: Create the K-Means model
    model = KMeans(
        n_clusters=k,
        random_state=42,
        n_init=10
    )

    # STEP 8: Train the model and predict clusters
    labels = model.fit_predict(pixels)

    # STEP 9: Find representative RGB colors
    centers = np.rint(model.cluster_centers_)
    centers = np.clip(centers, 0, 255).astype(int)

    # STEP 10: Count how many pixels belong to each cluster
    counts = np.bincount(labels, minlength=k)

    # STEP 11: Sort colors by frequency
    sorted_indices = np.argsort(counts)[::-1]

    # STEP 12: Prepare the results
    colors = []

    for index in sorted_indices:

        rgb = tuple(
            int(value) for value in centers[index]
        )

        hex_code = rgb_to_hex(rgb)

        percentage = (
            counts[index] / len(pixels)
        ) * 100

        colors.append({
            "rgb": rgb,
            "hex": hex_code,
            "percentage": round(
                float(percentage), 2
            )
        })

    # STEP 13: Return the extracted colors
    return colors
