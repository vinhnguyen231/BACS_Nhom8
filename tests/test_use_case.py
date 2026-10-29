import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from requirements_toolkit.use_case import UseCase, Extension, derive_requirement_stubs, scenario_coverage


def make_loan_use_case():
    return UseCase(
        uc_id="UC-01",
        name="Loan a Book",
        primary_actor="Librarian",
        preconditions=["Borrower has an active account", "Book is available"],
        postconditions=["A new loan record exists with status Out"],
        main_flow=[
            "accept a scanned book barcode and retrieve the catalog record",
            "verify the borrower has fewer than 5 active loans",
            "set the due date to 14 days from the loan date",
        ],
        extensions=[
            Extension("2a", "the barcode does not match any catalog record", "display 'Item not found' and reject the transaction"),
            Extension("5a", "the borrower has 5 or more active loans", "reject the loan and display the reason"),
        ],
    )


def test_scenario_count_includes_main_and_extensions():
    uc = make_loan_use_case()
    assert uc.scenario_count() == 3  # 1 main + 2 extensions


def test_derive_requirement_stubs_creates_one_per_main_flow_step():
    uc = make_loan_use_case()
    stubs = derive_requirement_stubs(uc, id_prefix="FR-2.1")
    main_flow_stubs = [s for s in stubs if "main flow" in s.source]
    assert len(main_flow_stubs) == 3


def test_derive_requirement_stubs_creates_one_per_extension():
    uc = make_loan_use_case()
    stubs = derive_requirement_stubs(uc, id_prefix="FR-2.1")
    ext_stubs = [s for s in stubs if "extension" in s.source]
    assert len(ext_stubs) == 2
    assert any("item not found" in s.statement.lower() for s in ext_stubs)


def test_derive_requirement_stubs_uses_shall_modal():
    uc = make_loan_use_case()
    stubs = derive_requirement_stubs(uc, id_prefix="FR-2.1")
    assert all("shall" in s.statement.lower() for s in stubs)


def test_scenario_coverage_full():
    uc = make_loan_use_case()
    coverage = scenario_coverage(uc, tested_step_refs={"main", "2a", "5a"})
    assert coverage == 1.0


def test_scenario_coverage_partial():
    uc = make_loan_use_case()
    coverage = scenario_coverage(uc, tested_step_refs={"main"})
    assert coverage == 1 / 3


def test_scenario_coverage_empty_use_case_is_zero():
    empty_uc = UseCase(uc_id="UC-99", name="Empty", primary_actor="Nobody")
    assert scenario_coverage(empty_uc, tested_step_refs=set()) == 0.0
