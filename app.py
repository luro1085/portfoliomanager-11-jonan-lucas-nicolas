from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:c0nygre@localhost/portfolio_manager'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# Root route
@app.route('/')
def home():
    return "Welcome to the Stock Portfolio Manager API"

class Stocks(db.Model):
    ticker_symbol = db.Column(db.String(10), primary_key=True)
    company_name = db.Column(db.String(100), nullable=False)
    current_price = db.Column(db.Numeric(10, 2), nullable=False)
    price_timestamp = db.Column(db.DateTime, nullable=False)
    opening_price = db.Column(db.Numeric(10, 2), nullable=False)
    closing_price = db.Column(db.Numeric(10, 2), nullable=False)
    
    
class Transactions(db.Model):
    transaction_id = db.Column(db.Integer, primary_key=True)
    transaction_type = db.Column(db.String(50), nullable=False)
    ticker_symbol = db.Column(db.String(10), db.ForeignKey('stocks.ticker_symbol'))
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    quantity = db.Column(db.Integer, nullable=True)
    purchase_price = db.Column(db.Numeric(10, 2), nullable=True)
    transaction_date = db.Column(db.DateTime, default=datetime.utcnow)
    

class Assets(db.Model):
    asset_id = db.Column(db.Integer, primary_key=True)
    asset_type = db.Column(db.String(50), nullable=False)
    ticker_symbol = db.Column(db.String(10), db.ForeignKey('stocks.ticker_symbol'))
    total_quantity = db.Column(db.Integer, nullable=False)
    purchase_price = db.Column(db.Numeric(10, 2), nullable=False)
    total_value = db.Column(db.Numeric(10, 2), nullable=False)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

@app.route('/stocks', methods=['GET'])
def get_stocks():
    stocks = Stocks.query.all()
    return jsonify([{
        'ticker_symbol': stock.ticker_symbol,
        'company_name': stock.company_name,
        'current_price': str(stock.current_price),
        'price_timestamp': stock.price_timestamp.isoformat(),
        'opening_price': str(stock.opening_price),
        'closing_price': str(stock.closing_price)
    } for stock in stocks])
    
@app.route('/transactions', methods=['GET'])
def get_transaction():
    transactions = Transactions.query.all()
    return jsonify([{
        'transaction_id': transaction.transaction_id,
        'transaction_type': transaction.transaction_type,
        'ticker_symbol': transaction.ticker_symbol,
        'amount': str(transaction.amount),
        'quantity': transaction.quantity,
        'purchase_price': str(transaction.purchase_price),
        'transaction_date': transaction.transaction_date.isoformat()
    } for transaction in transactions])
    
@app.route('/assets', methods=['GET'])
def get_assets():
    assets = Assets.query.all()
    return jsonify([{
        'asset_id': asset.asset_id,
        'asset_type': asset.asset_type,
        'ticker_symbol': asset.ticker_symbol,
        'total_quantity': asset.total_quantity,
        'purchase_price': str(asset.purchase_price),
        'total_value': str(asset.total_value),
        'last_updated': asset.last_updated.isoformat()
    } for asset in assets])

    
def update_assets(ticker_symbol, quantity, purchase_price):
    asset = Assets.query.filter_by(ticker_symbol=ticker_symbol).first()
    
    if asset:
        asset.total_quantity += quantity
        asset.purchase_price = purchase_price
        asset.total_value = asset.total_quantity * asset.purchase_price
    else:
        new_asset = Assets(
            asset_type='stock',
            ticker_symbol=ticker_symbol,
            total_quantity=quantity,
            purchase_price=purchase_price,
            total_value=quantity * purchase_price
        )
        db.session.add(new_asset)
    db.session.commit()
    
@app.route('/buy_stock', methods=['POST'])
def buy_stock():
    data = request.get_json()
    ticker_symbol = data['ticker_symbol']
    quantity = data['quantity']
    
    stock = Stocks.query.filter_by(ticker_symbol=ticker_symbol).first()
    if not stock:
        return jsonify({'message': 'Stock not found'}), 404
    
    purchase_price = stock.current_price
    amount = quantity * purchase_price
    
    transaction = Transactions(
        transaction_type = 'buy',
        ticker_symbol = ticker_symbol,
        amount = amount,
        quantity = quantity,
        purchase_price = purchase_price
    )
    
    db.session.add(transaction)
    db.session.commit()
    
    update_assets(ticker_symbol, quantity, purchase_price)
    
    return jsonify({'message': 'Stock bought successfully', 'purchase_price': str(purchase_price)})

if __name__ == '__main__':
    app.run(debug=True)
