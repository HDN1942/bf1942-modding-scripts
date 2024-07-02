import unittest
import bf1942.tests.util as testutil
from bf1942.pathmap.shell import detect_output_format

class DetectOutputFormat(unittest.TestCase):
    def setUp(self):
        testutil.remove_dummy_files(self)

        self.root = testutil.create_dummy_files({
            'dir': {},
            'file.bmp': '',
            'file.png': '',
            'file.raw': '',
            'file.bad': ''
        })

    def tearDown(self):
        testutil.remove_dummy_files(self)

    def test_detect_output_format(self):
        # happy path
        self.assertEqual('bmp', detect_output_format('raw', self.root / 'file.bmp'))
        self.assertEqual('png', detect_output_format('raw', self.root / 'file.png'))
        self.assertEqual('dds', detect_output_format('raw', self.root / 'dir'))
        self.assertEqual('raw', detect_output_format('dds', self.root / 'dir'))
        self.assertEqual('raw', detect_output_format('bmp', self.root / 'dir'))
        self.assertEqual('raw', detect_output_format('png', self.root / 'dir'))

        # unhappy path
        self.assertIsNone(detect_output_format('png', self.root / 'file.bmp'))
        self.assertIsNone(detect_output_format('bmp', self.root / 'file.png'))
        self.assertIsNone(detect_output_format('bmp', self.root / 'file.raw'))
        self.assertIsNone(detect_output_format('bmp', self.root / 'file.bad'))
        self.assertIsNone(detect_output_format('raw', self.root / 'none.bmp'))

        # error path
        with self.assertRaises(AssertionError):
            detect_output_format('foo', self.root / 'dir')

if __name__ == '__main__':
    unittest.main()