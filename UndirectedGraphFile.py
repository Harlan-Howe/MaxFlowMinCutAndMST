from DirectedGraphFile import DirectedGraph
from typing import Dict, List
from TypesAndConstants import *


class UndirectedGraph(DirectedGraph):

    def __init__(self,
                 V: Dict[int, Vertex] = None,
                 E: Dict[int, Edge] = None,
                 filename: str = None,
                 keys: Tuple[str] = ()) -> None:
        super().__init__(V=V, E=E, filename=filename, keys=keys)
        self.i_am_directed: bool = False
        self.EDGE_OFFSET: int = 0

        self.edge_tables_dirty = True
        self.edge_table: Dict[int, List[int]] = {}

    def generate_edge_tables(self) -> None:
        if self.edge_tables_dirty:
            self.edge_table.clear()
            for e_id in self.E:
                e: Edge = self.E[e_id]
                u: int = e[KEY_U]
                if u in self.edge_table:
                    self.edge_table[u].append(e_id)
                else:
                    self.edge_table[u] = [e_id]
                v = e[KEY_V]
                if v in self.edge_table:
                    self.edge_table[v].append(e_id)
                else:
                    self.edge_table[v] = [e_id]
            self.edge_tables_dirty = False

    def get_edges_touching(self, u_vertex_id: int) -> List[Edge]:
        """
        :param u_vertex_id: the id number for a given vertex, u
        :return: a list of edge id numbers for all edges that touch the vertex u. If there are no edges touching this
                vertex, returns an empty list.
        """
        if self.edge_tables_dirty:
            self.generate_edge_tables()
        if u_vertex_id in self.edge_table:
            edge_list: List[Edge] = []
            for edge_id in self.edge_table[u_vertex_id]:
                edge_list.append(self.E[edge_id])
            return edge_list
        return []

    def get_edges_from_u(self, u_id: int) -> List[Edge]:
        """ overrides directed version """
        return self.get_edges_touching(u_id)

    def get_edges_to_v(self, v_id: int) -> List[Edge]:
        """ overrides directed version """
        return self.get_edges_touching(v_id)
