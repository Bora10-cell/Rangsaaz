
"""
Supabase database functions for रंगSAAZ.

Each palette belongs to an authenticated user.
Supabase Row Level Security (RLS) prevents
users from accessing other users' palettes.
"""

from auth import get_supabase_client, get_current_user


def require_authenticated_user():
    """
    Get the verified logged-in user.

    Raise an error if nobody is logged in.
    """

    user = get_current_user()

    if user is None:
        raise PermissionError(
            "Please log in to access your Color Library."
        )

    return user


def save_palette(name, colors):
    """
    Save a palette to Supabase.

    Parameters:
        name: Palette name, such as Strawberry Daydream.
        colors: List containing HEX codes and percentages.
    """

    user = require_authenticated_user()

    client = get_supabase_client()

    response = (
        client.table("palettes")
        .insert({
            "user_id": str(user.id),
            "name": name,
            "colors": colors
        })
        .execute()
    )

    return response.data


def get_saved_palettes():
    """
    Retrieve only the logged-in user's palettes.
    """

    user = require_authenticated_user()

    client = get_supabase_client()

    response = (
        client.table("palettes")
        .select("*")
        .eq("user_id", str(user.id))
        .order("created_at", desc=True)
        .execute()
    )

    return response.data or []


def delete_palette(palette_id):
    """
    Delete a palette belonging to the current user.
    """

    user = require_authenticated_user()

    client = get_supabase_client()

    response = (
        client.table("palettes")
        .delete()
        .eq("id", str(palette_id))
        .eq("user_id", str(user.id))
        .execute()
    )

    return response.data


def initialize_database():
    """
    Compatibility function.

    Supabase already has the palettes table,
    so no local database initialization is needed.
    """

    pass
