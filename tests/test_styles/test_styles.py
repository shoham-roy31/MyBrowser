import unittest
from unittest.mock import MagicMock, patch
from Styles.parser_module import HTMLParser, Tag, Text
from Styles.format_module import DocumentLayout, BlockLayout

class TestParser(unittest.TestCase):
    def test_basic_parsing(self):
        body = "<html><body><p>Hello World</p></body></html>"
        parser = HTMLParser(body)
        root = parser.parse()
        self.assertEqual(root.tag, "html")
        self.assertEqual(root.children[0].tag, "body")
        self.assertEqual(root.children[0].children[0].tag, "p")
        self.assertEqual(root.children[0].children[0].children[0].text, "Hello World")

    def test_implicit_tags(self):
        # Testing that HTMLParser automatically adds <html>, <body> etc.
        body = "Hello World"
        parser = HTMLParser(body)
        root = parser.parse()
        self.assertEqual(root.tag, "html")
        # Structure should be html -> body -> text
        self.assertEqual(root.children[0].tag, "body")
        self.assertIsInstance(root.children[0].children[0], Text)

    def test_self_closing_tags(self):
        body = "<html><body><img src='test.jpg'><br>Text</body></html>"
        parser = HTMLParser(body)
        root = parser.parse()
        body_node = root.children[0]
        # img and br should be children of body, not parents of "Text"
        self.assertEqual(body_node.children[0].tag, "img")
        self.assertEqual(body_node.children[1].tag, "br")
        self.assertIsInstance(body_node.children[2], Text)

    def test_attributes_parsing(self):
        body = '<div class="main" id="top" data-custom="val">Content</div>'
        parser = HTMLParser(body)
        root = parser.parse()
        # Since we didn't provide <html>, it will be the root
        div_node = root.children[0].children[0] if root.tag == "html" else root.children[0]
        self.assertEqual(div_node.attrs["class"], "main")
        self.assertEqual(div_node.attrs["id"], "top")
        self.assertEqual(div_node.attrs["data-custom"], "val")

    def test_quoted_attributes_with_spaces(self):
        body = '<div title="Hello World" class=\'my class\'>Content</div>'
        parser = HTMLParser(body)
        root = parser.parse()
        div_node = root.children[0].children[0] if root.tag == "html" else root.children[0]
        self.assertEqual(div_node.attrs["title"], "Hello World")
        self.assertEqual(div_node.attrs["class"], "my class")

    def test_malformed_html_recovery(self):
        # Unclosed tags should be closed by finish()
        body = "<html><body><div>Unclosed div"
        parser = HTMLParser(body)
        root = parser.parse()
        self.assertEqual(root.tag, "html")
        # Verify that the stack is drained and we have a valid tree
        self.assertTrue(len(root.children) > 0)

class TestFormat(unittest.TestCase):
    def setUp(self):
        # Create a minimal mock tree for layout tests
        self.root_node = Tag("html", {}, None)
        self.body_node = Tag("body", {}, self.root_node)
        self.root_node.children.append(self.body_node)
        self.text_node = Text("Hello World", self.body_node)
        self.body_node.children.append(self.text_node)

    @patch('tkinter.font.Font')
    def test_block_layout_init(self, mock_font):
        # Mock font.measure to return fixed width
        mock_font_instance = mock_font.return_value
        mock_font_instance.measure.return_value = 10

        # Fix: metrics() is called in two ways in format_module.py:
        # 1. font.metrics() -> returns a dict (used in flush() to get max ascent/descent)
        # 2. font.metrics('ascent') -> returns a value (used in flush() for y calculation)
        def side_effect(key=None):
            metrics = {'ascent': 10, 'descent': 2, 'linespace': 12}
            if key is None:
                return metrics
            return metrics.get(key, 0)

        mock_font_instance.metrics.side_effect = side_effect

        # We need a parent for BlockLayout
        parent = MagicMock()
        parent.x = 10
        parent.y = 20
        parent.width = 1000

        prev = MagicMock()
        prev.y = 0
        prev.height = 0

        layout = BlockLayout(self.text_node, parent, prev)

        # Trigger layout to populate x, y, width
        layout.layout()

        self.assertEqual(layout.x, 10)
        # Test that basic layout properties are initialized

    def test_document_layout_structure(self):
        parent = MagicMock()
        parent.x = 10
        parent.y = 20
        parent.width = 1000

        doc_layout = DocumentLayout(self.root_node, parent, None)
        # we avoid calling .layout() because it depends on tkFont which requires a display
        self.assertEqual(doc_layout.node, self.root_node)

if __name__ == "__main__":
    unittest.main()
