
import streamlit as st
from supabase import create_client


def get_supabase_client():
    """Create one Supabase client per Streamlit session."""

    if "supabase_client" not in st.session_state:
        st.session_state.supabase_client = create_client(
            st.secrets["SUPABASE_URL"],
            st.secrets["SUPABASE_KEY"]
        )

    return st.session_state.supabase_client


def sign_up_user(email, password):
    """Create a new Supabase user account."""

    client = get_supabase_client()

    return client.auth.sign_up({
        "email": email,
        "password": password
    })


def login_user(email, password):
    """Sign in with email and password."""

    client = get_supabase_client()

    return client.auth.sign_in_with_password({
        "email": email,
        "password": password
    })


def get_current_user():
    """Verify and return the current authenticated user."""

    client = get_supabase_client()
    session_response = client.auth.get_session()

    if session_response is None:
        return None

    response = client.auth.get_user()
    return response.user


def logout_user():
    """Sign out and clear local authentication state."""

    client = get_supabase_client()

    try:
        client.auth.sign_out()
    finally:
        st.session_state.pop("supabase_client", None)
        st.session_state.pop("logged_in_user", None)
