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

    def generate_train_data(self, start_date, intervals, stop_step=None):
        # TODO update return value
        """ Generate train data for MLE model

        :param start_date:      Start date in second
        :param intervals:       Interval between each step in seconds
        :param stop_step:       Stop step

        :return:                Train data
        """
        ADOPTED_STEP = "AdoptedStep"
        ADOPTED_NEIGHBORS = "AdoptedNeightbors"
        SENTIMENT = "SENTIMENT"

        num_non_adopters = len(self.network)
        adopted_users = []
        current_date = start_date
        step = 0

        # Build neighbor_info hashmap
        # "AdoptedStep":          This node adopted step in integer. -1 if node never adopted.
        # "AdoptedNeightbors":    A list contains the number of this node's adopted neighbors in every step. Note: If a
        #                         neighbor is adopted in current step, it will not include into the count.
        # "Sentiment":            A list contains the sentiment value in every step.
        # TODO neighbor_info get sentiment data
        neighbor_info = {}
        for n in self.network.nodes():
            neighbor_info[n] = {ADOPTED_STEP: -1, ADOPTED_NEIGHBORS: [0], SENTIMENT: [0]}
        while num_non_adopters > 0:
            new_adopted = set()
            for node in self.network.nodes():
                # Skip the adoptor
                if neighbor_info[node][ADOPTED_STEP] != -1:
                    continue

                if self.user_adopted_time(node) <= current_date:
                    new_adopted.add(node)
                    num_non_adopters -= 1

                # Skip first step, since first step adopted neighbors are always 0
                if step == 0:
                    continue
                adopted_friends = 0
                for friend in self.friends(node, current_date):
                    if self.user_adopted_time(friend) <= current_date:
                        adopted_friends += 1
                neighbor_info[node][ADOPTED_NEIGHBORS].append(self.num_adopted_friends(node, current_date))

            previous = 0
            if len(adopted_users) > 0:
                previous = adopted_users[-1]
            adopted_users.append(len(new_adopted) + previous)
            for n in new_adopted:
                neighbor_info[n][ADOPTED_STEP] = step

            current_date += intervals
            step += 1

            # fill limited weeks/ days (steps)
            if stop_step is not None and step >= stop_step:
                break
        # print('Final step is step {}'.format(step))

        # Generate train data
        train_data_exog = []
        train_data_endog = []
        for node, value in neighbor_info.iteritems():
            # TODO check -1 case, 0 case
            # Adotped user
            if value[ADOPTED_STEP] != -1:
                for _adopted_neighbors, _sentiment_value in zip(value[ADOPTED_NEIGHBORS][1:-1], value[SENTIMENT][1:-1]):
                    train_data_exog.append([1, _adopted_neighbors, _sentiment_value])
                    train_data_endog.append(0)
                # Adopted step
                train_data_exog.append(value[ADOPTED_NEIGHBORS][-1])
                train_data_endog.append(1)
            # Never adopted user
            elif value[ADOPTED_STEP] == -1:
                for _adopted_neighbors, _sentiment_value in zip(value[ADOPTED_NEIGHBORS][1:], value[SENTIMENT][1:]):
                    train_data_exog.append([1, _adopted_neighbors, _sentiment_value])
                    train_data_endog.append(0)

        train_data_exog = DataFrame(train_data_exog, columns=["CONSTANT", "ADOPTED_NEIGHBORS", "SENTIMENT"])
        train_data_endog = Series(train_data_endog, name="ADOPTION")
        print(train_data_exog.head())
        print(train_data_endog.head())
        return (train_data_exog, train_data_endog)