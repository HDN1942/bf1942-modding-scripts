import unittest
from bf1942.pathmap.util import pack_data2b

class PackData2bTest(unittest.TestCase):
    def test_pack_data2b_single_byte(self):
        packed = pack_data2b([0, 0, 0, 0])
        self.assertEqual(1, len(packed))
        self.assertEqual(0, packed[0])

        packed = pack_data2b([3, 3, 3, 3])
        self.assertEqual(0xff, packed[0])

        packed = pack_data2b([1, 0, 0, 0])
        self.assertEqual(0x01, packed[0])

        packed = pack_data2b([0, 0, 0, 1])
        self.assertEqual(0x40, packed[0])

        packed = pack_data2b([0, 1, 0, 1])
        self.assertEqual(0x44, packed[0])

        packed = pack_data2b([1, 0, 1, 0])
        self.assertEqual(0x11, packed[0])

        packed = pack_data2b([1, 2, 3, 0])
        self.assertEqual(0x39, packed[0])

        packed = pack_data2b([3, 0, 1, 2])
        self.assertEqual(0x93, packed[0])

    def test_pack_multiple_bytes(self):
        packed = pack_data2b([
            0, 1, 0, 1, # 0x44
            2, 0, 3, 0, # 0x32
            1, 1, 1, 1, # 0x55
            3, 3, 3, 3, # 0xff
            3, 0, 0, 2, # 0x83
            0, 0, 0, 0, # 0x00
            0, 0, 0, 1, # 0x40
            2, 0, 0, 0  # 0x02
        ])
        self.assertEqual(8, len(packed))
        self.assertEqual([0x44, 0x32, 0x55, 0xff, 0x83, 0x00, 0x40, 0x02], packed)

    def test_pack_data_not_multiple_of_4(self):
        packed = pack_data2b([1])
        self.assertEqual(1, len(packed))
        self.assertEqual(1, packed[0])

        packed = pack_data2b([0, 1, 1])
        self.assertEqual(0x14, packed[0])

    def test_bad_data(self):
        packed = pack_data2b([])
        self.assertEqual([], packed)

        with self.assertRaises(TypeError):
            pack_data2b(None)

        with self.assertRaises(TypeError):
            pack_data2b(1)

        with self.assertRaises(TypeError):
            pack_data2b("foobar")

        with self.assertRaises(TypeError):
            pack_data2b([0.1])

if __name__ == '__main__':
    unittest.main()