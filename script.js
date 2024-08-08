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

// Function to fetch current prices from the API
async function fetchCurrentPrices() {
  try {
    const response = await fetch('http://127.0.0.1:5000/current_prices');
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }
    const currentPricesData = await response.json();
    console.log(currentPricesData);
    return currentPricesData;
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

// Function to fetch profit/loss data from the API
async function fetchProfitLossData() {
  try {
    const response = await fetch('http://127.0.0.1:5000/profit_loss');
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }
    const profitLossData = await response.json();
    console.log(profitLossData);
    return profitLossData;
  } catch (error) {
    console.error('There has been a problem with your fetch operation:', error);
  }
}


async function getCombinedStockData() {
  const stocksData = await fetchStockData();
  const currentPricesData = await fetchCurrentPrices();

  if (stocksData && currentPricesData) {
    const currentPricesMap = new Map();
    currentPricesData.forEach(priceData => {
      currentPricesMap.set(priceData.ticker_symbol, priceData.current_price);
    });

    const combinedData = stocksData.map(stock => {
      const currentPrice = currentPricesMap.get(stock.ticker_symbol);
      return {
        ...stock,
        current_price: currentPrice !== undefined ? currentPrice : "N/A"
      };
    });

    return combinedData;
  }

  return [];
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
  const profitLossData = await fetchProfitLossData();

  if (assetsData && profitLossData) {
    // Sort assets alphabetically by ticker symbol
    assetsData.sort((a, b) => a.ticker_symbol.localeCompare(b.ticker_symbol));

    // Calculate total gains
    const total_gains = (parseFloat(profitLossData.unrealized_gains) + parseFloat(profitLossData.realized_gains)).toFixed(2);

    // Determine the color class based on the value
    const unrealizedGainsClass = parseFloat(profitLossData.unrealized_gains) >= 0 ? 'positive-change' : 'negative-change';
    const realizedGainsClass = parseFloat(profitLossData.realized_gains) >= 0 ? 'positive-change' : 'negative-change';
    const totalGainsClass = parseFloat(total_gains) >= 0 ? 'positive-change' : 'negative-change';

    // Display overall profit/loss
    const profitLossSummary = document.createElement('div');
    profitLossSummary.classList.add('profit-loss-summary');
    profitLossSummary.innerHTML = `
      <p class="${unrealizedGainsClass}">Unrealized Gains: $${profitLossData.unrealized_gains}</p>
      <p class="${realizedGainsClass}">Realized Gains: $${profitLossData.realized_gains}</p>
      <p class="${totalGainsClass}">Total Gains: $${total_gains}</p><br><br>
      <h3>Your Shares</h3>
    `;
    assetsDetails.appendChild(profitLossSummary);

    assetsData.forEach(asset => {
      if (asset.asset_type === 'stock') {
        const stockDetails = profitLossData.stock_details.find(stock => stock.ticker_symbol === asset.ticker_symbol);
        const changeClass = parseFloat(stockDetails.percentage_value_change_from_cost) >= 0 ? 'positive-change' : 'negative-change';
        const assetElement = document.createElement('div');
        assetElement.classList.add('asset');
        const infoElement = document.createElement('div');
        infoElement.classList.add('info');
        infoElement.innerHTML = `
          <strong>${asset.company_name} (${asset.ticker_symbol})</strong><br>
          Quantity: ${asset.total_quantity}<br>
          Total Cost: $${asset.total_cost}<br>
          Total Market Value: $${stockDetails.total_market_value}<br>
          <p class="${changeClass}">Percentage Change from Cost: <b>${stockDetails.percentage_value_change_from_cost}%</b></p>
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
    });

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
    `;
    cashAccountDetails.innerHTML = accountInfo;
  }

  // Fetch and display recent cash transactions
  const recentCashTransactions = document.getElementById('cashTransactions');
  recentCashTransactions.innerHTML = '';
  const transactionsData = await fetchTransactionData();

  // Filter to only include deposit and withdraw transactions
  const filteredTransactions = transactionsData.filter(a => a.transaction_type === "deposit" || a.transaction_type === "withdrawal");

  // Sort transactions by datetime in descending order
  filteredTransactions.sort((a, b) => new Date(b.transaction_datetime) - new Date(a.transaction_datetime));

  if (transactionsData) {
    filteredTransactions.forEach(transaction => {
      const transactionItem = document.createElement('li');
      if (transaction.transaction_type === 'withdrawal') {
        transactionItem.innerHTML = `
          <span style="font-weight: bold;">WITHDRAW</span>
          –$${transaction.cash_amount} on ${new Date(transaction.transaction_datetime).toLocaleString()}
        `;
      } else if (transaction.transaction_type === 'deposit') {
        transactionItem.innerHTML = `
          <span style="font-weight: bold;">DEPOSIT</span>
          +$${transaction.cash_amount} on ${new Date(transaction.transaction_datetime).toLocaleString()}
        `;
      }
      recentCashTransactions.appendChild(transactionItem);
    });
  }
}

// Function to deposit cash
async function deposit() {
  const amount = parseFloat(document.getElementById('cashAmount').value);
  if (amount <= 0 || isNaN(amount)) {
    alert("Please enter a valid amount to deposit.");
    return;
  }

  try {
    const response = await fetch('http://127.0.0.1:5000/deposit', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ amount: amount })
    });

    const result = await response.json();
    if (response.ok) {
      alert(result.message);
      displayCashAccount(); // Refresh cash account details
    } else {
      alert(`Error: ${result.message}`);
    }
  } catch (error) {
    console.error('Error:', error);
  }
}

// Function to withdraw cash
async function withdraw() {
  const amount = parseFloat(document.getElementById('cashAmount').value);
  if (amount <= 0 || isNaN(amount)) {
    alert("Please enter a valid amount to withdraw.");
    return;
  }

  const cashAccountData = await fetchCashAccountData();
  if (amount > parseFloat(cashAccountData.balance)) {
    alert("Insufficient funds for this withdrawal.");
    return;
  }

  try {
    const response = await fetch('http://127.0.0.1:5000/withdraw', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ amount: amount })
    });

    const result = await response.json();
    if (response.ok) {
      alert(result.message);
      displayCashAccount(); // Refresh cash account details
    } else {
      alert(`Error: ${result.message}`);
    }
  } catch (error) {
    console.error('Error:', error);
  }
}

// Function to filter stocks based on search Input
function filterStocks(){
  const searchQuery = document.getElementById('stockSearchBar').value.toLowerCase();
  const stockElements = document.querySelectorAll('#accountDetails .stock');

  stockElements.forEach(stockElement => {
    const stockName = stockElement.querySelector('.info strong').textContent.toLowerCase();

    if(stockName.includes(searchQuery)){
      stockElement.style.display = 'block';
    }
    else {
      stockElement.style.display = 'none';
    }
  });
}

// Function to display stocks
async function displayStocks() {
  const accountDetails = document.getElementById('accountDetails');
  accountDetails.innerHTML = '';
  const combinedStockData = await getCombinedStockData();

  if (combinedStockData) {
    // Sort stocks alphabetically by ticker symbol
    combinedStockData.sort((a, b) => a.ticker_symbol.localeCompare(b.ticker_symbol));

    combinedStockData.forEach(stock => {
      const stockElement = document.createElement('div');
      stockElement.classList.add('stock');
      const infoElement = document.createElement('div');
      infoElement.classList.add('info');
      infoElement.innerHTML = `
        <strong>${stock.company_name} (${stock.ticker_symbol})</strong><br>
        Opening Price: $${stock.opening_price}<br>
        Closing Price: $${stock.closing_price}<br>
        Current Price: <b> $${stock.current_price}</b> <br>
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
    // Filter to only include buy and sell transactions
    const filteredTransactions = transactionsData.filter(a => a.transaction_type === "sell" || a.transaction_type === "buy");

    // Sort transactions by datetime in descending order
    filteredTransactions.sort((a, b) => new Date(b.transaction_datetime) - new Date(a.transaction_datetime));

    filteredTransactions.forEach(transaction => {
      const transactionItem = document.createElement('li');
      if (transaction.transaction_type === 'sell') {
        transactionItem.innerHTML = `
          <span>${transaction.transaction_type.toUpperCase()}</span>
          ${transaction.ticker_symbol} – ${transaction.quantity} shares on ${new Date(transaction.transaction_datetime).toLocaleString()}
        `;
      } else {
        transactionItem.innerHTML = `
          <span>${transaction.transaction_type.toUpperCase()}</span>
          ${transaction.ticker_symbol} + ${transaction.quantity} shares @ $${transaction.purchase_price_per_share || transaction.sell_price_per_share} each
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

let count = 0;
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
    if (count == 0) {
      displayStocks();
    }
    count++;
  }
}
// Initialize by showing the assets overview view
document.addEventListener('DOMContentLoaded', () => {
  showView('assetsOverviewView');
});
