document.addEventListener("DOMContentLoaded", function () {
  const searchInput = document.getElementById("deptSearchInput");
  const rows = document.querySelectorAll(".dept-row");
  const noMatch = document.getElementById("deptNoMatch");

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

  const addBtn = document.getElementById("addDeptBtn");
  const form = document.getElementById("deptForm");
  const modalLabel = document.getElementById("deptModalLabel");
  const actionInput = document.getElementById("deptFormAction");
  const idInput = document.getElementById("deptFormId");
  const modalEl = document.getElementById("deptModal");
  const bsModal = modalEl ? new bootstrap.Modal(modalEl) : null;

  if (addBtn) {
    addBtn.addEventListener("click", function () {
      form.reset();
      actionInput.value = "create";
      idInput.value = "";
      modalLabel.textContent = "Add Department";
    });
  }

  document.querySelectorAll(".edit-dept-btn").forEach(function (btn) {
    btn.addEventListener("click", function () {
      const row = btn.closest(".dept-row");
      actionInput.value = "update";
      idInput.value = row.dataset.id;
      modalLabel.textContent = "Edit Department";

      document.getElementById("deptNameInput").value = row.dataset.name;
      document.getElementById("deptDescInput").value = row.dataset.description;

      if (bsModal) bsModal.show();
    });
  });
});