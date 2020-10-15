from typing import TypedDict, Tuple
KEY_LABEL = "label"
KEY_LOCATION = "location"
KEY_COLOR = "color"
KEY_U = "u"
KEY_V = "v"

class Vertex(TypedDict, total=False):
    KEY_LABEL: str
    KEY_LOCATION: Tuple[int, int]
    KEY_COLOR: Tuple[float, float, float]


class Edge(TypedDict, total=False):  # total = False means that you can still have an edge if these aren't filled in.
    u: int
    v: int
    capacity: int
    # add more, as needed.

