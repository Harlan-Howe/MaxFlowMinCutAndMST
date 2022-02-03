import cv2
import numpy as np
import random
from TypesAndConstants import *
from typing import List, Tuple, Optional, Set, TypedDict, Dict


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
        self.generate_edge_tables()

    def update_max_edge_id(self) -> None:
        """
        a quick function to figure out what the largest "E" node id was, so that we can be sure to give a unique id to all
        future edges.
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
        line numVertices+1 --> numVertices+numEdges: Edge id number <tab> u vertex id <tab> v vertex id <tab> attribute1key <tab> attribute1 <tab> attribute2key <tab> attribute2 ... etc.
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
                    self.V[int(items[0])] = {KEY_LABEL: items[1], KEY_LOCATION: (int(items[2]), int(items[3])), KEY_COLOR: (1.0, 1.0, 1.0)}
                else:
                    self.E[int(items[0])] = {KEY_U: int(items[1]), KEY_V: int(items[2])}
                    for i in range(3,len(items),2):
                        self.E[int(items[0])][items[i]] = int(items[i+1])
                        if items[i] not in self.additional_keys:
                            self.additional_keys.append(items[i])
                count += 1

    def generate_edge_tables(self) -> None:
        """
        generate a quick lookup to find_root the edges associated with exiting a node or entering a node quickly.
        This method runs in O(M). The resulting lookup is O(1) to get the list of items entering or exiting a node (though
        the list may be as long as O(N).
        :return: None
        """
        if self.edge_tables_dirty:
            self.u_edge_table: Dict[int, List[Edge]] = {}
            self.v_edge_table: Dict[int, List[Edge]] = {}
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
        :param u_index: the id number for a given vertex, u
        :return: a list of all edges that exit the vertex u. If there are no edges leaving this vertex,
                returns an empty list.
        """
        if self.edge_tables_dirty:
            self.generate_edge_tables()
        if u_id in self.u_edge_table:
            return self.u_edge_table[u_id]
        return []

    def get_edges_to_v(self, v_id: int) -> List[Edge]:
        """
        gets a list of id numbers for all the edges that head into v.
        :param v_id: the id number for a given vertex, v
        :return: a list of all the edges that enter the vertex v. If there are no edges entering
                this vertex, returns an empty list.
        """
        if self.edge_tables_dirty:
            self.generate_edge_tables()
        if v_id in self.v_edge_table:
            return self.v_edge_table[v_id]
        return []

    def get_edge_id_from_u_to_v(self, u_id: int, v_id: int) -> int:
        """
        gets the edge_id of an edge from U to V, if any.
        :param u_id:
        :param v_id:
        :return: the id of the edge sought, or None if not found.
        """
        if self.edge_tables_dirty:
            self.generate_edge_tables()
        if u_id in self.u_edge_table:
            for edge_id in self.u_edge_table[u_id]:
                if self.E[edge_id][KEY_V] == v_id:
                    return edge_id
        return None
    def get_edge_from_u_to_v(self, u_id: int, v_id: int) --> Edge:
        """
        gets the edge from U to V, if any.
        :param u_id:
        :param v_id:
        :return: the edge from u -> v, if any, or None if not found.
        """
        edge_id = self.get_edge_id_from_u_to_v(u_id,v_id) 
        if edge_id is None:
            return None
        return self.E[edge_id]
    
    def get_vertex_for_id(self, v_id: int) -> Vertex:
        return self.V[v_id]

    def get_edge_for_id(self, e_id: int) -> Edge:
        return self.E[e_id]

    def get_ID_for_vertex_with_label(self, label: str) -> int:
        """
        gets the id number for a vertex with the given label. If no such vertex exists, returns None
        :param label: the label to search for
        :return: the id of the vertex with a matching label, or None if one isn't found.
        """
        for v_id in self.V:
            v = self.V[v_id]
            if v[KEY_LABEL] == label:
                return v_id
        return None

    def add_edge(self, u_id: int, v_id: int , additional_info: Dict[str,int]) -> None:
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
            if key not in self.additional_keys:
                self.additional_keys.append(key)
        self.edge_tables_dirty = True

    def draw_self(self, window: np.ndarray = None,
                  origin: List[int] = [0, 0],
                  caption: str =None,
                  color: Tuple[float, float, float] = None,
                  cut_color: Tuple[float, float, float] = (0.8,0,0.5)) -> np.ndarray:
        """
        Draws this graph in the given window (or a new, 800 x 800 one), potentially with a caption
        :param window: the numpy Array in which to draw. Should be a (h x w x 3) np array, with values 0.0-1.0. (
                        Or None, and one will be created for you.)
        :param origin: An offset for this graph, so that you can draw more than one per window
        :param caption: An optional piece of text to draw at (0,15) for this plot.
        :return: the window in which this was drawn
        """
        if window is None:
            window = np.zeros([800,800,3],dtype=float)

        # DRAW EDGES
        for key in self.E:
            e: Edge = self.E[key]
            u: Vertex = self.V[e[KEY_U]]
            v: Vertex = self.V[e[KEY_V]]
            dx: int = u[KEY_LOCATION][0] - v[KEY_LOCATION][0]
            dy: int = u[KEY_LOCATION][1] - v[KEY_LOCATION][1]
            d: float = np.sqrt(dx**2 + dy**2)
            # print(f"u={u}\tv={v}\tdx={dx}\tdy={dy}\d={d}")
            if d > 2*self.VERTEX_RADIUS:
                i: Tuple[float, float] = (dx/d, dy/d)
                j: Tuple[float, float] = (-i[1], i[0])
                # print(f"i={i}\tj={j}")
                if color is None:
                    c: Tuple[float, float, float] = (random.randrange(25,100)/100, random.randrange(25,100)/100, random.randrange(25,100)/100)
                else:
                    if u[KEY_COLOR] == v[KEY_COLOR]:
                        c = color
                    else:
                        c = cut_color
                pu = (int(origin[0]+u[KEY_LOCATION][0]-i[0]*self.VERTEX_RADIUS+j[0]*self.EDGE_OFFSET),
                      int(origin[1]+u[KEY_LOCATION][1]-i[1]*self.VERTEX_RADIUS+j[1]*self.EDGE_OFFSET))
                pv = (int(origin[0]+v[KEY_LOCATION][0] + i[0] * self.VERTEX_RADIUS + j[0] * self.EDGE_OFFSET),
                      int(origin[1]+v[KEY_LOCATION][1] + i[1] * self.VERTEX_RADIUS + j[1] * self.EDGE_OFFSET))
                cv2.line(window,pu,pv,c,1)
                # draw arrowheads
                if self.i_am_directed:
                    a1 = (int(pv[0] + i[0] * self.ARROW_SIZE + j[0] * self.ARROW_SIZE),
                          int(pv[1] + i[1] * self.ARROW_SIZE + j[1] * self.ARROW_SIZE))
                    a2 = (int(pv[0] + i[0] * self.ARROW_SIZE - j[0] * self.ARROW_SIZE),
                          int(pv[1] + i[1] * self.ARROW_SIZE - j[1] * self.ARROW_SIZE))
                    cv2.line(window,pv,a1,c,1)
                    cv2.line(window,pv,a2,c,1)
                    cv2.line(window,a1,a2,c,1)
                #draw edge labels
                angle = np.arctan2(dy,-dx)*180/np.pi
                tx = int(origin[0]+(v[KEY_LOCATION][0]+u[KEY_LOCATION][0])/2+j[0]*self.TEXT_OFFSET)
                ty = int(origin[1]+(v[KEY_LOCATION][1]+u[KEY_LOCATION][1])/2+j[1]*self.TEXT_OFFSET)

                if len(self.additional_keys)>0:
                    text_to_draw = ""
                    for key in self.additional_keys:
                        # print(key)
                        text_to_draw=f"{text_to_draw} {e[key]},"
                    text_to_draw = text_to_draw[:-1]
                    self.draw_rotated_text_centered_at(text_to_draw, (tx, ty), angle, window, color=c)

        # DRAW VERTICES
        for key in self.V:
            v: Vertex = self.V[key]
            cv2.circle(window, (origin[0]+v[KEY_LOCATION][0],origin[1]+v[KEY_LOCATION][1]), self.VERTEX_RADIUS, v[KEY_COLOR],-1)
            cv2.circle(window,(origin[0]+v[KEY_LOCATION][0],origin[1]+v[KEY_LOCATION][1]),self.VERTEX_RADIUS,(0.75,0.75,0.75))
            cv2.putText(window,v[KEY_LABEL],(origin[0]+v[KEY_LOCATION][0]-5,origin[1]+v[KEY_LOCATION][1]+5),cv2.FONT_HERSHEY_PLAIN,1,(0,0,0),1,cv2.LINE_AA)

        # DRAW CAPTION
            if caption is not None:
                cv2.putText(window,caption,(origin[0],origin[1]+15),cv2.FONT_HERSHEY_PLAIN,1,(1.0,1.0,1.0),1)

        return window

    def draw_rotated_text_centered_at(self, text: str,
                                      center: Tuple[float, float],
                                      angle: float,
                                      window: np.ndarray,
                                      color: Tuple[float, float, float] = (1.0, 1.0, 1.0))-> None:
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
        M = cv2.getRotationMatrix2D((int(window.shape[0]/2),int(window.shape[1]/2)), angle, 1.0)
        canvas = np.zeros(window.shape)
        cv2.putText(canvas,text,(int(window.shape[0]/2),int(window.shape[1]/2)),cv2.FONT_HERSHEY_PLAIN,1,color,1,cv2.LINE_AA)
        canvas = cv2.warpAffine(canvas,M,(canvas.shape[0],canvas.shape[1]))
        mask = np.sum(canvas,axis=2)
        horizontal_mask = np.sum(mask,axis=0)
        nonzero_range_horz = np.nonzero(horizontal_mask)
        vertical_mask=np.sum(mask,axis=1)
        nonzero_range_vert = np.nonzero(vertical_mask)
        trimmed_canvas = canvas[nonzero_range_vert[0][0]-2:nonzero_range_vert[0][-1]+2,nonzero_range_horz[0][0]-2:nonzero_range_horz[0][-1]+2,:]
        rows,cols,colors = trimmed_canvas.shape
        startx =int( center[0]-cols/2)
        starty =int( center[1]-rows/2)
        if startx<0:
            trimmed_canvas = trimmed_canvas[:,-startx:]
            startx=0
        if starty<0:
            trimmed_canvas = trimmed_canvas[-starty:,:]
            starty=0
        endx =  int(center[0]+cols/2)
        endy = int(center[1]+rows/2)
        mask = trimmed_canvas > 0

        # print(f"text: '{text}'\tstartx:{startx}\tendx:{endx}\tstarty:{starty}\tendy:{endy}")
        # print(f"mask shape:{mask.shape}\twindow shape:{window[starty:endy,startx:endx].shape}\ttrimmed_canvas shape:{trimmed_canvas.shape}")

        window[starty:endy,startx:endx] =(1-mask)*window[starty:endy,startx:endx] + trimmed_canvas
