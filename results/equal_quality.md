# Equal-quality check (phone-model VMAF, tolerance 0.5)


## phone/belgium_4g  (D default: 1.856 MiB, VMAF 71.07)

| Baseline | MiB | phone VMAF | rebuffer s | D MiB at >= that VMAF | bytes saved |
|---|---:|---:|---:|---:|---:|
| A  dash.js (unconstrained) | 4.882 | 82.81 | 0.0 | 4.225 | 13.5% |
| A720  dash.js, 720p cap | 4.882 | 82.81 | 0.0 | 4.225 | 13.5% |
| A480  dash.js, 480p cap | 2.076 | 73.88 | 0.0 | 1.871 | 9.9% |
| B  BOLA | 5.384 | 88.74 | 0.0 | n/a | n/a |
| C  our ladder + throughput ABR | 4.864 | 85.48 | 0.0 | 4.864 | 0.0% |

## phone/norway_3g  (D default: 0.691 MiB, VMAF 61.59)

| Baseline | MiB | phone VMAF | rebuffer s | D MiB at >= that VMAF | bytes saved |
|---|---:|---:|---:|---:|---:|
| A  dash.js (unconstrained) | 1.268 | 67.03 | 0.766 | n/a | n/a |
| A720  dash.js, 720p cap | 1.268 | 67.03 | 0.766 | n/a | n/a |
| A480  dash.js, 480p cap | 1.268 | 67.03 | 0.766 | n/a | n/a |
| B  BOLA | 5.384 | 88.74 | 38.958 | n/a | n/a |
| C  our ladder + throughput ABR | 1.289 | 76.77 | 0.766 | n/a | n/a |

## phone/sudden_drop  (D default: 1.144 MiB, VMAF 66.49)

| Baseline | MiB | phone VMAF | rebuffer s | D MiB at >= that VMAF | bytes saved |
|---|---:|---:|---:|---:|---:|
| A  dash.js (unconstrained) | 2.076 | 73.88 | 0.0 | 2.955 | -42.3% |
| A720  dash.js, 720p cap | 2.076 | 73.88 | 0.0 | 2.955 | -42.3% |
| A480  dash.js, 480p cap | 2.076 | 73.88 | 0.0 | 2.955 | -42.3% |
| B  BOLA | 5.384 | 88.74 | 5.107 | n/a | n/a |
| C  our ladder + throughput ABR | 2.064 | 79.98 | 0.0 | n/a | n/a |

## phone/jio_4g_metro  (D default: 1.856 MiB, VMAF 71.07)

| Baseline | MiB | phone VMAF | rebuffer s | D MiB at >= that VMAF | bytes saved |
|---|---:|---:|---:|---:|---:|
| A  dash.js (unconstrained) | 9.553 | 89.83 | 0.0 | n/a | n/a |
| A720  dash.js, 720p cap | 4.882 | 82.81 | 0.0 | 4.225 | 13.5% |
| A480  dash.js, 480p cap | 2.076 | 73.88 | 0.0 | 1.871 | 9.9% |
| B  BOLA | 4.299 | 86.68 | 0.0 | 8.485 | -97.4% |
| C  our ladder + throughput ABR | 9.553 | 89.83 | 0.0 | n/a | n/a |

## phone/airtel_4g_tier2  (D default: 1.856 MiB, VMAF 71.07)

| Baseline | MiB | phone VMAF | rebuffer s | D MiB at >= that VMAF | bytes saved |
|---|---:|---:|---:|---:|---:|
| A  dash.js (unconstrained) | 9.553 | 89.83 | 0.0 | n/a | n/a |
| A720  dash.js, 720p cap | 4.882 | 82.81 | 0.0 | 4.225 | 13.5% |
| A480  dash.js, 480p cap | 2.076 | 73.88 | 0.0 | 1.871 | 9.9% |
| B  BOLA | 4.299 | 86.68 | 0.0 | 8.485 | -97.4% |
| C  our ladder + throughput ABR | 9.553 | 89.83 | 0.0 | n/a | n/a |

## phone/bsnl_3g_rural  (D default: 0.903 MiB, VMAF 63.22)

| Baseline | MiB | phone VMAF | rebuffer s | D MiB at >= that VMAF | bytes saved |
|---|---:|---:|---:|---:|---:|
| A  dash.js (unconstrained) | 2.051 | 72.67 | 3.352 | n/a | n/a |
| A720  dash.js, 720p cap | 2.051 | 72.67 | 3.352 | n/a | n/a |
| A480  dash.js, 480p cap | 2.051 | 72.67 | 3.352 | n/a | n/a |
| B  BOLA | 5.384 | 88.74 | 29.146 | n/a | n/a |
| C  our ladder + throughput ABR | 1.765 | 78.78 | 2.392 | n/a | n/a |

## phone/metro_peak_hour  (D default: 1.856 MiB, VMAF 71.07)

| Baseline | MiB | phone VMAF | rebuffer s | D MiB at >= that VMAF | bytes saved |
|---|---:|---:|---:|---:|---:|
| A  dash.js (unconstrained) | 9.553 | 89.83 | 0.0 | n/a | n/a |
| A720  dash.js, 720p cap | 4.882 | 82.81 | 0.0 | 4.225 | 13.5% |
| A480  dash.js, 480p cap | 2.076 | 73.88 | 0.0 | 1.871 | 9.9% |
| B  BOLA | 4.299 | 86.68 | 0.0 | 8.485 | -97.4% |
| C  our ladder + throughput ABR | 9.553 | 89.83 | 0.0 | n/a | n/a |

## phone/jio_5g_metro  (D default: 1.856 MiB, VMAF 71.07)

| Baseline | MiB | phone VMAF | rebuffer s | D MiB at >= that VMAF | bytes saved |
|---|---:|---:|---:|---:|---:|
| A  dash.js (unconstrained) | 9.553 | 89.83 | 0.0 | n/a | n/a |
| A720  dash.js, 720p cap | 4.882 | 82.81 | 0.0 | 4.225 | 13.5% |
| A480  dash.js, 480p cap | 2.076 | 73.88 | 0.0 | 1.871 | 9.9% |
| B  BOLA | 4.299 | 86.68 | 0.0 | 8.485 | -97.4% |
| C  our ladder + throughput ABR | 9.553 | 89.83 | 0.0 | n/a | n/a |