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
    return statement(render_template("headline", t=info["title"], a=info["author"], d=info["date"]))

@ask.intent("Announcements")
def announcements():
    anDate, anList = scrape_announcements()

    return statement(render_template("announcements", date=anDate, announcements=anList))

@ask.intent("Recent", convert={"n": int})
def recent(n):
    if n is None:
        n = 3
    articles = scrape_latest(n)

    return statement(render_template("recent", articles=articles))

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

def scrape_announcements():
    """
    Scrape the most recent set of announcements from thereckoner.ca.

    Returns the announcements the date and a list of announcements.
    """

    announceTitle = reckonerPage(text=re.compile(r"Announcements"))[0]
    announceBox = announceTitle.parent.parent.parent
    announceLink = announceBox.find(class_="main-post").article.find(class_="post-content").h2.a["href"]

    # Scrape the announcements page
    announceReq = urllib.request.Request(announceLink, headers={"User-Agent": "Mozilla/5.0"})
    announcePage = bs4.BeautifulSoup(urllib.request.urlopen(announceReq).read())

    announceDate = announcePage.find(class_="entry-title").string
    announceTags = announcePage.find_all(class_="et_pb_accordion_item")

    announcements = [{"title": tag.h5.string, "content": tag.div.p.string} for tag in announceTags]

    return announceDate, announcements

def scrape_latest(n):
    """
    Scrape the latest articles from thereckoner.ca.

    n: the number of articles to scrape

    Returns a list of title and date in a dict.
    """

    articlesTitle = reckonerPage(text=re.compile(r"Recent Articles"))[0]
    articlesBox = articlesTitle.parent.parent.parent

    allArticles = articlesBox.find_all("article")

    articles = []
    for num, ar in enumerate(allArticles):
        if num >= n:
            break

        date = ar.div.div.div.span.string
        title = ar.a["title"]

        articles.append({"title": title, "date": date})

    return articles

if __name__ == "__main__":
    app.run(debug=True)
