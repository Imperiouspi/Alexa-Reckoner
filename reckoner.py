"""
An Alexa skill to look up content from The Reckoner homepage.
"""

import re
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

    housePoints = scrape_points()

    # Normalize house names
    synonyms = {
        "blue house": "blue", "house blue": "blue", "ravenclaw": "blue",
        "green house": "green", "house green": "green", "slytherin": "green",
        "red house": "red", "house red": "red", "gryffindor": "red",
        "yellow house": "yellow", "house yellow": "yellow", "hufflepuff": "yellow"
    }
    if house in ["blue", "green", "red", "yellow"]:
        normHouse = house
    elif house in synonyms:
        normHouse = synonyms[house]
    else:
        house = None

    if house is None:
        return statement(render_template("points_all", p=housePoints))
    else:
        return statement(render_template("points", h=house, p=housePoints[normHouse]))

@ask.intent("Headline")
def headline():
    info = scrape_headline()
    print(info["date"], ' ', info["author"], ' ', info["title"])
    return statement(render_template("info", t=info["title"], a=info["author"], d=info["date"]))

def scrape_points():
    """
    Scrape house points from thereckoner.ca.

    First, get the contents of the <script> that manipulates the house
    points bar graph.  That contains a JS object with the points.
    Next, use a regex to find (colour, points) pairs.  Finally,
    convert the list of pairs to a dict and return.
    """

    script = reckonerPage.find(id="mgci-points-wrapper").next_sibling.next_sibling.string # The <script> containing the points
    pointsExtractor = re.compile(r"\"mgci-points-(blue|green|red|yellow)\": ?(\d+)") # Extractor regex
    pointsGroups = pointsExtractor.findall(script) # Extract points and colour
    return dict(pointsGroups)

def scrape_headline():
    """
    Scrape the headline from thereckoner.ca.

    Returns title, author, and date in a dict.
    """

    featurebox = reckonerPage.find(href="http://www.thereckoner.ca/category/featured-post/")
    date = featurebox.previous_sibling.previous_sibling.string
    author = featurebox.previous_sibling.previous_sibling.previous_sibling.previous_sibling.string
    title = featurebox.parent.parent.previous_sibling.previous_sibling.find("a").string

    return {"date": date, "author": author, "title": title}

if __name__ == "__main__":
    app.run(debug=True)
