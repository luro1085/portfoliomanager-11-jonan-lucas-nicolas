from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
from decimal import Decimal
import yfinance as yf

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:c0nygre@localhost/portfolio_manager'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
CORS(app)


# Root route
@app.route('/')
def home():
    return "Welcome to the Stock Portfolio Manager API"

class Stocks(db.Model):
    ticker_symbol = db.Column(db.String(10), primary_key=True)
    company_name = db.Column(db.String(100), nullable=False)
    price_timestamp = db.Column(db.DateTime, nullable=False)
    opening_price = db.Column(db.Numeric(10, 2), nullable=False)
    closing_price = db.Column(db.Numeric(10, 2), nullable=False)

    
class Transactions(db.Model):
    transaction_id = db.Column(db.Integer, primary_key=True)
    transaction_type = db.Column(db.String(50), nullable=False)
    ticker_symbol = db.Column(db.String(10), db.ForeignKey('stocks.ticker_symbol'))
    company_name = db.Column(db.String(50), nullable=True)
    purchase_cost = db.Column(db.Numeric(10, 2), nullable=True)
    sale_revenue = db.Column(db.Numeric(10, 2), nullable=True)
    quantity = db.Column(db.Integer, nullable=True)
    purchase_price_per_share = db.Column(db.Numeric(10, 2), nullable=True) # per share
    sell_price_per_share = db.Column(db.Numeric(10, 2), nullable=True) # per share
    transaction_datetime = db.Column(db.DateTime, default=datetime.utcnow)
    cash_amount = db.Column(db.Numeric(12, 2), nullable=True)
    #portfolio_value_before = db.Column(db.Numeric(10, 2), nullable=False)
    #portfolio_value_after = db.Column(db.Numeric(10, 2), nullable=True)
    
class CashAccount(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    balance = db.Column(db.Numeric(12, 2), default=0, nullable=False)
    
    def deposit(self, amount):
        if amount <= 0:
            return "Deposit amount must be greater than zero!"
        
        self.balance += Decimal(amount)
        transaction = Transactions(transaction_type='deposit', cash_amount=amount)
        db.session.add(transaction)
        db.session.commit()
        update_assets(None, None, None, 'deposit', amount)
        return f"Deposit of ${amount} successful. New balance: ${self.balance}"
    
    def withdraw(self, amount):
        if amount <= 0:
            return "Withdrawal amount must be greater than zero!"
        if amount > self.balance:
            return "Insufficient funds!"
        
        self.balance -= Decimal(amount)
        transaction = Transactions(transaction_type='withdrawal', cash_amount=amount)
        db.session.add(transaction)
        db.session.commit()
        update_assets(None, None, None, 'withdrawal', amount)
        return f"Withdrawal of ${amount} successful. New balance: ${self.balance}"

class Assets(db.Model):
    asset_id = db.Column(db.Integer, primary_key=True)
    asset_type = db.Column(db.String(50), nullable=False)
    ticker_symbol = db.Column(db.String(10), db.ForeignKey('stocks.ticker_symbol'))
    company_name = db.Column(db.String(50), nullable=True)
    total_quantity = db.Column(db.Integer, nullable=True)
    total_cost = db.Column(db.Numeric(10, 2), nullable=True)
    cash_balance = db.Column(db.Numeric(10, 2), nullable=True)
    #current_total_market_value = db.Column(db.Numeric(10, 2), nullable=False)
    #total_value_change_from_cost = db.Column(db.Numeric(10, 2), nullable=False) 
    #percentage_value_change_from_cost = db.Column(db.Numeric(10, 2), nullable=False)
    last_updated_timestamp = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

@app.route('/stocks', methods=['GET'])
def get_stocks():
    stocks = Stocks.query.all()
    return jsonify([{
        'ticker_symbol': stock.ticker_symbol,
        'company_name': stock.company_name,
        'price_timestamp': stock.price_timestamp.isoformat(),
        'opening_price': str(stock.opening_price),
        'closing_price': str(stock.closing_price)
    } for stock in stocks])
    
@app.route('/transactions', methods=['GET'])
def get_transactions():
    transactions = Transactions.query.all()
    return jsonify([{
        'transaction_id': transaction.transaction_id,
        'transaction_type': transaction.transaction_type,
        'ticker_symbol': transaction.ticker_symbol,
        'company_name': transaction.company_name,
        'purchase_cost': str(transaction.purchase_cost),
        'sale_revenue': str(transaction.sale_revenue),
        'quantity': transaction.quantity,
        'purchase_price_per_share': str(transaction.purchase_price_per_share),
        'sell_price_per_share': str(transaction.sell_price_per_share),
        'transaction_datetime': transaction.transaction_datetime.isoformat(),
        'cash_amount': str(transaction.cash_amount)
        #'portfolio_value_before': str(transaction.portfolio_value_before),
        #'portfolio_value_after': str(transaction.portfolio_value_after)
    } for transaction in transactions])
    
@app.route('/cash_account', methods=['GET'])
def get_cash_account():
    cash_account = CashAccount.query.first()
    if not cash_account:
        return jsonify({'message': 'Cash account not found.'}), 404
    
    return jsonify({
        'cash_account_id': cash_account.id,
        'balance': str(cash_account.balance),
    })
    
@app.route('/assets', methods=['GET'])
def get_assets():
    assets = Assets.query.all()
    return jsonify([{
        'asset_id': asset.asset_id,
        'asset_type': asset.asset_type,
        'ticker_symbol': asset.ticker_symbol,
        'company_name': asset.company_name,
        'total_quantity': asset.total_quantity,
        'total_cost': str(asset.total_cost),
        #'current_total_market_value': str(asset.current_total_market_value),
        #'total_value_change_from_cost': str(asset.total_value_change_from_cost),
        #'percentage_value_change_from_cost': str(asset.percentage_value_change_from_cost),
        'last_updated_timestamp': asset.last_updated_timestamp.isoformat(),
        'cash_balance': asset.cash_balance
        
    } for asset in assets])


    
def update_assets(ticker_symbol, quantity, transaction_price, transaction_type, cash_amount=None):
    if ticker_symbol:
        asset = Assets.query.filter_by(ticker_symbol=ticker_symbol).first()
        
        if asset:
            if transaction_type == 'buy': 
                asset.total_quantity += quantity
                asset.total_cost = asset.total_cost + (Decimal(transaction_price) * quantity)
            elif transaction_type == 'sell':
                if asset.total_quantity >= quantity:    
                    asset.total_quantity -= quantity
                    asset.total_cost = asset.total_cost - (Decimal(transaction_price) * quantity)
                    if asset.total_quantity == 0:
                        db.session.delete(asset)
            else: 
                return False
        else:
            if transaction_type == 'buy':
                new_asset = Assets(
                    asset_type='stock',
                    ticker_symbol=ticker_symbol,
                    company_name=Stocks.query.filter_by(ticker_symbol=ticker_symbol).first().company_name,
                    total_quantity=quantity,
                    total_cost=quantity * transaction_price
                )
                db.session.add(new_asset)
            else:
                return False
    else:
        asset = Assets.query.filter_by(asset_type='cash').first()
        if transaction_type == 'deposit':
            if asset:
                asset.cash_balance = (asset.cash_balance or Decimal(0)) + Decimal(cash_amount)
            else:
                new_asset = Assets(
                    asset_type='cash',
                    cash_balance=Decimal(cash_amount),
                )
                db.session.add(new_asset)
        elif transaction_type == 'withdrawal':
            if asset and asset.cash_balance >= Decimal(cash_amount):
                asset.cash_balance -= Decimal(cash_amount)
            else:
                return False

    db.session.commit()
    return True

    
    
def get_portfolio_value():
    assets = Assets.query.all()
    total_value = sum([asset.current_total_market_value for asset in assets])
    return total_value
    
@app.route('/buy_stock', methods=['POST'])
def buy_stock():
    data = request.get_json()
    ticker_symbol = data['ticker_symbol']
    quantity = data['quantity']
    
    stock = Stocks.query.filter_by(ticker_symbol=ticker_symbol).first()
    if not stock:
        return jsonify({'message': 'Stock not found'}), 404
    
    stock_info = yf.Ticker(ticker_symbol)

    
    purchase_price = stock_info.info.get('currentPrice')
    purchase_cost = quantity * purchase_price
    
    cash_account = CashAccount.query.first()
    if not cash_account or cash_account.balance < purchase_cost:
        return jsonify({'message': 'Insufficient funds to buy the stock'}), 400

    transaction = Transactions(
        transaction_type = 'buy',
        ticker_symbol = ticker_symbol,
        company_name = stock.company_name,
        purchase_cost = purchase_cost,
        quantity = quantity,
        purchase_price_per_share = purchase_price,
    )
    
    db.session.add(transaction)
    db.session.commit()
    
    update_assets(ticker_symbol, quantity, purchase_price, 'buy')
    cash_account.withdraw(purchase_cost)
    
    return jsonify({'message': 'Stock bought successfully', 'purchase_price': str(purchase_price)})

@app.route('/sell_stock', methods=['POST'])
def sell_stock():
    data = request.get_json()
    ticker_symbol = data['ticker_symbol']
    quantity = data['quantity']
    
    stock = Stocks.query.filter_by(ticker_symbol=ticker_symbol).first()
    if not stock:
        return jsonify({'message': 'Stock not found'}), 404
    
    stock_info = yf.Ticker(ticker_symbol)
    
    sell_price = stock_info.info.get('currentPrice')
    sale_revenue = quantity * sell_price
    
    asset = Assets.query.filter_by(ticker_symbol=ticker_symbol).first()
    if not asset or asset.total_quantity < quantity:
        return jsonify({'message': 'Insufficient quantity to sell'}), 400
    
    update_assets(ticker_symbol, quantity, sell_price, 'sell')
    
    cash_account = CashAccount.query.first()
    if not cash_account:
        cash_account = CashAccount(balance=0)
        db.session.add(cash_account)
        db.session.commit()
    
    cash_account.deposit(sale_revenue)
    db.session.commit()
    
    transaction = Transactions(
        transaction_type='sell',
        ticker_symbol=ticker_symbol,
        company_name=stock.company_name,
        sale_revenue=sale_revenue,
        quantity=quantity,
        sell_price_per_share=sell_price,
        transaction_datetime=datetime.utcnow()
    )
    
    db.session.add(transaction)
    db.session.commit()
    
    return jsonify({'message': 'Stock sold successfully', 'sell_price': str(sell_price), 'new_balance': str(cash_account.balance)})

@app.route('/deposit', methods=['POST'])
def deposit():
    data = request.json
    amount = float(data.get('amount'))
    
    cash_account = CashAccount.query.first()
    if not cash_account:
        cash_account = CashAccount(balance=0)
        db.session.add(cash_account)
        db.session.commit()
    
    message = cash_account.deposit(amount)
    return jsonify({'message': message, 'balance': str(cash_account.balance)})


@app.route('/withdraw', methods=['POST'])
def withdraw():
    data = request.json
    amount = float(data.get('amount'))
    
    cash_account = CashAccount.query.first()
    if not cash_account:
        return jsonify({'error': 'Cash account not found.'}), 404
    
    message = cash_account.withdraw(amount)
    return jsonify({'message': message, 'balance': str(cash_account.balance)})

@app.route('/current_prices', methods=['GET'])
def get_current_prices():
    sp500_tickers = [
    "A", "AAL", "AAP", "AAPL", "ABBV", "ABT", "ACN", "ADBE", "ADI", "ADM", "ADP", "ADSK", "AEE", "AEP", "AES", "AFL", 
    "AIG", "AIZ", "AJG", "AKAM", "ALB", "ALGN", "ALK", "ALL", "ALLE", "AMAT", "AMCR", "AMD", "AME", "AMGN", "AMP", 
    "AMT", "AMZN", "ANET", "ANSS", "AON", "AOS", "APA", "APD", "APH", "APTV", "ARE", "ATO", "AVB", "AVGO", "AVY", 
    "AWK", "AXP", "AZO", "BA", "BAC", "BAX", "BBWI", "BBY", "BDX", "BEN", "BIIB", "BIO", "BK", "BKNG", "BKR", "BLK", 
    "BMY", "BR", "BRO", "BSX", "BWA", "BX", "C", "CAG", "CAH", "CARR", "CAT", "CB", "CBOE", "CBRE", "CCI", "CCL",
    "CDNS", "CDW", "CE", "CEG", "CF", "CFG", "CHD", "CHRW", "CHTR", "CI", "CINF", "CL", "CLX", "CMA", 
    "CMCSA", "CME", "CMG", "CMI", "CMS", "CNC", "CNP", "COF", "COO", "COP", "COST", "CPB", "CPRT", "CPT", "CRL", 
    "CRM", "CSCO", "CSX", "CTAS", "CTLT", "CTRA", "CTSH", "CTVA", "CVS", "CVX", "D", "DAL", "DD", "DE", "DELL", 
    "DFS", "DG", "DGX", "DHI", "DHR", "DIS", "DLR", "DLTR", "DOV", "DOW", "DPZ", "DRI", "DTE", "DUK", "DVA", "DVN", 
    "DXC", "DXCM", "EA", "EBAY", "ECL", "ED", "EFX", "EIX", "EL", "EMN", "EMR", "ENPH", "EOG", "EPAM", "EQIX", 
    "EQR", "ES", "ESS", "ETN", "ETR", "EVRG", "EW", "EXC", "EXPD", "EXPE", "EXR", "F", "FANG", "FAST", "FCX", "FDS", 
    "FDX", "FE", "FFIV", "FIS", "FITB", "FLR", "FLS", "FMC", "FOX", "FOXA", "FRT", "FTI", "FTNT", "FTV", "GD", "GE", 
    "GILD", "GIS", "GL", "GLW", "GM", "GNRC", "GOOG", "GOOGL", "GPC", "GPN", "GPS", "GRMN", "GS", "GWW", "HAL", 
    "HAS", "HBAN", "HBI", "HCA", "HCI", "HIG", "HII", "HLT", "HOLX", "HON", "HPE", "HPQ", "HRL", "HSIC", "HST", 
    "HSY", "HUM", "HWM", "IBM", "ICE", "IDXX", "IEX", "IFF", "ILMN", "INCY", "INTC", "INTU", "IP", "IPG", "IPGP", 
    "IQV", "IR", "IRM", "ISRG", "IT", "ITW", "IVZ", "J", "JBHT", "JCI", "JKHY", "JNJ", "JNPR", "JPM", "K", "KEY", 
    "KEYS", "KHC", "KIM", "KLAC", "KMB", "KMI", "KMX", "KO", "KR", "KSS", "L", "LDOS", "LEG", "LEN", "LH", "LHX", 
    "LIN", "LKQ", "LLY", "LMT", "LNC", "LNT", "LOW", "LRCX", "LUMN", "LUV", "LYB", "MA", "MAA", "MAR", "MAS", 
    "MCD", "MCHP", "MCK", "MCO", "MDT", "MET", "META", "MGM", "MHK", "MKC", "MKTX", "MLM", "MMC", "MMM", "MNST", 
    "MO", "MOS", "MPC", "MPWR", "MRK", "MRO", "MS", "MSCI", "MSFT", "MSI", "MTB", "MTD", "MU", "NCLH", "NDAQ", 
    "NDSN", "NEE", "NEM", "NFLX", "NI", "NKE", "NOC", "NOV", "NRG", "NSC", "NTAP", "NTRS", "NUE", "NVDA", "NVR", 
    "NWL", "NWS", "NWSA", "O", "ODFL", "OKE", "OMC", "ORCL", "ORLY", "OTIS", "OXY", "PAYC", "PAYX", "PCAR", "PEG", 
    "PEP", "PFE", "PFG", "PG", "PGR", "PH", "PHM", "PKG", "PLD", "PLTR", "PM", "PNC", "PNR", "PNW", "POOL", "PPG", 
    "PPL", "PRGO", "PRU", "PSA", "PSX", "PTC", "PVH", "PWR", "PYPL", "QCOM", "QRVO", "RCL", "REG", "REGN", "RF", 
    "RHI", "RJF", "RL", "RMD", "ROK", "ROL", "ROP", "ROST", "RSG", "RTX", "SBAC", "SBUX", "SCHW", "SEE", "SHW", 
    "SJM", "SLB", "SNA", "SNPS", "SO", "SPG", "SPGI", "SRE", "STE", "STT", "STX", "STZ", "SWK", "SWKS", "SYF", 
    "SYK", "SYY", "T", "TAP", "TDG", "TDY", "TECH", "TEL", "TER", "TFC", "TFX", "TGNA", "TGT", "TJX", "TMO", "TMUS", 
    "TPR", "TRMB", "TROW", "TRV", "TSCO", "TSLA", "TSN", "TT", "TTWO", "TXN", "TXT", "TYL", "UA", "UAL", "UDR", 
    "UHS", "ULTA", "UNH", "UNM", "UNP", "UPS", "URI", "USB", "V", "VFC", "VLO", "VMC", "VNO", "VRSK", "VRSN", 
    "VRTX", "VTR", "VTRS", "VZ", "WAB", "WAT", "WBA", "WDC", "WEC", "WELL", "WFC", "WHR", "WM", "WMB", "WMT", 
    "WRB", "WST", "WY", "WYNN", "XEL", "XOM", "XRAY", "XYL", "YUM", "ZBH", "ZBRA", "ZION", "ZTS"
]

    prices = []
    for ticker in sp500_tickers:
        stock = yf.Ticker(ticker)
        current_price = stock.info.get('currentPrice')
        if current_price:
            prices.append({'ticker_symbol': ticker, 'current_price': current_price})
    
    return jsonify(prices)

if __name__ == '__main__':
    app.run(debug=True)
