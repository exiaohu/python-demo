import asyncio

import click
import uvicorn
from alembic import command
from alembic.config import Config

from app.core.config import settings
from app.db.init_db import main as init_db


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
        host="0.0.0.0",  # nosec B104
        port=settings.PORT,
        reload=settings.DEBUG,
        workers=settings.WORKERS,
    )


@cli.command()
def migrate() -> None:
    click.echo("Running migrations...")
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")


@cli.command()
def seed() -> None:
    click.echo("Seeding database...")
    asyncio.run(init_db())


if __name__ == "__main__":
    cli()
