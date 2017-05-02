# Pre-processing sentiment data, remove the tweet post to self.
import json

sentiment = json.load(open("../sentiment_data/sentiment.json"))
# for from_id, to_dict in sentiment.items():
#     # Remove tweet post to user itself.
#     to_dict.pop(from_id, None)
#
# json.dump(sentiment, open("strip_sentiment.json", "w"))
print(len(sentiment))