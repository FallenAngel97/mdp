import unittest
import MDPServer


class MDPClientTest(unittest.TestCase):
    def test_generating_strings(self):
        self.assertEqual(len(MDPServer.MDPServer().random_string(4)), 4)

if __name__ == '__main__':
    unittest.main()
