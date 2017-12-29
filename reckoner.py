"""
An Alexa skill to look up content from The Reckoner homepage.
"""

import urllib2

import beautifulsoup
from flask import Flask, render_template
from flask_ask import Ask, statement

app = Flask(__name__)
ask = Ask(app, "/")

reckonerPage = beautifulsoup.BeautifulSoup(urllib2.open("http://thereckoner.ca").read())

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
    featurebox = reckonerPage.find(class_='module featured-posts-slider-module et_pb_extra_module mobile-text et_pb_featured_posts_slider_0 et_pb_bg_layout_dark')[0].div.article.div.div
    title = featurebox.h3.a.contents
    author = featurebox.div.p.a.contents
    date = featurebox.div.p.span.contents
    return statement(render_template("headline", t=title, a=author, d='date'))

if __name__ == "__main__":
    app.run(debug=True)
