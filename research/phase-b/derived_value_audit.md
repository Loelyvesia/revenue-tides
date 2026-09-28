# Derived-value audit

MARVEL Contest of Champions is the only derived quantitative series.

Each quarter uses:

`official Netmarble consolidated revenue × official MCOC title share`

The title share is printed as a whole percentage. The point estimate uses the reported percentage. The compatible interval uses share ±0.5 percentage point and is rounded outward to 0.01 KRW billion. The denominator, share, formula, point, lower bound, upper bound, and extraction-page IDs are all retained.

Phase B uses `Decimal` arithmetic. This corrects small binary-floating artifacts in two Phase A.1 example bounds: 2024Q3 is 48.54–55.03 rather than 48.53–55.02, and 2024Q4 is 81.12–87.62 rather than 81.11–87.63. The underlying official inputs and ±0.5-point assumption are unchanged.

The result is an allocation estimate derived from official inputs. It is not a directly reported title amount and never receives the `OFFICIAL_REPORTED` class.
