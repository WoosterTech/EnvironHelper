import click

from .main import main as main_func


@click.command()
@click.option(
    "--settings-file",
    "-s",
    type=click.Path(exists=True, dir_okay=False),
    default="settings.py",
    help="Path to the settings file.",
)
@click.option(
    "--output-file",
    "-o",
    type=click.Path(exists=False, dir_okay=False),
    default=".env",
    help="Path to the output .env file.",
)
def main(settings_file: str, output_file: str) -> None:
    """Generate a .env file from a settings file."""
    click.echo(f"Settings file path: {settings_file}")
    click.echo(f"Output file path: {output_file}")

    main_func(settings_file, output_file)

    click.echo("Done!")
