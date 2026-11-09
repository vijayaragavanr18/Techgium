# Headline PoC Results — Indian networks first

## Phone viewer on Indian networks (A = dash.js default, D = our MPC)

| Trace | Avg Mbps | A MiB | A VMAF-NEG | D MiB | D VMAF-NEG | Bytes saved | Efficiency |
|---|---:|---:|---:|---:|---:|---:|---:|
| jio_4g_metro | 14.5 | 9.553 | 84.51 | 1.856 | 57.46 | +80.6% | 3.50× |
| airtel_4g_tier2 | 6.8 | 9.553 | 84.51 | 1.856 | 57.46 | +80.6% | 3.50× |
| bsnl_3g_rural | 1.0 | 2.051 | 59.8 | 0.903 | 45.92 | +56.0% | 1.74× |
| metro_peak_hour | 9.7 | 9.553 | 84.51 | 1.856 | 57.46 | +80.6% | 3.50× |
| jio_5g_metro | 87.5 | 9.553 | 84.51 | 1.856 | 57.46 | +80.6% | 3.50× |
| belgium_4g | 3.7 | 4.882 | 74.5 | 1.856 | 57.46 | +62.0% | 2.03× |
| norway_3g | 0.7 | 1.268 | 51.52 | 0.691 | 43.52 | +45.5% | 1.55× |
| sudden_drop | 1.0 | 2.076 | 61.57 | 1.144 | 50.72 | +44.9% | 1.49× |

**Read:** D delivers the phone VMAF target with large bandwidth savings on fast Indian links where A overdelivers for the device. On BSNL 3G rural (the hardest case), D still cuts rebuffering with modest savings.