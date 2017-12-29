"""
An Alexa skill to look up content from The Reckoner homepage.
"""

from flask import Flask, render_template
from flask_ask import Ask, statement

app = Flask(__name__)
ask = Ask(app, "/")

@ask.intent("HousePoints")
def points(house):
    """Return a summary of the house points (or all of them)"""

    if house is None:
        points = {
            "r": 450,
            "g": 450,
            "y": 450,
            "b": 450
        }
        return statement(render_template("points_all", p=points))

    return statement(render_template("points", h=house, p=450))

if __name__ == "__main__":
    app.run(debug=True)
