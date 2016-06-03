from flask import Flask
from flask_bootstrap import Bootstrap

# Main Application
from views import app


if __name__ == '__main__':
    app.run(debug=False)
