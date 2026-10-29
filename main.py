"""Demo: build the Chapter 1 'Library Management System' worked example
using the requirements_toolkit, generate an SRS skeleton, and run a
traceability/coverage report.

Run: python main.py
"""

from requirements_toolkit.requirement import (
    Requirement, RequirementSet, RequirementType, Priority, Status,
)
from requirements_toolkit.srs_generator import generate_srs_skeleton, write_srs, SRSMetadata
from requirements_toolkit.traceability import (
    DesignElement, TestCase, build_traceability_matrix, coverage_report,
)


def build_lms_requirements() -> RequirementSet:
    rs = RequirementSet(name="Library Management System")

    rs.add(Requirement(
        "FR-2.1.1", "The system shall accept a scanned book barcode and retrieve the corresponding catalog record.",
        RequirementType.FUNCTIONAL, Priority.MUST, source="UC-Loan-a-Book",
    ))
    rs.add(Requirement(
        "FR-2.1.3", "The system shall verify the borrower has fewer than 5 active loans before completing the transaction.",
        RequirementType.FUNCTIONAL, Priority.MUST, source="UC-Loan-a-Book",
    ))
    rs.add(Requirement(
        "FR-2.1.4", "If the borrower has 5 or more active loans, then the system shall reject the loan and display the reason.",
        RequirementType.FUNCTIONAL, Priority.MUST, source="UC-Loan-a-Book",
    ))
    rs.add(Requirement(
        "NFR-2.1", "The loan transaction shall complete within 5 seconds under normal load (up to 20 concurrent transactions).",
        RequirementType.NON_FUNCTIONAL, Priority.SHOULD, source="BR-01",
    ))
    rs.add(Requirement(
        "BR-02", "A borrower with any loan overdue by more than 30 days is blocked from new loans.",
        RequirementType.BUSINESS_RULE, Priority.MUST, source="Library policy",
    ))
    # Deliberately vague requirement to demonstrate the testability heuristic
    rs.add(Requirement(
        "FR-2.1.9", "The system should handle loans efficiently.",
        RequirementType.FUNCTIONAL, Priority.COULD, source="(unclear)",
    ))
    return rs


def build_lms_metadata() -> SRSMetadata:
    """Narrative content for the LMS worked example, matching the Chapter 1
    lecture's IEEE 830 / ISO 29148 hybrid template. Kept intentionally short
    for this demo -- see case-study-srs/build_lms_srs.py for the full,
    course-wide version of the same document."""
    return SRSMetadata(
        introduction=(
            "This document specifies the requirements for the Library "
            "Management System (LMS), a system for loaning, renewing, and "
            "tracking books for a university library, developed as the "
            "running worked example for CSE703095, Chapter 1."
        ),
        purpose=(
            "Define the functional, non-functional, and business-rule "
            "requirements for the LMS so that library staff, the "
            "development team, and QA share one authoritative reference "
            "for what the system must do."
        ),
        scope=(
            "Covers loan issuance, loan-limit enforcement, and the "
            "associated transaction performance target for library staff "
            "using the front-desk terminal. Excludes inter-library loans, "
            "remote renewal, and the automated sorting arm, which are "
            "introduced in later chapters."
        ),
        definitions=[
            ("LMS", "Library Management System"),
            ("Active Loan", "A loan record with status \"Out\" and no return date recorded"),
            ("Borrower", "A registered library patron eligible to take out loans"),
        ],
        references=[
            "IEEE Std 830-1998, Recommended Practice for Software Requirements Specifications",
            "CSE703095 Chapter 1 lecture deck, \"Requirements Specification and Documentation\"",
        ],
        overall_description=(
            "The LMS is a new, standalone module of the university's library "
            "system, used by front-desk staff to process book loans. It "
            "interacts with the existing library catalog for item lookups "
            "and enforces a 5-active-loan limit per borrower."
        ),
        external_interfaces=[
            ("User Interfaces", "A front-desk terminal UI for library staff, with a barcode-scanner input field."),
            ("Software Interfaces", "Read access to the existing library catalog database for item lookups."),
        ],
        appendices=[
            "Appendix A: Requirements Traceability Matrix -- see the coverage report printed above.",
            "Appendix B: Worked-example source -- requirements defined in build_lms_requirements() in this file.",
        ],
    )


def main() -> None:
    rs = build_lms_requirements()

    print("=== Requirements ===")
    for r in rs.requirements:
        print(r)

    print("\n=== Testability check (Chapter 1 heuristic) ===")
    for r in rs.untestable():
        print(f"NEEDS REWRITE: [{r.req_id}] {r.statement}")

    print("\n=== Priority breakdown ===")
    for priority, count in rs.count_by_priority().items():
        print(f"{priority}: {count}")

    design_elements = [
        DesignElement(id="DE-LoanService", satisfies=["FR-2.1.1", "FR-2.1.3", "FR-2.1.4"]),
        DesignElement(id="DE-RateLimiter", satisfies=["NFR-2.1"]),
    ]
    test_cases = [
        TestCase(id="TC-LMS-014", verifies=["FR-2.1.3"]),
        TestCase(id="TC-LMS-015", verifies=["FR-2.1.4"]),
    ]
    matrix = build_traceability_matrix(rs.requirements, design_elements, test_cases)

    print("\n=== Traceability / Coverage Report ===")
    print(coverage_report(matrix))

    metadata = build_lms_metadata()
    srs_text = generate_srs_skeleton("Library Management System", rs, metadata)
    write_srs("Library Management System", rs, "lms_srs_skeleton.md", metadata)
    print("\n=== SRS skeleton written to lms_srs_skeleton.md ===")
    print(srs_text[:400] + "\n...")


if __name__ == "__main__":
    main()
