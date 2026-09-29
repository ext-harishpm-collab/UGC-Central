# PROJECT_STATE

## Current Status
Phase 14 - Historical validation harness added. Local operations UI, historical import, earnings ingestion, payout preview/batch, UWT result processing, recovery/adjustment staging, configurable caps and mandatory QC foundation are implemented.

## Historical Baseline
Supplied processed workbooks observed:
- May UWT: processed 899, failed 257, reversed 12
- June UWT: processed 866, failed 254, reversed 18
- July UWT: processed 1069, failed 237, reversed 27
- August Finance copy: UTR Details has 604 processed rows

## Decisions
- Raw source files are not stored in the public GitHub repository.
- Historical records are persistent; imported source rows retain provenance.
- UWT remains the fixed 13-column external Finance interface.
- SUCCESS is the only successful-payment evidence allowed to validate bank account history.
- FAILED and REVERSED remain retryable.
- Novel, Series and N2A/A2A are separate operating dimensions.
- Payout batches start DRAFT_QC_REQUIRED and cannot be frozen until QC PASS.
- Marketing/COP/threshold rules are configurable and effective-dated.
- Lovable remains deferred until historical parity.

## Next Actions
1. Run the validation harness against May-Aug workbooks in Codespaces.
2. Resolve exact field mappings for UWT/UTR, Author Level, Fin Success, Inc Final, RS Final and Show Book Mapping.
3. Implement contract-effective RS, PAN/TDS and compliance QC from the actual source sheets.
4. Complete Show-level UWT ledger reconstruction and fixed-export parity.
5. Reconcile the system with all processed monthly outputs.
