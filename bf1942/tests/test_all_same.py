import unittest
from bf1942.pathmap import all_same

class AllSameTest(unittest.TestCase):
    def test_all_same(self):
        big_list = [255 for _ in range(1000)]

        self.assertTrue(all_same([]))
        self.assertTrue(all_same([1]))
        self.assertTrue(all_same([0]))
        self.assertTrue(all_same([0, 0]))
        self.assertTrue(all_same([1, 1]))
        self.assertTrue(all_same(big_list))

        self.assertFalse(all_same([0, 1]))
        big_list.append(0)
        self.assertFalse(all_same(big_list))

        with self.assertRaises(AssertionError):
            all_same(None)

        with self.assertRaises(AssertionError):
            all_same(1)

if __name__ == '__main__':
    unittest.main()