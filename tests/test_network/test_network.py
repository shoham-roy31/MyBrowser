import unittest
from unittest.mock import MagicMock, patch
from Network.connector_module import URL, assert_params

class TestNetwork(unittest.TestCase):
    # Tests for assert_params
    def test_assert_params_valid(self):
        # Should not raise any exception
        assert_params(url="http://google.com")

    def test_assert_params_none(self):
        with self.assertRaises(ValueError) as cm:
            assert_params(url=None)
        self.assertEqual(str(cm.exception), "URL cannot be None")

    def test_assert_params_type_error(self):
        with self.assertRaises(TypeError) as cm:
            assert_params(url=123)
        self.assertEqual(str(cm.exception), "URL must be a string")

    # Tests for URL class initialization
    def test_url_init_http(self):
        url_obj = URL("http://example.com/path/to/page")
        self.assertEqual(url_obj.scheme, "http")
        self.assertEqual(url_obj.host, "example.com")
        self.assertEqual(url_obj.path, "/path/to/page")
        self.assertEqual(url_obj.port, 80)

    def test_url_init_https(self):
        url_obj = URL("https://example.com/index.html")
        self.assertEqual(url_obj.scheme, "https")
        self.assertEqual(url_obj.host, "example.com")
        self.assertEqual(url_obj.path, "/index.html")
        self.assertEqual(url_obj.port, 443)

    def test_url_init_custom_port(self):
        url_obj = URL("http://example.com:8080/test")
        self.assertEqual(url_obj.host, "example.com")
        self.assertEqual(url_obj.port, 8080)

    def test_url_init_invalid_protocol(self):
        with self.assertRaises(ValueError) as cm:
            URL("ftp://example.com")
        self.assertIn("Unsupported Protocol", str(cm.exception))

    def test_url_init_malformed(self):
        with self.assertRaises(ValueError) as cm:
            URL("not_a_url")
        self.assertIn("Invalid URL", str(cm.exception))

    # Tests for URL.request using Mocks
    @patch('socket.socket')
    def test_request_success(self, mock_socket):
        # Mock the socket and the makefile response
        mock_s_instance = mock_socket.return_value
        mock_file = MagicMock()

        # Mock the response lines
        # 1. Status line, 2. Header 1, 3. Header 2, 4. Empty line (\r\n), 5. Body
        mock_file.readline.side_effect = [
            "HTTP/1.1 200 OK\r\n",
            "Content-Type: text/html\r\n",
            "\r\n"
        ]
        mock_file.read.return_value = "<html>Hello World</html>"
        mock_s_instance.makefile.return_value = mock_file

        url_obj = URL("http://example.com/")
        content = url_obj.request()

        self.assertEqual(content, "<html>Hello World</html>")
        mock_s_instance.connect.assert_called_with(("example.com", 80))
        mock_s_instance.send.assert_called()

    @patch('socket.socket')
    def test_request_failure(self, mock_socket):
        # Simulate a connection error
        mock_s_instance = mock_socket.return_value
        mock_s_instance.connect.side_effect = Exception("Connection timed out")

        url_obj = URL("http://example.com/")
        content = url_obj.request()

        self.assertEqual(content, -1)

if __name__ == "__main__":
    unittest.main()
