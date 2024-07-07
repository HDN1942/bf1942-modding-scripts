import unittest
import bf1942.tests.util as testutil
from bf1942.pathmap.shell import detect_input_format

class DetectInputFormatTest(unittest.TestCase):
    def setUp(self):
        testutil.remove_dummy_files(self)

        self.root = testutil.create_dummy_files({
            'dir': {},
            'file.bmp': '',
            'file.png': '',
            'file.raw': '',
            'file.bad': '',
            'file.dds': ''
        })

    def tearDown(self):
        testutil.remove_dummy_files(self)

    def test_detect_input_format(self):
        # happy path
        self.assertEqual('dds', detect_input_format(self.root / 'dir'))
        self.assertEqual('bmp', detect_input_format(self.root / 'file.bmp'))
        self.assertEqual('png', detect_input_format(self.root / 'file.png'))
        self.assertEqual('raw', detect_input_format(self.root / 'file.raw'))

        # unhappy path
        self.assertIsNone(detect_input_format(self.root / 'file.bad'))
        self.assertIsNone(detect_input_format(self.root / 'file.dds'))
        self.assertIsNone(detect_input_format(self.root / 'none.bmp'))

if __name__ == '__main__':
    unittest.main()