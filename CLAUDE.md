# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands
- Run the browser: `python -m Interface.browser_module`

## Architecture
The project is a custom web browser implementation organized into three primary modules:

- **Interface (`/Interface`)**: Handles the user interface and browser logic. The entry point is `browser_module.py`.
- **Network (`/Network`)**: Manages network connectivity and data retrieval, primarily handled in `connector_module.py`.
- **Styles (`/Styles`)**: Responsible for parsing and formatting web content, split between `parser_module.py` and `format_module.py`.
