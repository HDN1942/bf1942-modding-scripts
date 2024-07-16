import unittest
import bf1942.tests.util as testutil
from bf1942.pathmap.shell import parse_pathmap_filename

class ParsePathmapFilenameTest(unittest.TestCase):

    def test_parse_pathmap_filename(self):
        name, index, level = parse_pathmap_filename('Tank0Level0Map.raw')
        self.assertEqual('Tank', name)
        self.assertEqual(0, index)
        self.assertEqual(0, level)

        name, index, level = parse_pathmap_filename('Tank0Level1Map.raw')
        self.assertEqual('Tank', name)
        self.assertEqual(0, index)
        self.assertEqual(1, level)

        name, index, level = parse_pathmap_filename('Boat2Level2Map.raw')
        self.assertEqual('Boat', name)
        self.assertEqual(2, index)
        self.assertEqual(2, level)

        name, index, level = parse_pathmap_filename('TankInfo.raw')
        self.assertEqual('Tank', name)
        self.assertEqual(0, index)
        self.assertEqual(0, level)

        name, index, level = parse_pathmap_filename('InfantryInfo.raw')
        self.assertEqual('Infantry', name)
        self.assertEqual(1, index)
        self.assertEqual(0, level)

        name, index, level = parse_pathmap_filename('BoatInfo.raw')
        self.assertEqual('Boat', name)
        self.assertEqual(2, index)
        self.assertEqual(2, level)

        name, index, level = parse_pathmap_filename('LandingCraftInfo.raw')
        self.assertEqual('LandingCraft', name)
        self.assertEqual(3, index)
        self.assertEqual(2, level)

        name, index, level = parse_pathmap_filename('CarInfo.raw')
        self.assertEqual('Car', name)
        self.assertEqual(4, index)
        self.assertEqual(0, level)

        name, index, level = parse_pathmap_filename('AmphibiusInfo.raw')
        self.assertEqual('Amphibius', name)
        self.assertEqual(4, index)
        self.assertEqual(0, level)

        name, index, level = parse_pathmap_filename('UnknownInfo.raw')
        self.assertEqual('Unknown', name)
        self.assertEqual(0, index)
        self.assertEqual(0, level)

        name, index, level = parse_pathmap_filename('Tank.raw')
        self.assertEqual('Tank', name)
        self.assertEqual(0, index)
        self.assertEqual(0, level)

        name, index, level = parse_pathmap_filename('Infantry.raw')
        self.assertEqual('Infantry', name)
        self.assertEqual(1, index)
        self.assertEqual(0, level)

        name, index, level = parse_pathmap_filename('Boat.raw')
        self.assertEqual('Boat', name)
        self.assertEqual(2, index)
        self.assertEqual(2, level)

        name, index, level = parse_pathmap_filename('LandingCraft.raw')
        self.assertEqual('LandingCraft', name)
        self.assertEqual(3, index)
        self.assertEqual(2, level)

        name, index, level = parse_pathmap_filename('Car.raw')
        self.assertEqual('Car', name)
        self.assertEqual(4, index)
        self.assertEqual(0, level)

        name, index, level = parse_pathmap_filename('Amphibius.raw')
        self.assertEqual('Amphibius', name)
        self.assertEqual(4, index)
        self.assertEqual(0, level)

        name, index, level = parse_pathmap_filename('Unknown.raw')
        self.assertEqual('Unknown', name)
        self.assertEqual(0, index)
        self.assertEqual(0, level)

        name, index, level = parse_pathmap_filename('Unknown')
        self.assertEqual('Unknown', name)
        self.assertEqual(0, index)
        self.assertEqual(0, level)

        with self.assertRaises(TypeError):
            parse_pathmap_filename(None)

        with self.assertRaises(TypeError):
            parse_pathmap_filename(1)

        with self.assertRaises(AssertionError):
            parse_pathmap_filename('')

if __name__ == '__main__':
    unittest.main()