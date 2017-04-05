import argparse
import time
import datetime
import Hazard
from Utils.NetworkUtils import *
from Utils.Plot import *
from DynamicNetwork import DynamicNetwork
from HazardMLE import *

WEEK_IN_SECOND = 7 * 24 * 60 * 60
FAKE_HAZARD_BETA = [0.1, 0.3, 0.3]

def parse_args():
    """Input arguments"""
    program_description = "Hazard model"
    parser = argparse.ArgumentParser(description=program_description)
    parser.add_argument('g', help='Input network graph')
    parser.add_argument('-d', help='Start date(m/d/y)')

    args = vars(parser.parse_args())
    return args

# TODO generate fake data
def fake_train_data(fake_data):
    from pandas import DataFrame, Series
    train_data_exog = []
    train_data_endog = []

    # for k, i in fake_data.items():
    #     train_data_exog.append([k[0], k[1]] + [1] + list(i[1:]) + [i[0]])
    #     train_data_endog.append(i[0])
    # train_data_exog.sort(key=lambda i: (i[0], i[1]))
    # train_data_exog = DataFrame(train_data_exog, columns=["NODEID", "SECONDS", "CONSTANT", "ADOPTED_NEIGHBORS", "SENTIMENT", "ADOPTION"])
    # train_data_endog = Series(train_data_endog, name="ADOPTION")
    for k, i in fake_data.items():
        train_data_exog.append([1] + list(i[1:]))
        train_data_endog.append(i[0])
    # train_data_exog.sort(key=lambda i: (i[0], i[1]))
    print(train_data_exog)
    train_data_exog = DataFrame(train_data_exog, columns=["CONSTANT", "ADOPTED_NEIGHBORS", "SENTIMENT"])
    train_data_endog = Series(train_data_endog, name="ADOPTION")

    return train_data_exog, train_data_endog

def main():
    args = parse_args()
    start_date = int(time.mktime(datetime.datetime.strptime(args['d'], "%m/%d/%Y").timetuple()))
    g = get_graphml(args['g'])
    # g = sample(g, 10/len(g))
    graph_info(g)
    g = DynamicNetwork(g)
    model = Hazard.Hazard(g, start_date, WEEK_IN_SECOND, FAKE_HAZARD_BETA)
    ref_result, fake_data = model.hazard()
    print(ref_result)
    print("{} steps".format(len(ref_result)))
    # plot(result)

    exog, endog = fake_train_data(fake_data)
    print(exog[:10])
    print(len(exog))

    # g.generate_train_data(start_date, WEEK_IN_SECOND, fake_data)
    result = HazardModel(exog=exog, endog=endog).fit(method="lbfgs", bounds=[(0.00001, .999), (0.00001, .999), (0.00001, .999)])
    print("MLE loglikelihood")
    print_loglikelihood(exog, endog, result.params)
    print("Original loglikelihood")
    print_loglikelihood(exog, endog, FAKE_HAZARD_BETA)
    exit()

    sim_model = Hazard.Hazard(g, start_date, WEEK_IN_SECOND, result.params)
    sim_result, _ = sim_model.hazard()
    plot([ref_result, sim_result])
    return

def print_loglikelihood(exogs, endogs, params):
    exogs = np.asarray(exogs)
    endogs = np.asarray(endogs)
    log_likelihood = 0

    for exog, endog in zip(exogs, endogs):
        if endog == 1:
            log_likelihood += stats.norm.logcdf(np.dot(exog, params)).sum()
        elif endog == 0:
            log_likelihood += stats.norm.logcdf(-1 * np.dot(exog, params)).sum()
        else:
            assert False, "Shouldn't run into this line"

    print("{}, {}".format([round(i, 5) for i in params], log_likelihood))


if __name__ == "__main__":
    main()


