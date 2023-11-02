import cv2
from MSTFile import MST

from UndirectedGraphFile import UndirectedGraph


def main():
    graph = UndirectedGraph(filename="UndirectedGraph1.txt")
    window = graph.draw_self(caption="Original")
    mst = MST(graph)
    mst.solve(method=MST.METHOD_KRUSKAL)

    #  Change the caption to "Prim" if desired....
    window = mst.draw_self(origin=(0, 400), window=window, caption="Kruskal", color=(1.0, 0.75, 0.25))

    cv2.imshow("MST", window)
    cv2.waitKey()


# if this is the file you are telling to run, then call main().
if __name__ == '__main__':
    main()
