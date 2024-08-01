from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route('/home')
def index():
    return "This is the Index Page"

if __name__ == '__main__':
    app.run()