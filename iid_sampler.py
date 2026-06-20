"""Sample instance graphs from a type graph under the known i.i.d. model."""
from __future__ import annotations
import numpy as np


def sample_instance(
    type_adj: list[list[int]],
    m: int | None = None,
    rng: np.random.Generator | None = None,
    p: np.ndarray | None = None,
) -> tuple[list[list[int]], np.ndarray]:
    """Draw m i.i.d. types from distribution p on L = {0,..,|L|-1}.

    Returns (instance_adj, types) where:
      - instance_adj[i] = neighbors of the i-th arriving online node
      - types[i] = the type index of the i-th arriving online node

    `p` is the type distribution. If None, uniform (the paper's default — with
    m = |L| and uniform, integral types holds, E(Z_l) = 1 ∈ Z). In the serving
    instantiation, p is the (non-uniform) traffic distribution over request types.
    """
    if rng is None:
        rng = np.random.default_rng()
    n_types = len(type_adj)
    if m is None:
        m = n_types
    if p is None:
        types = rng.integers(0, n_types, size=m)
    else:
        types = rng.choice(n_types, size=m, p=p)
    instance_adj = [type_adj[t] for t in types]
    return instance_adj, types
