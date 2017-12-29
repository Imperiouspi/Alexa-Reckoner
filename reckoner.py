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

    ## Scrape house points
    # First, get the contents of the <script> that manipulates the
    # house points bar graph. That contains a JS object with the
    # points. Next, use a regex to find (colour, points)
    # pairs. Finally, convert the list of pairs to a dict.
    script = reckonerPage.find(id="mgci-points-wrapper").next_sibling.next_sibling.string
    pointsExtractor = re.compile(r"\"mgci-points-(blue|green|red|yellow)\": ?(\d+)")
    pointsGroups = pointsExtractor.findall(script)
    housePoints = dict(pointsGroups)

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
    featurebox = reckonerPage.find(class_='module featured-posts-slider-module et_pb_extra_module mobile-text et_pb_featured_posts_slider_0 et_pb_bg_layout_dark')[0].div.article.div.div
    title = featurebox.h3.a.contents
    author = featurebox.div.p.a.contents
    date = featurebox.div.p.span.contents
    return statement(render_template("headline", t=title, a=author, d=date))

if __name__ == "__main__":
    app.run(debug=True)
