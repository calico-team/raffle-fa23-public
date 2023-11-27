"""
Creates data/processed/tickets.csv using data/raw/scoreboard.html.

data/processed/tickets.csv is a table that lists the number of tickets won by
each team, and data/raw/scoreboard.html is the scoreboard downloaded directly
from https://calicojudge.com/domjudge/public after the scoreboard has been
unfrozen for the current contest.
"""

from html.parser import HTMLParser
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SCOREBOARD_HTML = PROJECT_ROOT / 'data/raw/scoreboard.html'
REMIX_SCOREBOARD_HTML = PROJECT_ROOT / 'data/raw/remix_scoreboard.html'
tickets_CSV = PROJECT_ROOT / 'data/processed/tickets.csv'

print('Parsing scoreboard.html into tickets.csv...')

# Parse scoreboard html into a dict with tickets for each team
class ScoreboardTicketsParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.tickets = {}
        self.curr_team = None
    
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'td' and 'class' in attrs and 'scoretn' in attrs['class']:
            self.curr_team = attrs['title']
            assert self.curr_team not in self.tickets, 'found a duplicate team: ' + self.curr_team
            self.tickets[self.curr_team] = 0
        if tag == 'div' and 'class' in attrs and 'score_correct' in attrs['class']:
            if self.tickets[self.curr_team] == 0:
                self.tickets[self.curr_team] += 10
            else:
                self.tickets[self.curr_team] += 1
                
# parse regular scoreboard
parser = ScoreboardTicketsParser()
# utf8 because y'all love emojis so much xdddd
parser.feed(SCOREBOARD_HTML.read_text(encoding='utf8'))

#parse remix scoreboard
parser2 = ScoreboardTicketsParser()
parser2.feed(REMIX_SCOREBOARD_HTML.read_text(encoding='utf8'))
parser2.tickets = {k: 2 if v > 0 else 0 for k, v in parser2.tickets.items()}

final_tickets = {k: v + (parser2.tickets[k] if v >= 10 else 0) for k, v in parser.tickets.items()} 

# Load tickets dict into table
tickets = pd.DataFrame.from_records(list(final_tickets.items()))
tickets.columns = ['team_name', 'tickets']
tickets['team_name'] = tickets['team_name'].str.strip()

assert not any(tickets['team_name'].duplicated())

# Make csv from tickets table
tickets.to_csv(tickets_CSV, index=False, lineterminator='\n')

print('Done!')
