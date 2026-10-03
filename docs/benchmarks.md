# Synthetic experiments

`make reproduce OUTPUT=reports/local/reproduced` regenerates actual PNG round trips, CSV, JSON and figures.
[Configuration](../configs/benchmark.json) defines seed/dimensions/payload/depths;
[manifest](../reports/run_manifest.json) records source, date, Python/dependencies, CPU architecture, config/payload hashes.
The smooth cover deliberately uses even RGB values. Public random bytes are sequential/plain or keyed/HMAC plaintext;
there is no GCM tag in the measured capacity table.

PSNR uses RGB MSE/range255; identical RGB yields null with an infinity note. SSIM uses uniform window7, range255 and
channel_axis2; small images yield null. Exact [CSV](../reports/metrics.csv) includes effective capacity bits/pixel.
Recorded process runtime is not a general throughput claim.

Chi-square tests even/odd pair equality. Include totals≥10 (expected counts≥5); df counts included pairs. Record global and
16-row blocks; no included pairs yields null p. The null is equality, not absence of payload. Natural images may violate it.
Sequential changes locally equalize this constructed field; keyed changes spread. Headers differ too, so ordering alone
is not causally isolated. Public deterministic salts apply only to this benchmark. No accuracy, undetectability,
natural-image generalization, AES performance or password-entropy claim follows. Licensed evaluation remains open.
