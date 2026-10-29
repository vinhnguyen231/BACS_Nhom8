# Software Requirements Specification: Library Management System

## 1. Introduction
This document specifies the requirements for the Library Management System (LMS), a system for loaning, renewing, and tracking books for a university library, developed as the running worked example for CSE703095, Chapter 1.

## 1.1 Purpose
Define the functional, non-functional, and business-rule requirements for the LMS so that library staff, the development team, and QA share one authoritative reference for what the system must do.

## 1.2 Scope
Covers loan issuance, loan-limit enforcement, and the associated transaction performance target for library staff using the front-desk terminal. Excludes inter-library loans, remote renewal, and the automated sorting arm, which are introduced in later chapters.

## 1.3 Definitions, Acronyms, Abbreviations
- **LMS**: Library Management System
- **Active Loan**: A loan record with status "Out" and no return date recorded
- **Borrower**: A registered library patron eligible to take out loans

## 1.4 References
- IEEE Std 830-1998, Recommended Practice for Software Requirements Specifications
- CSE703095 Chapter 1 lecture deck, "Requirements Specification and Documentation"

## 2. Overall Description
The LMS is a new, standalone module of the university's library system, used by front-desk staff to process book loans. It interacts with the existing library catalog for item lookups and enforces a 5-active-loan limit per borrower.

## 3. System Features
- **FR-2.1.1**: The system shall accept a scanned book barcode and retrieve the corresponding catalog record.
- **FR-2.1.3**: The system shall verify the borrower has fewer than 5 active loans before completing the transaction.
- **FR-2.1.4**: If the borrower has 5 or more active loans, then the system shall reject the loan and display the reason.
- **FR-2.1.9**: The system should handle loans efficiently.

## 4. External Interface Requirements
- **User Interfaces**: A front-desk terminal UI for library staff, with a barcode-scanner input field.
- **Software Interfaces**: Read access to the existing library catalog database for item lookups.

## 5. Non-functional Requirements
- **NFR-2.1**: The loan transaction shall complete within 5 seconds under normal load (up to 20 concurrent transactions).

## 6. Other Requirements (Business Rules, Data)
- **BR-02**: A borrower with any loan overdue by more than 30 days is blocked from new loans.

## 7. Appendices
- Appendix A: Requirements Traceability Matrix -- see the coverage report printed above.
- Appendix B: Worked-example source -- requirements defined in build_lms_requirements() in this file.
