from typing import TypedDict, Tuple, Final
KEY_LABEL: Final[str] = "label"
KEY_LOCATION: Final[str] = "location"
KEY_COLOR: Final[str] = "color"
KEY_U: Final[str] = "u"
KEY_V: Final[str] = "v"
KEY_CAPACITY: Final[str] = "capacity"
KEY_WEIGHT: Final[str] = "weight"
KEY_FLOW: Final[str] = "flow"

class Vertex(TypedDict, total=False):
    KEY_LABEL: str
    KEY_LOCATION: Tuple[int, int]
    KEY_COLOR: Tuple[float, float, float]


class Edge(TypedDict, total=False):  # total = False means that you can still have an edge if these aren't filled in.
    u: int
    v: int
    capacity: int
    weight: int
    flow: int

    # add more, as needed.
