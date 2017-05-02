import random
import networkx as nx

class DynamicNetwork:
    # Node attribute 'create_time' and edge attribute 'create_time' are different attributes.
    # Node's 'create_time' is the node's adoption time.
    # Edge's 'create_time' is when that edge created.
    ADOPTION_TIME = 'create_time'
    EDGE_CREATE_TIME = 'create_time'

    def __init__(self, g, sentiment_data={}, start_date=None, intervals = None, stop_step = None):
        assert isinstance(g, nx.DiGraph), "Network must be instance of DiGraph"
        self.network = g
        if sentiment_data == {}:
            self.fake_sentiment = True
            self.sentiment_data = {}
        else:
            """
                Real sentiment data format
                {   "user_id1":
                        {   "timestamp1":   sentimentValue1,
                            "timestamp2":   sentimentValue2
                        }
                    "user_id2":
                        {   "timestamp1":   sentimentValue1,
                            "timestamp2":   sentimentValue2
                        }
                }   
            """
            assert isinstance(intervals, int)
            assert start_date != None
            assert stop_step != None
            self.fake_sentiment = False
            self.start_date = start_date
            self.intervals = intervals
            self.stop_step = stop_step
            self.sentiment_data = self.parse_sentiment_data(sentiment_data)

    def users(self):
        return self.network.nodes()

    def user_adopted_time(self, node):
        # A node's create time is its adopted time.
        return self.network.node[node][self.ADOPTION_TIME]

    def friends(self, node, current_date):
        """ Return Twitter user's friends before the current_date
        A --> B means B is successor in our case it means A retweets B thus B influences A
        This pattern applies to quote reply and mentions

        :param node:                Current node
        :param current_date:        Date
        :return:                    Friends list
        """

        friends = []
        for friend in self.network.successors_iter(node):
            # return friends which edge node->friends was created before the current date
            if (self.network[node][friend][self.EDGE_CREATE_TIME] <= current_date):
                friends.append(friend)
        return friends

    def num_adopted_friends(self, node, current_date):
        """ Return number of adopted friends before current_date """
        friends = self.friends(node, current_date)
        adopted_friends = 0

        for friend in friends:
            if self.user_adopted_time(friend) <= current_date:
                adopted_friends += 1
        return adopted_friends

    def adopted_friends_percentage(self, node, current_date):
        """ Return percentage of adopted friends before current_date """
        friends = self.friends(node, current_date)
        adopted_friends = 0
        total_friends = len(friends)

        if total_friends == 0:
            return 0

        for friend in friends:
            if self.user_adopted_time(friend) <= current_date:
                adopted_friends += 1
        # print("adopted friends {}".format(adopted_friends))
        return adopted_friends / total_friends

    def sentiment(self, n, current_date):
        if self.fake_sentiment:
            # fake sentiment
            if (n, current_date) not in self.sentiment_data:
                self.sentiment_data[(n, current_date)] = random.uniform(-1, 1)
            return self.sentiment_data[(n, current_date)]
        else:
            # real sentiment
            step = self.date_to_step(current_date)
            return self.sentiment_data[n][step]

    def generate_train_data(self, start_date, intervals, verbose=False, stop_step=-1):
        real_data = {}
        step = 0

        # b0, b1, b2 = self.beta

        non_adopted = self.users()
        adopted = []

        current_date = start_date
        if verbose:
            print("{:^20} {:^4} {:^16} {:^8}".format("Node", "Step", "AdoptedNeighbors", "Adoption"))
        while non_adopted:
            non_adopted_temp = []
            num_adopted = 0
            for n in non_adopted:
                sentiment = self.sentiment(n, current_date)

                num_adopted_neighbors = 0
                for f in self.friends(n, current_date):
                    if f not in non_adopted:
                        num_adopted_neighbors += 1

                adoption = 0
                if self.user_adopted_time(n) <= current_date:
                    adoption = 1
                    num_adopted += 1
                else:
                    non_adopted_temp.append(n)

                if verbose:
                    print("{:20} {:^4} {:^16} {:^8}".format(n, step, num_adopted_neighbors, adoption))

                real_data[(n, current_date)] = (adoption, num_adopted_neighbors, sentiment)
            non_adopted = non_adopted_temp
            if adopted == []:
                adopted.append(num_adopted)
            else:
                adopted.append(num_adopted + adopted[-1])
            current_date += intervals
            step += 1
            if stop_step != -1 and step >= stop_step:
                break
        return adopted, real_data

    def parse_sentiment_data(self, raw_data):
        debug = False

        if debug:
            print("start date: {}".format(self.start_date))

        sentiment_data = {}
        for user_id, messages in raw_data.items():
            sentiment_data[user_id] = [0 for _ in range(self.stop_step+1)]
            count = [0 for _ in range(self.stop_step+1)]
            for date, sentiment_value in messages.items():
                step = min(self.stop_step, self.date_to_step(int(date)))
                sentiment_data[user_id][step] += sentiment_value

                if debug:
                    print("{}({}): {}".format(date, step, sentiment_value))

                count[step] += 1

            for step in range(len(sentiment_data[user_id])):
                if count[step] != 0:
                    sentiment_data[user_id][step] = sentiment_data[user_id][step] / count[step]
                else:
                    # if no sentiment in this period use the previous one
                    if step == 0:
                        # this happenes if A post a tweets to hisself/herself
                        continue
                    sentiment_data[user_id][step] = sentiment_data[user_id][step-1]

        if debug:
            for k, v in sentiment_data.items():
                print("{} {}".format(k, v))

        return sentiment_data

    def date_to_step(self, timestamp):
        if timestamp < self.start_date:
            return 0
        return (timestamp - self.start_date) // self.intervals
