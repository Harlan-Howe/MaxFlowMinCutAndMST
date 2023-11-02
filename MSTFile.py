import random

import cv2
import heapq

from UndirectedGraphFile import UndirectedGraph
from TypesAndConstants import *
from typing import List, Set, Dict, Optional
import numpy as np


class MST:
    METHOD_KRUSKAL = 0
    METHOD_PRIMS = 1

    def __init__(self,
                 G: UndirectedGraph):
        self.source_G: UndirectedGraph = G
        self.MST_result: Optional[UndirectedGraph] = None  # "Optional" means "could be None or what's in the brackets."
        self.disjoint_set: Dict[int, List[int, int]] = {}  # {this_id: [parent_id, this_rank]}  -1 means No parent.

    def solve(self, method: int) -> None:
        if method == self.METHOD_PRIMS:
            self.find_MST_by_Prims()
        if method == self.METHOD_KRUSKAL:
            self.find_MST_by_Kruskals()

    def find_MST_by_Prims(self) -> None:
        """
            uses Prim's algorithm to generate self.MST_result, an undirected graph that consists of the same vertices as
            self.source_G, but only those edges needed for a minimal spanning tree.
            :return: None
        """
        # initialize the result, copying the vertices, but leaving the edges dictionary empty. (This edges dictionary is
        #        "X" in the video.)
        self.MST_result = UndirectedGraph(V=self.source_G.V, E={})
        num_Nodes: int = len(self.source_G.V)

        # initialize the set of vertices, S, with a random choice.
        u_id: int = random.choice(list(self.source_G.V))
        S: Set = set()
        S.add(u_id)

        # initialize a heapqueue (i.e., a priority queue). You can use your own class for this, if you'd rather. This is
        #  similar to the green dotted lines in the video, but there might also be internal edges you'll need to ignore.
        hq: List[List[int, int]] = []  # [weight, edge_id]
        for start_neighbor_edge in self.source_G.get_edges_touching(u_id):
            start_neighbor_edge_id = self.source_G.get_id_for_edge(start_neighbor_edge)
            heapq.heappush(hq, [start_neighbor_edge["weight"], start_neighbor_edge_id])  # note these are the edges,
            #                                                                              prioritized by lowest weight.

        while len(S) < num_Nodes:
            # TODO P1: you write this loop! I've got a start and an outline below.
            w, edge_id = heapq.heappop(hq)
            edge = self.source_G.E[edge_id]
            u_id: int = edge[KEY_U]
            v_id: int = edge[KEY_V]

            if u_id not in S:  # then swap u,v so that u is the one in S
                pass

            #     if this is an internal link in S, move onto the next edge in the queue.

            #     otherwise add this edge to our MST, and update S and the queue. (Hint see line 48-49 for some of
            #     this.)

            self.update_window(caption="Prims")  # optional (and time-expensive for more involved graphs) so you can
            #                                      see the algorithm in action.

    def find_MST_by_Kruskals(self) -> None:
        """
                uses Kruskal's algorithm to generate self.MST_result, an undirected graph that consists of the same
                vertices as self.source_G, but only those edges needed for a minimal spanning tree.
                :return: None
        """
        # initialize the result, copying the vertices, but leaving the edges dictionary empty. (This edges dictionary is
        #        "X" in the video.)
        self.MST_result: UndirectedGraph = UndirectedGraph(V=self.source_G.V, E={})

        # initialize the disjoint set.
        self.disjoint_set.clear()
        # TODO K3: add all vertices to the disjointed set, via the add_to_disjoint_set() method.


        # initialize a heapqueue (i.e., a priority queue). You can use your own class for this, if you'd rather.
        hq: List[Tuple[int, int]] = []
        # TODO K4: add all edges to this queue, weighed by their "weight." (See similar code in Prim's, above.)


        while len(self.MST_result.E) < len(self.MST_result.V)-1:
            # TODO K5: you write this loop! I've got a start and an outline below.

            w, edge_id = heapq.heappop(hq)
            u_id: int = self.source_G.E[edge_id][KEY_U]
            v_id: int = self.source_G.E[edge_id][KEY_V]

            #    find the roots of u and v in the disjointed set.

            #    if u and v are connected, then skip this edge and go on to the next one.

            #    otherwise, add this edge to the MST, and update the disjoint set. Hint: union().

            self.update_window(caption="Kruskal")  # optional (and time-expensive for complicated projects) so you can
            #                                        see the algorithm in action.

    def add_to_disjoint_set(self, x: int) -> None:
        """
        adds this vertex id to the disjoint set, with its parent set to -1, and its rank set to 1.
        :param x: an id for a vertex.
        :return: none
        """
        self.disjoint_set[x] = [-1, 1]

    def find_root(self, vertex_id: int) -> int:
        """
        finds the id of the vertex at the root of the disjointed set for vertex id x.
        :param vertex_id: the id of a vertex in the set
        :return: the id of the vertex at the root of the tree containing x. This might be x, or another id.
        """
        # TODO K1: you write this method!
        print ("Method find_root() has not been written yet.")


    def union(self, x_id: id, y_id: id) -> None:
        """
        combine the disjoint set trees containing vertex ids x and y into one disjoint set tree. If they are already in
        the same tree, then there should be no change.
        :param x_id: the id of a vertex
        :param y_id: the id of another vertex.
        :return: None
        """
        # TODO K2: you write this method!
        # Note: you are joining the _roots_ of the disjoint tree for these vertices, not the vertices, themselves
        # (unless they _are_ the roots, of course).
        print("Method union() has not been written yet.")

    def draw_self(self,
                  window: np.ndarray = None,
                  origin: Tuple[int, int] = (0, 0),
                  caption: str = None,
                  color: Tuple[float, float, float] = None) -> np.ndarray:
        return self.MST_result.draw_self(window=window, origin=origin, caption=caption, color=color)

    def update_window(self, caption: str):
        window: np.ndarray = self.source_G.draw_self(caption="Original")
        window = self.draw_self(caption=caption, window=window, origin=(400, 0), color=(1.0, 0.75, 0.25))
        print("With drawing window holding focus, press any button to proceed.")
        cv2.imshow("MST", window)
        cv2.waitKey()
