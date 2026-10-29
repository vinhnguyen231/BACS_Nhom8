"""Chapter 1 -- generate a Markdown SRS skeleton from a RequirementSet.

Follows the course SRS template (adapted IEEE 830 / ISO/IEC/IEEE 29148 hybrid)
introduced in the Chapter 1 lecture deck.

The generator fills the requirement-driven sections (System Features,
Non-functional Requirements, Other Requirements) straight from a
``RequirementSet``. The narrative sections (Introduction, Purpose, Scope,
Definitions, References, Overall Description, External Interfaces,
Appendices) are *not* derivable from requirement objects alone -- they need
project-level context a requirement doesn't carry (why the product exists,
who its users are, what terms mean, and so on). ``SRSMetadata`` supplies
that context; any section left unset still falls back to the "_TBD_"
placeholder, so callers can generate a partial document early and fill in
metadata incrementally as the project matures.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .requirement import RequirementSet, RequirementType

TEMPLATE_SECTIONS = [
    "1. Introduction",
    "1.1 Purpose",
    "1.2 Scope",
    "1.3 Definitions, Acronyms, Abbreviations",
    "1.4 References",
    "2. Overall Description",
    "3. System Features",
    "4. External Interface Requirements",
    "5. Non-functional Requirements",
    "6. Other Requirements (Business Rules, Data)",
    "7. Appendices",
]

_SECTION_TYPE_MAP = {
    "3. System Features": RequirementType.FUNCTIONAL,
    "5. Non-functional Requirements": RequirementType.NON_FUNCTIONAL,
    "6. Other Requirements (Business Rules, Data)": RequirementType.BUSINESS_RULE,
}


@dataclass
class SRSMetadata:
    """Narrative/project-context content for the sections a RequirementSet
    can't fill on its own. Every field is optional: an unset field renders
    as "_TBD_", exactly like the original placeholder behaviour, so this is
    fully backward compatible -- ``SRSMetadata()`` with everything left
    unset reproduces the old "no metadata supplied" output.
    """

    introduction: str | None = None
    purpose: str | None = None
    scope: str | None = None
    # (term, definition) pairs, rendered as a bullet glossary.
    definitions: list[tuple[str, str]] = field(default_factory=list)
    references: list[str] = field(default_factory=list)
    overall_description: str | None = None
    # (interface_name, description) pairs, e.g. ("User Interfaces", "...").
    external_interfaces: list[tuple[str, str]] = field(default_factory=list)
    appendices: list[str] = field(default_factory=list)

    def render(self, section: str) -> list[str] | None:
        """Return the rendered lines for `section`, or None if this
        metadata has nothing set for it (caller should fall back to TBD)."""
        if section == "1. Introduction" and self.introduction:
            return [self.introduction]
        if section == "1.1 Purpose" and self.purpose:
            return [self.purpose]
        if section == "1.2 Scope" and self.scope:
            return [self.scope]
        if section == "1.3 Definitions, Acronyms, Abbreviations" and self.definitions:
            return [f"- **{term}**: {definition}" for term, definition in self.definitions]
        if section == "1.4 References" and self.references:
            return [f"- {ref}" for ref in self.references]
        if section == "2. Overall Description" and self.overall_description:
            return [self.overall_description]
        if section == "4. External Interface Requirements" and self.external_interfaces:
            return [f"- **{name}**: {desc}" for name, desc in self.external_interfaces]
        if section == "7. Appendices" and self.appendices:
            return [f"- {item}" for item in self.appendices]
        return None


def generate_srs_skeleton(
    product_name: str,
    requirement_set: RequirementSet | None = None,
    metadata: SRSMetadata | None = None,
) -> str:
    """Return a Markdown SRS document skeleton.

    If a RequirementSet is supplied, its requirements are inserted under the
    matching section (System Features, Non-functional Requirements, Business
    Rules). If an SRSMetadata is supplied, its narrative content fills the
    remaining sections (Introduction, Purpose, Scope, Definitions,
    References, Overall Description, External Interfaces, Appendices).
    Any section still unfilled after both sources are checked falls back to
    a "_TBD_" placeholder.
    """
    lines = [f"# Software Requirements Specification: {product_name}", ""]
    for section in TEMPLATE_SECTIONS:
        lines.append(f"## {section}")
        req_type = _SECTION_TYPE_MAP.get(section)
        rendered: list[str] | None = None
        if requirement_set and req_type:
            matching = requirement_set.by_type(req_type)
            if matching:
                rendered = [f"- **{r.req_id}**: {r.statement}" for r in matching]
        elif metadata:
            rendered = metadata.render(section)

        if rendered:
            lines.extend(rendered)
        else:
            lines.append("_TBD_")
        lines.append("")
    return "\n".join(lines)


def write_srs(
    product_name: str,
    requirement_set: RequirementSet,
    output_path: str,
    metadata: SRSMetadata | None = None,
) -> None:
    content = generate_srs_skeleton(product_name, requirement_set, metadata)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
