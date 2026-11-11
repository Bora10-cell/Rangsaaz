
import streamlit as st

from PIL import (
    Image,
    UnidentifiedImageError,
    ImageDraw
)

from io import BytesIO
from pathlib import Path

import base64
import html
import textwrap
import re

from color_extractor import extract_colors

from auth import (
    sign_up_user,
    login_user,
    get_current_user,
    logout_user
)

from database import (
    save_palette,
    get_saved_palettes,
    delete_palette
)


# ==========================================
# 1. PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="रंगSAAZ | Your Little Color Studio",
    page_icon="🌷",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ==========================================
# 2. HELPER FUNCTIONS
# ==========================================

def render_html(content):
    """
    Display multiline HTML without Streamlit
    interpreting it as a code block.
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


def safe_hex(value):
    """
    Validate a HEX color before using it in HTML.

    Example:
        #DF678F
    """

    value = str(value).strip()

    if re.fullmatch(r"#[0-9a-fA-F]{6}", value):
        return value.upper()

    return "#CCCCCC"


def create_palette_image(colors):
    """
    Create a downloadable PNG containing
    all palette colors and their HEX codes.
    """

    width = 1000
    height = 300

    palette_image = Image.new(
        "RGB",
        (width, height),
        "#feeddd"
    )

    draw = ImageDraw.Draw(palette_image)

    count = len(colors)

    if count == 0:
        raise ValueError("Palette cannot be empty.")

    for index, color in enumerate(colors):

        x1 = round(index * width / count)
        x2 = round((index + 1) * width / count)

        hex_code = safe_hex(color["hex"])

        draw.rectangle(
            (x1, 0, x2, 240),
            fill=hex_code
        )

        draw.text(
            (x1 + 10, 260),
            hex_code,
            fill="#753c54"
        )

    buffer = BytesIO()

    palette_image.save(
        buffer,
        format="PNG"
    )

    return buffer.getvalue()


# ==========================================
# 3. LOAD DESIGN ASSETS
# ==========================================

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

flower_url = (
    f"data:image/svg+xml;base64,{flower_base64}"
)


# ==========================================
# 4. AUTHENTICATION SESSION
# ==========================================

try:
    current_user = get_current_user()

except Exception:
    current_user = None


# ==========================================
# 5. LOGIN AND SIGNUP SCREEN
# ==========================================

if current_user is None:

    render_html(
        """
<div style="
    text-align:center;
    padding:40px 10px 20px;
">

    <div style="
        font-family:'Baloo 2',sans-serif;
        font-size:clamp(55px,10vw,100px);
        color:#df678f;
        font-weight:800;
    ">
        रंगSAAZ
    </div>

    <div style="
        font-family:'DM Serif Display',serif;
        font-size:28px;
        color:#753c54;
    ">
        Your Little Color Studio ♡
    </div>

    <p style="
        font-family:'Nunito',sans-serif;
        color:#956b7e;
    ">
        A little color, a lot of magic.
        <br>
        Your favorite shades are waiting!
    </p>

</div>
        """
    )

    left_space, center, right_space = st.columns(
        [1, 1.5, 1]
    )

    with center:

        login_tab, signup_tab = st.tabs(
            ["♡ Log in", "✿ Sign up"]
        )

        # ----------------------------------
        # LOGIN FORM
        # ----------------------------------

        with login_tab:

            st.markdown(
                "### Welcome back, color lover! ♡"
            )

            with st.form("login_form"):

                login_email = st.text_input(
                    "Email address",
                    placeholder="you@example.com",
                    key="login_email"
                )

                login_password = st.text_input(
                    "Password",
                    type="password",
                    key="login_password"
                )

                login_submitted = st.form_submit_button(
                    "♡ Log in to रंगSAAZ",
                    use_container_width=True
                )

            if login_submitted:

                if (
                    not login_email.strip()
                    or not login_password
                ):

                    st.warning(
                        "Please enter your email "
                        "and password."
                    )

                else:

                    try:

                        response = login_user(
                            login_email.strip(),
                            login_password
                        )

                        if (
                            response.user
                            and response.session
                        ):

                            st.rerun()

                        else:

                            st.warning(
                                "Please confirm your email "
                                "before logging in."
                            )

                    except Exception:

                        st.error(
                            "Unable to log in. Please check "
                            "your email and password."
                        )

        # ----------------------------------
        # SIGNUP FORM
        # ----------------------------------

        with signup_tab:

            st.markdown(
                "### Join our little color studio ✿"
            )

            with st.form("signup_form"):

                signup_email = st.text_input(
                    "Your email address",
                    placeholder="you@example.com",
                    key="signup_email"
                )

                signup_password = st.text_input(
                    "Create a password",
                    type="password",
                    key="signup_password"
                )

                confirm_password = st.text_input(
                    "Confirm password",
                    type="password",
                    key="confirm_password"
                )

                signup_submitted = st.form_submit_button(
                    "✿ Create my account",
                    use_container_width=True
                )

            if signup_submitted:

                if not signup_email.strip():

                    st.warning(
                        "Please enter your email address."
                    )

                elif len(signup_password) < 8:

                    st.warning(
                        "Password must contain at least "
                        "8 characters."
                    )

                elif signup_password != confirm_password:

                    st.error(
                        "Passwords do not match."
                    )

                else:

                    try:

                        response = sign_up_user(
                            signup_email.strip(),
                            signup_password
                        )

                        if (
                            response.user
                            and response.session
                        ):

                            st.rerun()

                        else:

                            st.success(
                                "♡ Signup request received! "
                                "Please check your email "
                                "for a confirmation link."
                            )

                    except Exception:

                        st.error(
                            "Unable to complete signup. "
                            "Please try again later."
                        )

        st.caption(
            "✿ Your personal color journey "
            "starts here."
        )

    st.stop()


# ==========================================
# 6. LOGGED-IN USER HEADER
# ==========================================

header_left, header_right = st.columns(
    [3, 1]
)

with header_left:

    st.caption(
        "♡ Signed in as "
        f"{current_user.email or 'Color lover'}"
    )

with header_right:

    if st.button(
        "Log out ♡",
        use_container_width=True
    ):

        try:
            logout_user()
            st.rerun()

        except Exception:
            st.error(
                "Logout failed. Please try again."
            )


# ==========================================
# 7. NAVIGATION BAR
# ==========================================

render_html(
    """
<div class="rang-nav">

    <div class="nav-logo">
        ✿ रंगSAAZ
    </div>

    <div class="nav-links">
        <a href="#studio">Studio</a>
        <a href="#create">Create Palette</a>
        <a href="#saved">Color Library</a>
        <a href="#about">About</a>
    </div>

</div>
    """
)


# ==========================================
# 8. HERO SECTION
# ==========================================

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


# ==========================================
# 9. PALETTE PLAYGROUND
# ==========================================

render_html(
    """
<div id="create"></div>

<div class="section-heading">
    The Palette Playground ✿
</div>

<div class="section-caption">
    Every beautiful color story begins
    with a picture.
</div>
    """
)

left, right = st.columns(
    [1, 1],
    gap="large"
)


# ==========================================
# 10. IMAGE UPLOAD SECTION
# ==========================================

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

    <div style="font-size:55px;">
        🌷
    </div>

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


# ==========================================
# 11. GENERATED COLOR PALETTE
# ==========================================

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

        # Display generated colors

        for start in range(0, len(colors), 3):

            row_colors = colors[start:start + 3]
            columns = st.columns(3)

            for column, color in zip(
                columns,
                row_colors
            ):

                with column:

                    hex_code = safe_hex(
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

        # Copy generated HEX codes

        st.markdown(
            "#### ♡ Copy your colors"
        )

        all_hex_codes = ", ".join(
            safe_hex(color["hex"])
            for color in colors
        )

        st.code(
            all_hex_codes,
            language=None
        )

        # Save palette to Supabase

        st.markdown(
            "### ♡ Save your color story"
        )

        palette_name = st.text_input(
            "Give your palette a cute name",
            placeholder="e.g. Strawberry Daydream",
            max_chars=60,
            key="new_palette_name"
        )

        if st.button(
            "♡ Save this palette",
            use_container_width=True,
            key="save_cloud_palette"
        ):

            if not palette_name.strip():

                st.warning(
                    "Please give your palette a name."
                )

            else:

                try:

                    save_palette(
                        palette_name.strip(),
                        colors
                    )

                    st.success(
                        "♡ Your palette has been saved "
                        "to your personal Color Library!"
                    )

                    st.rerun()

                except Exception:

                    st.error(
                        "Unable to save this palette. "
                        "Please try again."
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

    <div style="font-size:55px;">
        🎨
    </div>

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


# ==========================================
# 12. SAVED PALETTE POP-UP VIEWER
# ==========================================

@st.dialog(
    "♡ Your Saved Color Story",
    width="large"
)
def show_saved_palette(palette):
    """
    Open a saved palette.

    Users can copy HEX codes and
    download their palette again.
    """

    palette_name = html.escape(
        palette["name"]
    )

    st.markdown(
        f"### ✿ {palette_name}"
    )

    st.caption(
        "Your favorite shades, always "
        "here for you ♡"
    )

    selected_colors = palette["colors"]

    # Display horizontal palette preview

    swatches = "".join(
        (
            '<div style="'
            f'background:{safe_hex(color["hex"])};'
            'height:100px;flex:1;"></div>'
        )
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

    st.markdown(
        "#### ✿ Your HEX codes"
    )

    # Individual colors and copy buttons

    for start in range(
        0,
        len(selected_colors),
        2
    ):

        row_colors = selected_colors[
            start:start + 2
        ]

        columns = st.columns(2)

        for column, color in zip(
            columns,
            row_colors
        ):

            with column:

                hex_code = safe_hex(
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

                st.code(
                    hex_code,
                    language=None
                )

                st.caption(
                    f'{color["percentage"]}% '
                    'of your palette'
                )

    # Copy complete palette

    st.markdown(
        "#### ♡ Copy the complete palette"
    )

    all_hex_codes = ", ".join(
        safe_hex(color["hex"])
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
        file_name=(
            f"rangsaaz_{palette['id']}.png"
        ),
        mime="image/png",
        key=f"download_{palette['id']}",
        use_container_width=True
    )

    # Close dialog

    if st.button(
        "✿ Close",
        key=f"close_{palette['id']}",
        use_container_width=True
    ):
        st.rerun()


# ==========================================
# 13. PERSONAL COLOR LIBRARY
# ==========================================

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

try:

    saved_palettes = get_saved_palettes()

except Exception:

    saved_palettes = None

    st.error(
        "Unable to load your saved palettes. "
        "Please try again."
    )


if saved_palettes is not None:

    if not saved_palettes:

        st.info(
            "♡ Your Color Library is empty. "
            "Create and save your first palette!"
        )

    else:

        # Display palettes in rows of three

        for start in range(
            0,
            len(saved_palettes),
            3
        ):

            palette_row = saved_palettes[
                start:start + 3
            ]

            columns = st.columns(3)

            for column, palette in zip(
                columns,
                palette_row
            ):

                with column:

                    palette_name = html.escape(
                        palette["name"]
                    )

                    # Build color preview strip

                    swatches = "".join(
                        (
                            '<div style="'
                            f'background:{safe_hex(color["hex"])};'
                            'height:75px;flex:1;"></div>'
                        )
                        for color in palette["colors"]
                    )

                    # Display saved palette card

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
            Saved on {
                html.escape(
                    str(palette["created_at"])[:10]
                )
            }
        </div>

        <div class="saved-palette-count">
            ♡ {len(palette["colors"])} lovely shades
        </div>

    </div>

</div>
                        """
                    )

                    # View saved palette

                    if st.button(
                        "♡ View palette",
                        key=f"view_{palette['id']}",
                        use_container_width=True
                    ):

                        show_saved_palette(
                            palette
                        )

                    # Delete saved palette

                    if st.button(
                        "🗑 Delete",
                        key=f"delete_{palette['id']}",
                        use_container_width=True
                    ):

                        try:

                            delete_palette(
                                palette["id"]
                            )

                            st.rerun()

                        except Exception:

                            st.error(
                                "Unable to delete this palette."
                            )


# ==========================================
# 14. ABOUT SECTION
# ==========================================

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


# ==========================================
# 15. FOOTER
# ==========================================

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
