import unittest
from unittest.mock import MagicMock, patch
from Interface.browser_module import lex, layout, Browser
from Styles.format_module import Text, Tag
import tkinter.font

class TestInterfaceLexer(unittest.TestCase):
    def test_lex_basic(self):
        body = "Hello <b>World</b>!"
        tokens = lex(body)
        self.assertEqual(len(tokens), 5)
        self.assertIsInstance(tokens[0], Text)
        self.assertEqual(tokens[0].text, "Hello ")
        self.assertIsInstance(tokens[1], Tag)
        self.assertEqual(tokens[1].tag, "b")
        self.assertIsInstance(tokens[2], Text)
        self.assertEqual(tokens[2].text, "World")
        self.assertIsInstance(tokens[3], Tag)
        self.assertEqual(tokens[3].tag, "/b")
        self.assertIsInstance(tokens[4], Text)
        self.assertEqual(tokens[4].text, "!")

    def test_lex_empty(self):
        self.assertEqual(lex(""), [])

    def test_lex_only_tags(self):
        body = "<b><i></i></b>"
        tokens = lex(body)
        # Fixed the attribute access: Tag has .tag, Text has .text
        result = [t.tag if hasattr(t, 'tag') else t.text for t in tokens]
        self.assertEqual(result, ["b", "i", "/i", "/b"])

class TestInterfaceLayout(unittest.TestCase):
    @patch('tkinter.font.Font')
    def test_layout_text_wrapping(self, mock_font):
        mock_font_instance = mock_font.return_value
        mock_font_instance.measure.return_value = 2000

        # Fix for the 'dict' * 'float' error:
        # layout() calls font.metrics("linespace"), not font.metrics()
        def metrics_side_effect(key):
            metrics = {'linespace': 12}
            return metrics.get(key, 0)
        mock_font_instance.metrics.side_effect = metrics_side_effect

        tokens = [Text("Word1 Word2")]
        # Mock measure to return 600 for each word, 10 for space,
        # and then return 10 for all subsequent calls to avoid StopIteration.
        mock_font_instance.measure.side_effect = [600, 600, 10, 10, 10, 10]


        try:
            display_list = layout(tokens)
            self.assertEqual(display_list[0][1], 20)
            self.assertGreater(display_list[1][1], 20)
        except AttributeError:
            self.fail("Interface.browser_module.layout() crashed on Text objects because it tries to access .tag")

    @patch('tkinter.font.Font')
    def test_layout_styles(self, mock_font):
        mock_font_instance = mock_font.return_value
        mock_font_instance.measure.return_value = 10
        mock_font_instance.metrics.return_value = {'linespace': 12}

        # Fix: Tag.__init__ in format_module.py takes (tag, parent=None)
        # Let's double check parser_module.Tag which is what lex() uses.
        # ParserModule.Tag: (tag, attrs, parent=None)
        # FormatModule.Tag: (tag)
        # Browser_module imports both!
        # Actually, browser_module.lex returns Styles.format_module.Tag/Text
        # based on the imports at the top of browser_module.py:
        # from Styles.format_module import Text, Tag

        tokens = [
            Tag("b"), Text("Bold"), Tag("/b"),
            Tag("i"), Text("Italic"), Tag("/i")
        ]
        try:
            display_list = layout(tokens)
            self.assertTrue(len(display_list) >= 2)
        except AttributeError:
            self.fail("Interface.browser_module.layout() crashed on Text objects during style processing")

class TestBrowser(unittest.TestCase):
    @patch('tkinter.Tk')
    @patch('tkinter.Canvas')
    def test_browser_init(self, mock_canvas, mock_tk):
        with patch.object(Browser, 'load'):
            with patch('tkinter.Entry') as mock_entry:
                instance = mock_entry.return_value
                instance.get.return_value = ""
                browser = Browser()
                self.assertEqual(browser.scroll, 0)
                self.assertEqual(browser.display_list, [])
                mock_tk.return_value.title.assert_called_with("Portal")

    @patch('tkinter.Tk')
    @patch('tkinter.Canvas')
    @patch('Interface.browser_module.URL')
    def test_fuzzy_scheme_correction(self, mock_url, mock_canvas, mock_tk):
        with patch.object(Browser, 'load') as mock_load:
            browser = Browser()
            browser.url_entry.get = MagicMock(return_value="htttps://google.com")
            browser.navigate()
            mock_url.assert_called_with("https://www.google.com/")
            mock_load.assert_called()

    @patch('tkinter.Tk')
    @patch('tkinter.Canvas')
    @patch('Interface.browser_module.URL')
    def test_fuzzy_tld_correction(self, mock_url, mock_canvas, mock_tk):
        with patch.object(Browser, 'load') as mock_load:
            browser = Browser()
            browser.url_entry.get = MagicMock(return_value="google.comm")
            browser.navigate()
            mock_url.assert_called_with("https://www.google.com/")
            mock_load.assert_called()

    @patch('tkinter.Tk')
    @patch('tkinter.Canvas')
    @patch('Interface.browser_module.URL')
    def test_partial_url_augmentation(self, mock_url, mock_canvas, mock_tk):
        with patch.object(Browser, 'load') as mock_load:
            browser = Browser()
            browser.url_entry.get = MagicMock(return_value="google.com")
            browser.navigate()
            mock_url.assert_called_with("https://www.google.com/")
            mock_load.assert_called()

    @patch('tkinter.Tk')
    @patch('tkinter.Canvas')
    @patch('Interface.browser_module.URL')
    def test_trailing_slash_addition(self, mock_url, mock_canvas, mock_tk):
        with patch.object(Browser, 'load') as mock_load:
            browser = Browser()
            browser.url_entry.get = MagicMock(return_value="http://google.com")
            browser.navigate()
            mock_url.assert_called_with("http://www.google.com/")
            mock_load.assert_called()

    @patch('tkinter.Tk')
    @patch('tkinter.Canvas')
    @patch('Interface.browser_module.URL')
    def test_complex_mistyped_url(self, mock_url, mock_canvas, mock_tk):
        with patch.object(Browser, 'load') as mock_load:
            browser = Browser()
            browser.url_entry.get = MagicMock(return_value="htttp://google.con")
            browser.navigate()
            mock_url.assert_called_with("http://www.google.com/")
            mock_load.assert_called()

    @patch('tkinter.Tk')
    @patch('tkinter.Canvas')
    @patch('Interface.browser_module.URL')
    def test_navigate_full_url(self, mock_url, mock_canvas, mock_tk):
        with patch.object(Browser, 'load') as mock_load:
            browser = Browser()
            # Mock the entry to return a specific string
            browser.url_entry.get = MagicMock(return_value="https://google.com")
            browser.navigate()
            mock_url.assert_called_with("https://www.google.com/")
            mock_load.assert_called()

    @patch('tkinter.Tk')
    @patch('tkinter.Canvas')
    @patch('Interface.browser_module.URL')
    def test_navigate_partial_url(self, mock_url, mock_canvas, mock_tk):
        with patch.object(Browser, 'load') as mock_load:
            browser = Browser()
            browser.url_entry.get = MagicMock(return_value="google.com")
            browser.navigate()
            mock_url.assert_called_with("https://www.google.com/")
            mock_load.assert_called()

    @patch('tkinter.Tk')
    @patch('tkinter.Canvas')
    @patch('Interface.browser_module.URL')
    def test_navigate_invalid_url(self, mock_url, mock_canvas, mock_tk):
        mock_url.side_effect = ValueError("Invalid URL")
        with patch.object(Browser, 'load') as mock_load:
            browser = Browser()
            browser.url_entry.get = MagicMock(return_value="invalid-url")
            # Should not raise exception
            browser.navigate()
            mock_url.assert_called()
            mock_load.assert_not_called()

    @patch('tkinter.Tk')
    @patch('tkinter.Canvas')
    @patch('Interface.browser_module.URL')
    @patch('sys.argv', ['browser_module.py', 'http://test.com'])
    def test_initial_url_loading(self, mock_url, mock_canvas, mock_tk):
        with patch.object(Browser, 'load') as mock_load:
            # Mock the Entry object's behavior
            with patch('tkinter.Entry') as mock_entry:
                instance = mock_entry.return_value
                instance.get.return_value = 'http://test.com'

                browser = Browser()
                instance.insert.assert_called_with(0, 'http://www.test.com/')
                mock_load.assert_called()

    @patch('tkinter.Tk')
    @patch('tkinter.Canvas')
    def test_scroll_logic(self, mock_canvas, mock_tk):
        with patch.object(Browser, 'load'):
            # Mock the Entry object's behavior to avoid TypeError in __init__
            with patch('tkinter.Entry') as mock_entry:
                instance = mock_entry.return_value
                instance.get.return_value = ""
                browser = Browser()
                browser.scroll_down(None)
                self.assertEqual(browser.scroll, 10)
                browser.scroll_up(None)
                self.assertEqual(browser.scroll, 0)
                browser.scroll_up(None)
                self.assertEqual(browser.scroll, 0)

    @patch('tkinter.Tk')
    @patch('tkinter.Canvas')
    def test_draw_filtering(self, mock_canvas, mock_tk):
        with patch.object(Browser, 'load'):
            with patch('tkinter.Entry') as mock_entry:
                instance = mock_entry.return_value
                instance.get.return_value = ""
                browser = Browser()
                cmd_visible = MagicMock()
                cmd_visible.y = 100
                cmd_visible.y2 = 110
                cmd_above = MagicMock()
                cmd_above.y = -100
                cmd_above.y2 = -90
                cmd_below = MagicMock()
                cmd_below.y = 2000
                cmd_below.y2 = 2010
                browser.display_list = [cmd_visible, cmd_above, cmd_below]
                browser.scroll = 0
                browser.draw()
                cmd_visible.execute.assert_called()
                cmd_above.execute.assert_not_called()
                cmd_below.execute.assert_not_called()

if __name__ == "__main__":
    unittest.main()
