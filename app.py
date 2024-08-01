from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:c0nygre@localhost/portfolio_manager'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Stocks(db.Model):
    ticker_symbol = db.Column(db.String(10), primary_key=True)
    company_name = db.Column(db.String(100), nullable=False)
    current_price = db.Column(db.Numeric(10, 2), nullable=False)
    price_timestamp = db.Column(db.DateTime, nullable=False)
    opening_price = db.Column(db.Numeric(10, 2), nullable=False)
    closing_price = db.Column(db.Numeric(10, 2), nullable=False)
    
class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    account_number = db.Column(db.String(20), unique=True, nullable=False)
    balance = db.Column(db.Numeric(12,2), default=0, nullable=False)
    
    def deposit(self, amount):
        if amount <=0 :
            return "Deposit amount must be hreater than zero!"
        
        self.balance += amount
        transaction = Transactions(user_id=self.id, transaction_type='Deposit', amount=amount)
        db.session.add(transaction)
        db.session.commit()
        return f"Deposit of ${amount} successful. New balance: ${self.balance}"
    
    def withdraw(self, amount):
        if amount <=0:
            return "Withdrawal amount must be greater than zero!"
        if amount > self.balance:
            return "Insufficient funds!"
        
        self.balance -= amount
        transaction = Transactions(user_id=self.id, transaction_type='Withdrawal', amount=amount)
        db.session.add(transaction)
        db.session.commit()
        return f"Withdrawal of ${amount} successful. New balance: ${self.balance}"

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
    
@app.route('/deposit', methods=['POST'])
def deposit():
    data = request.json
    account_number = data.get('account_number')
    amount = float(data.get('amount'))
    
    account = Account.query.filter_by(account_number=account_number).first()
    if not account:
        return jsonify({'error': 'Account not found.'}), 404
    
    message = account.deposit(amount)
    return jsonify({'message': message, 'balance': str(account.balance)})


@app.route('/withdraw', methods = ['POST'])
def withdraw():
    data = request.json
    aaccount_number = data.get('account_number')
    amount = float(data.get('amount'))
    
    account = Account.query.filter_by(account_number=account_number).first()
    if not account:
        return jsonify({'error': 'Account not found.'}), 404
    
    message = account.dwithdraw(amount)
    return jsonify({'message': message, 'balance': str(account.balance)})
    
    

if __name__ == '__main__':
    app.run(debug=True)
