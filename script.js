document.addEventListener('DOMContentLoaded', () => {
  let jsonData;

  fetch('dummy_data.json')
      .then(response => response.json())
      .then(data => {
          jsonData = data;
          displayJsonContent(jsonData);
          createVolumeChart(jsonData.price_data.volume, jsonData.price_data.timestamp);
      })
      .catch(error => console.error('Error reading JSON file:', error));
});

function displayJsonContent(data) {
  const jsonContent = document.getElementById('jsonContent');
  jsonContent.textContent = JSON.stringify(data, null, 2);
}

function createVolumeChart(volumeData, timestamps) {
  const ctx = document.getElementById('volumeChart').getContext('2d');
  const chart = new Chart(ctx, {
      type: 'line',
      data: {
          labels: timestamps,
          datasets: [{
              label: 'Volume',
              data: volumeData,
              backgroundColor: 'rgba(75, 192, 192, 0.2)',
              borderColor: 'rgba(75, 192, 192, 1)',
              borderWidth: 1
          }]
      },
      options: {
          scales: {
              x: {
                  type: 'time',
                  time: {
                      unit: 'minute'
                  },
                  title: {
                      display: true,
                      text: 'Timestamp'
                  }
              },
              y: {
                  beginAtZero: true,
                  title: {
                      display: true,
                      text: 'Volume'
                  }
              }
          }
      }
  });
}
