// Data for the chart
const data = {
    labels: ['Requested', 'Closed', 'Assigned'],
    datasets: [{
        label: 'Service Requests',
        data: [120, 80, 30], // Example data
        backgroundColor: [
            'rgba(54, 162, 235, 0.7)', // Requested (Blue)
            'rgba(75, 192, 192, 0.7)', // Closed (Green)
            'rgba(255, 99, 132, 0.7)'  // Assigned (Red)
        ],
        borderColor: [
            'rgba(54, 162, 235, 1)',
            'rgba(75, 192, 192, 1)',
            'rgba(255, 99, 132, 1)'
        ],
        borderWidth: 1
    }]
};

// Configuration
const config = {
    type: 'bar',
    data: data,
    options: {
        responsive: true,
        scales: {
            y: {
                beginAtZero: true
            }
        }
    }
};

// Render the chart
const ctx = document.getElementById('serviceChart').getContext('2d');
const serviceChart = new Chart(ctx, config);
