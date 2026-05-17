# Interface Module Documentation

## Code Practices
- **Type Hinting**: Strict use of Python type hints for all function signatures and method definitions.
- **GUI Framework**: Utilizes `tkinter` for the main window and a `tkinter.Canvas` for low-level rendering of web content.
- **Mocking Strategy**: Employs `unittest.mock` to isolate GUI components and network requests during testing.
- **Complexity Management**: Helper methods (like `_levenshtein_distance`) are kept private to the `Browser` class to maintain a clean public API.

## Logic Modules
- **Lexer (`lex`)**: Converts raw HTML body strings into a sequence of `Text` and `Tag` tokens.
- **Layout Engine (`layout`)**: Processes tokens to calculate absolute `(x, y)` coordinates for text elements, handling basic styling (`b`, `i`) and word wrapping.
- **URL Augmenter (`augment_url`)**: A robust preprocessing pipeline that:
    - Corrects mistyped schemes using Levenshtein distance.
    - Enforces the presence of `https://` and `www.`.
    - Corrects common TLD typos (e.g., `.comm` $\rightarrow$ `.com`).
    - Ensures trailing slashes are present.
- **Browser Controller (`Browser`)**: Orchestrates the window lifecycle, navigation, rendering, and scrolling logic.

## Functional Specification
- **Navigation**: Users can navigate via command-line arguments or a GUI search bar.
- **Search Bar**: A top-aligned `tkinter.Frame` containing an `Entry` field and a "Go" button.
- **Smarter Input**: Partial or mistyped URLs are automatically corrected before the request is made.
- **Content Rendering**: HTML is parsed and drawn to a canvas. Only elements within the current scroll viewport are executed to optimize performance.
- **Scrolling**: Supports keyboard (`Up`/`Down`) and mouse wheel interaction.

## Sanity Logic Criteria
- **URL Validation**: Every URL must pass through `augment_url` before being instantiated as a `URL` object.
- **Error Boundary**: `ValueError` exceptions during `URL` instantiation are caught to prevent GUI crashes on malformed input.
- **Canvas Bounds**: The layout engine respects `WIDTH` and `HEIGHT` constants to trigger word wrapping.
- **State Isolation**: The `display_list` is cleared and repopulated upon each page `load` to ensure a fresh render.

## Future Improvements
- **Enhanced CSS Support**: Implement more complex styling beyond bold and italic.
- **History Management**: Add a back/forward navigation system using a stack of visited URLs.
- **Async Networking**: Move `url.request()` to a background thread to prevent the GUI from freezing during long network requests.
- **Dynamic Sizing**: Allow the canvas to resize dynamically based on the content height instead of a fixed `HEIGHT`.
