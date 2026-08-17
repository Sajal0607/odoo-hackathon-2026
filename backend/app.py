from flask import Flask

# 1. This initializes your app
app = Flask(__name__)

# 2. This says: When someone visits the home page, show this text
@app.route('/')
def home_page():
    return "<h1>Welcome to our project! It works!</h1>"

# 3. This starts the engine
if __name__ == '__main__':
    app.run()
