import typer

app = typer.Typer(name="netadmin", help=" ", add_completion=False)

from netadmin.cli.commands import *


def main():
    app()


if __name__ == "__main__":
    main()
