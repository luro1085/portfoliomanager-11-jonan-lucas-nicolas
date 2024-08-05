// Hardcoded JSON data for stocks
const stocksData = [
  {
    "closing_price": "222.08",
    "company_name": "Apple Inc.",
    "current_price": "222.08",
    "opening_price": "222.08",
    "price_timestamp": "2024-08-01T16:00:00",
    "ticker_symbol": "AAPL"
  },
  {
    "closing_price": "186.98",
    "company_name": "Amazon Inc.",
    "current_price": "186.98",
    "opening_price": "186.98",
    "price_timestamp": "2024-08-01T16:00:00",
    "ticker_symbol": "AMZN"
  },
  {
    "closing_price": "64.88",
    "company_name": "Citigroup Inc.",
    "current_price": "64.88",
    "opening_price": "64.88",
    "price_timestamp": "2024-08-01T16:00:00",
    "ticker_symbol": "C"
  },
  {
    "closing_price": "662.67",
    "company_name": "Tesla Inc.",
    "current_price": "662.67",
    "opening_price": "662.67",
    "price_timestamp": "2022-06-15T16:00:00",
    "ticker_symbol": "TSLA"
  }
];

// Hardcoded JSON data for transactions
const transactionsData = [
  {
    "amount": "6626.70",
    "purchase_price": "662.67",
    "quantity": 10,
    "ticker_symbol": "TSLA",
    "transaction_date": "2024-08-01T19:52:06",
    "transaction_id": 1,
    "transaction_type": "buy"
  },
  {
    "amount": "6626.70",
    "purchase_price": "662.67",
    "quantity": 10,
    "ticker_symbol": "TSLA",
    "transaction_date": "2024-08-01T19:55:32",
    "transaction_id": 2,
    "transaction_type": "buy"
  },
  {
    "amount": "324.40",
    "purchase_price": "64.88",
    "quantity": 5,
    "ticker_symbol": "C",
    "transaction_date": "2024-08-01T19:56:11",
    "transaction_id": 3,
    "transaction_type": "buy"
  },
  {
    "amount": "6626.70",
    "purchase_price": "662.67",
    "quantity": 10,
    "ticker_symbol": "TSLA",
    "transaction_date": "2024-08-02T13:26:59",
    "transaction_id": 4,
    "transaction_type": "buy"
  },
  {
    "amount": "2664.96",
    "purchase_price": "222.08",
    "quantity": 12,
    "ticker_symbol": "AAPL",
    "transaction_date": "2024-08-05T14:20:37",
    "transaction_id": 5,
    "transaction_type": "buy"
  }
];

// Function to display account details based on selected type
function displayAccount() {
  // Get the selected account type
  const accountType = document.getElementById('accountType').value;
  // Get the account details container
  const accountDetails = document.getElementById('accountDetails');
  // Clear any existing content
  accountDetails.innerHTML = '';

  // If the selected type is 'stocks', display stock details
  if (accountType === 'stocks') {
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

// Function to show the selected view and hide others
function showView(viewId) {
  // Get all view elements
  const views = document.querySelectorAll('.view');
  // Hide all views
  views.forEach(view => view.style.display = 'none');
  // Show the selected view
  document.getElementById(viewId).style.display = 'block';
  
  // If the assets overview view is selected, display transaction summary
  if (viewId === 'assetsOverviewView') {
    displayTransactionSummary();
  }
}

// Function to display transaction summary in assets overview
function displayTransactionSummary() {
  const recentTransactions = document.getElementById('recentTransactions');
  const totalBuysElement = document.getElementById('totalBuys');
  const totalSellsElement = document.getElementById('totalSells');
  const totalAmountElement = document.getElementById('totalAmount');
  
  let totalBuys = 0;
  let totalSells = 0;
  let totalAmount = 0;

  recentTransactions.innerHTML = '';

  transactionsData.forEach(transaction => {
    // Create a list item for each transaction
    const transactionItem = document.createElement('li');
    transactionItem.innerHTML = `
      <span>${transaction.transaction_type.toUpperCase()}</span>
      ${transaction.ticker_symbol} - ${transaction.quantity} shares @ $${transaction.purchase_price} each
      on ${new Date(transaction.transaction_date).toLocaleString()}
    `;

    // Append the transaction item to the recent transactions list
    recentTransactions.appendChild(transactionItem);

    // Update the totals based on transaction type
    if (transaction.transaction_type === 'buy') {
      totalBuys += transaction.quantity;
      totalAmount += parseFloat(transaction.amount);
    } else if (transaction.transaction_type === 'sell') {
      totalSells += transaction.quantity;
      totalAmount -= parseFloat(transaction.amount);
    }
  });

  // Update the summary elements with the totals
  totalBuysElement.textContent = totalBuys;
  totalSellsElement.textContent = totalSells;
  totalAmountElement.textContent = totalAmount.toFixed(2);
}
