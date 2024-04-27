import unittest
from bf1942.pathmap import pack_data

class PackDataTest(unittest.TestCase):
    def test_pack_single_byte(self):
        packed = pack_data([0, 0, 0, 0, 0, 0, 0, 0])
        self.assertEqual(1, len(packed))
        self.assertEqual(0, packed[0])

        packed = pack_data([1, 1, 1, 1, 1, 1, 1, 1])
        self.assertEqual(0xff, packed[0])

        packed = pack_data([1, 0, 0, 0, 0, 0, 0, 0])
        self.assertEqual(0x01, packed[0])

        packed = pack_data([0, 0, 0, 0, 0, 0, 0, 1])
        self.assertEqual(0x80, packed[0])

        packed = pack_data([0, 0, 0, 1, 0, 0, 0, 1])
        self.assertEqual(0x88, packed[0])

        packed = pack_data([0, 1, 0, 1, 0, 1, 0, 1])
        self.assertEqual(0xaa, packed[0])

        packed = pack_data([1, 0, 0, 0, 1, 1, 0, 0])
        self.assertEqual(0x31, packed[0])

        packed = pack_data([1, 1, 0, 0, 0, 0, 1, 0])
        self.assertEqual(0x43, packed[0])

    def test_pack_multiple_bytes(self):
        packed = pack_data([
            0, 0, 0, 1, 0, 0, 0, 1, # 0x88
            1, 0, 0, 0, 1, 1, 0, 0, # 0x31
            0, 1, 0, 1, 0, 1, 0, 1, # 0xaa
            1, 1, 1, 1, 1, 1, 1, 1, # 0xff
            1, 1, 0, 0, 0, 0, 1, 0, # 0x43
            0, 0, 0, 0, 0, 0, 0, 0, # 0x00
            0, 0, 0, 0, 0, 0, 0, 1, # 0x80
            1, 0, 0, 0, 0, 0, 0, 0  # 0x01
        ])
        self.assertEqual(8, len(packed))
        self.assertEqual([0x88, 0x31, 0xaa, 0xff, 0x43, 0x00, 0x80, 0x01], packed)

    def test_pack_data_not_multiple_of_8(self):
        packed = pack_data([1])
        self.assertEqual(1, len(packed))
        self.assertEqual(1, packed[0])

        packed = pack_data([1, 0, 0, 0, 1, 1])
        self.assertEqual(0x31, packed[0])

    def test_bad_data(self):
        packed = pack_data([])
        self.assertEqual([], packed)

        with self.assertRaises(TypeError):
            pack_data(None)

        with self.assertRaises(TypeError):
            pack_data(1)

        with self.assertRaises(TypeError):
            packed = pack_data("foobar")

        with self.assertRaises(TypeError):
            packed = pack_data([0.1])

        with self.assertRaises(ValueError, msg='Invalid data, values must be 0 or 1'):
            packed = pack_data([0, 1, 0, 4, 0, 1, 0, 0])

if __name__ == '__main__':
    unittest.main()