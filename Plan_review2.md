## 1. Rulings on §10 Open Questions (Q1 – Q14)

### **Q1: Test scores between listed bands (IELTS non-contiguous thresholds)**

* **Ruling:** **APPROVED AS PROPOSED.**
* **Logic:** CRS scoring uses a floor-threshold evaluation ($score \ge threshold$). A score like IELTS Speaking 4.5 meets the floor for CLB 4 (4.0) but fails CLB 5 (5.0); therefore, it maps to **CLB 4**. Similarly, IELTS Reading 4.5 meets the floor for CLB 5 (4.0) but fails CLB 6 (5.0); therefore, it maps to **CLB 5**. Restrict the UI dropdowns/inputs for IELTS to standard 0.5 step increments.

---

### **Q2: Scores below CLB 4 bound**

* **Ruling:** **APPROVED AS PROPOSED.**
* **Logic:** Any raw score mapping below CLB 4 translates to `<4` and earns 0 points across all sections. The mapper must return `<4` gracefully without throwing validation errors.

---

### **Q3: Same-language test input for 1st and 2nd language**

* **Ruling:** **APPROVED AS PROPOSED.**
* **Logic:** First and second official language tests must evaluate different languages (one English, one French). The backend engine and frontend must throw a validation error if both are set to the same language.

---

### **Q4: French bonus when English results are mixed (CLB 5+ on some, CLB 4/none on others)**

* **Ruling:** **APPROVED WITH SPECIFIC LOGIC.**
* **Logic:** The IRCC criteria state:
* **50 points:** NCLC 7+ across all 4 French abilities **AND** CLB 5+ across **ALL 4** English abilities.
* **25 points:** NCLC 7+ across all 4 French abilities **AND** English CLB 4 or lower in **ANY** ability (including taking no English test at all).


* **Rule:** If French $\ge$ NCLC 7 in all four abilities, award **50 points** *only if* $\min(\text{English CLB}) \ge 5$. If $\min(\text{English CLB}) < 5$ or if English is omitted, award **25 points**.

---

### **Q5: Single Bachelor's in Skill Transferability (Education Group)**

* **Ruling:** **APPROVED AS PROPOSED.**
* **Logic:** IRCC groups all post-secondary credentials of $\ge 1$ year (that do not meet the "high" threshold of two or more credentials or Master's/Ph.D.) into the **Post-secondary credential of one year or longer** tier (13 points with CLB 7–8/CWE 1 yr; 25 points with CLB 9+/CWE 2+ yrs). A single Bachelor's degree falls into this tier.

---

### **Q6: Two credentials, none $\ge 3$ years (e.g., two 2-year diplomas)**

* **Ruling:** **APPROVED AS PROPOSED.**
* **Logic:** IRCC explicitly requires that for the "Two or more credentials" row, at least one credential must be a program of **three or more years**. If an applicant has two 2-year credentials, they do not qualify for the "Two or more" row:
* Core Education (Section A/B): Score as **Two-year post-secondary program** (91 points W / 98 points S).
* Transferability (Section C): Tier as **Post-secondary credential of one year or longer** (13/25 points).



---

### **Q7: Second Language Cap for Couples**

* **Ruling:** **APPROVED AS PROPOSED.**
* **Logic:** The mathematical sum of 4 abilities at max 6 points each is 24. For a candidate scored with a spouse, apply `min(sum, 22)`. For a single candidate, apply `min(sum, 24)`.

---

### **Q8: Language test older than 2 years**

* **Ruling:** **REVISED — DROP THE CHECKBOX, HANDLE VIA HELP TEXT.**
* **Logic:** CRS calculators evaluate points based on valid submitted scores. Including a test date/validity checkbox overcomplicates the core scoring engine. Add help text under the language section: *"Language test results must be less than 2 years old on the date of Express Entry profile submission and invitation."* Assume submitted scores are valid.

---

### **Q9: Section D Cap when PNP + others**

* **Ruling:** **APPROVED AS PROPOSED.**
* **Logic:** Strictly enforce `min(600, sum_of_additional_points)` on Section D.

---

### **Q10: Job-Offer Points**

* **Ruling:** **APPROVED AS PROPOSED.**
* **Logic:** Do not include job-offer input or point calculations. Display an informational notice box stating that arranged employment points were removed from the CRS effective March 25, 2025.

---

### **Q11: Age Input**

* **Ruling:** **APPROVED AS PROPOSED.**
* **Logic:** Use a simple integer input for age (17 to 100). Add help text indicating that age is calculated based on the candidate's age on the day they receive an Invitation to Apply (ITA).

---

### **Q12: ECA & Language Validity Checklists**

* **Ruling:** **APPROVED AS PROPOSED.**
* **Logic:** Render as informational help text tooltips. Do not block calculation or add complex validation logic to the scoring engine.

---

### **Q13: Spouse "Language Not Applicable"**

* **Ruling:** **APPROVED AS PROPOSED.**
* **Logic:** Provide an option or checkbox for "Spouse did not take an official language test" which assigns 0 points for Section B language.

---

### **Q14: Maximum Test Score Validation**

* **Ruling:** **APPROVED AS PROPOSED.**
* **Logic:** Bound the input fields according to each test's maximum valid score:
* **IELTS:** 0.0 – 9.0 (step 0.5)
* **CELPIP:** 0 – 12
* **PTE Core:** 0 – 90
* **TEF Canada:** 0 – 450 (or relevant section max)
* **TCF Canada:** Speaking/Writing: 0 – 20; Reading/Listening: 0 – 699



---

## 2. Authorization to Proceed

`REQUIREMENTS_ANALYSIS.md` is approved with the adjustments above. You are authorized to begin **Task 2 (Project Scaffold)** and proceed sequentially through Tasks 3–7.