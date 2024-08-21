import unittest
from filtering import extract_url, form_name_of_site, clean_string


class UnitTests(unittest.TestCase):
    def test_extract_url(self):
        self.assertEqual(extract_url('https://www.socialexplorer.com'), 'socialexplorer')
        self.assertEqual(extract_url('https://us.socialexplorer.com'), 'ussocialexplorer')
        self.assertEqual(extract_url('https://socialexplorer.com'), 'socialexplorer')

    def test_form_name_of_site(self):
        self.assertEqual(form_name_of_site('Social Explorer'), 'socialexplorer')
        self.assertEqual(form_name_of_site('Social?-.,Explorer'), 'socialexplorer')
        self.assertEqual(form_name_of_site('   socialexplorer'), 'socialexplorer')

    def test_clean_string(self):
        self.assertEqual(clean_string('selfstoragesocialexplorer'), 'socialexplorer')
        self.assertEqual(clean_string('stosocialexplorerrage'), 'stosocialexplorerrage')
        self.assertEqual(clean_string('selfstorage'), '')


if __name__ == "__main__":
    unittest.main()
