"""Resource precedence graph for bounded repair of an unexecuted plan."""

from collections import defaultdict, deque


def dependency_graph(sorties):
    groups = defaultdict(list)
    for r in sorties:
        groups["drone", r["drone_id"]].append(r)
        groups["battery", r["battery_id"]].append(r)
    successors = {r["sortie_id"]: set() for r in sorties}
    edges = []
    for (kind, resource), routes in groups.items():
        routes.sort(key=lambda r: (r["prepare_start_s"], r["sortie_id"]))
        for a, b in zip(routes, routes[1:]):
            successors[a["sortie_id"]].add(b["sortie_id"])
            edges.append(
                {
                    "from_sortie_id": a["sortie_id"],
                    "to_sortie_id": b["sortie_id"],
                    "resource_kind": kind,
                    "resource_id": resource,
                }
            )
    return successors, edges


def affected_closure(sorties, initial):
    successors, edges = dependency_graph(sorties)
    affected = set(initial)
    queue = deque(sorted(initial))
    while queue:
        for child in sorted(successors[queue.popleft()]):
            if child not in affected:
                affected.add(child)
                queue.append(child)
    return affected, edges
