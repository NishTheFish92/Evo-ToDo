from evotodo.config import TOKEN_FILE, INDEX_FILE, BASE_URL
import click
import json

def _get_token():
    """Return the saved JWT token, or None if not logged in."""
    if TOKEN_FILE.exists():
        return TOKEN_FILE.read_text().strip()
    return None


def _require_token():
    """Return the JWT token, exiting with an error if the user is not logged in."""
    token = _get_token()
    if not token:
        raise click.ClickException("Not logged in. Run: evotodo login <username> <password>")
    return token


def _headers():
    """Return auth headers using the saved token."""
    return {"Authorization": f"Bearer {_require_token()}"}


def _save_index(todos):
    """Save a list of todo IDs to the index file, keyed by 1-based position.

    Args:
        todos: The list of todo dicts returned by the API.
    """
    INDEX_FILE.write_text(json.dumps([t["_id"] for t in todos]))


def _resolve_index(n):
    """Look up the real todo ID for a 1-based index number.

    Args:
        n: 1-based integer index shown by the list command.

    Returns:
        The MongoDB ObjectId string for that todo.
    """
    if not INDEX_FILE.exists():
        raise click.ClickException("No index found. Run `evotodo list` first.")
    ids = json.loads(INDEX_FILE.read_text())
    if not 1 <= n <= len(ids):
        raise click.ClickException(f"Index {n} out of range (1–{len(ids)}). Run `evotodo list` to refresh.")
    return ids[n - 1]