
from typing import List
from TypesAndConstants import *
from DirectedGraphFile import DirectedGraph
from MaxFlowMinCutSolverFile import MaxFlowMinCutSolver


def main():
    capacity: DirectedGraph = DirectedGraph(filename="DirectedGraph1.txt")
    solver: MaxFlowMinCutSolver = MaxFlowMinCutSolver()
    flow, residual = solver.find_max_flow(capacity)

    S: List[int] = solver.find_reachable_vertices(residual)
    for v_id in capacity.V:
        if v_id in S:
            capacity.V[v_id][KEY_COLOR] = (0.25,0.75,1.0)
        else:
            capacity.V[v_id][KEY_COLOR] = (1.0,0.75,0.25)

    print(f"Nodes reachable from S: {S}")
    solver.display_graphs(capacity, flow, residual)


# if this is the file you are telling to run, then call main().
if __name__ == '__main__':
    main()
