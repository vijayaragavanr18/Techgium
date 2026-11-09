# Headline PoC Results — Indian networks first

## Phone viewer on Indian networks (A = dash.js default, D = our MPC)

| Trace | Avg Mbps | A MiB | A VMAF-NEG | D MiB | D VMAF-NEG | Bytes saved | Efficiency |
|---|---:|---:|---:|---:|---:|---:|---:|
| jio_4g_metro | 14.5 | 9.553 | 84.51 | 2.41 | 76.6 | +74.8% | 3.59× |
| airtel_4g_tier2 | 6.8 | 9.553 | 84.51 | 2.41 | 76.6 | +74.8% | 3.59× |
| bsnl_3g_rural | 1.0 | 2.051 | 59.8 | 1.399 | 69.48 | +31.8% | 1.70× |
| metro_peak_hour | 9.7 | 9.553 | 84.51 | 2.41 | 76.6 | +74.8% | 3.59× |
| jio_5g_metro | 87.5 | 9.553 | 84.51 | 2.41 | 76.6 | +74.8% | 3.59× |
| belgium_4g | 3.7 | 4.882 | 74.5 | 2.41 | 76.6 | +50.6% | 2.08× |
| norway_3g | 0.7 | 1.268 | 51.52 | 1.057 | 65.48 | +16.6% | 1.52× |
| sudden_drop | 1.0 | 2.076 | 61.57 | 1.917 | 73.65 | +7.7% | 1.30× |

**Read:** D delivers the phone VMAF target with large bandwidth savings on fast Indian links where A overdelivers for the device. On BSNL 3G rural (the hardest case), D still cuts rebuffering with modest savings.