import random
import networkx as nx
from Utils.NetworkUtils import *
from DynamicNetwork import DynamicNetwork

class Hazard:
    def __init__(self, g, start_date, intervals, beta):
        """
        :param g:               Network
        :param start_date:      Adoption from start_date
        :param intervals:       Interval between each step in seconds
        """
        assert isinstance(g, DynamicNetwork), "Network must be instance of DynamicNetwork"
        assert len(beta) == 3, "Beta parameters for hazard mode must be 3 float value between 0 and 1"
        self.network = g
        self.start_date = start_date
        self.intervals = intervals
        self.beta = beta

    def hazard(self):
        # TODO fake sentiment value and return it for MLE. Need to replace it with real sentiment value
        # TODO fake adopted time
        fake_data = {}
        fake_step = 0

        b0, b1, b2 = self.beta

        non_adopted = self.network.users()
        adopted = []
        # num_non_adopted = len(non_adopted)
        # dyn_neighbors, total_adopted, _ = self.dynamic_adopted_neighbour_info()
        current_date = self.start_date

        while non_adopted:
            # adopted_in_step =
            non_adopted_temp = []
            num_adopted = 0
            for n in non_adopted:
                fake_s = random.uniform(-1, 1)  # TODO fakevalue
                adopted_possibility = b0 + \
                                     b1 * self.network.adopted_friends_percentage(n, current_date) +\
                                     b2 * fake_s            # TODO fake value
                assert (n, current_date) not in fake_data, "Fatal ERROR, element already exist in fake sentiment"
                u = random.uniform(0, 1)
                if adopted_possibility >= 0 and u <= adopted_possibility:
                    num_adopted += 1
                    fake_data[(n, current_date)] = (1, fake_step, fake_s)
                else:
                    non_adopted_temp.append(n)
                    fake_data[(n, current_date)] = (0, fake_step, fake_s)
            non_adopted = non_adopted_temp
            if adopted == []:
                adopted.append(num_adopted)
            else:
                adopted.append(num_adopted + adopted[-1])
            current_date += self.intervals
            fake_step += 1 # TODO fake step
        return adopted, fake_data     # TODO fake value


