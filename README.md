# CSE703095 Requirements Toolkit

A small Python requirements-management toolkit built incrementally across the semester.
Each course chapter contributes one module, so by the end of the term the class has a
working (if minimal) requirements management application — mirroring real RM tools such
as DOORS, Jama, or Polarion.

See [`ARCHITECTURE.md`](ARCHITECTURE.md) for how the modules are layered and how data
flows from `Requirement` objects to the generated SRS/CSV/JSON artifacts.


## Module Map (chapter -> module)

| Chapter | Topic | Module | Status |
|---|---|---|---|
| 1 | Requirements Specification and Documentation | `requirement.py`, `srs_generator.py`, `traceability.py` | Complete |
| 2 | Requirements Validation and Verification | `validation.py` | Complete |
| 3 | Managing Changing Requirements | `change_management.py` | Complete |
| 4 | Non-functional Requirements | `nfr.py` | Complete |
| 5 | Collaborating with Stakeholders | `stakeholders.py` | Complete |
| 6 | Use Case Modeling | `use_case.py` | Complete |
| 7 | Modeling Techniques and Notations | `diagrams.py` | Complete |
| 8 | Safety-Critical Requirements | `safety.py` | Complete |
| 9 | Tool Support for RE | `export.py` | Complete |
| 10 | SRE Processes | `process.py` | Complete |
| 11 | Elicitation and Analysis | `elicitation.py` | Complete |

All 11 modules are fully implemented with unit tests (86 tests total, all passing).

## Quick start

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python main.py
pytest
```

## Project Purpose

Students use this toolkit throughout the term project (see `../big-project-guide/`) to:

1. Record their own project's requirements as `Requirement` objects (Ch.1)
2. Auto-generate an SRS skeleton in the standard course template (Ch.1)
3. Lint requirement text and track review defects (Ch.2)
4. Manage change requests, baselines, and volatility (Ch.3)
5. Model and verify non-functional requirements via quality attribute scenarios (Ch.4)
6. Manage a stakeholder register with power/interest analysis (Ch.5)
7. Model use cases and derive requirement stubs from them (Ch.6)
8. Check class/domain model consistency against the data dictionary (Ch.7)
9. Perform hazard analysis and FMEA for safety-critical features (Ch.8)
10. Export requirements to CSV/JSON and build a metrics dashboard (Ch.9)
11. Model a tailored process and compute a maturity score (Ch.10)
12. Record elicitation sessions, assumptions, and Kano prioritization (Ch.11)

