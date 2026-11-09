# Equal-quality check (phone-model VMAF, tolerance 0.5)


## phone/belgium_4g  (D default: 2.41 MiB, VMAF 84.33)

| Baseline | MiB | phone VMAF | rebuffer s | D MiB at >= that VMAF | bytes saved |
|---|---:|---:|---:|---:|---:|
| A  dash.js (unconstrained) | 4.882 | 82.81 | 0.0 | 1.917 | 60.7% |
| A720  dash.js, 720p cap | 4.882 | 82.81 | 0.0 | 1.917 | 60.7% |
| A480  dash.js, 480p cap | 2.076 | 73.88 | 0.0 | 1.057 | 49.1% |
| B  BOLA | 5.384 | 88.74 | 0.0 | 5.209 | 3.3% |
| C  our ladder + throughput ABR | 4.864 | 85.48 | 0.0 | 3.486 | 28.3% |

## phone/norway_3g  (D default: 1.057 MiB, VMAF 76.77)

| Baseline | MiB | phone VMAF | rebuffer s | D MiB at >= that VMAF | bytes saved |
|---|---:|---:|---:|---:|---:|
| A  dash.js (unconstrained) | 1.268 | 67.03 | 0.766 | 1.057 | 16.6% |
| A720  dash.js, 720p cap | 1.268 | 67.03 | 0.766 | 1.057 | 16.6% |
| A480  dash.js, 480p cap | 1.268 | 67.03 | 0.766 | 1.057 | 16.6% |
| B  BOLA | 5.384 | 88.74 | 38.958 | n/a | n/a |
| C  our ladder + throughput ABR | 1.289 | 76.77 | 0.766 | 1.057 | 18.0% |

## phone/sudden_drop  (D default: 1.917 MiB, VMAF 82.33)

| Baseline | MiB | phone VMAF | rebuffer s | D MiB at >= that VMAF | bytes saved |
|---|---:|---:|---:|---:|---:|
| A  dash.js (unconstrained) | 2.076 | 73.88 | 0.0 | 1.057 | 49.1% |
| A720  dash.js, 720p cap | 2.076 | 73.88 | 0.0 | 1.057 | 49.1% |
| A480  dash.js, 480p cap | 2.076 | 73.88 | 0.0 | 1.057 | 49.1% |
| B  BOLA | 5.384 | 88.74 | 5.107 | n/a | n/a |
| C  our ladder + throughput ABR | 2.064 | 79.98 | 0.0 | 1.399 | 32.2% |

## phone/jio_4g_metro  (D default: 2.41 MiB, VMAF 84.33)

| Baseline | MiB | phone VMAF | rebuffer s | D MiB at >= that VMAF | bytes saved |
|---|---:|---:|---:|---:|---:|
| A  dash.js (unconstrained) | 9.553 | 89.83 | 0.0 | 5.209 | 45.5% |
| A720  dash.js, 720p cap | 4.882 | 82.81 | 0.0 | 1.917 | 60.7% |
| A480  dash.js, 480p cap | 2.076 | 73.88 | 0.0 | 1.057 | 49.1% |
| B  BOLA | 4.299 | 86.68 | 0.0 | 3.486 | 18.9% |
| C  our ladder + throughput ABR | 9.553 | 89.83 | 0.0 | 5.209 | 45.5% |

## phone/airtel_4g_tier2  (D default: 2.41 MiB, VMAF 84.33)

| Baseline | MiB | phone VMAF | rebuffer s | D MiB at >= that VMAF | bytes saved |
|---|---:|---:|---:|---:|---:|
| A  dash.js (unconstrained) | 9.553 | 89.83 | 0.0 | 5.209 | 45.5% |
| A720  dash.js, 720p cap | 4.882 | 82.81 | 0.0 | 1.917 | 60.7% |
| A480  dash.js, 480p cap | 2.076 | 73.88 | 0.0 | 1.057 | 49.1% |
| B  BOLA | 4.299 | 86.68 | 0.0 | 3.486 | 18.9% |
| C  our ladder + throughput ABR | 9.553 | 89.83 | 0.0 | 5.209 | 45.5% |

## phone/bsnl_3g_rural  (D default: 1.399 MiB, VMAF 79.49)

| Baseline | MiB | phone VMAF | rebuffer s | D MiB at >= that VMAF | bytes saved |
|---|---:|---:|---:|---:|---:|
| A  dash.js (unconstrained) | 2.051 | 72.67 | 3.352 | 1.057 | 48.5% |
| A720  dash.js, 720p cap | 2.051 | 72.67 | 3.352 | 1.057 | 48.5% |
| A480  dash.js, 480p cap | 2.051 | 72.67 | 3.352 | 1.057 | 48.5% |
| B  BOLA | 5.384 | 88.74 | 29.146 | n/a | n/a |
| C  our ladder + throughput ABR | 1.765 | 78.78 | 2.392 | 1.399 | 20.7% |

## phone/metro_peak_hour  (D default: 2.41 MiB, VMAF 84.33)

| Baseline | MiB | phone VMAF | rebuffer s | D MiB at >= that VMAF | bytes saved |
|---|---:|---:|---:|---:|---:|
| A  dash.js (unconstrained) | 9.553 | 89.83 | 0.0 | 5.209 | 45.5% |
| A720  dash.js, 720p cap | 4.882 | 82.81 | 0.0 | 1.917 | 60.7% |
| A480  dash.js, 480p cap | 2.076 | 73.88 | 0.0 | 1.057 | 49.1% |
| B  BOLA | 4.299 | 86.68 | 0.0 | 3.486 | 18.9% |
| C  our ladder + throughput ABR | 9.553 | 89.83 | 0.0 | 5.209 | 45.5% |

## phone/jio_5g_metro  (D default: 2.41 MiB, VMAF 84.33)

| Baseline | MiB | phone VMAF | rebuffer s | D MiB at >= that VMAF | bytes saved |
|---|---:|---:|---:|---:|---:|
| A  dash.js (unconstrained) | 9.553 | 89.83 | 0.0 | 5.209 | 45.5% |
| A720  dash.js, 720p cap | 4.882 | 82.81 | 0.0 | 1.917 | 60.7% |
| A480  dash.js, 480p cap | 2.076 | 73.88 | 0.0 | 1.057 | 49.1% |
| B  BOLA | 4.299 | 86.68 | 0.0 | 3.486 | 18.9% |
| C  our ladder + throughput ABR | 9.553 | 89.83 | 0.0 | 5.209 | 45.5% |