/* ========================================================
   Payslips Management & Isolated Print Driver (JS)
   ======================================================== */
document.addEventListener("DOMContentLoaded", function () {
  // 1. Table search filter
  const searchInput = document.getElementById("slipSearchInput");
  const rows = document.querySelectorAll(".slip-row");
  const noMatch = document.getElementById("slipNoMatch");

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

  // 2. High-Fidelity Isolated Print Driver
  function printHtmlSnippet(htmlContent) {
    const oldFrame = document.getElementById("printEngineFrame");
    if (oldFrame) oldFrame.remove();

    const iframe = document.createElement("iframe");
    iframe.id = "printEngineFrame";
    iframe.style.position = "fixed";
    iframe.style.right = "0";
    iframe.style.bottom = "0";
    iframe.style.width = "0";
    iframe.style.height = "0";
    iframe.style.border = "none";
    document.body.appendChild(iframe);

    const doc = iframe.contentWindow.document;
    doc.open();
    doc.write(`
      <!DOCTYPE html>
      <html>
      <head>
        <meta charset="utf-8">
        <title>Salary Payslip</title>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
        <style>
          @page {
            size: A4;
            margin: 15mm;
          }
          body {
            background: #ffffff !important;
            color: #0f172a;
            font-family: system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 0;
          }
          .payslip-invoice {
            max-width: 720px;
            margin: 0 auto;
            padding: 10px;
          }
          .company-logo-text {
            font-weight: 800;
            letter-spacing: 0.5px;
            color: #0f172a;
          }
          .invoice-title {
            color: #2563eb;
            font-weight: 700;
            font-size: 1.25rem;
            letter-spacing: 2px;
            margin: 0.75rem 0;
          }
          .section-heading {
            font-weight: 700;
            font-size: 0.85rem;
            text-transform: uppercase;
            color: #475569;
            border-bottom: 2px solid #e2e8f0;
            padding-bottom: 0.35rem;
            margin-bottom: 0.75rem;
          }
          .net-summary-box {
            background-color: #eff6ff !important;
            border: 1px solid #bfdbfe !important;
            border-radius: 8px;
            padding: 1rem 1.25rem;
            margin-top: 1.5rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            -webkit-print-color-adjust: exact !important;
            print-color-adjust: exact !important;
          }
          .print-slip-page {
            page-break-after: always;
            break-after: page;
            margin-bottom: 2rem;
          }
          .print-slip-page:last-child {
            page-break-after: auto;
            break-after: auto;
          }
        </style>
      </head>
      <body>
        ${htmlContent}
      </body>
      </html>
    `);
    doc.close();

    setTimeout(() => {
      iframe.contentWindow.focus();
      iframe.contentWindow.print();
    }, 300);
  }

  // 3. Print Single Payslip (From Modal Button)
  document.querySelectorAll(".print-single-btn").forEach(function (btn) {
    btn.addEventListener("click", function () {
      const targetId = btn.dataset.target;
      const invoiceEl = document.getElementById(targetId);
      if (invoiceEl) {
        printHtmlSnippet(invoiceEl.outerHTML);
      }
    });
  });

  // 4. Print All Payslips (From Top Button)
  const printAllBtn = document.getElementById("printAllBtn");
  if (printAllBtn) {
    printAllBtn.addEventListener("click", function () {
      const allSlips = document.getElementById("printAllContainer");
      if (allSlips) {
        printHtmlSnippet(allSlips.innerHTML);
      }
    });
  }
});