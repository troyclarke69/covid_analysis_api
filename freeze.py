from flask_frozen import Freezer
# from myapp import app
from covid_analysis_api import app

freezer = Freezer(app)

if __name__ == '__main__':
    freezer.freeze()
