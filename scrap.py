import requests
from bs4 import BeautifulSoup


# For original match attribute
def parseTreeLink(subtree):
    subtree = [t for t in subtree if t != ' ']
    i = 0
    while i < len(subtree):
        name = getattr(subtree[i], "name", None)
        if name is not None:
            if name == 'a':
                subtree[i].append(subtree[i]['href'])
            subtree[i] = parseTree(subtree[i])
        i += 1
    subtree = [t
               for t in subtree
               if t != ' ' and t != '' and t is not None and t != []]
    if len(subtree) == 1:
        subtree = subtree[0]
    return subtree


def get_content_ts(url):
    # Request html from the site using http get
    response = requests.get(url)
    # Parse the response text using html parser and BeautifulSoup library
    soup = BeautifulSoup(response.text, 'html.parser')
    # Select only the require content subtree from the website
    [content] = soup.select('body > div.wrapper > div.content')
    return content


def extractTag(tree, tag, cssClass):
    return [t.extract() for t in tree.findAll(tag, class_=cssClass)]


def get_score(url):
    content = get_content_ts(url)

    # some not required tags
    extractTag(content, 'div', 'cal-wrap')
    extractTag(content, 'div', 'star')
    extractTag(content, 'div', 'row mt4 bb bt')
    extractTag(content, 'div', 'cal clear')

#    links = content.findAll('a')
#    score = parseTree(content)
#    score[0] = score[0][1]
#    score = score[:-1]
#    score.pop()
    return content


def parseTable(table):
    for row in table.findAll('tr')[1:]:
        col = row.findAll('td')
        rank = col[0].string
        artist = col[1].string
        album = col[2].string
        cover_link = col[3].img['src']
        record = (rank, artist, album, cover_link)
        print "|".join(record)


# This is to be used for each match stats
def parseTree(subtree):
    subtree = [t for t in subtree if t != ' ']
    i = 0
    while i < len(subtree):
        name = getattr(subtree[i], "name", None)
        if name is not None:
            if name == 'span':
                if subtree[i].has_attr('class'):
                    if subtree[i]['class'][0] == 'inc':
                        subtree[i].append(subtree[i]['class'][1])
            subtree[i] = parseTree(subtree[i])
        i += 1
    subtree = [t
               for t in subtree
               if t != ' ' and t != '' and t is not None and t != []]
    if len(subtree) == 1:
        subtree = subtree[0]
    return subtree

score = get_score('http://www.livescore.com/soccer/england/premier-league/')
pscore = parseTreeLink(score)

res = requests.get('http://www.livescore.com/soccer/england/premier-league/liverpool-vs-stoke-city/1-1989032/')
soup = BeautifulSoup(res.text, 'html.parser')

details = soup.findAll('div', {'data-id': 'details'})  # Match Details
details = parseTree(details)
lineup = soup.findAll('div', {'data-id': 'substitutions'})  # Lineups, Formations and substitutions
lineup = parseTree(lineup)
statistics = soup.findAll('div', {'data-id': 'stats'})  # Statistics
statistics = parseTree(statistics)
