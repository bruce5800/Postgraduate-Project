# ★4 — F1–F3 on real graphs (random partition, 95% CI)

### Caltech36 (n=769, 16656 edges, 40 trials)

| Algorithm | perfect | noisy | adversarial | garbage |
|---|---|---|---|---|
| SimpleGreedy  *(advice-free)* | 0.914 ±0.003 | 0.914 ±0.003 | 0.914 ±0.003 | 0.914 ±0.003 |
| Ranking  *(advice-free)* | 0.913 ±0.005 | 0.913 ±0.005 | 0.913 ±0.005 | 0.913 ±0.005 |
| Feldman  *(advice-free)* | 0.756 ±0.005 | 0.756 ±0.005 | 0.756 ±0.005 | 0.756 ±0.005 |
| JailletLu  *(advice-free)* | 0.790 ±0.005 | 0.790 ±0.005 | 0.790 ±0.005 | 0.790 ±0.005 |
| MinDegree (oracle)  *(advice-free)* | 0.969 ±0.004 | 0.969 ±0.004 | 0.969 ±0.004 | 0.969 ±0.004 |
| MPD | 0.967 ±0.004 | 0.929 ±0.004 | 0.843 ±0.005 | 0.909 ±0.004 |
| Feldman(MPD) | 0.957 ±0.004 | 0.944 ±0.004 | 0.921 ±0.004 | 0.938 ±0.004 |
| JailletLu(MPD) | 0.953 ±0.004 | 0.944 ±0.003 | 0.926 ±0.004 | 0.938 ±0.004 |

*F1 crash=True, aug-safe=True; F2 robust=True (aug spread 0.036 vs MPD 0.124, ratio 0.29); F3 upside=+0.054*

### Reed98 (n=962, 18812 edges, 40 trials)

| Algorithm | perfect | noisy | adversarial | garbage |
|---|---|---|---|---|
| SimpleGreedy  *(advice-free)* | 0.900 ±0.004 | 0.900 ±0.004 | 0.900 ±0.004 | 0.900 ±0.004 |
| Ranking  *(advice-free)* | 0.904 ±0.003 | 0.904 ±0.003 | 0.904 ±0.003 | 0.904 ±0.003 |
| Feldman  *(advice-free)* | 0.746 ±0.004 | 0.746 ±0.004 | 0.746 ±0.004 | 0.746 ±0.004 |
| JailletLu  *(advice-free)* | 0.778 ±0.005 | 0.778 ±0.005 | 0.778 ±0.005 | 0.778 ±0.005 |
| MinDegree (oracle)  *(advice-free)* | 0.958 ±0.003 | 0.958 ±0.003 | 0.958 ±0.003 | 0.958 ±0.003 |
| MPD | 0.954 ±0.003 | 0.915 ±0.003 | 0.841 ±0.004 | 0.903 ±0.003 |
| Feldman(MPD) | 0.943 ±0.004 | 0.931 ±0.003 | 0.912 ±0.003 | 0.926 ±0.003 |
| JailletLu(MPD) | 0.940 ±0.003 | 0.931 ±0.003 | 0.913 ±0.003 | 0.924 ±0.003 |

*F1 crash=True, aug-safe=True; F2 robust=True (aug spread 0.032 vs MPD 0.113, ratio 0.28); F3 upside=+0.050*

### CE-GN (n=2220, 53683 edges, 40 trials)

| Algorithm | perfect | noisy | adversarial | garbage |
|---|---|---|---|---|
| SimpleGreedy  *(advice-free)* | 0.894 ±0.003 | 0.894 ±0.003 | 0.894 ±0.003 | 0.894 ±0.003 |
| Ranking  *(advice-free)* | 0.895 ±0.003 | 0.895 ±0.003 | 0.895 ±0.003 | 0.895 ±0.003 |
| Feldman  *(advice-free)* | 0.758 ±0.003 | 0.758 ±0.003 | 0.758 ±0.003 | 0.758 ±0.003 |
| JailletLu  *(advice-free)* | 0.789 ±0.002 | 0.789 ±0.002 | 0.789 ±0.002 | 0.789 ±0.002 |
| MinDegree (oracle)  *(advice-free)* | 0.954 ±0.003 | 0.954 ±0.003 | 0.954 ±0.003 | 0.954 ±0.003 |
| MPD | 0.952 ±0.003 | 0.917 ±0.003 | 0.805 ±0.003 | 0.894 ±0.003 |
| Feldman(MPD) | 0.951 ±0.002 | 0.941 ±0.003 | 0.916 ±0.002 | 0.933 ±0.002 |
| JailletLu(MPD) | 0.951 ±0.002 | 0.943 ±0.002 | 0.922 ±0.002 | 0.936 ±0.002 |

*F1 crash=True, aug-safe=True; F2 robust=True (aug spread 0.034 vs MPD 0.148, ratio 0.23); F3 upside=+0.057*

### CE-PG (n=1871, 47754 edges, 40 trials)

| Algorithm | perfect | noisy | adversarial | garbage |
|---|---|---|---|---|
| SimpleGreedy  *(advice-free)* | 0.882 ±0.003 | 0.882 ±0.003 | 0.882 ±0.003 | 0.882 ±0.003 |
| Ranking  *(advice-free)* | 0.883 ±0.004 | 0.883 ±0.004 | 0.883 ±0.004 | 0.883 ±0.004 |
| Feldman  *(advice-free)* | 0.791 ±0.004 | 0.791 ±0.004 | 0.791 ±0.004 | 0.791 ±0.004 |
| JailletLu  *(advice-free)* | 0.817 ±0.004 | 0.817 ±0.004 | 0.817 ±0.004 | 0.817 ±0.004 |
| MinDegree (oracle)  *(advice-free)* | 0.961 ±0.002 | 0.961 ±0.002 | 0.961 ±0.002 | 0.961 ±0.002 |
| MPD | 0.957 ±0.002 | 0.911 ±0.003 | 0.782 ±0.003 | 0.885 ±0.003 |
| Feldman(MPD) | 0.960 ±0.002 | 0.951 ±0.003 | 0.921 ±0.003 | 0.944 ±0.003 |
| JailletLu(MPD) | 0.958 ±0.002 | 0.953 ±0.002 | 0.928 ±0.003 | 0.946 ±0.002 |

*F1 crash=True, aug-safe=True; F2 robust=True (aug spread 0.039 vs MPD 0.175, ratio 0.22); F3 upside=+0.077*

### beause (n=507, 39427 edges, 40 trials)

| Algorithm | perfect | noisy | adversarial | garbage |
|---|---|---|---|---|
| SimpleGreedy  *(advice-free)* | 0.967 ±0.003 | 0.967 ±0.003 | 0.967 ±0.003 | 0.967 ±0.003 |
| Ranking  *(advice-free)* | 0.965 ±0.003 | 0.965 ±0.003 | 0.965 ±0.003 | 0.965 ±0.003 |
| Feldman  *(advice-free)* | 0.736 ±0.005 | 0.736 ±0.005 | 0.736 ±0.005 | 0.736 ±0.005 |
| JailletLu  *(advice-free)* | 0.771 ±0.005 | 0.771 ±0.005 | 0.771 ±0.005 | 0.771 ±0.005 |
| MinDegree (oracle)  *(advice-free)* | 1.000 ±0.000 | 1.000 ±0.000 | 1.000 ±0.000 | 1.000 ±0.000 |
| MPD | 1.000 ±0.000 | 0.983 ±0.002 | 0.893 ±0.005 | 0.967 ±0.004 |
| Feldman(MPD) | 0.995 ±0.002 | 0.978 ±0.003 | 0.939 ±0.004 | 0.968 ±0.003 |
| JailletLu(MPD) | 0.993 ±0.002 | 0.978 ±0.003 | 0.942 ±0.003 | 0.968 ±0.003 |

*F1 crash=True, aug-safe=False; F2 robust=False (aug spread 0.056 vs MPD 0.107, ratio 0.53); F3 upside=+0.035*

### mbeaw (n=487, 41686 edges, 40 trials)

| Algorithm | perfect | noisy | adversarial | garbage |
|---|---|---|---|---|
| SimpleGreedy  *(advice-free)* | 0.979 ±0.003 | 0.979 ±0.003 | 0.979 ±0.003 | 0.979 ±0.003 |
| Ranking  *(advice-free)* | 0.977 ±0.003 | 0.977 ±0.003 | 0.977 ±0.003 | 0.977 ±0.003 |
| Feldman  *(advice-free)* | 0.731 ±0.006 | 0.731 ±0.006 | 0.731 ±0.006 | 0.731 ±0.006 |
| JailletLu  *(advice-free)* | 0.764 ±0.005 | 0.764 ±0.005 | 0.764 ±0.005 | 0.764 ±0.005 |
| MinDegree (oracle)  *(advice-free)* | 0.999 ±0.000 | 0.999 ±0.000 | 0.999 ±0.000 | 0.999 ±0.000 |
| MPD | 0.999 ±0.000 | 0.989 ±0.002 | 0.913 ±0.004 | 0.980 ±0.002 |
| Feldman(MPD) | 0.999 ±0.001 | 0.987 ±0.003 | 0.951 ±0.003 | 0.980 ±0.002 |
| JailletLu(MPD) | 0.998 ±0.001 | 0.987 ±0.002 | 0.955 ±0.003 | 0.978 ±0.003 |

*F1 crash=True, aug-safe=False; F2 robust=False (aug spread 0.048 vs MPD 0.086, ratio 0.55); F3 upside=+0.022*
