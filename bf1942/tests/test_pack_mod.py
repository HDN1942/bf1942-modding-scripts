import platform
import shutil
import unittest
from pathlib import Path
from bf1942.rfa_facade import *
from bf1942.testutil import *

class TestMethod(unittest.TestCase):
    def setUp(self):
        self.base = create_dummy_directory(__file__)
        self.src = self.base / 'src'
        self.dst = self.base / 'dst'
        self.levels = ['Level1', 'Level2']

        for directory in TOP_LEVEL_RFAS:
            create_dummy_file(self.src / Path(directory, f'{directory}.con'))

        for directory in BF1942_LEVEL_RFAS:
            create_dummy_file(self.src / Path(BF1942_DIRECTORY, directory, f'{directory}.con'))

        for directory in self.levels:
            create_dummy_file(self.src / Path(BF1942_DIRECTORY, LEVELS_DIRECTORY, directory, f'{directory}.con'))

    def tearDown(self):
        shutil.rmtree(self.base)

    def test_correct_rfa_created(self):
        pack_mod(str(self.src), str(self.dst), False)

        for directory in TOP_LEVEL_RFAS:
            assert_rfa(self, self.dst / f'{directory}.rfa', [
                f'{directory}/{directory}.con'
            ])

        for directory in BF1942_LEVEL_RFAS:
            assert_rfa(self, self.dst / Path(BF1942_DIRECTORY, f'{directory}.rfa'), [
                f'{BF1942_DIRECTORY}/{directory}/{directory}.con'
            ])

        for directory in self.levels:
            assert_rfa(self, self.dst / Path(BF1942_DIRECTORY, LEVELS_DIRECTORY, f'{directory}.rfa'), [
                f'{BF1942_DIRECTORY}/{LEVELS_DIRECTORY}/{directory}/{directory}.con'
            ])

    @unittest.skipIf(platform.system() != 'Linux', 'Test can only be run on a case-sensitive file system')
    def test_handles_paths_case_insensitive(self):
        shutil.move(Path(self.src, BF1942_DIRECTORY), Path(self.src, 'Bf1942'))
        shutil.move(Path(self.src, 'objects'), Path(self.src, 'Objects'))
        shutil.move(Path(self.src, 'standardmesh'), Path(self.src, 'standardMesh'))

        pack_mod(str(self.src), str(self.dst), False)

        assert_rfa(self, self.dst / 'Objects.rfa', ['Objects/objects.con'])
        assert_rfa(self, self.dst / 'standardMesh.rfa', ['standardMesh/standardmesh.con'])
        assert_rfa(self, self.dst / Path('Bf1942', 'game.rfa'), ['Bf1942/game/game.con'])

        for directory in self.levels:
            assert_rfa(self, self.dst / Path('Bf1942', 'levels', f'{directory}.rfa'), [
                f'Bf1942/levels/{directory}/{directory}.con'
            ])

    def test_non_rfa_directories_are_not_packed(self):
        create_dummy_file(self.src / Path('foo', 'foo.con'))
        create_dummy_file(self.src / Path('bf1942', 'bar', 'bar.con'))

        pack_mod(str(self.src), str(self.dst), False)

        self.assertFalse((self.dst / 'foo.rfa').exists())
        self.assertFalse((self.dst / Path('bf1942', 'bar.rfa')).exists())

if __name__ == '__main__':
    unittest.main()