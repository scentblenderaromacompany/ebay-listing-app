import unittest
from unittest.mock import patch, mock_open, MagicMock
import tempfile
import os

# Import functions from the main script
from ebay_image_search import read_config, validate_base64_string, ebay_image_search, process_subfolders

class TestEbayImageSearch(unittest.TestCase):

    @patch("builtins.open", new_callable=mock_open, read_data="base64stringdata")
    @patch("yaml.safe_load", return_value={
        'api.production.ebay.com': {'token': 'testtoken', 'base_url': 'testurl'}
    })
    def test_read_config(self, mock_yaml, mock_file):
        config = read_config('production')
        self.assertEqual(config['token'], 'testtoken')
        self.assertEqual(config['base_url'], 'testurl')

    def test_validate_base64_string(self):
        valid_base64 = "aGVsbG8gd29ybGQ="  # "hello world" in base64
        invalid_base64 = "invalid base64"
        self.assertTrue(validate_base64_string(valid_base64))
        self.assertFalse(validate_base64_string(invalid_base64))

    @patch("requests.post")
    def test_ebay_image_search(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True}
        mock_post.return_value = mock_response

        response = ebay_image_search("aGVsbG8gd29ybGQ=", "testtoken", "testurl")
        self.assertEqual(response, {"success": True})

    @patch("os.walk")
    @patch("builtins.open", new_callable=mock_open, read_data="aGVsbG8gd29ybGQ=")
    @patch("ebay_image_search.ebay_image_search", return_value={"success": True})
    def test_process_subfolders(self, mock_search, mock_file, mock_walk):
        with tempfile.TemporaryDirectory() as tmpdirname:
            test_subdir = os.path.join(tmpdirname, 'base64')
            os.makedirs(test_subdir)
            with open(os.path.join(test_subdir, 'file.txt'), 'w') as f:
                f.write("aGVsbG8gd29ybGQ=")  # Write valid base64 content

            mock_walk.return_value = [(test_subdir, ('subdir',), ('file.txt',))]
            process_subfolders(tmpdirname, 'testtoken', 'testurl')
            mock_search.assert_called_with("aGVsbG8gd29ybGQ=", 'testtoken', 'testurl')

if __name__ == "__main__":
    unittest.main()
