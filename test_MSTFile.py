from unittest import TestCase
from MSTFile import MST
from UndirectedGraphFile import UndirectedGraph


class TestMST(TestCase):
    def test_find_root(self):
        G = UndirectedGraph(filename="UndirectedGraph2.txt")
        generator = MST(G)
        generator.disjoint_set = {0: [-1, 2], 1: [0, 1], 2: [-1, 1], 3: [-1, 3], 4: [5, 2], 5: [3, 1]}
        expected_roots = (0, 0, 2, 3, 3, 3)
        for i in range(len(expected_roots)):
            root = generator.find_root(i)
            self.assertEquals(expected_roots[i],
                              root,
                              f"Found root incorrect. You found root to be {root}, "
                              f"but it should be {expected_roots[i]}.")

    def test_union(self):
        G = UndirectedGraph(filename="UndirectedGraph2.txt")
        generator = MST(G)
        generator.disjoint_set = {0: [-1, 2], 1: [0, 1], 2: [-1, 1], 3: [-1, 3], 4: [5, 2], 5: [3, 1]}
        generator.union(1, 2)

        expected_disjoint1 = {0: [-1, 2], 1: [0, 1], 2: [0, 1], 3: [-1, 3], 4: [5, 2], 5: [3, 1]}
        self.assertEquals(expected_disjoint1, generator.disjoint_set, "issue joining 1 & 2.")
        generator.union(0, 2)
        self.assertEquals(expected_disjoint1, generator.disjoint_set,"0 and 2 already connected. disjoint set should not change.")
        generator.union(2, 3)
        expected_disjoint2 = {0: [3, 2], 1: [0, 1], 2: [0, 1], 3: [-1, 3], 4: [5, 2], 5: [3, 1]}
        self.assertEquals(expected_disjoint2, generator.disjoint_set, "issue joining large branches 2 and 3.")

        # resetting with slightly different starting point:
        generator.disjoint_set = {0: [-1, 3], 1: [0, 2], 2: [1, 1], 3: [-1, 3], 4: [5, 2], 5: [3, 1]}
        generator.union(1, 5)
        expected_disjoint3a = {0: [3, 3], 1: [0, 2], 2: [1, 1], 3: [-1, 4], 4: [5, 2], 5: [3, 1]}
        expected_disjoint3b = {0: [-1, 4], 1: [0, 2], 2: [1, 1], 3: [0, 3], 4: [5, 2], 5: [3, 1]}
        self.assertTrue((expected_disjoint3a == generator.disjoint_set) or (expected_disjoint3b == generator.disjoint_set),
                        "Joining trees with equal rank did not satisfy either option for end condition.")
