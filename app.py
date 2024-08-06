from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime

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
    current_price = db.Column(db.Numeric(10, 2), nullable=False)
    price_timestamp = db.Column(db.DateTime, nullable=False)
    opening_price = db.Column(db.Numeric(10, 2), nullable=False)
    closing_price = db.Column(db.Numeric(10, 2), nullable=False)
    
    
class Transactions(db.Model):
    transaction_id = db.Column(db.Integer, primary_key=True)
    transaction_type = db.Column(db.String(50), nullable=False)
    ticker_symbol = db.Column(db.String(10), db.ForeignKey('stocks.ticker_symbol'))
    company_name = db.Column(db.String(50), nullable=False)
    purchase_cost = db.Column(db.Numeric(10, 2), nullable=True)
    sale_revenue = db.Column(db.Numeric(10, 2), nullable=True)
    quantity = db.Column(db.Integer, nullable=True)
    purchase_price_per_share = db.Column(db.Numeric(10, 2), nullable=True) # per share
    sell_price_per_share = db.Column(db.Numeric(10, 2), nullable=True) # per share
    transaction_datetime = db.Column(db.DateTime, default=datetime.utcnow)
    #portfolio_value_before = db.Column(db.Numeric(10, 2), nullable=False)
    #portfolio_value_after = db.Column(db.Numeric(10, 2), nullable=True)
    

class Assets(db.Model):
    asset_id = db.Column(db.Integer, primary_key=True)
    asset_type = db.Column(db.String(50), nullable=False)
    ticker_symbol = db.Column(db.String(10), db.ForeignKey('stocks.ticker_symbol'))
    company_name = db.Column(db.String(50), nullable=False)
    total_quantity = db.Column(db.Integer, nullable=False)
    total_cost = db.Column(db.Numeric(10, 2), nullable=False)
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
        'current_price': str(stock.current_price),
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
        #'portfolio_value_before': str(transaction.portfolio_value_before),
        #'portfolio_value_after': str(transaction.portfolio_value_after)
    } for transaction in transactions])
    
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
        'last_updated_timestamp': asset.last_updated_timestamp.isoformat()
    } for asset in assets])


    
def update_assets(ticker_symbol, quantity, transaction_price, transaction_type):
    asset = Assets.query.filter_by(ticker_symbol=ticker_symbol).first()
    
    if asset:
        if transaction_type == 'buy': 
            asset.total_quantity += quantity
            asset.total_cost =  asset.total_cost + (transaction_price * quantity)
        elif transaction_type == 'sell':
            if asset.total_quantity >= quantity:    
                asset.total_quantity -= quantity
                asset.total_cost = asset.total_cost - (transaction_price * quantity)
                if asset.total_quantity == 0:
                    db.session.delete(asset)
        else: 
            return False
        
        #asset.current_total_market_value = asset.total_quantity * transaction_price
        #asset.total_value_change_from_cost = asset.current_total_market_value - asset.total_cost
        #asset.percentage_value_change_from_cost = (asset.total_value_change_from_cost / asset.current_total_market_value) * 100
        
    else:
        if transaction_type == 'buy':
            new_asset = Assets(
                asset_type='stock',
                ticker_symbol=ticker_symbol,
                company_name=Stocks.query.filter_by(ticker_symbol=ticker_symbol).first().company_name,
                total_quantity=quantity,
                total_cost = quantity * transaction_price,
                #current_total_market_value = quantity * transaction_price,
                #total_value_change_from_cost = 0,
                #percentage_value_change_from_cost = 0
            )
            db.session.add(new_asset)
            
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
    
    purchase_price = stock.current_price
    purchase_cost = quantity * purchase_price
    #portfolio_value_before = get_portfolio_value()
    
    transaction = Transactions(
        transaction_type = 'buy',
        ticker_symbol = ticker_symbol,
        company_name = stock.company_name,
        purchase_cost = purchase_cost,
        quantity = quantity,
        purchase_price_per_share = purchase_price,
        #portfolio_value_before = portfolio_value_before,
        #portfolio_value_after = portfolio_value_before + purchase_cost
    )
    
    db.session.add(transaction)
    db.session.commit()
    
    update_assets(ticker_symbol, quantity, purchase_price, 'buy')
    
    return jsonify({'message': 'Stock bought successfully', 'purchase_price': str(purchase_price)})

@app.route('/sell_stock', methods=['POST'])
def sell_stock():
    data = request.get_json()
    ticker_symbol = data['ticker_symbol']
    quantity = data['quantity']
    
    stock = Stocks.query.filter_by(ticker_symbol=ticker_symbol).first()
    if not stock:
        return jsonify({'message': 'Stock not found'}), 404
    
    sell_price = stock.current_price
    sale_revenue = quantity * sell_price
    #portfolio_value_before = get_portfolio_value()
    
    transaction = Transactions(
        transaction_type = 'sell',
        ticker_symbol = ticker_symbol,
        company_name = stock.company_name,
        sale_revenue = sale_revenue,
        quantity = quantity,
        sell_price_per_share = sell_price,
        #portfolio_value_before = portfolio_value_before,
        #portfolio_value_after = portfolio_value_before - sale_revenue
    )
    
    db.session.add(transaction)
    db.session.commit()
    
    if not update_assets(ticker_symbol, quantity, sell_price, 'sell'):
        return jsonify({'message': 'Insufficient quantity to sell'}), 400
    
    return jsonify({'message': 'Stock sold successfully', 'sell_price': str(sell_price)})

if __name__ == '__main__':
    app.run(debug=True)
