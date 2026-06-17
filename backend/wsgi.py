from app import app
from config import Config

Config.validate()

if __name__ == "__main__":
    app.run()
