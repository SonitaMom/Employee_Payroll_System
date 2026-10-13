document.addEventListener("DOMContentLoaded", () => {
    const dataElement = document.getElementById("monthly-payment-data");
    let chartData = [];

    if (dataElement && dataElement.textContent.trim()) {
        try {
            chartData = JSON.parse(dataElement.textContent);
        } catch (e) {
            console.error("Failed to parse monthly-payment-data JSON:", e);
        }
    }

    let labels = [];
    let totals = [];

    if (Array.isArray(chartData) && chartData.length > 0) {
        labels = chartData.map(item => item.month || "");
        totals = chartData.map(item => Number(item.total) || 0);
    } else {
        //Dummy data
        labels = ["May", "Jun", "Jul", "Aug", "Sep", "Oct"];
        totals = [16000, 20000, 15000, 22000, 17000, 19000];
    }

    const canvas = document.getElementById("paymentChart");
    if (!canvas) return;

    const ctx = canvas.getContext("2d");

    // Create vibrant primary blue gradient for bars matching reference screenshot
    const gradient = ctx.createLinearGradient(0, 0, 0, 300);
    gradient.addColorStop(0, "#0066FF");
    gradient.addColorStop(1, "#00B0FF");

    new Chart(canvas, {
        type: "bar",
        data: {
            labels: labels,
            datasets: [{
                label: "Payroll ($)",
                data: totals,
                backgroundColor: gradient,
                hoverBackgroundColor: "#0052cc",
                borderRadius: 8,
                borderSkipped: false,
                barPercentage: 0.55,
                categoryPercentage: 0.7,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: "#172033",
                    titleFont: {
                        family: "Inter",
                        size: 13,
                        weight: "600"
                    },
                    bodyFont: {
                        family: "Inter",
                        size: 12
                    },
                    padding: 10,
                    cornerRadius: 8,
                    displayColors: false,
                    callbacks: {
                        label: function (context) {
                            const val = context.parsed.y;
                            return "$" + Number(val).toLocaleString();
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: {
                        display: false,
                        drawBorder: false
                    },
                    ticks: {
                        font: {
                            family: "Inter",
                            size: 12,
                            weight: "500"
                        },
                        color: "#94A3B8"
                    }
                },
                y: {
                    border: {
                        dash: [4, 4],
                        display: false
                    },
                    grid: {
                        color: "#F1F5F9",
                        drawBorder: false
                    },
                    ticks: {
                        font: {
                            family: "Inter",
                            size: 12,
                            weight: "500"
                        },
                        color: "#94A3B8",
                        callback: function (value) {
                            if (value >= 1000) {
                                return "$" + (value / 1000) + "k";
                            }
                            return "$" + value;
                        }
                    }
                }
            }
        }
    });
});