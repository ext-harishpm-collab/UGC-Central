# PROJECT_STATE

## Current Status
Phase 32 - Operational monthly control report added.

## Implemented
- Two-dump monthly processing
- Persistent source row lineage
- Eligibility and N2A/A2A incentive exclusion
- Novel / Series / N2A/A2A dimensions
- Author-level CSV and QC CSV
- Contract/PAN/TDS/compliance reference masters
- Recovery and adjustment staging
- Configurable Marketing/COP caps
- Payout batch, line QC and freeze gate
- UWT import/reconciliation and fixed-format export foundation
- Finance -> reconstructed ledger allocation foundation
- Monthly close report
- Detailed Author/Book/Show parity report
- Monthly operational control report

## Final validation work
1. Run real processed May-August source files in Codespaces.
2. Validate exact field mappings and Finance matching keys.
3. Resolve BLOCK/REVIEW cases and compare all historical totals.
4. Connect detailed Author/Book/Show drill-down UI.
5. Add production auth/storage/RLS.
6. Move approved frontend to Lovable.
