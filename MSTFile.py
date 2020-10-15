import random

import cv2
import heapq

from UndirectedGraphFile import UndirectedGraph
from TypesAndConstants import *
from typing import List, Set, Dict
import numpy as np

class MST:
    METHOD_KRUSKAL = 0
    METHOD_PRIMS = 1

    def __init__(self,
                 G: UndirectedGraph,
                 method: int = METHOD_PRIMS):
        self.source_G: UndirectedGraph = G
        if method == self.METHOD_PRIMS:
            self.find_MST_by_Prims()
        if method == self.METHOD_KRUSKAL:
            self.find_MST_by_Kruskals()


    def find_MST_by_Prims(self) -> None:
        """
            uses Prim's algorithm to generate self.MST_result, an undirected graph that consists of the same vertices as
            self.source_G, but only those edges needed for a minimal spanning treee.
            :return: None
        """
        #initialize the result, copying the vertices, but leaving the edges dictionary empty. (This edges dictionary is
        #        "X" in the video.)
        self.MST_result = UndirectedGraph(V=self.source_G.V, E={})
        num_Nodes:int  = len(self.source_G.V)

        # initialize the set of vertices, S, with a random choice.
        u_id: int = random.choice(list(self.source_G.V))
        S: Set = set()
        S.add(u_id)

        # initialize a heapqueue (i.e., a priority queue). You can use your own class for this, if you'd rather. This is
        #   similar to the green dotted lines in the video, but there might also be internal edges you'll need to ignore.
        hq: List[Edge] = []
        for e_id in self.source_G.get_edges_touching(u_id):
            heapq.heappush(hq, [self.source_G.E[e_id]["weight"], e_id]) #note these are the edges, prioritized by lowest
                                                                        #     weight.

        while len(S) < num_Nodes:
            # TODO: you write this loop! I've got a start and an outline below.
            w,e_id = heapq.heappop(hq)
            u_id: int = self.source_G.E[e_id][UndirectedGraph.KEY_U]
            v_id: int = self.source_G.E[e_id][UndirectedGraph.KEY_V]

            if u_id not in S: #then swap u,v so that u is the one in S
                temp:int  = u_id
                u_id = v_id
                v_id = temp

            #     if this is an internal link in S, move onto the next edge in the queue.

            #     otherwise add this edge to our MST, and update S and the queue.



            self.update_window(caption="Prims") #optional (and time consuming) so you can see the algorithm in action.

    def find_MST_by_Kruskals(self) -> None:
        """
                uses Kruskal's algorithm to generate self.MST_result, an undirected graph that consists of the same vertices as
                self.source_G, but only those edges needed for a minimal spanning treee.
                :return: None
        """
        # initialize the result, copying the vertices, but leaving the edges dictionary empty. (This edges dictionary is
        #        "X" in the video.)
        self.MST_result: UndirectedGraph = UndirectedGraph(V=self.source_G.V, E={})

        # initialize the disjoint set.
        self.parents: Dict[int, int] = {}
        self.ranks: Dict[int, int] = {}
        # TODO: add all vertices to the disjointed set, via the add_to_disjoint_set() method.


        # initialize a heapqueue (i.e., a priority queue). You can use your own class for this, if you'd rather.
        hq: List[Edge] = []
        # TODO: add all edges to this queue, weighed by their "weight." (See similar code in Prim's, above.)


        while len(self.MST_result.E) < len(self.MST_result.V)-1:
            #TODO: you write this loop! I've got a start and an outline below.

            w,e_id = heapq.heappop(hq)
            u: Vertex = self.source_G.E[e_id][UndirectedGraph.KEY_U]
            v: Vertex = self.source_G.E[e_id][UndirectedGraph.KEY_V]

            #    find the roots of u and v in the disjointed set.

            #    if u and v are connected, then skip this edge and go on to the next one.

            #    otherwise, add this edge to the MST, and update the disjoint set. Hint: union().

            self.update_window(caption="Kruskal")#optional (and time consuming) so you can see the algorithm in action.

    def add_to_disjoint_set(self, x: int) -> None:
        """
        adds this vertex id to the disjoint set, with its parent set to None, and its rank set to 1.
        :param x: an id for a vertex.
        :return: none
        """
        self.parents[x] = None
        self.ranks[x] = 1

    def find_root(self, x: int) -> int:
        """
        finds the id of the vertex at the root of the disjointed set for vertex id x.
        :param x: the id of a vertex in the set
        :return: the id of the vertex at the root of the tree containing x. This might be x, or another id.
        """
       #TODO: you write this method!


    def union(self,x: int, y:int) -> None:
        """
        combine the disjoint set trees containing vertex ids x and y into one disjoint set tree. If they are already in
        the same tree, then there should be no change.
        :param x: the id of a vertex
        :param y: the id of another vertex.
        :return: None
        """
        #TODO: you write this method!


    def draw_self(self,
                  window: np.ndarray = None,
                  origin: List[int] = [0, 0],
                  caption: str = None,
                  color: Tuple[float, float, float] = None) -> np.ndarray:
        return self.MST_result.draw_self(window=window,origin=origin, caption=caption, color=color)

    def update_window(self, caption: str):
        window: np.ndarray = self.source_G.draw_self(caption="Original")
        window = self.draw_self(caption=caption, window=window, origin=(400, 0), color=(1.0, 0.75, 0.25))
        print ("With drawing window holding focus, press any button to proceed.")
        cv2.imshow("MST", window)
        cv2.waitKey()