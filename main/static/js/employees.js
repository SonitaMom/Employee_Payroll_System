document.addEventListener("DOMContentLoaded", function () {
  const searchInput = document.getElementById("empSearchInput");
  const deptFilter = document.getElementById("empDeptFilter");
  const statusFilter = document.getElementById("empStatusFilter");
  const rows = document.querySelectorAll(".emp-row");
  const counter = document.getElementById("visibleEmpCount");
  const noMatch = document.getElementById("empNoMatch");

  function filterEmployees() {
    const query = searchInput.value.trim().toLowerCase();
    const dept = deptFilter.value;
    const status = statusFilter.value;
    let visible = 0;

    rows.forEach(function (row) {
      const textMatch = row.textContent.toLowerCase().includes(query);
      const deptMatch = !dept || row.dataset.dept === dept;
      const statusMatch = !status || row.dataset.status === status;

      if (textMatch && deptMatch && statusMatch) {
        row.style.display = "";
        visible++;
      } else {
        row.style.display = "none";
      }
    });

    if (counter) counter.textContent = visible;
    if (noMatch) noMatch.style.display = visible === 0 && rows.length > 0 ? "" : "none";
  }

  if (searchInput) searchInput.addEventListener("input", filterEmployees);
  if (deptFilter) deptFilter.addEventListener("change", filterEmployees);
  if (statusFilter) statusFilter.addEventListener("change", filterEmployees);

  // Modal binding for Add / Edit
  const addBtn = document.getElementById("addEmpBtn");
  const form = document.getElementById("empForm");
  const modalLabel = document.getElementById("empModalLabel");
  const actionInput = document.getElementById("empFormAction");
  const idInput = document.getElementById("empFormId");
  const modalEl = document.getElementById("employeeModal");
  const bsModal = modalEl ? new bootstrap.Modal(modalEl) : null;

  if (addBtn) {
    addBtn.addEventListener("click", function () {
      form.reset();
      actionInput.value = "create";
      idInput.value = "";
      modalLabel.textContent = "Add Employee";
    });
  }

  document.querySelectorAll(".edit-emp-btn").forEach(function (btn) {
    btn.addEventListener("click", function () {
      const row = btn.closest(".emp-row");
      actionInput.value = "update";
      idInput.value = row.dataset.id;
      modalLabel.textContent = "Edit Employee";

      document.getElementById("empFirstName").value = row.dataset.firstName;
      document.getElementById("empLastName").value = row.dataset.lastName;
      document.getElementById("empSex").value = row.dataset.sex;
      document.getElementById("empHireDate").value = row.dataset.hireDate;
      document.getElementById("empPhone").value = row.dataset.phone;
      document.getElementById("empEmail").value = row.dataset.email;
      document.getElementById("empDeptSelect").value = row.dataset.deptId;
      document.getElementById("empPosSelect").value = row.dataset.posId;
      document.getElementById("empStatusSelect").value = row.dataset.status;
      document.getElementById("empAddress").value = row.dataset.address;

      if (bsModal) bsModal.show();
    });
  });
});