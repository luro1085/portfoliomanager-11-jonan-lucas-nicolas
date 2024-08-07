from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
from decimal import Decimal

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
                asset.total_cost = asset.total_cost + (transaction_price * quantity)
            elif transaction_type == 'sell':
                if asset.total_quantity >= quantity:    
                    asset.total_quantity -= quantity
                    asset.total_cost = asset.total_cost - (transaction_price * quantity)
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
    
    purchase_price = stock.current_price
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
    
    sell_price = stock.current_price
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



if __name__ == '__main__':
    app.run(debug=True)
