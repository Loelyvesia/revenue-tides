# Deterministic rebuild audit

The Phase E validator runs the Phase D builder twice, compares every canonical output hash, and then performs a temporary clean-root build from controlled Phase B/Phase D inputs. The temporary output must match canonical bytes. The validator hashes canonical inputs before and after validation to confirm that validation itself does not mutate them. Rebuild requires Python standard library only and retained local inputs; it does not depend on network access, browser/login state, private API keys, Sensor Tower, or AppMagic.
