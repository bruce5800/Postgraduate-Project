# Arrival order as an independent variable (probe)

## A. The tight construction (m=250, OPT=500, 20 tie-break seeds)

Same graph in both rows; only the arrival order differs.

| Arrival order | Greedy | Ranking | MPD (true degrees) |
|---|---|---|---|
| flexible first (hostile) | 0.500 ± 0.000 | 0.746 ± 0.007 | 1.000 ± 0.000 |
| inflexible first (friendly) | 1.000 ± 0.000 | 1.000 ± 0.000 | 1.000 ± 0.000 |

## B. Order as a variable on the thesis's own instances

inflexible-first (friendly) / random / flexible-first (hostile).

**clvb_zipf** (30 trials)

| Algorithm | friendly | random | hostile |
|---|---|---|---|
| Greedy | 0.947 | 0.914 | 0.858 |
| Ranking | 0.965 | 0.944 | 0.904 |
| Feldman | 0.888 | 0.888 | 0.888 |
| JailletLu | 0.908 | 0.903 | 0.897 |
| MPD (perfect) | 0.992 | 0.989 | 0.983 |

**left_regular d=5** (30 trials)

| Algorithm | friendly | random | hostile |
|---|---|---|---|
| Greedy | 0.890 | 0.890 | 0.890 |
| Ranking | 0.890 | 0.889 | 0.890 |
| Feldman | 0.759 | 0.759 | 0.759 |
| JailletLu | 0.787 | 0.785 | 0.787 |
| MPD (perfect) | 0.930 | 0.930 | 0.930 |

**Caltech36** (20 trials)

| Algorithm | friendly | random | hostile |
|---|---|---|---|
| Greedy | 0.951 | 0.907 | 0.816 |
| Ranking | 0.953 | 0.907 | 0.814 |
| Feldman | 0.751 | 0.751 | 0.751 |
| JailletLu | 0.783 | 0.783 | 0.772 |
| MPD (perfect) | 0.996 | 0.961 | 0.886 |

**Reed98** (20 trials)

| Algorithm | friendly | random | hostile |
|---|---|---|---|
| Greedy | 0.943 | 0.906 | 0.823 |
| Ranking | 0.945 | 0.904 | 0.817 |
| Feldman | 0.747 | 0.747 | 0.747 |
| JailletLu | 0.783 | 0.784 | 0.777 |
| MPD (perfect) | 0.996 | 0.957 | 0.879 |

**CE-GN** (20 trials)

| Algorithm | friendly | random | hostile |
|---|---|---|---|
| Greedy | 0.938 | 0.895 | 0.786 |
| Ranking | 0.940 | 0.896 | 0.787 |
| Feldman | 0.758 | 0.758 | 0.758 |
| JailletLu | 0.795 | 0.789 | 0.783 |
| MPD (perfect) | 0.993 | 0.955 | 0.871 |

**CE-PG** (20 trials)

| Algorithm | friendly | random | hostile |
|---|---|---|---|
| Greedy | 0.948 | 0.879 | 0.757 |
| Ranking | 0.949 | 0.882 | 0.761 |
| Feldman | 0.790 | 0.790 | 0.790 |
| JailletLu | 0.816 | 0.817 | 0.811 |
| MPD (perfect) | 0.986 | 0.959 | 0.895 |

**beause** (20 trials)

| Algorithm | friendly | random | hostile |
|---|---|---|---|
| Greedy | 1.000 | 0.971 | 0.881 |
| Ranking | 1.000 | 0.970 | 0.881 |
| Feldman | 0.731 | 0.731 | 0.731 |
| JailletLu | 0.763 | 0.763 | 0.762 |
| MPD (perfect) | 1.000 | 0.999 | 0.979 |

**mbeaw** (20 trials)

| Algorithm | friendly | random | hostile |
|---|---|---|---|
| Greedy | 1.000 | 0.980 | 0.907 |
| Ranking | 1.000 | 0.980 | 0.909 |
| Feldman | 0.726 | 0.726 | 0.726 |
| JailletLu | 0.765 | 0.768 | 0.765 |
| MPD (perfect) | 1.000 | 0.999 | 0.994 |

## C. The prefix test under a type-clustered order, eta=0.0 (n=2000, r=8, k=200, 30 trials)

| Algorithm | random arrival | type-clustered arrival |
|---|---|---|
| Ranking | 0.991 ± 0.001 | 0.951 ± 0.003 |
| MPD (perfect) | 0.999 ± 0.000 | 0.983 ± 0.002 |
| FollowPrediction | 1.000 ± 0.000 | 1.000 ± 0.000 |
| TestAndMatch (Choo) | 1.000 ± 0.000 | 0.956 ± 0.003 |
| TestAndMatch (BEM) | 0.998 ± 0.001 | 0.956 ± 0.003 |

| Test decision | random arrival | type-clustered arrival |
|---|---|---|
| CHOO misjudgement rate | 0.00 | 1.00 |
| BEM misjudgement rate | 0.17 | 1.00 |
| CHOO followed-advice rate | 1.00 | 0.00 |
| BEM followed-advice rate | 0.83 | 0.00 |

## C. The prefix test under a type-clustered order, eta=0.15 (n=2000, r=8, k=200, 30 trials)

| Algorithm | random arrival | type-clustered arrival |
|---|---|---|
| Ranking | 0.991 ± 0.001 | 0.951 ± 0.003 |
| MPD (perfect) | 0.999 ± 0.000 | 0.983 ± 0.002 |
| FollowPrediction | 0.921 ± 0.007 | 0.921 ± 0.007 |
| TestAndMatch (Choo) | 0.942 ± 0.011 | 0.956 ± 0.003 |
| TestAndMatch (BEM) | 0.980 ± 0.009 | 0.956 ± 0.003 |

| Test decision | random arrival | type-clustered arrival |
|---|---|---|
| CHOO misjudgement rate | 0.77 | 0.03 |
| BEM misjudgement rate | 0.20 | 0.03 |
| CHOO followed-advice rate | 0.77 | 0.00 |
| BEM followed-advice rate | 0.20 | 0.00 |
