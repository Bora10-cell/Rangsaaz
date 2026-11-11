
import streamlit as st
from PIL import Image, UnidentifiedImageError, ImageDraw
from io import BytesIO
from pathlib import Path
import base64
import html
import textwrap

from color_extractor import extract_colors

from database import (
    initialize_database,
    save_palette,
    get_saved_palettes,
    delete_palette
)


# -----------------------------------
# 1. PAGE CONFIGURATION
# -----------------------------------

st.set_page_config(
    page_title="रंगSAAZ | Your Little Color Studio",
    page_icon="🌷",
    layout="wide",
    initial_sidebar_state="collapsed"
)

initialize_database()


# -----------------------------------
# 2. HELPER FUNCTION FOR HTML
# -----------------------------------

def render_html(content):
    """
    Display multiline HTML correctly without
    Streamlit showing HTML inside code blocks.
    """

    clean_html = textwrap.dedent(content).strip()

    clean_html = "\n".join(
        line.lstrip()
        for line in clean_html.splitlines()
    )

    st.markdown(
        clean_html,
        unsafe_allow_html=True
    )


# -----------------------------------
# 3. LOAD CSS AND FLOWER ILLUSTRATION
# -----------------------------------

BASE_DIR = Path(__file__).resolve().parent

css_path = BASE_DIR / "assets" / "style.css"
flower_path = BASE_DIR / "assets" / "flowers.svg"

with open(css_path, encoding="utf-8") as file:
    css = file.read()

st.markdown(
    f"<style>{css}</style>",
    unsafe_allow_html=True
)

with open(flower_path, "rb") as file:
    flower_base64 = base64.b64encode(
        file.read()
    ).decode("utf-8")

flower_url = f"data:image/svg+xml;base64,{flower_base64}"


# -----------------------------------
# 4. CREATE DOWNLOADABLE PALETTE
# -----------------------------------

def create_palette_image(colors):
    """Create a PNG image containing palette colors."""

    width = 1000
    height = 300

    palette = Image.new(
        "RGB",
        (width, height),
        "#feeddd"
    )

    draw = ImageDraw.Draw(palette)

    count = len(colors)

    for i, color in enumerate(colors):

        x1 = round(i * width / count)
        x2 = round((i + 1) * width / count)

        draw.rectangle(
            (x1, 0, x2, 240),
            fill=color["hex"]
        )

        draw.text(
            (x1 + 10, 260),
            color["hex"],
            fill="#753c54"
        )

    buffer = BytesIO()

    palette.save(
        buffer,
        format="PNG"
    )

    return buffer.getvalue()


# -----------------------------------
# 5. SAVED PALETTE POP-UP VIEWER
# -----------------------------------

@st.dialog("♡ Your Saved Color Story", width="large")
def show_saved_palette(palette):
    """
    Open a saved palette in a pop-up window.

    Users can view colors, copy HEX codes,
    and download the palette again.
    """

    st.markdown(
        f"### ✿ {html.escape(palette['name'])}"
    )

    st.caption(
        "Your favorite shades, always here for you ♡"
    )

    selected_colors = palette["colors"]

    # Display horizontal palette preview
    swatches = "".join(
        f'<div style="background:{html.escape(color["hex"])};'
        'height:100px;flex:1;"></div>'
        for color in selected_colors
    )

    render_html(
        f"""
<div style="
display:flex;
overflow:hidden;
border-radius:18px;
margin-bottom:20px;
">
{swatches}
</div>
        """
    )

    st.markdown("#### ✿ Your HEX codes")

    # Display individual colors and copy controls
    for start in range(0, len(selected_colors), 2):

        row_colors = selected_colors[start:start + 2]
        columns = st.columns(2)

        for column, color in zip(
            columns,
            row_colors
        ):

            with column:

                hex_code = html.escape(
                    color["hex"]
                )

                render_html(
                    f"""
<div style="
background:{hex_code};
height:55px;
border-radius:12px;
margin-bottom:8px;
"></div>
                    """
                )

                # Built-in copy button
                st.code(
                    color["hex"],
                    language=None
                )

                st.caption(
                    f'{color["percentage"]}% of your palette'
                )

    # Copy complete palette
    st.markdown(
        "#### ♡ Copy the complete palette"
    )

    all_hex_codes = ", ".join(
        color["hex"]
        for color in selected_colors
    )

    st.code(
        all_hex_codes,
        language=None
    )

    # Download saved palette
    saved_png = create_palette_image(
        selected_colors
    )

    st.download_button(
        "♡ Download this palette",
        data=saved_png,
        file_name=f"rangsaaz_{palette['id']}.png",
        mime="image/png",
        key=f"dialog_download_{palette['id']}",
        use_container_width=True
    )

    # Close the dialog
    if st.button(
        "✿ Close",
        key=f"dialog_close_{palette['id']}",
        use_container_width=True
    ):
        st.rerun()


# -----------------------------------
# 6. NAVIGATION BAR
# -----------------------------------

render_html(
    """
<div class="rang-nav">
    <div class="nav-logo">✿ रंगSAAZ</div>

    <div class="nav-links">
        <a href="#studio">Studio</a>
        <a href="#create">Create Palette</a>
        <a href="#saved">Saved Palettes</a>
        <a href="#about">About</a>
    </div>
</div>
    """
)


# -----------------------------------
# 7. HERO SECTION
# -----------------------------------

render_html(
    f"""
<div id="studio" class="rang-hero">

    <div class="hero-eyebrow">
        A LITTLE STUDIO FOR COLOR LOVERS
    </div>

    <div class="hero-title">
        रंगSAAZ
    </div>

    <div class="hero-description">
        A little color, a lot of magic.
    </div>

    <div class="hero-small">
        Turn your favorite pictures into
        beautiful color stories.
    </div>

    <a href="#create" class="hero-button">
        Create your palette ♡
    </a>

    <img
        class="hero-flower"
        src="{flower_url}"
        alt="Decorative flower"
    />

</div>
    """
)


# -----------------------------------
# 8. PALETTE PLAYGROUND HEADING
# -----------------------------------

render_html(
    """
<div id="create"></div>

<div class="section-heading">
    The Palette Playground ✿
</div>

<div class="section-caption">
    Every beautiful color story begins with a picture.
</div>
    """
)


# -----------------------------------
# 9. TWO-COLUMN DASHBOARD
# -----------------------------------

left, right = st.columns(
    [1, 1],
    gap="large"
)


# -----------------------------------
# 10. IMAGE UPLOAD SECTION
# -----------------------------------

with left:

    render_html(
        """
<div class="section-heading" style="font-size:28px;">
    01. Your inspiration
</div>
        """
    )

    uploaded_file = st.file_uploader(
        "Upload your favorite picture ♡",
        type=["png", "jpg", "jpeg", "webp"]
    )

    n_colors = st.slider(
        "How many colors shall we find?",
        min_value=2,
        max_value=10,
        value=5
    )

    if uploaded_file is not None:

        try:
            image = Image.open(uploaded_file)
            image.load()

            st.image(
                image,
                caption="Your little inspiration ♡",
                use_container_width=True
            )

        except (
            UnidentifiedImageError,
            OSError,
            ValueError
        ):

            image = None

            st.error(
                "Oops! Please upload a valid image."
            )

    else:

        image = None

        render_html(
            """
<div class="empty-card">
    <div style="font-size:55px;">🌷</div>

    <div class="empty-title">
        Your canvas awaits
    </div>

    <p class="empty-text">
        Upload a photo, artwork or moodboard
        to begin your color adventure.
    </p>

    <div style="font-size:24px;">
        ✿ ♡ ✦
    </div>
</div>
            """
        )


# -----------------------------------
# 11. GENERATED COLOR PALETTE
# -----------------------------------

with right:

    render_html(
        """
<div class="section-heading" style="font-size:28px;">
    02. Your color story
</div>
        """
    )

    if image is not None:

        with st.spinner(
            "Finding your prettiest shades..."
        ):

            colors = extract_colors(
                image.copy(),
                n_colors=n_colors
            )

        st.success(
            "Your palette is ready! ✨"
        )

        # Display extracted color swatches
        for start in range(0, len(colors), 3):

            row_colors = colors[start:start + 3]
            columns = st.columns(3)

            for column, color in zip(
                columns,
                row_colors
            ):

                with column:

                    hex_code = html.escape(
                        color["hex"]
                    )

                    render_html(
                        f"""
<div class="palette-card">
    <div
        class="color-swatch"
        style="background:{hex_code};">
    </div>

    <div class="color-code">
        {hex_code}
    </div>

    <div class="color-share">
        {color["percentage"]}%
    </div>
</div>
                        """
                    )

        # Copy all generated HEX codes
        st.markdown(
            "#### ♡ Copy your colors"
        )

        hex_codes = ", ".join(
            color["hex"]
            for color in colors
        )

        st.code(
            hex_codes,
            language=None
        )

        # Save generated palette
        st.markdown(
            "### ♡ Save your color story"
        )

        palette_name = st.text_input(
            "Give your palette a cute name",
            placeholder="e.g. Strawberry Daydream",
            max_chars=60
        )

        if st.button(
            "♡ Save this palette",
            use_container_width=True
        ):

            if palette_name.strip():

                save_palette(
                    palette_name.strip(),
                    colors
                )

                st.success(
                    f"'{palette_name.strip()}' has been saved! ♡"
                )

                st.rerun()

            else:

                st.warning(
                    "Please give your palette a name first."
                )

        # Download generated palette
        palette_png = create_palette_image(
            colors
        )

        st.download_button(
            "♡ Download your palette",
            data=palette_png,
            file_name="rangsaaz_palette.png",
            mime="image/png",
            use_container_width=True
        )

    else:

        render_html(
            """
<div class="empty-card">
    <div style="font-size:55px;">🎨</div>

    <div class="empty-title">
        A little magic is coming...
    </div>

    <p class="empty-text">
        Your beautiful colors will appear
        here once you upload an image.
    </p>

    <div style="font-size:24px;">
        ♡ ✿ ♡
    </div>
</div>
            """
        )


# -----------------------------------
# 12. SAVED PALETTES SECTION
# -----------------------------------

render_html(
    """
<div id="saved"></div>

<div class="library-heading">
    <div class="library-eyebrow">
        ✿ YOUR LITTLE COLLECTION ✿
    </div>

    <div class="section-heading">
        ♡ Your Color Library
    </div>

    <div class="section-caption">
        All your favorite shades, tucked away
        in one happy little place.
    </div>
</div>
    """
)

saved_palettes = get_saved_palettes()

if not saved_palettes:

    st.info(
        "No saved palettes yet. "
        "Create your first color story above! ♡"
    )

else:

    # Display saved palettes in rows of three
    for start in range(0, len(saved_palettes), 3):

        palette_row = saved_palettes[start:start + 3]

        columns = st.columns(3)

        for column, palette in zip(
            columns,
            palette_row
        ):

            with column:

                palette_name = html.escape(
                    palette["name"]
                )

                swatches = "".join(
                    f'<div style="background:{html.escape(color["hex"])};'
                    'height:75px;flex:1;"></div>'
                    for color in palette["colors"]
                )

                # New saved palette card design
                render_html(
                    f"""
<div class="saved-palette-card">

    <div class="saved-palette-strip">
        {swatches}
    </div>

    <div class="saved-palette-info">

        <div class="saved-palette-name">
            ✿ {palette_name}
        </div>

        <div class="saved-palette-date">
            Saved on {html.escape(str(palette["created_at"]))}
        </div>

        <div class="saved-palette-count">
            ♡ {len(palette["colors"])} lovely shades
        </div>

    </div>

</div>
                    """
                )

                # Open saved palette in a pop-up
                if st.button(
                    "♡ View palette",
                    key=f"view_{palette['id']}",
                    use_container_width=True
                ):
                    show_saved_palette(palette)

                # Delete saved palette
                if st.button(
                    "🗑 Delete",
                    key=f"delete_{palette['id']}",
                    use_container_width=True
                ):

                    delete_palette(
                        palette["id"]
                    )

                    st.rerun()


# -----------------------------------
# 13. ABOUT SECTION
# -----------------------------------

render_html(
    """
<div id="about" class="about-section">

    <h2>
        Made with love & a little color ✿
    </h2>

    <p>
        रंगSAAZ is a creative color studio
        that uses machine learning to discover
        beautiful shades hidden inside
        your favorite pictures.
    </p>

    <p>
        Upload. Explore. Create.
        Fall in love with colors.
    </p>

</div>
    """
)


# -----------------------------------
# 14. FOOTER
# -----------------------------------

render_html(
    """
<div style="
    text-align:center;
    padding:35px;
    color:#753c54;
    font-family:'Nunito',sans-serif;
">
    ✿ रंगSAAZ ✿
    <br>
    Made for the love of colors ♡
</div>
    """
)
