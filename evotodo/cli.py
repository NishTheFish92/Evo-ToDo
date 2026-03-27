"""Evo-ToDo CLI — command-line interface for the Evo-ToDo app."""

from evotodo.config import TOKEN_FILE, INDEX_FILE, BASE_URL
from evotodo.utils import _headers, _save_index, _resolve_index
import click
import requests

@click.group()
def cli():
    """Evo-ToDo: manage your tasks from the terminal.

    \b
    Quick start:
      evotodo register alice secret123
      evotodo login alice secret123
      evotodo add "Buy groceries"
      evotodo list
      evotodo complete 1
      evotodo delete 2
    """


@cli.command()
@click.argument("username")
@click.argument("password")
def register(username, password):
    """Register a new account with USERNAME and PASSWORD."""
    r = requests.post(f"{BASE_URL}/auth/register", json={"username": username, "password": password})
    if r.ok:
        click.echo(f"Registered '{username}'. You can now log in.")
    else:
        raise click.ClickException(r.json().get("detail", r.text))


@cli.command()
@click.argument("username")
@click.argument("password")
def login(username, password):
    """Log in with USERNAME and PASSWORD and save the session token."""
    r = requests.post(f"{BASE_URL}/auth/login", data={"username": username, "password": password})
    if r.ok:
        TOKEN_FILE.write_text(r.json()["access_token"])
        click.echo(f"Logged in as '{username}'.")
    else:
        raise click.ClickException(r.json().get("detail", r.text))


@cli.command()
def logout():
    """Log out and remove the saved session token."""
    TOKEN_FILE.unlink(missing_ok=True)
    INDEX_FILE.unlink(missing_ok=True)
    click.echo("Logged out.")


@cli.command("list")
def list_todos():
    """List all your todos."""
    r = requests.get(f"{BASE_URL}/todos", headers=_headers())
    if not r.ok:
        raise click.ClickException(r.json().get("detail", r.text))
    todos = r.json()
    if not todos:
        click.echo("No todos yet.")
        return
    _save_index(todos)
    for i, t in enumerate(todos, 1):
        status = "x" if t["completed"] else " "
        click.echo(f"{i:>3}. [{status}] {t['title']}")


@cli.command()
@click.argument("title")
def add(title):
    """Add a new todo with the given TITLE."""
    r = requests.post(f"{BASE_URL}/todos/new", json={"title": title}, headers=_headers())
    if r.ok:
        t = r.json()
        click.echo(f"Added: {t['title']}")
    else:
        raise click.ClickException(r.json().get("detail", r.text))


@cli.command()
@click.argument("index", type=int)
def complete(index):
    """Toggle the completion status of a todo by its INDEX number."""
    todo_id = _resolve_index(index)
    r = requests.patch(f"{BASE_URL}/todos/{todo_id}", headers=_headers())
    if r.ok:
        click.echo(r.json().get("message", "Updated."))
    else:
        raise click.ClickException(r.json().get("detail", r.text))


@cli.command()
@click.argument("index", type=int)
def delete(index):
    """Delete a todo by its INDEX number."""
    todo_id = _resolve_index(index)
    r = requests.delete(f"{BASE_URL}/todos/delete/{todo_id}", headers=_headers())
    if r.ok:
        click.echo(r.json().get("message", "Deleted."))
    else:
        raise click.ClickException(r.json().get("detail", r.text))


if __name__ == "__main__":
    cli()
