import unittest
import bf1942.tests.util as testutil
from pathlib import Path
from PIL import Image, ImageChops, ImageDraw
from bf1942.pathmap.conversion import image_to_pathmap, image_from_pathmap

class ImageToPathmapRoundtripTest(unittest.TestCase):
    def setUp(self):
        testutil.remove_dummy_files(self)

        self.root = testutil.create_dummy_files({})

        self.image = Image.new('1', (1024, 1024))
        self.draw = ImageDraw.Draw(self.image)

    def tearDown(self):
        testutil.remove_dummy_files(self)

    def assertImageEqual(self, first, second):
        diff = ImageChops.difference(first, second)
        bbox = diff.getbbox()
        if bbox:
            self.fail(f'images are different {bbox[0]}x{bbox[1]} {bbox[2]}x{bbox[3]}')

    def roundtrip(self):
        self.image.save(self.root / 'test.bmp')
        pm = image_to_pathmap(self.root / 'test.bmp', self.root)
        return image_from_pathmap(self.root / 'test0Level0Map.raw')

    def test_image_to_pathmap_roundtrip_triangle1(self):
        self.draw.polygon([(0, 0), (1023, 1023), (0, 1023)], fill=255)
        result = self.roundtrip()
        self.assertImageEqual(self.image, result)

    # def test_image_to_pathmap_roundtrip_triangle2(self):
    #     self.draw.polygon([(0, 0), (1023, 0), (1023, 1023)], fill=255)
    #     result = self.roundtrip()
    #     self.assertImageEqual(self.image, result)

    # def test_image_to_pathmap_roundtrip_triangle3(self):
    #     self.draw.polygon([(0, 0), (1023, 0), (0, 1023)], fill=255)
    #     result = self.roundtrip()
    #     self.assertImageEqual(self.image, result)

    # def test_image_to_pathmap_roundtrip_triangle4(self):
    #     self.draw.polygon([(0, 1023), (1023, 1023), (1023, 0)], fill=255)
    #     result = self.roundtrip()
    #     self.assertImageEqual(self.image, result)

    # def test_image_to_pathmap_roundtrip_noise(self):
    #     thresh = 200
    #     fn = lambda x : 255 if x > thresh else 0
    #     self.image = Image.effect_noise((1024, 1024), 255).point(fn, mode='1')
    #     result = self.roundtrip()
    #     self.assertImageEqual(self.image, result)

if __name__ == '__main__':
    unittest.main()