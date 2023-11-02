import copy
import random

import numpy as np
import cv2
import time
from typing import List, Optional
from TypesAndConstants import *
from DirectedGraphFile import DirectedGraph


class MaxFlowMinCutSolver:
    def find_max_flow(self, capacity: DirectedGraph, capacity_key: str = KEY_CAPACITY) -> Tuple[DirectedGraph,
                                                                                              DirectedGraph]:
        """
        finds the maximum flow from "S" to "T" for the given graph -
        :param capacity: The directed graph in which to perform the search - it should contain a vertex labeled "S" and
                         one labeled "T".
        :param capacity_key: the key used to ask each edge for the capacity of this connection
        :return: flow - a parallel graph to capacity, with the same vertices, and edges labeled by KEY_FLOW with the
                            amount of flow through that edge
                 residual - a similar graph to capacity, with the same vertices, and edges laid out parallel and
                             anti-parallel to the original. The residual is what is used to calculate the max flow,
                             and it is included in the output to be used for finding the min cut.
        """
        # --> We'll start by initializing KEY_FLOW.....
        flow: DirectedGraph = DirectedGraph(capacity.V, {})  # make a flow be a copy of the capacity's vertices,
        # with no edges.
        # add edges with KEY_FLOW = 0 that otherwise match the edges in capacity.
        for e_id in capacity.E:
            flow.add_edge(u_id=capacity.E[e_id][KEY_U],
                          v_id=capacity.E[e_id][KEY_V],
                          additional_info={KEY_FLOW: 0})


        while True:
            # --> Generate the residual graph.
            residual: DirectedGraph = self.generate_residual(capacity, flow)

            # --> Find a path from S to T
            path: List[int] = self.find_nonzero_path_in_graph(residual)
            # path should be in the format of a list of Vertex ids....

            # --> GRAPHICS: build a graph with just the vertices and only those edges in the path
            path_display: DirectedGraph = self.generate_path_display(capacity, path)
            # show what the capacity, flow, residual and path look like...
            self.display_graphs(capacity, flow, residual,
                                path_display)  # NOTE: this takes time to generate, so you will likely want to comment
            #                                          this out for a complicated graph.
            if path is None:
                break

            # TODO #3 - write the remainder of this....

            # find the minimum value along the path in the residual graph.

            # adjust the flow graph, based on this minimum value you just found.

        return flow, residual

    @staticmethod
    def generate_residual(capacity: DirectedGraph, flow: DirectedGraph) -> DirectedGraph:
        """
        generates the "residual" graph - a consequence of the capacity and flow graphs.
        :param capacity:
        :param flow:
        :return:
        """
        residual: DirectedGraph = DirectedGraph(capacity.V, {})  # create a new graph with the same vertices, but no
        #                                                          edges.
        for e_id in capacity.E:  # loop through all the edges in capacity graph...

            # try to find the corresponding edge in flow graph...
            capacity_edge: Edge = capacity.E[e_id]
            # find the vertices for this edge.
            u: int = capacity_edge[KEY_U]
            v: int = capacity_edge[KEY_V]

            # find the corresponding edge in flow.
            flow_edge: Edge = flow.get_edge_from_u_to_v(u, v)
            # just checking.... this shouldn't ever happen.
            if flow_edge is None:
                raise AssertionError(f"edge {u}-->{v} not found in flow graph")

            capacity_amount: int = capacity_edge[KEY_CAPACITY]
            flow_amount: int = flow_edge[KEY_FLOW]

            # build the "capacity" edge or edges in residual that go with this particular pair of capacity and flow
            # edges
            # TODO #1: You write this.
            #     You'll want to use "residual.add_edge(u_id=<?>, v_id=<?>, additional_info = {KEY_CAPACITY: <???>})"
            #     (Obviously, replace <?> with something useful.)

        return residual

    @staticmethod
    def generate_path_display(capacity: DirectedGraph, path: List[int]) -> DirectedGraph:
        """
        Creates another graph with the vertices from the capacity graph and just the edges described by path. For use in
        displaying a selected path, graphically.
        :param capacity:
        :param path: a list of vertex ids.
        :return: a new graph, as described.
        """
        path_display: DirectedGraph = DirectedGraph(capacity.V, {})
        if path is not None:
            for i in range(len(path) - 1):
                path_display.add_edge(path[i], path[i + 1], {})

        return path_display

    @staticmethod
    def find_nonzero_path_in_graph(graph: DirectedGraph,
                                   start_label: str = "S",
                                   end_label: str = "T",
                                   key: str = KEY_CAPACITY) -> Optional[List[int]]:
        """
        Uses a depth-first search (DFS) to find a path from the start label to the end label, where all edges have
        a value for "key" that is greater than zero.

        :param graph:  the DirectedGraph in which to search
        :param start_label: the label of the node to start at
        :param end_label: the label of the node to end at
        :param key: what parameter of the edges are we checking for non-zero status?
        :return: a list of id's for the vertices in the graph that compose a path from start_id to end_id (inclusive),
                 in order... or None, if no such path exists.
        """
        s_id: int = graph.get_id_for_vertex_with_label(start_label)
        t_id: int = graph.get_id_for_vertex_with_label(end_label)
        # TODO #2: find the path through the residual graph. I'd suggest something simple (BFS or DFS).
        #  Not essential, but more interesting: When performing the search, so you don't get the same paths every run,
        #  perhaps use a random selection/ordering when options are equivalent.... you can use
        #  "random.shuffle(name_of_list)"


    @staticmethod
    def display_graphs(capacity: DirectedGraph,
                       flow: DirectedGraph,
                       residual: DirectedGraph,
                       path_display: DirectedGraph = None) -> np.ndarray:
        """
        Draws the graphs in one window and waits for the user to press a key
        :param capacity:
        :param flow:
        :param residual:
        :param path_display:
        :return: the numpy array (shape: h x w x 3, dtype = float) that was drawn.
        """
        start_time: float = time.time()
        window: np.ndarray = capacity.draw_self(origin=(0, 0), caption=KEY_CAPACITY, color=(0.75, 1.0, 0.25))
        window = flow.draw_self(origin=(400, 0), caption=KEY_FLOW, window=window, color=(0.75, 1.0, 0.25))
        window = residual.draw_self(origin=(0, 400), caption="Residual", window=window, color=(0.75, 1.0, 0.25))
        if path_display is not None:
            window = path_display.draw_self(origin=(400, 400), caption="Path", window=window, color=(0.75, 1.0, 0.25))
        cv2.imshow("Graphs", window)
        print(f"Time to Display: {time.time()-start_time}")
        print("With focus in the graphics window, press a key to continue.")
        cv2.waitKey()

        return window

    def find_reachable_vertices(self,
                                residual: DirectedGraph,
                                start_node_label: str = "S") -> List[int]:
        """
        gets a list of ids for all the vertices that can be reached from the start node.
        :param residual:
        :param start_node_label:  the letter we wish to use as the starting point, most likely "S".
        :return: list of vertex id's that can be reached by a walk from the start node.
        """
        s_id: int = residual.get_id_for_vertex_with_label(start_node_label)
        result: List[int] = [s_id]
        frontier: List[int] = [s_id]
        # TODO #4: use a search algorithm to find all the vertices that are reachable from the elements in the
        #  frontier. (This is the part at the end that makes the Cut... not the pathfinding to build the flow and
        #  residual.)

        return result
