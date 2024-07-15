import unittest
from PIL import Image
from bf1942.pathmap.conversion import pathmap_header_from_image
from bf1942.pathmap.pathmap import PathmapHeader

class PathmapHeaderFromImageTest(unittest.TestCase):
    def test_pathmap_header_from_image(self):
        image = Image.new('1', (1024, 1024))
        pm = pathmap_header_from_image(image, 0)

        self.assertEqual(4, pm.ln2_tiles_per_row)
        self.assertEqual(4, pm.ln2_tiles_per_column)
        self.assertEqual(6, pm.ln2_tile_resolution)
        self.assertEqual(0, pm.compression_level)
        self.assertEqual(0, pm.is_info)
        self.assertEqual(2, pm.data_offset)
        self.assertEqual(16, pm.tile_length)
        self.assertEqual(256, pm.tile_total)
        self.assertEqual(64, pm.tile_size)
        self.assertEqual(512, pm.tile_packed_size)
        self.assertEqual(1024, pm.map_width)
        self.assertEqual(1024, pm.map_height)

        image = Image.new('1', (2048, 2048))
        pm = pathmap_header_from_image(image, 0)

        self.assertEqual(5, pm.ln2_tiles_per_row)
        self.assertEqual(5, pm.ln2_tiles_per_column)
        self.assertEqual(6, pm.ln2_tile_resolution)
        self.assertEqual(0, pm.compression_level)
        self.assertEqual(0, pm.is_info)
        self.assertEqual(2, pm.data_offset)
        self.assertEqual(32, pm.tile_length)
        self.assertEqual(1024, pm.tile_total)
        self.assertEqual(64, pm.tile_size)
        self.assertEqual(512, pm.tile_packed_size)
        self.assertEqual(2048, pm.map_width)
        self.assertEqual(2048, pm.map_height)

        image = Image.new('1', (4096, 4096))
        pm = pathmap_header_from_image(image, 0)

        self.assertEqual(6, pm.ln2_tiles_per_row)
        self.assertEqual(6, pm.ln2_tiles_per_column)
        self.assertEqual(6, pm.ln2_tile_resolution)
        self.assertEqual(0, pm.compression_level)
        self.assertEqual(0, pm.is_info)
        self.assertEqual(2, pm.data_offset)
        self.assertEqual(64, pm.tile_length)
        self.assertEqual(4096, pm.tile_total)
        self.assertEqual(64, pm.tile_size)
        self.assertEqual(512, pm.tile_packed_size)
        self.assertEqual(4096, pm.map_width)
        self.assertEqual(4096, pm.map_height)

        image = Image.new('1', (2048, 2048))
        pm = pathmap_header_from_image(image, 1)

        self.assertEqual(5, pm.ln2_tiles_per_row)
        self.assertEqual(5, pm.ln2_tiles_per_column)
        self.assertEqual(7, pm.ln2_tile_resolution)
        self.assertEqual(1, pm.compression_level)
        self.assertEqual(0, pm.is_info)
        self.assertEqual(2, pm.data_offset)
        self.assertEqual(32, pm.tile_length)
        self.assertEqual(1024, pm.tile_total)
        self.assertEqual(64, pm.tile_size)
        self.assertEqual(512, pm.tile_packed_size)
        self.assertEqual(4096, pm.map_width)
        self.assertEqual(4096, pm.map_height)

        image = Image.new('1', (1024, 1024))
        pm = pathmap_header_from_image(image, 2)

        self.assertEqual(4, pm.ln2_tiles_per_row)
        self.assertEqual(4, pm.ln2_tiles_per_column)
        self.assertEqual(8, pm.ln2_tile_resolution)
        self.assertEqual(2, pm.compression_level)
        self.assertEqual(0, pm.is_info)
        self.assertEqual(2, pm.data_offset)
        self.assertEqual(16, pm.tile_length)
        self.assertEqual(256, pm.tile_total)
        self.assertEqual(64, pm.tile_size)
        self.assertEqual(512, pm.tile_packed_size)
        self.assertEqual(4096, pm.map_width)
        self.assertEqual(4096, pm.map_height)

if __name__ == '__main__':
    unittest.main()