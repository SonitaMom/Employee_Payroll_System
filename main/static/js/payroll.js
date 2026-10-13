document.addEventListener("DOMContentLoaded", function () {
    const tableBody = document.getElementById("payrollItemsBody");
    const totalFormsInput = document.getElementById("id_items-TOTAL_FORMS");
    const emptyRowTemplate = document.getElementById("emptyItemRowTemplate");
    const btnAddRow = document.getElementById("btnAddItemRow");

    const empSelect = document.getElementById("id_employee");
    const periodInput = document.getElementById("id_pay_period");

    const basicSalaryEl = document.getElementById("calc_basic_salary");
    const otAmountEl = document.getElementById("calc_ot_amount");
    const netSalaryEl = document.getElementById("calc_net_salary");

    let currentBasic = parseFloat(basicSalaryEl ? basicSalaryEl.dataset.value || 0 : 0) || 0;
    let currentOt = parseFloat(otAmountEl ? otAmountEl.dataset.value || 0 : 0) || 0;

    // Recalculate net salary client-side from Basic + OT + Bonuses/Allowances - Deductions/Tax
    function updateNetSalary() {
        let itemsSum = 0;
        const rows = tableBody ? tableBody.querySelectorAll("tr.item-row") : [];

        rows.forEach(row => {
            const deleteInput = row.querySelector("input[name$='-DELETE']");
            if (deleteInput && deleteInput.value === "true") {
                return; // skipped deleted row
            }

            const typeSelect = row.querySelector("select[name$='-type']");
            const amountInput = row.querySelector("input[name$='-amount']");
            const type = typeSelect ? typeSelect.value : "";
            const amount = parseFloat(amountInput ? amountInput.value : 0) || 0;

            if (type === "Bonus" || type === "Allowance") {
                itemsSum += amount;
            } else if (type === "Deduction" || type === "Tax") {
                itemsSum -= amount;
            }
        });

        const net = currentBasic + currentOt + itemsSum;
        if (netSalaryEl) {
            netSalaryEl.textContent = "$" + net.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });
        }
    }

    // Dynamic Row Addition
    if (btnAddRow && emptyRowTemplate && totalFormsInput && tableBody) {
        btnAddRow.addEventListener("click", function () {
            const formIdx = parseInt(totalFormsInput.value, 10);
            const templateHtml = emptyRowTemplate.innerHTML.replace(/__prefix__/g, formIdx);
            
            // Remove empty placeholder row if present
            const emptyTr = tableBody.querySelector(".empty-items-tr");
            if (emptyTr) {
                emptyTr.remove();
            }

            const tempContainer = document.createElement("tbody");
            tempContainer.innerHTML = templateHtml;
            const newRow = tempContainer.querySelector("tr");

            tableBody.appendChild(newRow);
            totalFormsInput.value = formIdx + 1;
            updateNetSalary();
        });
    }

    // Dynamic Row Deletion with confirmation if row has data
    if (tableBody) {
        tableBody.addEventListener("click", function (e) {
            const btnDelete = e.target.closest(".btn-delete-row");
            if (!btnDelete) return;

            const row = btnDelete.closest("tr.item-row");
            if (!row) return;

            const nameInput = row.querySelector("input[name$='-name']");
            const amountInput = row.querySelector("input[name$='-amount']");
            const nameVal = nameInput ? nameInput.value.trim() : "";
            const amountVal = amountInput ? amountInput.value.trim() : "";

            const hasData = nameVal !== "" || (amountVal !== "" && parseFloat(amountVal) > 0);

            if (hasData) {
                const confirmed = confirm(`Are you sure you want to delete "${nameVal || "this item"}"?`);
                if (!confirmed) {
                    return;
                }
            }

            const deleteInput = row.querySelector("input[name$='-DELETE']");
            const idInput = row.querySelector("input[name$='-id']");

            // If existing DB record, mark DELETE checked/value and hide row
            if (idInput && idInput.value) {
                if (deleteInput) {
                    deleteInput.value = "true";
                    if (deleteInput.type === "checkbox") {
                        deleteInput.checked = true;
                    }
                }
                row.style.display = "none";
            } else {
                // Newly added row in current session
                row.remove();
            }

            updateNetSalary();
        });

        // Listen for changes in row type or amount to update live Net Salary
        tableBody.addEventListener("input", function (e) {
            if (e.target.matches("input[name$='-amount']") || e.target.matches("select[name$='-type']")) {
                updateNetSalary();
            }
        });

        tableBody.addEventListener("change", function (e) {
            if (e.target.matches("select[name$='-type']")) {
                updateNetSalary();
            }
        });
    }

    // Fetch employee data and OT info when employee or period changes (for new payroll or period switch)
    function fetchPayrollCalc() {
        const empId = empSelect ? empSelect.value : "";
        const period = periodInput ? periodInput.value : "";

        if (!empId || !period) return;

        fetch(`/payroll/api/calc/?employee_id=${encodeURIComponent(empId)}&pay_period=${encodeURIComponent(period)}`)
            .then(res => res.json())
            .then(data => {
                if (!data.error) {
                    currentBasic = data.basic_salary || 0;
                    currentOt = data.ot_amount || 0;

                    if (basicSalaryEl) {
                        basicSalaryEl.textContent = "$" + currentBasic.toFixed(2);
                        basicSalaryEl.dataset.value = currentBasic;
                    }
                    if (otAmountEl) {
                        otAmountEl.textContent = "$" + currentOt.toFixed(2) + ` (${data.ot_hours || 0} hrs)`;
                        otAmountEl.dataset.value = currentOt;
                    }
                    updateNetSalary();
                }
            })
            .catch(err => console.error("Error fetching payroll calculation:", err));
    }

    if (empSelect) {
        empSelect.addEventListener("change", fetchPayrollCalc);
    }
    if (periodInput) {
        periodInput.addEventListener("change", fetchPayrollCalc);
    }

    // Initial calculation trigger
    updateNetSalary();
});
