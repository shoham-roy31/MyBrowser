import unittest
import sys
import os

# Add the root directory to sys.path to ensure imports work across different test modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the test cases from the specific modules
from tests.test_network.test_network import TestNetwork
from tests.test_styles.test_styles import TestParser, TestFormat
from tests.test_interface.test_interface import TestInterfaceLexer, TestInterfaceLayout, TestBrowser

class TestSuite(unittest.TestCase):
    """
    Wrapper class to orchestrate all unit tests in the project.
    This allows running all tests from a single entry point.
    """
    def test_network_module(self):
        """Runs all tests in the Network module."""
        self.run_test_class(TestNetwork)

    def test_styles_module(self):
        """Runs all tests in the Styles module."""
        self.run_test_class(TestParser)
        self.run_test_class(TestFormat)

    def test_interface_module(self):
        """Runs all tests in the Interface module."""
        self.run_test_class(TestInterfaceLexer)
        self.run_test_class(TestInterfaceLayout)
        self.run_test_class(TestBrowser)

    def run_test_class(self, test_class):
        """Helper to run all methods of a specific TestCase class."""
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromTestCase(test_class)
        result = unittest.TextTestRunner(verbosity=1).run(suite)
        if not result.wasSuccessful():
            self.fail(f"Tests in {test_class.__name__} failed.")

if __name__ == "__main__":
    unittest.main()
