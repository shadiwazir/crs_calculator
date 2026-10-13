(() => {
  const TESTS = window.CRS_TESTS;
  const ABILITIES = ["speaking", "listening", "reading", "writing"];
  const SECTIONS = {
    core: "Core / human capital", spouse: "Spouse / partner",
    transferability: "Skill transferability", additional: "Additional points",
  };
  const ITEM_LABELS = {
    age: "Age", education: "Education", first_language: "First language", second_language: "Second language",
    canadian_work: "Canadian work", language: "Language", foreign_work: "Foreign work",
    certificate: "Certificate", sibling: "Sibling", french: "French", canadian_study: "Canadian study",
    nomination: "Nomination",
  };
  const form = document.getElementById("form");
  const $ = (sel, root = document) => root.querySelector(sel);

  // ---- language blocks -------------------------------------------------------------
  const langBlocks = {};
  document.querySelectorAll("fieldset.lang").forEach((fs) => {
    const key = fs.dataset.lang;
    const block = { fs, test: $("[data-role=test]", fs), scores: $("[data-role=scores]", fs) };
    langBlocks[key] = block;
    block.test.addEventListener("change", () => renderScores(key));
  });

  function fillTestOptions(key) {
    const block = langBlocks[key];
    const first = langBlocks.first_language.test.value;
    const forbid = key === "second_language" && first ? TESTS[first].language : null;
    const current = block.test.value;
    const noneLabel = key === "first_language" ? "Select a test…" : "No test";
    block.test.innerHTML = `<option value="">${noneLabel}</option>` + Object.entries(TESTS)
      .filter(([, t]) => t.language !== forbid)
      .map(([id, t]) => `<option value="${id}">${t.label} (${t.language === "english" ? "English" : "French"})</option>`).join("");
    if ([...block.test.options].some((o) => o.value === current)) block.test.value = current;
  }

  function renderScores(key) {
    const block = langBlocks[key];
    const test = TESTS[block.test.value];
    block.scores.innerHTML = "";
    if (test) {
      ABILITIES.forEach((a) => {
        const [lo, hi] = test.ranges[a];
        const label = document.createElement("label");
        label.innerHTML = `${a[0].toUpperCase() + a.slice(1)}<input type="number" data-ability="${a}" min="${lo}" max="${hi}" step="${test.step}" placeholder="${lo}–${hi}">`;
        block.scores.appendChild(label);
      });
    }
    if (key === "first_language") {
      fillTestOptions("second_language");
      renderScores("second_language");
    }
    schedule();
  }

  function readLanguage(key) {
    const block = langBlocks[key];
    if (!block.test.value) return { empty: true };
    const scores = {};
    for (const input of block.scores.querySelectorAll("input")) {
      if (input.value === "") return { incomplete: true };
      scores[input.dataset.ability] = Number(input.value);
    }
    return { value: { test: block.test.value, scores } };
  }

  // ---- request -----------------------------------------------------------------------
  const val = (name) => form.elements[name].value;
  const checked = (name) => form.elements[name].checked;

  function updateSpouseVisibility() {
    const married = ["married", "common_law"].includes(val("marital_status"));
    $("#spouse-status").hidden = !married;
    const citizen = checked("spouse_is_citizen_or_pr");
    $("#accompanying-row").hidden = citizen;
    const couple = married && !citizen && checked("spouse_accompanying");
    $("#spouse-card").hidden = !couple;
    return couple;
  }

  function buildBody(couple) {
    const first = readLanguage("first_language");
    if (!first.value || val("age") === "" || val("education") === "") return null;
    const second = readLanguage("second_language");
    if (second.incomplete) return null;
    const body = {
      marital_status: val("marital_status"),
      spouse_is_citizen_or_pr: checked("spouse_is_citizen_or_pr"),
      spouse_accompanying: checked("spouse_accompanying"),
      age: Number(val("age")), education: val("education"),
      first_language: first.value, second_language: second.value || null,
      canadian_work_years: Number(val("canadian_work_years")),
      foreign_work_years: Number(val("foreign_work_years")),
      has_certificate_of_qualification: checked("has_certificate_of_qualification"),
      has_provincial_nomination: checked("has_provincial_nomination"),
      has_sibling_in_canada: checked("has_sibling_in_canada"),
      canadian_study: val("canadian_study"),
    };
    if (couple) {
      const lang = readLanguage("spouse_language");
      if (lang.incomplete) return null;
      body.spouse = {
        education: val("spouse_education"),
        canadian_work_years: Number(val("spouse_canadian_work_years")),
        language: lang.value || null,
      };
    }
    return body;
  }

  // ---- render ------------------------------------------------------------------------
  const message = $("#message");
  function showError(text) {
    message.textContent = text;
    message.className = "hint error";
  }

  function render(result) {
    message.textContent = result.scored_as_couple ? "Scored with spouse / common-law partner." : "Scored without a spouse / partner.";
    message.className = "hint";
    $("#total").textContent = result.total;
    $("#breakdown").innerHTML = Object.entries(SECTIONS).filter(([k]) => k !== "spouse" || result.scored_as_couple)
      .map(([key, title]) => {
        const s = result.sections[key];
        const items = Object.entries(s.items).map(([k, v]) => `${ITEM_LABELS[k] || k}: ${v}`).join(" · ");
        return `<li><div class="row"><span>${title}</span><span>${s.total} / ${s.max}</span></div>
          <div class="bar"><div style="width:${Math.min(100, (s.total / s.max) * 100)}%"></div></div>
          <div class="items">${items}</div></li>`;
      }).join("");
  }

  let timer, seq = 0;
  function schedule() { clearTimeout(timer); timer = setTimeout(run, 150); }

  async function run() {
    const couple = updateSpouseVisibility();
    const body = buildBody(couple);
    if (!body) {
      $("#total").textContent = "–";
      $("#breakdown").innerHTML = "";
      message.className = "hint";
      message.textContent = "Fill in age, education and your first-language test to see your score.";
      return;
    }
    const mine = ++seq;
    try {
      const res = await fetch("/api/calculate", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
      const data = await res.json();
      if (mine !== seq) return;
      if (!res.ok) { $("#total").textContent = "–"; $("#breakdown").innerHTML = ""; return showError(data.error); }
      render(data);
    } catch (e) {
      showError("Could not reach the server.");
    }
  }

  form.addEventListener("input", schedule);
  form.addEventListener("change", schedule);
  ["first_language", "second_language", "spouse_language"].forEach((k) => fillTestOptions(k));
  renderScores("first_language");
  renderScores("spouse_language");
  updateSpouseVisibility();
})();
