# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands
- Run the browser: `python -m Interface.browser_module`
- Run all tests: `python -m unittest discover tests`
- Run network tests: `python -m unittest tests/test_network/test_network.py`
- Run styles tests: `python -m unittest tests/test_styles/test_styles.py`
- Run interface tests: `python -m unittest tests/test_interface/test_interface.py`

## Architecture
The project is a custom web browser implementation organized into three primary modules:

- **Interface (`/Interface`)**: Handles the user interface and browser logic. The entry point is `browser_module.py`.
- **Network (`/Network`)**: Manages network connectivity and data retrieval, primarily handled in `connector_module.py`.
- **Styles (`/Styles`)**: Responsible for parsing and formatting web content, split between `parser_module.py` and `format_module.py`.

## Coding Best Practices
- **Type Hinting**: Use Python type hints for all function signatures to improve maintainability and IDE support.
- **Code Commenting** : Use brief and logic necessary comments only.
- **Error Handling**: Implement specific exception handling instead of generic `except Exception` blocks, especially in the Network module.
- **Modularity**: Keep logic separated between the three primary modules; avoid circular dependencies.
- **Documentation**: Use concise docstrings for complex logic. Favor clear naming over extensive commenting.
## Testing
- **Test Suite**: Unit tests are located in the `/tests` directory.
- **Mocking**: Use `unittest.mock` to isolate GUI (`tkinter`) and Network (`socket`) dependencies.
- **Known Issues**: `Interface.browser_module.layout()` may crash on `Text` objects due to incorrect `.tag` attribute access.
