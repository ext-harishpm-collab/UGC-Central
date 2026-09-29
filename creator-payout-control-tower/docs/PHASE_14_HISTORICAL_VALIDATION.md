# Phase 14 - Historical validation harness

Use `tools/validate_history.py` in Codespaces against the four processed payout workbooks.

The harness checks:
- UWT / UTR status distributions
- Incentive and Revenue Share row counts, Pay? flags and IP type distribution
- Missing Book IDs
- Show Book Mapping uniqueness signals

Observed baseline from the supplied workbooks:
- May UWT: processed 899, failed 257, reversed 12
- June UWT: processed 866, failed 254, reversed 18
- July UWT: processed 1069, failed 237, reversed 27
- August Finance copy: UTR Details processed 604 (August file uses UTR Details rather than a "uwt final" sheet)

These are validation baselines, not business-rule truth. Any discrepancy must be investigated against the source workbook before changing calculation logic.
