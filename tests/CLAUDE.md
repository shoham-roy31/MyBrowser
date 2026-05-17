# Test Module Documentation

## Code Practices
- **Mock-Driven Testing**: Heavy use of `unittest.mock.patch` and `MagicMock` to isolate the GUI (`tkinter`) and Network layers.
- **Interface Mocking**: All `tkinter` widgets (Tk, Canvas, Entry) are mocked to allow tests to run in headless environments (e.g., GitHub Actions).
- **Behavioral Verification**: Tests focus on verifying that specific methods (like `Browser.load`) are called with the expected augmented URLs.
- **Boundary Testing**: Inclusion of tests for empty strings, malformed URLs, and layout edge cases (e.g., text wrapping).

## Logic Modules
- **Lexer Tests**: Verifies that HTML strings are correctly tokenized into `Text` and `Tag` objects.
- **Layout Tests**: Validates the coordinate calculation and text wrapping logic, mocking `tkinter.font` to provide deterministic measurements.
- **Browser Logic Tests**:
    - **Augmentation Tests**: Verifies the Levenshtein-based fuzzy correction of schemes and TLDs.
    - **Navigation Tests**: Ensures the search bar triggers the correct load sequence.
    - **Viewport Tests**: Validates that `draw()` only executes commands visible within the current scroll range.

## Functional Tests Standards
- **Deterministic Output**: Every test must have a predictable outcome, avoiding any real network calls.
- **Complete Coverage**: Tests cover the "happy path" (valid URLs), "unhappy path" (invalid URLs), and "fuzzy path" (mistyped URLs).
- **Requirement Alignment**: Tests are directly mapped to functional requirements, such as the requirement that all URLs must end with a trailing slash.

## Sanity Logic Criteria
- **Crash Prevention**: Tests specifically check that `ValueError` in `URL` instantiation is caught and does not propagate to the main loop.
- **State Consistency**: Verified that `Browser` initialization does not accidentally trigger a network request without a valid URL.
- **Regression Testing**: The suite ensures that adding new features (like the search bar) does not break existing functionality (like scrolling).

## Future Improvements
- **Integration Tests**: Implement a small local mock server to test the actual network-to-interface pipeline.
- **Parameterized Testing**: Use `unittest` subtests or `pytest` parametrization to test a wider variety of mistyped URL patterns.
- **Visual Regression**: Implement a way to capture and compare canvas snapshots for layout verification.
- **Performance Benchmarking**: Add tests to measure the efficiency of the `display_list` filtering during high-frequency scrolling.
