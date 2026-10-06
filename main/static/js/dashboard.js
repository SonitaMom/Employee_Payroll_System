const data = JSON.parse(
    document.getElementById("monthly-payment-data").textContent
);

const labels = data.map(item => item.month);
const totals = data.map(item => item.total);

new Chart(document.getElementById("paymentChart"), {
    type: "line",

    data: {
        labels: labels,
        datasets: [{
            label: "Monthly Payment",
            data: totals
        }]
    }
});