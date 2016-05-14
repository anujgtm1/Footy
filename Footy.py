#!/usr/bin/env python
# -*- coding:utf-8 -*-
import MySQLdb as sql
import datetime
import requests
from bs4 import BeautifulSoup


sql_dict = {
        'shots on target': '_SHOTS_TARGET',
        'shots off target': '_SHOTS_NTARGET',
        'possession (%)': '_POS',
        'corners': '_CORNER',
        'offsides': '_OFF',
        'fouls': '_FOUL',
        'yellow cards': '_YELLOW',
        'red cards': '_RED',
        'goal kicks': '_GK',
        'treatments': '_TREAT'
        }


def extractTag(tree, tag, cssClass):
    return [t.extract() for t in tree.findAll(tag, class_=cssClass)]


def get_content_ts(url):
    # Request html from the site using http get
    response = requests.get(url)
    # Parse the response text using html parser and BeautifulSoup library
    soup = BeautifulSoup(response.text, 'html.parser')
    # Select only the require content subtree from the website
    [content] = soup.select('body > div.wrapper > div.content')
    extractTag(content, 'div', 'cal-wrap')
    extractTag(content, 'div', 'star')
    extractTag(content, 'div', 'row mt4 bb bt')
    extractTag(content, 'div', 'cal clear')
    return content


def parseTree(subtree):
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


def fix_date(date):
    if len(date) < 15:
        date = date.strip() + ', 2016'
    date = str(datetime.datetime.
               strptime(str(date).strip(), '%B %d, %Y').date())
    return date


def get_stats(slug):
    res = requests.get('http://www.livescore.com/'+slug)
    soup = BeautifulSoup(res.text, 'html.parser')
    statistics = soup.findAll('div', {'data-id': 'stats'})  # Statistics
    statistics = parseTree(statistics)
    statistics.pop(0)
    return statistics


def scrapAll(url, table):

    # Connect to database
    db = sql.connect('localhost', 'root', 'workingclasshero', 'footy')
    # Create a cursor
    cursor = db.cursor()

    # url(string) is the url from which to scrap all the data
    # table(string) is the name of the table in the database
    data = get_content_ts(url)
    data = parseTree(data)

    cursor.execute('DROP TABLE IF EXISTS {0}'.format(table))
    sql_command = maketable(table)
    cursor.execute(sql_command)

    for x in data:
        data_dict = {}
        print(x)
        if type(x) != list:
            date = fix_date(x)
        if len(x) == 4:
            data_dict['DATE'] = date
            data_dict['HOME_TEAM'] = x[1].strip()
            data_dict['AWAY_TEAM'] = x[3].strip()
            [data_dict['HOME_GOAL'], data_dict['AWAY_GOAL']] = \
                x[2][0].split(' - ')
            stats = get_stats(x[2][1])
            for row in stats:
                string = row[1]
                data_dict['HOME' + sql_dict[string]] = row[0]
                data_dict['AWAY' + sql_dict[string]] = row[2]
            sql_command = ('INSERT INTO {0}'.format(table) + '(' +
                           ', '.join(key for key in data_dict.keys()) + ')' +
                           ' VALUES ' + '(' +
                           ', '.join("'{0}'".format(value) for value in data_dict.values()) +
                           ');')

            cursor.execute(sql_command)
    db.commit()
    cursor.close()
    db.close()
    return


def maketable(table):
    sql_command = ('CREATE TABLE {0} ('
                   'DATE TINYTEXT,'
                   'HOME_TEAM TINYTEXT,'
                   'AWAY_TEAM TINYTEXT,'
                   'HOME_GOAL TINYINT,'
                   'AWAY_GOAL TINYINT,'
                   'HOME_SHOTS_TARGET TINYINT,'
                   'AWAY_SHOTS_TARGET TINYINT,'
                   'HOME_SHOTS_NTARGET TINYINT,'
                   'AWAY_SHOTS_NTARGET TINYINT,'
                   'HOME_POS TINYINT,'
                   'AWAY_POS TINYINT,'
                   'HOME_CORNER TINYINT,'
                   'AWAY_CORNER TINYINT,'
                   'HOME_OFF TINYINT,'
                   'AWAY_OFF TINYINT,'
                   'HOME_FOUL TINYINT,'
                   'AWAY_FOUL TINYINT,'
                   'HOME_YELLOW TINYINT,'
                   'AWAY_YELLOW TINYINT,'
                   'HOME_RED TINYINT,'
                   'AWAY_RED TINYINT,'
                   'HOME_GK TINYINT,'
                   'AWAY_GK TINYINT,'
                   'HOME_TREAT TINYINT,'
                   'AWAY_TREAT TINYINT)').format(table)
    return sql_command

scrapAll('http://www.livescore.com/soccer/england/premier-league/results/all/', 'EPL')
