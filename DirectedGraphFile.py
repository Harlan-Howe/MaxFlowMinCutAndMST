import cv2
import numpy as np
import random
from TypesAndConstants import *
from typing import List, Tuple, Optional, Dict
import logging


class DirectedGraph:

    VERTEX_RADIUS = 10
    EDGE_OFFSET = 4
    ARROW_SIZE = 5
    TEXT_OFFSET = 10

    def __init__(self, V: Dict[int, Vertex] = None,
                 E: Dict[int, Edge] = None,
                 filename: str = None,
                 keys: Tuple[str] = ()) -> None:
        self.i_am_directed = True
        self.V = V
        if V is None:
            self.V: Dict[int, Vertex] = {}
        self.E = E
        if E is None:
            self.E: Dict[int, Edge] = {}
        self.additional_keys: List[str] = list(keys)
        if filename is not None:
            self.load_from_file(filename)
        self.max_edge_id: int = 0
        self.update_max_edge_id()

        self.edge_tables_dirty = True
        self.u_edge_table: Dict[int, List[int]] = {}
        self.v_edge_table: Dict[int, List[int]] = {}
        self.generate_edge_tables()

    def update_max_edge_id(self) -> None:
        """
        a quick function to figure out what the largest "E" node id was, so that we can be sure to give a unique id to
        all future edges.
        :return: None
        """
        self.max_edge_id = 0
        for e_id in self.E:
            if e_id > self.max_edge_id:
                self.max_edge_id = e_id

    def load_from_file(self, filename: str) -> None:
        """
        Load the graph from a file. The format is as follows:
        Line 0: number of Vertices <tab> number of edges
        Line 1-->numVertices: Vertex id number <tab> Vertex label <tab> Vertex x pos <tab> Vertex y pos
        line numVertices+1 --> numVertices+numEdges: Edge id number <tab> u vertex id <tab> v vertex id <tab>
        attribute1key <tab> attribute1 <tab> attribute2key <tab> attribute2 ... etc.
        :param filename: the name of the file to load
        :return: None (but this graph will now have info in it.)
        """
        with open(filename, 'r') as file:
            count: int = 0
            for line in file:
                items: List[str] = line.split("\t")
                if count == 0:
                    num_V: int = int(items[0])
                    num_E: int = int(items[1])
                elif count <= num_V:
                    self.V[int(items[0])] = {KEY_LABEL: items[1], KEY_LOCATION: (int(items[2]), int(items[3])),
                                             KEY_COLOR: (1.0, 1.0, 1.0)}
                else:
                    self.E[int(items[0])] = {KEY_U: int(items[1]), KEY_V: int(items[2])}
                    for i in range(3, len(items), 2):
                        self.E[int(items[0])][items[i]] = int(items[i+1])
                        if items[i] not in self.additional_keys:
                            self.additional_keys.append(items[i])
                count += 1
        assert count == 1 + num_V + num_E, "Number of lines read is incorrect."

    def generate_edge_tables(self) -> None:
        """
        generate a quick lookup to find the edges associated with exiting a node or entering a node quickly.
        This method runs in O(M). The resulting lookup is O(1) to get the list of items entering or exiting a node
        (though the list may be as long as O(N).)
        :return: None
        """
        if self.edge_tables_dirty:
            self.u_edge_table.clear()
            self.v_edge_table.clear()
            for e_id in self.E:
                e = self.E[e_id]
                u = e[KEY_U]
                if u in self.u_edge_table:
                    self.u_edge_table[u].append(e_id)
                else:
                    self.u_edge_table[u] = [e_id]
                v = e[KEY_V]
                if v in self.v_edge_table:
                    self.v_edge_table[v].append(e_id)
                else:
                    self.v_edge_table[v] = [e_id]
            self.edge_tables_dirty = False

    def get_edges_from_u(self, u_id: int) -> List[Edge]:
        """
        :param u_id: the id number for a given vertex, u
        :return: a list of all edges that exit the vertex u. If there are no edges leaving this vertex,
                returns an empty list.
        """
        if self.edge_tables_dirty:  # if V and/or E have changed since the last time we generated the tables...
            self.generate_edge_tables()

        if u_id in self.u_edge_table:
            edge_list: List[Edge] = []
            for edge_id in self.u_edge_table[u_id]:
                edge_list.append(self.E[edge_id])
            return edge_list
        return []

    def get_edges_to_v(self, v_id: int) -> List[Edge]:
        """
        gets a list of id numbers for all the edges that head into v.
        :param v_id: the id number for a given vertex, v
        :return: a list of all the edges that enter the vertex v. If there are no edges entering
                this vertex, returns an empty list.
        """
        if self.edge_tables_dirty:  # if V and/or E have changed since the last time we generated the tables...
            self.generate_edge_tables()

        if v_id in self.v_edge_table:
            edge_list: List[Edge] = []
            for edge_id in self.v_edge_table[v_id]:
                edge_list.append(self.E[edge_id])
            return edge_list
        return []

    def get_edge_id_from_u_to_v(self, u_id: int, v_id: int) -> int:
        """
        gets the edge_id of an edge from U to V, if any.
        :param u_id:
        :param v_id:
        :return: the id of the edge sought, or None if not found.
        """
        if self.edge_tables_dirty:  # if V and/or E have changed since the last time we generated the tables...
            self.generate_edge_tables()

        if u_id in self.u_edge_table:
            for edge_id in self.u_edge_table[u_id]:
                if self.E[edge_id][KEY_V] == v_id:
                    return edge_id
        return -1

    def get_edge_from_u_to_v(self, u_id: int, v_id: int) -> Optional[Edge]:
        """
        gets the edge from U to V, if any.
        :param u_id:
        :param v_id:
        :return: the edge from u -> v, if any, or None if not found.
        """
        edge_id = self.get_edge_id_from_u_to_v(u_id, v_id)
        if edge_id is None:
            return None
        return self.E[edge_id]

    def get_edge_for_id(self, e_id: int) -> Optional[Edge]:
        """
        finds the edge for the given id, or None if it is not in this graph.
        :param e_id: the id we are searching for
        :return: the corresponding edge, or None.
        """
        if e_id in self.E:
            return self.E[e_id]
        return None
    
    def get_id_for_edge(self, edge: Edge) -> int:
        """
        finds the id number for the given edge, or -1 if edge is not in this graph.
        :param edge: the edge to find. (Searching by memory location, not content.)
        :return: the index of the edge in the dictionary E, or -1 if not found.
        """
        for edge_id in self.E.keys():
            if self.E[edge_id] == edge:
                return edge_id
        return -1

    def get_vertex_for_id(self, v_id: int) -> Optional[Vertex]:
        """
        finds the vertex for the given id, or None if there isn't one with that id in this graph.
        :param v_id: the id we're looking for
        :return: the Vertex, or None.
        """
        if v_id in self.V:
            return self.V[v_id]
        return None

    def get_id_for_vertex_with_label(self, label: str) -> int:
        """
        gets the id number for a vertex with the given label. If no such vertex exists, returns None
        :param label: the label to search for
        :return: the id of the vertex with a matching label, or -1 if one isn't found.
        """
        for v_id in self.V:
            v = self.V[v_id]
            if v[KEY_LABEL] == label:
                return v_id
        return -1

    def add_edge(self, u_id: int, v_id: int, additional_info: Dict[str, int]) -> None:
        """
        Adds an edge to this graph from u to v, with information about the edge in "additional info" dictionary
        :param u_id:
        :param v_id:
        :param additional_info:
        :return:
        """
        self.max_edge_id += 1
        self.E[self.max_edge_id] = {KEY_U: u_id, KEY_V: v_id}
        for key in additional_info:
            self.E[self.max_edge_id][key] = additional_info[key]
            if key not in self.additional_keys:  # track other keys that have been used in this program.
                self.additional_keys.append(key)

        self.edge_tables_dirty = True  # the edge_tables will need an update before we use them.

    def receive_edge(self, edge: Edge) -> None:
        """
        essentially an overload of add edge, this one adds a fully-built edge from another graph to this one
        and sets the edge_tables_dirty flag. This edge will likely have a different id number in this graph
        than it did in the source graph.
        :param edge: the edge to add
        :return: None
        """
        self.max_edge_id += 1
        self.E[self.max_edge_id] = edge
        self.edge_tables_dirty = True  # the edge_tables will need an update before we can use them.

    def draw_self(self, window: np.ndarray = None,
                  origin: Tuple[int, int] = (0, 0),
                  caption: str = None,
                  color: Tuple[float, float, float] = None,
                  cut_color: Tuple[float, float, float] = (1.0, 0.5, 0.85)) -> np.ndarray:
        """
        Draws this graph in the given window (or a new, 800 x 800 one), potentially with a caption
        :param window: the numpy Array in which to draw. Should be a (h x w x 3) np array, with values 0.0-1.0. (
                        Or None, and one will be created for you.)
        :param origin: An offset for this graph, so that you can draw more than one per window
        :param caption: An optional piece of text to draw at (0,15) for this plot.
        :param color: A BGR tuple [0.0-1.0) for the standard color of this edge.
        :param cut_color: A BGR tuple [0.0-1.0) for the color of this edge if is cut.
        :return: the window in which this was drawn
        """
        if window is None:
            window = np.zeros([800, 800, 3], dtype=float)

        # DRAW EDGES
        for key in self.E:
            e: Edge = self.E[key]
            u: Vertex = self.V[e[KEY_U]]
            v: Vertex = self.V[e[KEY_V]]
            dx: int = u[KEY_LOCATION][0] - v[KEY_LOCATION][0]
            dy: int = u[KEY_LOCATION][1] - v[KEY_LOCATION][1]
            d: float = np.sqrt(dx**2 + dy**2)
            # logging.info(f"u={u}\tv={v}\tdx={dx}\tdy={dy}\d={d}")
            if d > 2*self.VERTEX_RADIUS:
                i: Tuple[float, float] = (dx/d, dy/d)
                j: Tuple[float, float] = (-i[1], i[0])
                # logging.info(f"i={i}\tj={j}")
                if color is None:
                    line_color_to_draw: Tuple[float, float, float] = (random.randrange(25, 100)/100,
                                                                      random.randrange(25, 100)/100,
                                                                      random.randrange(25, 100)/100)
                else:
                    if u[KEY_COLOR] == v[KEY_COLOR]:
                        line_color_to_draw = color
                    else:
                        line_color_to_draw = cut_color
                point_u = (int(origin[0]+u[KEY_LOCATION][0]-i[0]*self.VERTEX_RADIUS+j[0]*self.EDGE_OFFSET),
                           int(origin[1]+u[KEY_LOCATION][1]-i[1]*self.VERTEX_RADIUS+j[1]*self.EDGE_OFFSET))

                point_v = (int(origin[0]+v[KEY_LOCATION][0] + i[0] * self.VERTEX_RADIUS + j[0] * self.EDGE_OFFSET),
                           int(origin[1]+v[KEY_LOCATION][1] + i[1] * self.VERTEX_RADIUS + j[1] * self.EDGE_OFFSET))
                cv2.line(window, point_u, point_v, line_color_to_draw, 1)

                # draw arrowheads
                if self.i_am_directed:
                    a1 = (int(point_v[0] + i[0] * self.ARROW_SIZE + j[0] * self.ARROW_SIZE),
                          int(point_v[1] + i[1] * self.ARROW_SIZE + j[1] * self.ARROW_SIZE))
                    a2 = (int(point_v[0] + i[0] * self.ARROW_SIZE - j[0] * self.ARROW_SIZE),
                          int(point_v[1] + i[1] * self.ARROW_SIZE - j[1] * self.ARROW_SIZE))
                    cv2.line(window, point_v, a1, line_color_to_draw, 1)
                    cv2.line(window, point_v, a2, line_color_to_draw, 1)
                    cv2.line(window, a1, a2, line_color_to_draw, 1)

                # draw edge labels
                angle = np.arctan2(dy, -dx) * 180 / np.pi
                tx = int(origin[0] + (v[KEY_LOCATION][0] + u[KEY_LOCATION][0]) / 2 + j[0] * self.TEXT_OFFSET)
                ty = int(origin[1] + (v[KEY_LOCATION][1] + u[KEY_LOCATION][1]) / 2 + j[1] * self.TEXT_OFFSET)

                if len(self.additional_keys) > 0:
                    text_to_draw = ""
                    for additional_key in self.additional_keys:
                        # print(key)
                        text_to_draw = f"{text_to_draw} {e[additional_key]},"
                    text_to_draw = text_to_draw[:-1]

                    self.draw_rotated_text_centered_at(text_to_draw, (tx, ty), angle, window, color=line_color_to_draw)

        # DRAW VERTICES
        for additional_key in self.V:
            v: Vertex = self.V[additional_key]
            cv2.circle(window, (origin[0] + v[KEY_LOCATION][0], origin[1] + v[KEY_LOCATION][1]),
                       self.VERTEX_RADIUS, v[KEY_COLOR], -1)  # Fill
            cv2.circle(window, (origin[0] + v[KEY_LOCATION][0], origin[1] + v[KEY_LOCATION][1]),
                       self.VERTEX_RADIUS, (0.75, 0.75, 0.75))  # Stroke
            cv2.putText(window, v[KEY_LABEL], (origin[0]+v[KEY_LOCATION][0]-5, origin[1]+v[KEY_LOCATION][1]+5),
                        cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 0), 1, cv2.LINE_AA)

        # DRAW CAPTION
            if caption is not None:
                cv2.putText(window, caption, (origin[0], origin[1]+15), cv2.FONT_HERSHEY_PLAIN, 1, (1.0, 1.0, 1.0), 1)

        return window

    @staticmethod
    def draw_rotated_text_centered_at(text: str,
                                      center: Tuple[float, float],
                                      angle: float,
                                      window: np.ndarray,
                                      color: Tuple[float, float, float] = (1.0, 1.0, 1.0)) -> None:
        """
        draws the given text rotated by the given amount, centered on the point given, into the window.
        :param: text - the string to print, expected to be short enough not to cause issues in window borders
        :param: center a tuple (cx, cy) where the text should be centered.
        :param: angle - the angle of rotation
        :param: window - the window into which to draw
        :param: color - the color to draw the text, a tuple of 3 values 0.0-1.0.
        with some help from https://www.pyimagesearch.com/2017/01/02/rotate-images-correctly-with-opencv-and-python/
        and https://stackoverflow.com/questions/40895785/using-opencv-to-overlay-transparent-image-onto-another-image
        """
        M = cv2.getRotationMatrix2D((int(window.shape[0] / 2), int(window.shape[1] / 2)), angle, 1.0)
        canvas = np.zeros(window.shape)
        cv2.putText(canvas, text, (int(window.shape[0] / 2), int(window.shape[1] / 2)), cv2.FONT_HERSHEY_PLAIN, 1,
                    color, 1, cv2.LINE_AA)
        canvas = cv2.warpAffine(canvas, M, (canvas.shape[0], canvas.shape[1]))
        mask = np.sum(canvas, axis=2)
        horizontal_mask = np.sum(mask, axis=0)
        nonzero_range_horizontal = np.nonzero(horizontal_mask)
        vertical_mask = np.sum(mask, axis=1)
        nonzero_range_vertical = np.nonzero(vertical_mask)
        trimmed_canvas = canvas[nonzero_range_vertical[0][0] - 2:nonzero_range_vertical[0][-1] + 2,
                                nonzero_range_horizontal[0][0] - 2:nonzero_range_horizontal[0][-1] + 2, :]
        rows, cols, colors = trimmed_canvas.shape
        start_x = int(center[0]-cols/2)
        start_y = int(center[1]-rows/2)
        if start_x < 0:
            trimmed_canvas = trimmed_canvas[:, -start_x:]
            start_x = 0
        if start_y < 0:
            trimmed_canvas = trimmed_canvas[-start_y:, :]
            start_y = 0
        end_x = int(center[0]+cols / 2)
        end_y = int(center[1]+rows / 2)
        mask = trimmed_canvas > 0

        # logging.info(f"text: '{text}'\tstart_x:{start_x}\tend_x:{end_x}\tstart_y:{start_y}\tend_y:{end_y}")
        # logging.info(f"mask shape:{mask.shape}\twindow shape:{window[start_y:end_y,start_x:end_x].shape}\t"
        # "trimmed_canvas shape:{trimmed_canvas.shape}")

        window[start_y:end_y, start_x:end_x] = (1 - mask) * window[start_y:end_y, start_x:end_x] + trimmed_canvas
