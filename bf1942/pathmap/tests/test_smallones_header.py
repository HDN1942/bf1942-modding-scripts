import unittest
from io import BytesIO
from struct import pack
from bf1942.pathmap.smallones import SmallonesHeader

class SmallonesHeaderTest(unittest.TestCase):
    def test_from_file(self):
        file = BytesIO(bytes([0x20, 0, 0, 0, 0x20, 0, 0, 0]))

        header = SmallonesHeader.from_file(file)

        self.assertEqual(32, header.tiles_per_row)
        self.assertEqual(32, header.tiles_per_column)

    def test_write(self):
        data = [32, 32]
        header = SmallonesHeader(data)
        file = BytesIO()

        header.write(file)
        file.seek(0, 0)

        data_bytes = bytes([0x20, 0, 0, 0, 0x20, 0, 0, 0])
        self.assertSequenceEqual(data_bytes, file.read(8))

if __name__ == '__main__':
    unittest.main()
