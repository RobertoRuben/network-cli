from netadmin.utils.console import console_manager
from netadmin.cli import app
from netadmin.config import APP_NAME, APP_VERSION


def main():
    try:
        import sys

        if len(sys.argv) <= 1 or (
            len(sys.argv) == 2 and sys.argv[1] in ["--help", "-h"]
        ):
            console_manager.mostrar_titulo(
                f"{APP_NAME} v{APP_VERSION}",
                "Herramienta para administración de red",
            )

        app()

    except KeyboardInterrupt:
        console_manager.mostrar_advertencia("Operación cancelada por el usuario.")
    except Exception as e:
        console_manager.mostrar_error(f"Error inesperado: {str(e)}")
        raise


if __name__ == "__main__":
    main()
