import unittest
from bf1942.pathmap.util import unpack_data

class UnpackDataTest(unittest.TestCase):
    def test_unpack_single_byte(self):
        unpacked = unpack_data([0x00])
        self.assertEqual([0, 0, 0, 0, 0, 0, 0, 0], unpacked)

        unpacked = unpack_data([0xff])
        self.assertEqual([1, 1, 1, 1, 1, 1, 1, 1], unpacked)

        unpacked = unpack_data([0x01])
        self.assertEqual([1, 0, 0, 0, 0, 0, 0, 0], unpacked)

        unpacked = unpack_data([0x80])
        self.assertEqual([0, 0, 0, 0, 0, 0, 0, 1], unpacked)

        unpacked = unpack_data([0x88])
        self.assertEqual([0, 0, 0, 1, 0, 0, 0, 1], unpacked)

        unpacked = unpack_data([0xaa])
        self.assertEqual([0, 1, 0, 1, 0, 1, 0, 1], unpacked)

        unpacked = unpack_data([0x31])
        self.assertEqual([1, 0, 0, 0, 1, 1, 0, 0], unpacked)

        unpacked = unpack_data([0x43])
        self.assertEqual([1, 1, 0, 0, 0, 0, 1, 0], unpacked)

    def test_unpack_multiple_bytes(self):
        unpacked = unpack_data([0x88, 0x31, 0xaa, 0xff, 0x43, 0x00, 0x80, 0x01])
        self.assertEqual([
            0, 0, 0, 1, 0, 0, 0, 1, # 0x88
            1, 0, 0, 0, 1, 1, 0, 0, # 0x31
            0, 1, 0, 1, 0, 1, 0, 1, # 0xaa
            1, 1, 1, 1, 1, 1, 1, 1, # 0xff
            1, 1, 0, 0, 0, 0, 1, 0, # 0x43
            0, 0, 0, 0, 0, 0, 0, 0, # 0x00
            0, 0, 0, 0, 0, 0, 0, 1, # 0x80
            1, 0, 0, 0, 0, 0, 0, 0  # 0x01
        ], unpacked)

    def test_bad_data(self):
        unpacked = unpack_data([])
        self.assertEqual([], unpacked)

        with self.assertRaises(TypeError):
            unpack_data(None)

        with self.assertRaises(TypeError):
            unpack_data(1)

        with self.assertRaises(TypeError):
            unpack_data("foobar")

        with self.assertRaises(TypeError):
            unpack_data([0.1])

if __name__ == '__main__':
    unittest.main()