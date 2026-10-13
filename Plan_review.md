# CRS Calculator Proposal – Architectural & Domain Review

**Status:** Approved with Required Updates

This is a solid, well-researched proposal. Catching the March 25, 2025, removal of the job offer points is a critical detail that many outdated calculators miss. To ensure this application meets production-grade standards for the immigration sector, the following updates must be integrated before proceeding to the requirements phase.

## 1. Critical UX Flaw: Language Test Inputs

Relying strictly on CLB/NCLC level inputs is unacceptable for an immigration calculator. Applicants rarely know their exact CLB/NCLC levels; they know their raw test scores (e.g., IELTS 8.0 in Listening, TEF 310 in Speaking).

* **UI Requirement:** The interface must ask for the specific test taken (IELTS, CELPIP, PTE Core, TEF Canada, or TCF Canada) and the raw scores for Reading, Writing, Listening, and Speaking.
* **Architecture Impact:** Build a `language_mapper.py` utility in the core that translates raw test scores to the appropriate CLB/NCLC bands *before* feeding them into the scoring engine.

## 2. Architecture & Maintainability: Data-Driven Rules

Immigration rules and point allocations change frequently. Hardcoding point values deep inside Python logic will create immediate technical debt.

* **Architecture Impact:** The `tables.py` module must act as a configuration layer. Define the scoring grids, bands, and caps using declarative data structures (e.g., Python dictionaries or loaded JSON/yaml configs) rather than nested conditional logic. The core engine should evaluate the profile object against these configuration maps.

## 3. Edge Cases & Nuances for Requirements Analysis

The `REQUIREMENTS_ANALYSIS.md` must explicitly address the following domain-specific edge cases:

* **Marital Status Logic:** There are three distinct marital states for CRS scoring purposes:
1. Single / No Spouse (Scored as Single)
2. Married/Common-law, but spouse is a Canadian Citizen/PR OR is *not accompanying* (Scored as Single)
3. Married/Common-law, and spouse *is accompanying* (Scored as Couple)


* **Sibling Points Cap:** The cap is exactly 15 points total, regardless of the number of eligible siblings in Canada.
* **Canadian Study vs. General Education:** Prevent UI confusion between generic "Education" (Section A/B) and the "Canadian Study" bonus (Section D). A 3-year Canadian bachelor's degree yields points in both sections, but they have distinct selection criteria and point allocations that the user must navigate seamlessly.

## 4. Implementation Steps Adjustments

Adjust the proposed implementation tasks as follows:

* **Update Task 3:** Ensure the core architecture includes the raw-score-to-CLB mapping layer (`language_mapper.py`).
* **Update Task 6 (Frontend):** Ensure the UI accurately reflects the conditional logic of the official form (e.g., dynamically displaying the spouse's education and language sections only if "Spouse is accompanying" is selected).

## Next Steps

Proceed immediately to **Task 1**. Generate the `REQUIREMENTS_ANALYSIS.md` document, encompassing your initial findings plus these architectural and domain constraints. Present the markdown for final sign-off before writing any Python code.