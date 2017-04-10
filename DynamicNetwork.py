import random
import networkx as nx
from pandas import DataFrame, Series

class DynamicNetwork:
    # Node attribute 'create_time' and edge attribute 'create_time' are different attributes.
    # Node's 'create_time' is the node's adoption time.
    # Edge's 'create_time' is when that edge created.
    ADOPTION_TIME = 'create_time'
    EDGE_CREATE_TIME = 'create_time'

    def __init__(self, g):
        assert isinstance(g, nx.DiGraph), "Network must be instance of DiGraph"
        self.network = g
        self.fake_sentiment = {}

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

    # def adopted_friends(self, node, current_date):
    #     """ Return percentage of adopted friends before current_date """
    #     friends = self.friends(node, current_date)
    #     adopted_friends = 0
    #
    #     for friend in friends:
    #         if self.user_adopted_time(friend) <= current_date:
    #             adopted_friends += 1
    #     # print("adopted friends {}".format(adopted_friends))
    #     return adopted_friends

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
        # TODO fake sentiment data
        if (n, current_date) not in self.fake_sentiment:
            self.fake_sentiment[(n, current_date)] = random.uniform(-1, 1)

        return self.fake_sentiment[(n, current_date)]

    def generate_train_data(self, start_date, intervals, verbose=False):
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
                fake_s = self.sentiment(n, current_date)

                num_adopted_neighbors = 0
                for f in self.friends(n, current_date):
                    if f not in non_adopted:
                        num_adopted_neighbors += 1

                # Demo use
                sentiment = fake_s
                adoption = 0
                if self.user_adopted_time(n) <= current_date:
                    adoption = 1
                    num_adopted += 1
                else:
                    non_adopted_temp.append(n)

                if verbose:
                    print("{:20} {:^4} {:^16} {:^8}".format(n, step, num_adopted_neighbors, adoption))

                real_data[(n, current_date)] = (adoption, num_adopted_neighbors, fake_s)
            non_adopted = non_adopted_temp
            if adopted == []:
                adopted.append(num_adopted)
            else:
                adopted.append(num_adopted + adopted[-1])
            current_date += intervals
            step += 1
        return adopted, real_data