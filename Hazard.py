import random
from Utils.NetworkUtils import *
from DynamicNetwork import DynamicNetwork
from scipy import stats
import numpy as np

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

    def hazard(self, verbose=False):
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

        if verbose:
            print("{:^20} {:^4} {:^16} {:^19} {:^6} {:^8}".format("Node", "Step", "AdoptedNeighbors", "AdoptionPossibility", "Random", "Adoption"))
        while non_adopted:
            # adopted_in_step =
            non_adopted_temp = []
            num_adopted = 0
            for n in non_adopted:
                fake_s = random.uniform(-1, 1)  # TODO fakevalue
                # print("beta {}".format(self.beta))
                # print("all friends {}".format(len(self.network.friends(n, current_date))))
                # print("fake s {}".format(fake_s))
                num_adopted_neighbors = 0
                for f in self.network.friends(n, current_date):
                    if f not in non_adopted:
                        num_adopted_neighbors += 1

                factors = [1, num_adopted_neighbors, fake_s]
                adopted_possibility = stats.norm.cdf(np.dot(factors, self.beta))

                # if num_adopted_neighbors != 0:
                #     print("Node {} Week {}, adopted neighbors {} Adoption Possibility {:.5f}, got {:.5f}, Adopted".format(n, current_date, num_adopted_neighbors, adopted_possibility, u))
                # # print("friends_factor {}".format(friends_factor))
                # if friends_factor != 0:
                #     adopted_possibility += b1 * friends_factor + b2 * fake_s            # TODO fake value
                # assert (n, current_date) not in fake_data, "Fatal ERROR, element already exist in fake sentiment"
                u = random.uniform(0, 1)
                # print("adoption possibility {}, random {}".format(adopted_possibility, u))
                if adopted_possibility >= 0 and u <= adopted_possibility:
                    adoption = 1
                    num_adopted += 1
                else:
                    adoption = 0
                    non_adopted_temp.append(n)

                if verbose:
                    print("{:20} {:^4} {:^16} {:^19.3f} {:^6.3f} {:^8}".format(n, fake_step, num_adopted_neighbors, adopted_possibility, u, adoption))
                    # print(
                    #     "Node {}, neighobrs {} adopted neighbors {} Adopted".format(
                    #         n, self.network.friends(n, current_date), num_adopted_neighbors))
                    # print("Node {} Week {}, adopted neighbors {} Adoption Possibility {:.5f}, got {:.5f}, Adopted".format(n, current_date, num_adopted_neighbors, adopted_possibility, u))

                fake_data[(n, current_date)] = (adoption, num_adopted_neighbors, fake_s)
                # else:
                    # print(
                    #     "Node {}, neighobrs {} adopted neighbors {} Not Adopted".format(
                    #         n, self.network.friends(n, current_date), num_adopted_neighbors))
                    #
                    # print("Node {} week {} adopted neighbors {} Adoption Possibility {:.5f}, got {:.5f}, Not Adopted".format(n, current_date, num_adopted_neighbors, adopted_possibility, u))

                    # fake_data[(n, current_date)] = (0, num_adopted_neighbors, fake_s)
            non_adopted = non_adopted_temp
            if adopted == []:
                adopted.append(num_adopted)
            else:
                adopted.append(num_adopted + adopted[-1])
            current_date += self.intervals
            fake_step += 1 # TODO fake step
        return adopted, fake_data     # TODO fake value


