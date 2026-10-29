# requirements_toolkit -- Architecture

This document describes how the eleven per-chapter modules fit together,
what depends on what, and how data flows from raw requirement objects to
the generated artifacts (`main.py`'s demo output, and the full
`case-study-srs/` case study).

## 1. Layering

The toolkit is organized in three layers. Each layer only depends on the
layer(s) below it -- there are no upward or sideways dependencies between
modules in the same layer, which keeps each chapter's module independently
testable.

```
Layer 3: Cross-cutting / reporting
  export.py (Ch.9)         -- combines Layer 1+2 outputs into CSV/JSON/dashboard
  srs_generator.py (Ch.1)  -- combines Layer 1 data + SRSMetadata into a Markdown SRS

Layer 2: Process & analysis modules (each independent, all consume Layer 1)
  validation.py (Ch.2)         -- lints Requirement.statement, tracks ReviewDefect
  change_management.py (Ch.3)  -- ChangeRequest / Baseline / volatility over a RequirementSet
  nfr.py (Ch.4)                 -- QualityAttributeScenario -> NFR text; NFRVerification tracking
  stakeholders.py (Ch.5)        -- Stakeholder register, power/interest grid
  use_case.py (Ch.6)            -- UseCase / Extension -> derive_requirement_stubs() -> Requirement
  diagrams.py (Ch.7)            -- class/domain model vs. data-dictionary consistency check
  safety.py (Ch.8)              -- Hazard / FMEA -> SafetyRequirement
  process.py (Ch.10)            -- tailored SRE process model + maturity score
  elicitation.py (Ch.11)        -- ElicitationSession, Assumption log, Kano prioritization
  traceability.py (Ch.1/3/9)    -- DesignElement / TestCase -> traceability matrix, coverage

Layer 1: Core domain model
  requirement.py (Ch.1) -- Requirement, RequirementSet, RequirementType, Priority, Status
```

`traceability.py` is listed in Layer 2 but is really a *shared* utility:
Chapter 1 introduces it, Chapter 3 reuses it for change-impact analysis,
and Chapter 9 reuses it again for the coverage metric in the dashboard.
It depends only on plain data (requirements, `DesignElement`, `TestCase`)
and has no dependency on any other Layer 2 module, so it doesn't break the
"no sideways dependencies" rule.

## 2. Data flow: from Requirement objects to generated artifacts

```
Requirement, RequirementSet          (Layer 1 -- requirement.py)
        |
        |--------------------------------------------------------------+
        v                                                              v
generate_srs_skeleton(product_name,                         build_traceability_matrix(
    requirement_set,                                            requirements,
    metadata: SRSMetadata)             (Ch.1 srs_generator.py)      design_elements,
        |                                                            test_cases)
        v                                                        (Ch.1/9 traceability.py)
  LMS_SRS_generated_body.md                                          |
  (or lms_srs_skeleton.md                                            v
   in the python-project demo)                              coverage_report(matrix)
                                                              find_untested_requirements(matrix)
        ^                                                             |
        |                                                             v
  SRSMetadata                                              build_dashboard_summary(
  (narrative content: purpose,                                 requirement_set, defects,
   scope, definitions, ...)                                     verifications, matrix)
                                                                (Ch.9 export.py)
                                                                       |
                                                                       v
                                                          LMS_dashboard.json
                                                          (ambiguity_rate, defect_density,
                                                           nfr_pass_rate, untested_requirements)
```

Two independent scripts drive this pipeline with different requirement
sets:

- **`main.py`** -- a small, single-chapter-style demo: six requirements,
  two design elements, two test cases, and a short `SRSMetadata`. Good for
  reading end-to-end in a few minutes.
- **`case-study-srs/build_lms_srs.py`** -- the capstone case study: 21
  requirements spanning Chapters 1-11, 5 design elements, 19 test cases
  (100% traceability coverage), 6 verified NFRs, and a full `SRSMetadata`
  whose content is kept consistent with the hand-polished `LMS_SRS.md`.

Both scripts import the *same* `requirements_toolkit` package -- there is
exactly one implementation of each Chapter's logic, exercised by two
different datasets. This is the "docs-as-code" principle taught in
Chapter 9: one source of truth (the Python requirement/verification
objects), multiple generated views (Markdown SRS, CSV export, JSON
dashboard, console reports).

## 3. Why `export.py` imports locally, not at module load time

`build_dashboard_summary()` in `export.py` imports `ambiguity_rate` /
`defect_density` from `validation.py` and `nfr_pass_rate` from `nfr.py`
*inside the function body*, not at the top of the file. This avoids a
hard import-time dependency cycle: `export.py` is Chapter 9's module, but
it needs metrics defined in Chapters 2 and 4. Deferring the import to call
time means `export.py` can be imported on its own (e.g. by a test that only
exercises `export_to_csv`) without pulling in every other chapter's module
graph. All other cross-module calls in the toolkit are similarly kept
one-directional (Layer 3 -> Layer 2 -> Layer 1) to keep this the only
place such a deferred import is needed.

## 4. Extending the toolkit

To add a new generated view (Layer 3) or a new analysis (Layer 2):

1. Only depend on `requirement.py` (Layer 1) and, if you need
   traceability, `traceability.py`.
2. Do not import another Layer 2 module directly. If you need combined
   data from two modules, do the composition in the *caller* (as
   `build_lms_srs.py` / `main.py` do), or add a Layer 3 function similar to
   `build_dashboard_summary()` with a local (deferred) import.
3. Add a `tests/test_<module>.py` covering the new module's public
   functions in isolation, following the existing per-chapter test files.
