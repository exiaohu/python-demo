import click
import uvicorn

from app.core.config import settings


@click.group()
def cli() -> None:
    pass


@cli.command()
def version() -> None:
    """Print the version."""
    click.echo(f"{settings.APP_NAME} v{settings.VERSION}")


@cli.command()
def server() -> None:
    click.echo("Starting server...")
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=settings.DEBUG,
    )


@cli.command()
def migrate() -> None:
    click.echo("Running migrations...")
    # Add migration logic here
    pass


if __name__ == "__main__":
    cli()
