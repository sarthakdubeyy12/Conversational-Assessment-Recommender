"""
Application entry point.

Initializes and runs the FastAPI application.
"""

import uvicorn
from src.shared.config.settings import get_settings
from src.shared.logging.logger import setup_logger, configure_root_logger


def main() -> None:
    """Main application entry point."""
    # Get settings
    settings = get_settings()
    
    # Configure logging
    configure_root_logger(level=settings.log_level)
    logger = setup_logger(__name__, level=settings.log_level)
    
    logger.info(f"Starting application in {settings.environment} mode")
    logger.info(f"Debug mode: {settings.debug}")
    
    # Import app here to ensure logging is configured first
    from src.api.app import create_app
    
    app = create_app()
    
    # Run server
    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
        log_level=settings.log_level.lower(),
        access_log=True,
    )


if __name__ == "__main__":
    main()
