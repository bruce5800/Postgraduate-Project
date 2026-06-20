"""Load a real request trace (Wikipedia pageviews) as serving traffic.

Each article = a request type; daily view counts = the traffic mix. A forecast is
simply an EARLIER day's distribution, so forecast error is real temporal drift —
no synthetic perturbation. The older the forecast day, the staler the forecast.

Data: cached Wikimedia "top articles per day" JSON in data/trace/wiki/. Maps to
serving as: pages = request types, cache shards / replicas = resources, a cache
hit = a match, "predict today's hot pages from an old day" = the traffic forecast.
"""
from __future__ import annotations
import json
from pathlib import Path

import numpy as np

_DROP_PREFIXES = (
    "Special:", "Wikipedia:", "Portal:", "File:", "Help:", "Category:",
    "Talk:", "Template:", "User:", "Draft:", "MediaWiki:",
)


def load_day(path: str | Path) -> dict[str, int]:
    """Return {article: views} for one cached day, filtered to content articles."""
    items = json.loads(Path(path).read_text())["items"][0]["articles"]
    out: dict[str, int] = {}
    for a in items:
        title = a["article"]
        if title == "Main_Page" or title.startswith(_DROP_PREFIXES):
            continue
        out[title] = int(a["views"])
    return out


def build_trace(
    live_path: str | Path,
    forecast_paths: dict[str, str | Path],
    n_types: int,
) -> tuple[list[str], np.ndarray, dict[str, tuple[np.ndarray, float]]]:
    """Build the trace.

    Returns (types, p_live, forecasts) where:
      - types      = the n_types most-viewed content articles on the live day
      - p_live     = live traffic distribution over those types (sums to 1)
      - forecasts  = {label: (q, L1)} for each forecast day — q is the forecast
                     distribution over the SAME types (0 for types absent from that
                     day's top list), and L1 = real drift L1(p_live, q).
    """
    live = load_day(live_path)
    types = sorted(live, key=lambda t: -live[t])[:n_types]
    live_v = np.array([live[t] for t in types], dtype=float)
    p_live = live_v / live_v.sum()

    forecasts: dict[str, tuple[np.ndarray, float]] = {}
    for label, path in forecast_paths.items():
        day = load_day(path)
        q_v = np.array([day.get(t, 0) for t in types], dtype=float)
        if q_v.sum() == 0:
            continue
        q = q_v / q_v.sum()
        l1 = float(np.abs(p_live - q).sum())
        forecasts[label] = (q, l1)
    return types, p_live, forecasts
