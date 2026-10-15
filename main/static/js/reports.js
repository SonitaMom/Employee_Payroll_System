document.addEventListener("DOMContentLoaded", function () {
  // 1. Department Donut Chart
  const deptDataEl = document.getElementById("dept-distribution-data");
  if (deptDataEl) {
    const rawDeptData = JSON.parse(deptDataEl.textContent);
    const deptLabels = rawDeptData.map(item => item.name);
    const deptCounts = rawDeptData.map(item => item.count);

    const ctxDept = document.getElementById("deptChart");
    if (ctxDept) {
      new Chart(ctxDept, {
        type: "doughnut",
        data: {
          labels: deptLabels,
          datasets: [{
            data: deptCounts,
            backgroundColor: ["#3b82f6", "#10b981", "#f59e0b", "#8b5cf6", "#ec4899", "#64748b"],
            borderWidth: 2,
            borderColor: "#ffffff"
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              position: "bottom"
            }
          }
        }
      });
    }
  }

  // 2. Monthly Payroll Trend Bar Chart
  const labelsEl = document.getElementById("month-labels-data");
  const amountsEl = document.getElementById("month-amounts-data");
  if (labelsEl && amountsEl) {
    const labels = JSON.parse(labelsEl.textContent);
    const amounts = JSON.parse(amountsEl.textContent);

    const ctxBar = document.getElementById("monthlyPayrollChart");
    if (ctxBar) {
      new Chart(ctxBar, {
        type: "bar",
        data: {
          labels: labels,
          datasets: [{
            label: "Payroll Expenditure ($)",
            data: amounts,
            backgroundColor: "#2563eb",
            borderRadius: 6
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            y: {
              beginAtZero: true,
              ticks: {
                callback: function (val) {
                  return "$" + val.toLocaleString();
                }
              }
            }
          }
        }
      });
    }
  }
});