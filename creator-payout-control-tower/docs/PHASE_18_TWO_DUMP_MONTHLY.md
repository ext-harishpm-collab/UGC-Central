# Phase 18 - Two-dump monthly processing

The monthly cycle accepts exactly two Tech inputs:
1. Incentive Dump
2. Revenue Share Dump

The result is persisted and immediately queryable. The processor retains source file/sheet/row references, applies Pay? eligibility, excludes N2A/A2A incentives, resolves content type from maintained master data when available, and flags unresolved classification instead of silently guessing.

Exports:
- Author Level CSV with source references and QC evidence count
- QC Results CSV
- Source Lines endpoint for row-level cross verification

The Author Level CSV is an audit output. The final Finance/UWT export remains gated behind full contract, PAN/TDS, recovery, adjustment, bank and payment QC.
