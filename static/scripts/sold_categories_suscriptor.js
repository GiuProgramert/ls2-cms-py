const ctx = document.getElementById("categoriesChart").getContext("2d");

// Ensure earnings and buyersPerCategory are defined and populated with data
const earnings = window.earnings || [];
const buyersPerCategory = window.buyersPerCategory || {};

// Function to generate random colors
const getRandomColor = () =>
  `rgba(${Math.floor(Math.random() * 255)}, ${Math.floor(
    Math.random() * 255
  )}, ${Math.floor(Math.random() * 255)}, 0.5)`;

// Generate random colors for each category
const barColors = Array(window.payments_prices.length)
  .fill()
  .map(getRandomColor);

const categoriesChart = new Chart(ctx, {
  type: "bar",
  data: {
    labels: categories,
    datasets: [
      {
        label: "Monto gastado por categoría",
        data: window.payments_prices,
        backgroundColor: barColors,
        borderColor: barColors.map((color) => color.replace("0.5", "1")),
        borderWidth: 1,
      },
    ],
  },

  options: {
    responsive: true,
    maintainAspectRatio: false, // Allow the chart to resize dynamically
    scales: {
      y: {
        beginAtZero: true,
        title: {
          display: true,
          text: "Monto en $",
        },
      },
    },
    plugins: {
      tooltip: {
        callbacks: {
          label: function (context) {
            // Customize tooltip label
            return `Monto gastado ${context.raw} $`;
          },
        },
      },
      legend: {
        display: true,
        labels: {
          generateLabels: function (chart) {
            const dataset = chart.data.datasets[0];
            return chart.data.labels.map((label, index) => ({
              text: label,
              fillStyle: dataset.backgroundColor[index],
              strokeStyle: dataset.borderColor[index],
              lineWidth: 1,
            }));
          },
        },
      },
    },
  },
});
