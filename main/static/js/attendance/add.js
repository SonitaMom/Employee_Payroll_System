(function () {
  const $ = (id) => document.getElementById(id);
  const modal = $("attModal");
  if (!modal) {
    console.error("attModal not found in page");
    return;
  }

  // Style the popup from JS, so no CSS file is needed
  document.body.appendChild(modal);
  Object.assign(modal.style, {
    position: "fixed",
    top: "0",
    right: "0",
    bottom: "0",
    left: "0",
    background: "rgba(0,0,0,.5)",
    display: "none",
    alignItems: "center",
    justifyContent: "center",
    zIndex: "5000",
    padding: "16px",
  });
  const box = modal.querySelector(".att-box");
  Object.assign(box.style, {
    background: "#fff",
    color: "#212529",
    borderRadius: "10px",
    padding: "20px",
    width: "100%",
    maxWidth: "460px",
    maxHeight: "92vh",
    overflow: "auto",
    boxShadow: "0 10px 40px rgba(0,0,0,.3)",
  });

  const form = $("attForm");
  const dept = $("m_dept"),
    emp = $("m_emp");
  const cin = $("m_in"),
    cout = $("m_out"),
    st = $("m_status");
  const ADD_URL = modal.dataset.addUrl;
  const TODAY = modal.dataset.today;

  // Read employees safely
  let employees = [];
  try {
    employees = JSON.parse($("employees-data").textContent);
    if (typeof employees === "string")
      employees = JSON.parse(employees || "[]");
  } catch (e) {
    console.error("employees-data problem:", e);
  }
  if (!Array.isArray(employees)) employees = [];

  const show = () => {
    modal.style.display = "flex";
  };
  const hide = () => {
    modal.style.display = "none";
  };

 function fillEmps(selected) {
  if (!dept.value) {
    emp.innerHTML = '<option value="">Select department first</option>';
    return;
  }
  if (employees.length === 0) {
    emp.innerHTML = '<option value="">No employees received from server</option>';
    return;
  }
  const list = employees.filter(
    (e) => String(e.department_id) === String(dept.value)
  );
  if (list.length === 0) {
    emp.innerHTML =
      '<option value="">No employee has department_id ' + dept.value + "</option>";
    console.log("department_id values in data:",
      [...new Set(employees.map((e) => e.department_id))]);
    return;
  }
  emp.innerHTML = '<option value="">Select employee</option>';
  list.forEach((e) => {
    const o = document.createElement("option");
    o.value = e.employee_id;
    o.textContent = e.employee_id + " - " + e.first_name + " " + e.last_name;
    emp.appendChild(o);
  });
  if (selected) emp.value = selected;
}

  function applyStatus() {
    const off = st.value === "Absent" || st.value === "Leave";
    [cin, cout].forEach((el) => {
      el.disabled = off;
      if (off) el.value = "";
    });
  }

  // Add
  $("btnAdd").addEventListener("click", () => {
    show(); // show FIRST, so it opens even if something below fails
    form.reset();
    form.action = ADD_URL;
    $("m_title").textContent = "Add Attendance";
    $("m_date").textContent = TODAY;
    $("m_auto").hidden = false;
    dept.disabled = emp.disabled = false;
    dept.value = "";
    fillEmps();
    applyStatus();
  });

  // Edit
  document.querySelectorAll("[data-edit]").forEach((btn) => {
    btn.addEventListener("click", () => {
      show();
      const d = btn.dataset;
      form.reset();
      form.action = d.url;
      $("m_title").textContent = "Edit Attendance";
      $("m_date").textContent = d.date;
      $("m_auto").hidden = true;
      dept.value = d.dept;
      fillEmps(d.emp);
      dept.disabled = emp.disabled = true;
      st.value = d.status;
      applyStatus();
      cin.value = d.cin;
      cout.value = d.cout;
    });
  });

  dept.addEventListener("change", () => fillEmps());
  $("m_cancel").addEventListener("click", hide);
  modal.addEventListener("click", (e) => {
    if (e.target === modal) hide();
  });

  document.querySelectorAll("[data-now]").forEach((b) => {
    b.addEventListener("click", () => {
      const n = new Date(),
        p = (x) => String(x).padStart(2, "0");
      $(b.dataset.now).value = p(n.getHours()) + ":" + p(n.getMinutes());
      cin.dispatchEvent(new Event("change"));
    });
  });

  cin.addEventListener("change", () => {
    if (cin.value && st.value !== "Absent" && st.value !== "Leave") {
      st.value = cin.value > "08:15" ? "Leave" : "Present";
    }
  });
  st.addEventListener("change", applyStatus);
})();
