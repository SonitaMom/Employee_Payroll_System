document.addEventListener("DOMContentLoaded", function () {
  // 1. Department Donut Chart
  const deptDataEl = document.getElementById("dept-distribution-data");
  if (deptDataEl) {
    const rawDeptData = JSON.parse(deptDataEl.textContent);
    const deptLabels = rawDeptData.map(item => item.name);
    const deptCounts = rawDeptData.map(item => item.count);

    const ctxDept = document.getElementById("deptChart");
    if (ctxDept) {
      // The donut sits in its own box (size set in reports.css), so it stays round.
      ctxDept.parentElement.classList.add("donut-box");

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
          devicePixelRatio: Math.max(window.devicePixelRatio || 1, 2),
          plugins: {
            legend: {
              position: "bottom",
              labels: { font: { size: 12 }, padding: 14 }
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
            borderRadius: 6,
            maxBarThickness: 48   // one month no longer makes one giant bar
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          devicePixelRatio: Math.max(window.devicePixelRatio || 1, 2),
          plugins: {
            legend: { labels: { font: { size: 12 } } }
          },
          scales: {
            y: {
              beginAtZero: true,
              ticks: {
                font: { size: 12 },
                callback: function (val) {
                  return "$" + val.toLocaleString();
                }
              }
            },
            x: { ticks: { font: { size: 12 } } }
          }
        }
      });
    }
  }
});