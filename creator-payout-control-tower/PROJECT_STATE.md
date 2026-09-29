# PROJECT_STATE

## Current Status
Phase 4 - Calculation, mandatory QC and reconciliation foundation implemented. Frontend now exposes Historical Import and Calculation & QC local views.

## Decisions Made
- GitHub repository: ext-harishpm-collab/UGC-Central
- Lovable remains deferred until core calculation, QC, UWT reconciliation and historical validation are stable.
- Raw source files remain immutable evidence.
- Historical records remain persistent and queryable.
- UWT remains a fixed external format.
- SUCCESS / FAILED / REVERSED / UNMATCHED are normalized internally.
- Only successful payments can provide successful-payment bank evidence.
- Marketing/COP/payment-threshold rules are configurable and effective-dated.
- Blocking QC prevents a record from being treated as ready for payout.

## Current Technical Scope
- XLSX/XLSM inspection and import
- Raw row provenance
- Normalized payment events
- Author/content/payment master foundation
- Configurable rule storage
- Calculation API
- QC API
- UWT/Finance reconciliation API
- Local browser UI for import and calculation/QC

## Known Issues / Open Business Decisions
- Exact Finance result matching key must be confirmed by historical workbook validation; deterministic fallback currently uses payout ID, UTR, then Author + Book + Amount.
- Final marketing/COP cap semantics need business confirmation where contracts differ.
- Final Finance UWT export field formatting and success/failed/reversal source sheets need field-level validation against all historical months.
- Production Supabase/auth/RLS intentionally deferred.

## Next Actions
1. Validate May-Aug historical workbooks through the import pipeline.
2. Build master matching and content classification from actual source sheets.
3. Build payout-line consolidation and reward lineage.
4. Build full UWT result import and Show-level ledger generator.
5. Add automated month-by-month reconciliation report.
6. Only after historical parity, move the UI to Lovable.
