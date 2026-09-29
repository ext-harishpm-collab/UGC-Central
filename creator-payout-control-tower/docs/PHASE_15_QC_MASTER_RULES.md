# Phase 15 - QC persistence and business-rule adapters

Added rule adapters for contract RS comparison and PAN/TDS normalization, plus persistent QC/Exception records and deterministic Show-level ledger rebuilding.

Important: the supplied SOP contains business rules whose exact field semantics need validation against the historical source files. The system therefore keeps source-specific adapters separate and does not infer missing contract/TDS fields from unrelated columns.

The next validation step is field-level mapping for actual May-August workbooks before enabling production payout approval.
