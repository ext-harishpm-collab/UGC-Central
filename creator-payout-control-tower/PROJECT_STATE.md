# PROJECT_STATE

## Current Status
Phase 16 - Cycle readiness and payout-batch QC are added.

## Controls
- Immutable source staging and provenance
- UWT fixed 13-column interface
- SUCCESS / FAILED / REVERSED / UNMATCHED normalization
- SUCCESS-only bank-payment evidence
- Novel / Series / N2A/A2A separation
- Author payout preview and configurable caps
- Recovery / adjustment staging
- QC-gated payout batch freeze
- Cycle readiness checks for missing Author/Book, unmatched payments and duplicate UTRs
- Batch QC sets each payout line PASS/BLOCK

## Next
1. Validate exact field mappings against May-August actual files.
2. Persist contract/PAN/TDS/compliance QC from their true source columns.
3. Complete exact Show-level Finance-to-ledger matching.
4. Generate fixed UWT export from approved payout lines.
5. Run system-vs-processed parity reports.
6. Finalize UI then move to Lovable.
