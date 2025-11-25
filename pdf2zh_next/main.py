#!/usr/bin/env python3
"""A command line tool for extracting text and images from PDF and
output it to plain text, html, xml or tags.
"""

from __future__ import annotations

import asyncio
import logging
import os
import sys
from pathlib import Path

import babeldoc.assets.assets

from pdf2zh_next.config import ConfigManager
from pdf2zh_next.high_level import do_translate_file_async

__version__ = "2.7.1"

logger = logging.getLogger(__name__)


def _get_default_backend_from_cli() -> str:
    """
    Determine the default backend based on how the CLI was invoked.
    - pdf2zh or pdf2zh2: use 'stable' backend
    - pdf2zh_next: use 'experimental' backend
    """
    if len(sys.argv) > 0:
        command = Path(sys.argv[0]).name.lower()
        # Strip .exe extension on Windows
        if command.endswith('.exe'):
            command = command[:-4]
        
        if command in ('pdf2zh', 'pdf2zh2'):
            return 'stable'
        elif command == 'pdf2zh_next':
            return 'experimental'
    
    # Default to stable for safety
    return 'stable'


def find_all_files_in_directory(directory_path):
    """
    Recursively search all PDF files in the given directory and return their paths as a list.

    :param directory_path: str, the path to the directory to search
    :return: list of PDF file paths
    """
    directory_path = Path(directory_path)
    # Check if the provided path is a directory
    if not directory_path.is_dir():
        raise ValueError(f"The provided path '{directory_path}' is not a directory.")

    file_paths = []

    # Walk through the directory recursively
    for root, _, files in os.walk(directory_path):
        for file in files:
            # Check if the file is a PDF
            if file.lower().endswith(".pdf"):
                # Append the full file path to the list
                file_paths.append(Path(root) / file)

    return file_paths


async def main() -> int:
    from rich.logging import RichHandler

    logging.basicConfig(level=logging.INFO, handlers=[RichHandler()])

    settings = ConfigManager().initialize_config()
    if settings.basic.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    # disable httpx, openai, httpcore, http11 logs
    logging.getLogger("httpx").setLevel("CRITICAL")
    logging.getLogger("httpx").propagate = False
    logging.getLogger("openai").setLevel("CRITICAL")
    logging.getLogger("openai").propagate = False
    logging.getLogger("httpcore").setLevel("CRITICAL")
    logging.getLogger("httpcore").propagate = False
    logging.getLogger("http11").setLevel("CRITICAL")
    logging.getLogger("http11").propagate = False

    for v in logging.Logger.manager.loggerDict.values():
        if getattr(v, "name", None) is None:
            continue
        if (
            v.name.startswith("pdfminer")
            or v.name.startswith("peewee")
            or v.name.startswith("httpx")
            or "http11" in v.name
            or "openai" in v.name
            or "pdfminer" in v.name
        ):
            v.disabled = True
            v.propagate = False

    logger.debug(f"settings: {settings}")

    if settings.basic.version:
        print(f"pdf2zh-next version: {__version__}")
        return 0

    logger.info("Warmup babeldoc assets...")
    babeldoc.assets.assets.warmup()

    if settings.basic.gui:
        from pdf2zh_next.server import run_server

        port = settings.gui_settings.server_port if settings.gui_settings.server_port else 7860
        gui_dev = settings.gui_settings.gui_dev if hasattr(settings.gui_settings, 'gui_dev') else False
        # Determine default backend based on CLI command used
        # pdf2zh/pdf2zh2 -> stable, pdf2zh_next -> experimental
        default_backend = _get_default_backend_from_cli()
        logger.info(f"Starting GUI with default backend: {default_backend}")
        await run_server(port=port, gui_dev=gui_dev, default_backend=default_backend)
        return 0

    assert len(settings.basic.input_files) >= 1, "At least one input file is required"
    await do_translate_file_async(settings, ignore_error=True)
    return 0


def cli():
    sys.exit(asyncio.run(main()))


async def gui_main() -> int:
    """Main entry point for GUI-only mode (pdf2zh_gui command).
    
    This function starts the GUI directly without needing the --gui flag.
    It uses 'stable' as the default backend, but users can switch between
    stable and experimental backends in the GUI settings.
    """
    from rich.logging import RichHandler

    logging.basicConfig(level=logging.INFO, handlers=[RichHandler()])

    # Initialize config manager to get GUI settings
    config_mgr = ConfigManager()
    settings = config_mgr.initialize_config()
    
    if settings.basic.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    # Disable noisy loggers
    for logger_name in ["httpx", "openai", "httpcore", "http11"]:
        logging.getLogger(logger_name).setLevel("CRITICAL")
        logging.getLogger(logger_name).propagate = False

    for v in logging.Logger.manager.loggerDict.values():
        if getattr(v, "name", None) is None:
            continue
        if (
            v.name.startswith("pdfminer")
            or v.name.startswith("peewee")
            or v.name.startswith("httpx")
            or "http11" in v.name
            or "openai" in v.name
            or "pdfminer" in v.name
        ):
            v.disabled = True
            v.propagate = False

    logger.info("Warmup babeldoc assets...")
    babeldoc.assets.assets.warmup()

    from pdf2zh_next.server import run_server

    port = settings.gui_settings.server_port if settings.gui_settings.server_port else 7860
    gui_dev = settings.gui_settings.gui_dev if hasattr(settings.gui_settings, 'gui_dev') else False
    
    # Use 'stable' as default for the universal GUI launcher
    # Users can switch backends in the GUI settings
    default_backend = 'stable'
    logger.info(f"Starting PDF Math Translate GUI (default backend: {default_backend})")
    logger.info("You can switch between Stable and Experimental backends in Settings.")
    
    await run_server(port=port, gui_dev=gui_dev, default_backend=default_backend)
    return 0


def gui_cli():
    """CLI entry point for starting the GUI directly.
    
    This is invoked by the 'pdf2zh_gui' command and starts the GUI
    without requiring any command line arguments.
    """
    sys.exit(asyncio.run(gui_main()))


if __name__ == "__main__":
    cli()
