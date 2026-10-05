# Phase 18 - Two-dump monthly processing

The monthly cycle accepts exactly two Tech inputs:
1. Incentive Dump
2. Revenue Share Dump

## Phase 1: Populate and segregate
The Populate step only reads the raw Incentive and Revenue Share dumps, preserves source file/sheet/row provenance, resolves content type from explicit source markers or maintained content master data, and produces:
- Author Level
- Author Level Novel
- Author Level Series
- Author Level N2A/A2A

There is **no eligibility, Pay?, compliance, payout-status, or other filtering in Phase 1**. No payout calculation is performed here. Rows with valid identity are retained even when eligibility fields are empty or negative; rows with no identity remain in raw storage and are reported as unrepresentable in an Author-level view.

## Phase 2+: Calculation and QC
Filtering, Gross/TDS/Net calculation, recovery, bank/PAN checks, QC and final Finance/UWT gating happen after Populate. Calculation column mapping is selected per month; the selected INC/RS Gross source column is applied to each source row by Book ID/source lineage, with the configured TDS factor column applied during calculation.

Exports:
- Author Level audit output with source references
- QC Results
- Source Lines for row-level cross verification
- Final Finance/UWT output only after mandatory downstream controls pass
