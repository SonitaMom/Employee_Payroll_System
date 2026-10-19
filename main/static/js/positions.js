document.addEventListener("DOMContentLoaded", function () {
  const searchInput = document.getElementById("posSearchInput");
  const rows = document.querySelectorAll(".pos-row");
  const noMatch = document.getElementById("posNoMatch");

  if (searchInput) {
    searchInput.addEventListener("input", function () {
      const q = searchInput.value.trim().toLowerCase();
      let visible = 0;
      rows.forEach(function (row) {
        const match = row.textContent.toLowerCase().includes(q);
        row.style.display = match ? "" : "none";
        if (match) visible++;
      });
      if (noMatch) noMatch.style.display = visible === 0 && rows.length > 0 ? "" : "none";
    });
  }

  const addBtn = document.getElementById("addPosBtn");
  const form = document.getElementById("posForm");
  const modalLabel = document.getElementById("posModalLabel");
  const actionInput = document.getElementById("posFormAction");
  const idInput = document.getElementById("posFormId");
  const modalEl = document.getElementById("posModal");
  const bsModal = modalEl ? new bootstrap.Modal(modalEl) : null;

  if (addBtn) {
    addBtn.addEventListener("click", function () {
      form.reset();
      actionInput.value = "create";
      idInput.value = "";
      modalLabel.textContent = "Add Position";
    });
  }

  document.querySelectorAll(".edit-pos-btn").forEach(function (btn) {
    btn.addEventListener("click", function () {
      const row = btn.closest(".pos-row");
      actionInput.value = "update";
      idInput.value = row.dataset.id;
      modalLabel.textContent = "Edit Position";

      document.getElementById("posNameInput").value = row.dataset.name;
      document.getElementById("posSalaryInput").value = row.dataset.salary;
      document.getElementById("posOtInput").value = row.dataset.ot;
      document.getElementById("posDescInput").value = row.dataset.description;

      if (bsModal) bsModal.show();
    });
  });
});