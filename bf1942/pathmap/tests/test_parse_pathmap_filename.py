import unittest
import bf1942.tests.util as testutil
from bf1942.pathmap.shell import parse_pathmap_filename

class ParsePathmapFilenameTest(unittest.TestCase):

    def test_parse_pathmap_filename(self):
        result = parse_pathmap_filename('Tank0Level0Map.raw')
        self.assertEqual('Tank', result.name)
        self.assertEqual(0, result.index)
        self.assertEqual(0, result.level)
        self.assertFalse(result.is_boat)

        result = parse_pathmap_filename('Tank0Level1Map.raw')
        self.assertEqual('Tank', result.name)
        self.assertEqual(0, result.index)
        self.assertEqual(1, result.level)
        self.assertFalse(result.is_boat)

        result = parse_pathmap_filename('Boat2Level2Map.raw')
        self.assertEqual('Boat', result.name)
        self.assertEqual(2, result.index)
        self.assertEqual(2, result.level)
        self.assertTrue(result.is_boat)

        result = parse_pathmap_filename('TankInfo.raw')
        self.assertEqual('Tank', result.name)
        self.assertEqual(0, result.index)
        self.assertEqual(0, result.level)
        self.assertFalse(result.is_boat)

        result = parse_pathmap_filename('InfantryInfo.raw')
        self.assertEqual('Infantry', result.name)
        self.assertEqual(1, result.index)
        self.assertEqual(0, result.level)
        self.assertFalse(result.is_boat)

        result = parse_pathmap_filename('BoatInfo.raw')
        self.assertEqual('Boat', result.name)
        self.assertEqual(2, result.index)
        self.assertEqual(2, result.level)
        self.assertTrue(result.is_boat)

        result = parse_pathmap_filename('LandingCraftInfo.raw')
        self.assertEqual('LandingCraft', result.name)
        self.assertEqual(3, result.index)
        self.assertEqual(2, result.level)
        self.assertTrue(result.is_boat)

        result = parse_pathmap_filename('CarInfo.raw')
        self.assertEqual('Car', result.name)
        self.assertEqual(4, result.index)
        self.assertEqual(0, result.level)
        self.assertFalse(result.is_boat)

        result = parse_pathmap_filename('AmphibiusInfo.raw')
        self.assertEqual('Amphibius', result.name)
        self.assertEqual(4, result.index)
        self.assertEqual(0, result.level)
        self.assertFalse(result.is_boat)

        result = parse_pathmap_filename('UnknownInfo.raw')
        self.assertEqual('Unknown', result.name)
        self.assertEqual(0, result.index)
        self.assertEqual(0, result.level)
        self.assertFalse(result.is_boat)

        result = parse_pathmap_filename('Tank.raw')
        self.assertEqual('Tank', result.name)
        self.assertEqual(0, result.index)
        self.assertEqual(0, result.level)
        self.assertFalse(result.is_boat)

        result = parse_pathmap_filename('Infantry.raw')
        self.assertEqual('Infantry', result.name)
        self.assertEqual(1, result.index)
        self.assertEqual(0, result.level)
        self.assertFalse(result.is_boat)

        result = parse_pathmap_filename('Boat.raw')
        self.assertEqual('Boat', result.name)
        self.assertEqual(2, result.index)
        self.assertEqual(2, result.level)
        self.assertTrue(result.is_boat)

        result = parse_pathmap_filename('LandingCraft.raw')
        self.assertEqual('LandingCraft', result.name)
        self.assertEqual(3, result.index)
        self.assertEqual(2, result.level)
        self.assertTrue(result.is_boat)

        result = parse_pathmap_filename('Car.raw')
        self.assertEqual('Car', result.name)
        self.assertEqual(4, result.index)
        self.assertEqual(0, result.level)
        self.assertFalse(result.is_boat)

        result = parse_pathmap_filename('Amphibius.raw')
        self.assertEqual('Amphibius', result.name)
        self.assertEqual(4, result.index)
        self.assertEqual(0, result.level)
        self.assertFalse(result.is_boat)

        result = parse_pathmap_filename('Unknown.raw')
        self.assertEqual('Unknown', result.name)
        self.assertEqual(0, result.index)
        self.assertEqual(0, result.level)
        self.assertFalse(result.is_boat)

        result = parse_pathmap_filename('Unknown')
        self.assertEqual('Unknown', result.name)
        self.assertEqual(0, result.index)
        self.assertEqual(0, result.level)
        self.assertFalse(result.is_boat)

        with self.assertRaises(TypeError):
            parse_pathmap_filename(None)

        with self.assertRaises(TypeError):
            parse_pathmap_filename(1)

        with self.assertRaises(AssertionError):
            parse_pathmap_filename('')

if __name__ == '__main__':
    unittest.main()