"""
An Alexa skill to look up content from The Reckoner homepage.
"""

import urllib.request

import bs4
from flask import Flask, render_template
from flask_ask import Ask, statement

app = Flask(__name__)
ask = Ask(app, "/")

req = urllib.request.Request("http://www.thereckoner.ca/", headers={"User-Agent": "Mozilla/5.0"})
reckonerPage = bs4.BeautifulSoup(urllib.request.urlopen(req).read())

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

@ask.intent("Headline")
def headline():
    date = 0
    author = 0
    title = 0

    featurebox = reckonerPage.find(href="http://www.thereckoner.ca/category/featured-post/")
    date = featurebox.previous_sibling.previous_sibling.string
    author = featurebox.previous_sibling.previous_sibling.previous_sibling.previous_sibling.string
    title = featurebox.parent.parent.previous_sibling.previous_sibling.find("a").string
    print(date, ' ', author, ' ', title)
    return statement(render_template("headline", t=title, a=author, d=date))

if __name__ == "__main__":
    app.run(debug=True)
