from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "Hello from minimal Flask app!"

@app.route('/test')
def test():
    return "Test route works!"

@app.route('/health')
def health():
    return "App is healthy!"

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080) 