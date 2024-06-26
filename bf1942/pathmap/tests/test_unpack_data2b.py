import unittest
from bf1942.pathmap.util import unpack_data2b

class UnpackDataTest(unittest.TestCase):
    def test_unpack_single_byte(self):
        unpacked = unpack_data2b([0x00])
        self.assertEqual([0, 0, 0, 0], unpacked)

        unpacked = unpack_data2b([0xff])
        self.assertEqual([3, 3, 3, 3], unpacked)

        unpacked = unpack_data2b([0x01])
        self.assertEqual([1, 0, 0, 0], unpacked)

        unpacked = unpack_data2b([0x80])
        self.assertEqual([0, 0, 0, 2], unpacked)

        unpacked = unpack_data2b([0x44])
        self.assertEqual([0, 1, 0, 1], unpacked)

        unpacked = unpack_data2b([0x11])
        self.assertEqual([1, 0, 1, 0], unpacked)

        unpacked = unpack_data2b([0x4e])
        self.assertEqual([2, 3, 0, 1], unpacked)

        unpacked = unpack_data2b([0x2d])
        self.assertEqual([1, 3, 2, 0], unpacked)

    def test_unpack_multiple_bytes(self):
        unpacked = unpack_data2b([0x44, 0x32, 0x55, 0xff, 0x83, 0x00, 0x40, 0x02])
        self.assertEqual([
            0, 1, 0, 1, # 0x44
            2, 0, 3, 0, # 0x32
            1, 1, 1, 1, # 0x55
            3, 3, 3, 3, # 0xff
            3, 0, 0, 2, # 0x83
            0, 0, 0, 0, # 0x00
            0, 0, 0, 1, # 0x40
            2, 0, 0, 0  # 0x02
        ], unpacked)

    def test_bad_data(self):
        unpacked = unpack_data2b([])
        self.assertEqual([], unpacked)

        with self.assertRaises(TypeError):
            unpack_data2b(None)

        with self.assertRaises(TypeError):
            unpack_data2b(1)

        with self.assertRaises(TypeError):
            unpack_data2b("foobar")

        with self.assertRaises(TypeError):
            unpack_data2b([0.1])

if __name__ == '__main__':
    unittest.main()