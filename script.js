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
  // Get the assets details container
  const assetsDetails = document.getElementById('assetsDetails');
  // Clear any existing content
  assetsDetails.innerHTML = '';

  // Fetch the asset data from the API
  const assetsData = await fetchUserAssetData();

  // Check if assetsData is not null or undefined
  if (assetsData) {
    assetsData.forEach(asset => {
      // Create a div element for each asset
      const assetElement = document.createElement('div');
      assetElement.classList.add('asset');

      // Create a div for asset information
      const infoElement = document.createElement('div');
      infoElement.classList.add('info');
      infoElement.innerHTML = `
        <strong>${asset.company_name} (${asset.ticker_symbol})</strong><br>
        Quantity: ${asset.total_quantity}
      `;

      // Append the info to the asset element
      assetElement.appendChild(infoElement);
      // Append the asset element to the assets details container
      assetsDetails.appendChild(assetElement);
    });
  }
}

// Function to display stocks
async function displayStocks() {
  // Get the account details container
  const accountDetails = document.getElementById('accountDetails');
  // Clear any existing content
  accountDetails.innerHTML = '';

  // Fetch the stock data from the API
  const stocksData = await fetchStockData();

  // Check if stocksData is not null or undefined
  if (stocksData) {
    stocksData.forEach(stock => {
      // Create a div element for each stock
      const stockElement = document.createElement('div');
      stockElement.classList.add('stock');

      // Create a div for stock information
      const infoElement = document.createElement('div');
      infoElement.classList.add('info');
      infoElement.innerHTML = `
        <strong>${stock.company_name} (${stock.ticker_symbol})</strong><br>
        Opening Price: $${stock.opening_price}<br>
        Closing Price: $${stock.closing_price}<br>
        Current Price: $${stock.current_price}<br>
        Price Timestamp: ${stock.price_timestamp}
      `;

      // Create a buy button
      const buyButton = document.createElement('button');
      buyButton.textContent = 'Buy';

      // Append the info and button to the stock element
      stockElement.appendChild(infoElement);
      stockElement.appendChild(buyButton);
      // Append the stock element to the account details container
      accountDetails.appendChild(stockElement);
    });
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

  // Clear any existing content
  recentTransactions.innerHTML = '';

  // Fetch the transaction data from the API
  const transactionsData = await fetchTransactionData();

  // Check if transactionsData is not null or undefined
  if (transactionsData) {
    transactionsData.forEach(transaction => {
      // Create a list item for each transaction
      const transactionItem = document.createElement('li');
      transactionItem.innerHTML = `
        <span>${transaction.transaction_type.toUpperCase()}</span>
        ${transaction.ticker_symbol} - ${transaction.quantity} shares @ $${transaction.purchase_price_per_share} each
        on ${new Date(transaction.transaction_datetime).toLocaleString()}
      `;

      // Append the transaction item to the recent transactions list
      recentTransactions.appendChild(transactionItem);

      // Update the totals based on transaction type
      if (transaction.transaction_type === 'buy') {
        totalBuys += transaction.quantity;
        totalAmount += parseFloat(transaction.purchase_cost);
      } else if (transaction.transaction_type === 'sell') {
        totalSells += transaction.quantity;
        totalAmount -= parseFloat(transaction.sale_revenue);
      }
    });

    // Update the summary elements with the totals
    totalBuysElement.textContent = totalBuys;
    totalSellsElement.textContent = totalSells;
    totalAmountElement.textContent = totalAmount.toFixed(2);
  }
}

// Function to show the selected view and hide others
function showView(viewId) {
  // Get all view elements
  const views = document.querySelectorAll('.view');
  // Hide all views
  views.forEach(view => view.style.display = 'none');
  // Show the selected view
  document.getElementById(viewId).style.display = 'block';
  
  // If the assets overview view is selected, display assets
  if (viewId === 'assetsOverviewView') {
    displayAssets();
  }

  // If the transactions view is selected, display transaction summary
  if (viewId === 'transactionsView') {
    displayTransactionSummary();
  }

  // If the stocks view is selected, display stocks
  if (viewId === 'stocksView') {
    displayStocks();
  }
}

// Initialize by showing the assets overview view
document.addEventListener('DOMContentLoaded', () => {
  showView('assetsOverviewView');
});
