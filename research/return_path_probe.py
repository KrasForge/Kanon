"""Connectivity counterexamples, not an electromagnetic return-current solver."""

import json
from collections import deque


def shortest(copper, start, end):
    queue = deque([(start, 0)])
    seen = {start}
    while queue:
        (x, y), distance = queue.popleft()
        if (x, y) == end:
            return distance
        for neighbor in [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]:
            if neighbor in copper and neighbor not in seen:
                seen.add(neighbor)
                queue.append((neighbor, distance + 1))
    return None


def experiment():
    plane = {(x, y) for x in range(21) for y in range(11)}
    scenarios = {
        "continuous": plane,
        "slot-with-detour": plane - {(10, y) for y in range(9)},
        "disconnected-islands": plane - {(10, y) for y in range(11)},
    }
    return [
        {
            "case": name,
            "ground_at_endpoints": (2, 5) in copper and (18, 5) in copper,
            "minimum_grid_path_steps": shortest(copper, (2, 5), (18, 5)),
            "straight_path_steps": 16,
        }
        for name, copper in scenarios.items()
    ]


if __name__ == "__main__":
    print(json.dumps(experiment(), indent=2))
