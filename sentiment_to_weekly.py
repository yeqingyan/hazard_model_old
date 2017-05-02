import DynamicNetwork
import json
import networkx as nx
import time
import datetime
import pickle

WEEK_IN_SECOND = 7 * 24 * 60 * 60

g = DynamicNetwork(
    nx.DiGraph(),
    json.load(open("./sentiment_data/sentiment.json")),
    start_date=int(time.mktime(datetime.datetime.strptime("09/19/2016", "%m/%d/%Y").timetuple())),
    intervals=WEEK_IN_SECOND,
    stop_step=13)
pickle.dump(g.sentiment_data, "sentiment.pickle")
