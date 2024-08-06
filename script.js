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

// Function to display assets
async function displayAssets() {
  const assetsDetails = document.getElementById('assetsDetails');
  assetsDetails.innerHTML = '';
  const assetsData = await fetchUserAssetData();

  if (assetsData) {
    assetsData.forEach(asset => {
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
        const numberOfShares = sellShareSelector.value;
        sellStock(asset, numberOfShares); // Call the sellStock function with the asset data and number of shares
      });

      assetElement.appendChild(infoElement);
      assetElement.appendChild(sellShareSelector);
      assetElement.appendChild(sellButton);
      assetsDetails.appendChild(assetElement);
    });
  }
}

// Function to display stocks
async function displayStocks() {
  const accountDetails = document.getElementById('accountDetails');
  accountDetails.innerHTML = '';
  const stocksData = await fetchStockData();

  if (stocksData) {
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
        const numberOfShares = shareSelector.value;
        buyStock(stock, numberOfShares); // Call the buyStock function with the stock data and number of shares
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
    quantity: parseInt(numberOfShares) // Ensure the quantity is an integer
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
    quantity: parseInt(numberOfShares) // Ensure the quantity is an integer
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
      transactionItem.innerHTML = `
        <span>${transaction.transaction_type.toUpperCase()}</span>
        ${transaction.ticker_symbol} - ${transaction.quantity} shares @ $${transaction.purchase_price_per_share || transaction.sell_price_per_share} each
        on ${new Date(transaction.transaction_datetime).toLocaleString()}
      `;
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
