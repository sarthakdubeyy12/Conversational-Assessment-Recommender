"""Application entry point."""

import uvicorn

from src.api.app import create_app
from src.shared.config.settings import Settings


def main() -> None:
    settings = Settings()
    app = create_app()
    
    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
        log_level=settings.log_level.lower(),
    )


if __name__ == "__main__":
    main()
