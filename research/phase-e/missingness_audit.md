# Missingness and null audit

All 66 expected grid rows are AVAILABLE and reference one or more canonical observations. No missing value is encoded as zero, interpolated, forward-filled, or silently omitted. Empty cells are intentional schema blanks: direct observations have no uncertainty/derivation ID; HTML sources have no PDF page/local snapshot; open-ended metric definitions have blank valid_to; first compatible observations have blank QoQ; unrecovered or non-recovery rows have blank recovery duration. No NaN, Infinity, -Infinity, undefined, string null, or string None occurs.
