// Function to fetch asset data from the API
async function fetchUserAssetData() {
  try {
    const response = await fetch('http://127.0.0.1:5000/assets');
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }
    const assetsData = await response.json();
    return assetsData;
  } catch (error) {
    console.error('There has been a problem with your fetch operation:', error);
  }
}

// Function to fetch stock data from the API
async function fetchStockData() {
  try {
    const response = await fetch('http://127.0.0.1:5000/stocks');
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }
    const stocksData = await response.json();
    return stocksData;
  } catch (error) {
    console.error('There has been a problem with your fetch operation:', error);
  }
}

// Function to fetch transaction data from the API
async function fetchTransactionData() {
  try {
    const response = await fetch('http://127.0.0.1:5000/transactions');
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }
    const transactionsData = await response.json();
    return transactionsData;
  } catch (error) {
    console.error('There has been a problem with your fetch operation:', error);
  }
}

// Function to fetch cash account data from the API
async function fetchCashAccountData() {
  try {
    const response = await fetch('http://127.0.0.1:5000/cash_account');
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }
    const cashAccountData = await response.json();
    console.log(cashAccountData)
    return cashAccountData;
  } catch (error) {
    console.error('There has been a problem with your fetch operation:', error);
  }
}

let assetsOverviewChart = null; // Global variable to hold the chart instance

// Function to create a chart of assets overview
async function createAssetsOverviewChart(){
  const ctx = document.getElementById('assetsOverviewChart').getContext('2d');

  if (!ctx) {
    console.error('Canvas element with ID "assetsOverviewChart" not found.');
    return;
  }

  // Destroy the previous chart instance if it exists
  if(assetsOverviewChart){
    assetsOverviewChart.destroy();
  }

  const assetsData = await fetchUserAssetData();

  if(!assetsData) return;

  // Prepare data for the chart
  const labels = assetsData.map(asset => asset.ticker_symbol);
  const data = assetsData.map(asset => asset.total_quantity);

  // Create the chart
  assetsOverviewChart = new Chart(ctx, {
    type: 'bar', // You can change to 'pie', 'doughnut', etc.
    data: {
      labels: labels,
      datasets: [{
        label: 'Asset Quantity',
        data: data,
        backgroundColor: 'rgba(75, 192, 192, 0.2)',
        borderColor: 'rgba(75, 192, 192, 1)',
        borderWidth: 1
      }]
    },

    options: {
      scales: {
        y: {
          beginAtZero: true
        }
      }
    }

  });
}

// Function to display assets along with the chart
async function displayAssets() {
  const assetsDetails = document.getElementById('assetsDetails');
  assetsDetails.innerHTML = '';
  const assetsData = await fetchUserAssetData();

  if (assetsData) {
    // Sort assets alphabetically by ticker symbol
    assetsData.sort((a, b) => a.ticker_symbol.localeCompare(b.ticker_symbol));

    assetsData.forEach(asset => {
      if (asset.asset_type == 'stock') {
        const assetElement = document.createElement('div');
        assetElement.classList.add('asset');
        const infoElement = document.createElement('div');
        infoElement.classList.add('info');
        infoElement.innerHTML = `
          <strong>${asset.company_name} (${asset.ticker_symbol})</strong><br>
          Quantity: ${asset.total_quantity}<br>
          Total Cost: $${asset.total_cost}
        `;

        // Create a share number selector for selling shares
        const sellShareSelector = document.createElement('input');
        sellShareSelector.type = 'number';
        sellShareSelector.min = 1;
        sellShareSelector.value = 1;
        sellShareSelector.classList.add('share-selector');

        // Create a sell button
        const sellButton = document.createElement('button');
        sellButton.textContent = 'Sell';
        sellButton.addEventListener('click', () => {
          const numberOfShares = parseFloat(sellShareSelector.value);
          if (numberOfShares < 1 || !Number.isInteger(numberOfShares)) {
            alert("The operation could not be completed. Please enter a valid number of shares (positive integer).");
          } else if (numberOfShares > asset.total_quantity) {
            alert("You can't perform this sale. You are trying to sell more shares than you own.");
          } else {
            sellStock(asset, numberOfShares); // Call the sellStock function with the asset data and number of shares
          }
        });

        assetElement.appendChild(infoElement);
        assetElement.appendChild(sellShareSelector);
        assetElement.appendChild(sellButton);
        assetsDetails.appendChild(assetElement);
      }
    }
  );
    

    // Create the chart after displaying the assets
    createAssetsOverviewChart();
  }
}

// Function to display cash account details
async function displayCashAccount() {
  const cashAccountDetails = document.getElementById('cashAccountDetails');
  cashAccountDetails.innerHTML = '';
  const cashAccountData = await fetchCashAccountData();

  if (cashAccountData) {
    const accountInfo = `
      <p>Cash Balance: $${cashAccountData.balance}</p>
      <p>Last Updated: ${new Date(cashAccountData.last_updated_timestamp).toLocaleString()}</p>
    `;
    cashAccountDetails.innerHTML = accountInfo;
  }
}

// Function to display stocks
async function displayStocks() {
  const accountDetails = document.getElementById('accountDetails');
  accountDetails.innerHTML = '';
  const stocksData = await fetchStockData();

  if (stocksData) {
    // Sort stocks alphabetically by ticker symbol
    stocksData.sort((a, b) => a.ticker_symbol.localeCompare(b.ticker_symbol));

    stocksData.forEach(stock => {
      const stockElement = document.createElement('div');
      stockElement.classList.add('stock');
      const infoElement = document.createElement('div');
      infoElement.classList.add('info');
      infoElement.innerHTML = `
        <strong>${stock.company_name} (${stock.ticker_symbol})</strong><br>
        Opening Price: $${stock.opening_price}<br>
        Closing Price: $${stock.closing_price}<br>
        Current Price: $${stock.current_price}<br>
        Price Timestamp: ${stock.price_timestamp}
      `;
      // Create a share number selector
      const shareSelector = document.createElement('input');
      shareSelector.type = 'number';
      shareSelector.min = 1;
      shareSelector.value = 1;
      shareSelector.classList.add('share-selector');

      // Create a buy button
      const buyButton = document.createElement('button');
      buyButton.textContent = 'Buy';
      buyButton.addEventListener('click', () => {
        const numberOfShares = parseFloat(shareSelector.value);
        if (numberOfShares < 1 || !Number.isInteger(numberOfShares)) {
          alert("The operation could not be completed. Please enter a valid number of shares (positive integer).");
        } else {
          buyStock(stock, numberOfShares); // Call the buyStock function with the stock data and number of shares
        }
      });

      stockElement.appendChild(infoElement);
      stockElement.appendChild(shareSelector);
      stockElement.appendChild(buyButton);
      accountDetails.appendChild(stockElement);
    });
  }
}

// Function to buy stock
async function buyStock(stock, numberOfShares) {
  const newTransaction = {
    ticker_symbol: stock.ticker_symbol,
    quantity: numberOfShares // Use the validated quantity
  };

  try {
    const response = await fetch('http://127.0.0.1:5000/buy_stock', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(newTransaction)
    });

    const result = await response.json();
    if (response.ok) {
      displayAssets(); // Refresh assets view
      displayTransactionSummary(); // Refresh transactions view
    } else {
      alert(`Error: ${result.message}`);
    }
  } catch (error) {
    console.error('Error:', error);
  }
}

// Function to sell stock
async function sellStock(asset, numberOfShares) {
  const newTransaction = {
    ticker_symbol: asset.ticker_symbol,
    quantity: numberOfShares // Use the validated quantity
  };

  try {
    const response = await fetch('http://127.0.0.1:5000/sell_stock', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(newTransaction)
    });

    const result = await response.json();
    if (response.ok) {
      displayAssets(); // Refresh assets view
      displayTransactionSummary(); // Refresh transactions view
    } else {
      alert(`Error: ${result.message}`);
    }
  } catch (error) {
    console.error('Error:', error);
  }
}

// Function to display transaction summary in transactions view
async function displayTransactionSummary() {
  const recentTransactions = document.getElementById('recentTransactions');
  const totalBuysElement = document.getElementById('totalBuys');
  const totalSellsElement = document.getElementById('totalSells');
  const totalAmountElement = document.getElementById('totalAmount');
  let totalBuys = 0;
  let totalSells = 0;
  let totalAmount = 0;
  recentTransactions.innerHTML = '';
  const transactionsData = await fetchTransactionData();

  if (transactionsData) {
    // Sort transactions by datetime in descending order
    transactionsData.sort((a, b) => new Date(b.transaction_datetime) - new Date(a.transaction_datetime));

    transactionsData.forEach(transaction => {
      const transactionItem = document.createElement('li');
      if (transaction.transaction_type === 'sell') {
        transactionItem.innerHTML = `
          <span>${transaction.transaction_type.toUpperCase()}</span>
          ${transaction.ticker_symbol} - ${transaction.quantity} shares on ${new Date(transaction.transaction_datetime).toLocaleString()}
        `;
      } else {
        transactionItem.innerHTML = `
          <span>${transaction.transaction_type.toUpperCase()}</span>
          ${transaction.ticker_symbol} - ${transaction.quantity} shares @ $${transaction.purchase_price_per_share || transaction.sell_price_per_share} each
          on ${new Date(transaction.transaction_datetime).toLocaleString()}
        `;
      }
      recentTransactions.appendChild(transactionItem);

      if (transaction.transaction_type === 'buy') {
        totalBuys += transaction.quantity;
        totalAmount += parseFloat(transaction.purchase_cost);
      } else if (transaction.transaction_type === 'sell') {
        totalSells += transaction.quantity;
        totalAmount -= parseFloat(transaction.sale_revenue);
      }
    });

    totalBuysElement.textContent = totalBuys;
    totalSellsElement.textContent = totalSells;
    totalAmountElement.textContent = totalAmount.toFixed(2);
  }
}

// Function to show the selected view and hide others
function showView(viewId) {
  const views = document.querySelectorAll('.view');
  views.forEach(view => view.style.display = 'none');
  document.getElementById(viewId).style.display = 'block';
  
  if (viewId === 'assetsOverviewView') {
    displayAssets();
  }

  if (viewId === 'cashAccountView') {
    displayCashAccount();
  }

  if (viewId === 'transactionsView') {
    displayTransactionSummary();
  }

  if (viewId === 'stocksView') {
    displayStocks();
  }
}
// Initialize by showing the assets overview view
document.addEventListener('DOMContentLoaded', () => {
  showView('assetsOverviewView');
});
