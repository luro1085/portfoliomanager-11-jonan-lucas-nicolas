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
  
  // Function to display account details based on selected type
  function displayAccount() {
    const accountType = document.getElementById('accountType').value;
    // Get the account details container
    const accountDetails = document.getElementById('accountDetails');
    // Clear any existing content
    accountDetails.innerHTML = '';
  
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
  