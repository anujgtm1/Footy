import pandas as pd
import matplotlib
import matplotlib.pyplot as pt


pt.style.use('ggplot')
data = pd.read_csv('E0.csv')
# Converting Date string to datestamp
data['Date'] = pd.to_datetime(data['Date'])
# Slice only upto the needed data
data = data.ix[:, :23]
# All data where home team is the seleceted team
home = data[data['HomeTeam'] == 'Leicester']
# All data where away team is the seleceted team
away = data[data['AwayTeam'] == 'Leicester']
columns = ['Div', 'Date', 'HomeTeam', 'AwayTeam', 'FTAG', 'FTHG', 'FTR',
           'HTAG', 'HTHG', 'HTR', 'Referee', 'AS', 'HS', 'AST', 'HST',
           'AF', 'HF', 'AC', 'HC', 'AY', 'HY', 'AR', 'HR']
away.columns = columns
total = pd.concat([home, away])
total.sort_values(by='Date', ascending=True)
total.describe()
