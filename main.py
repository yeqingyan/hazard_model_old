import argparse
import time
import datetime
import Hazard
from Utils.NetworkUtils import *
from Utils.Plot import *
from DynamicNetwork import DynamicNetwork
from HazardMLE import *
import pickle
import statsmodels.discrete.discrete_model
import logging
import json
WEEK_IN_SECOND = 7 * 24 * 60 * 60
FAKE_HAZARD_BETA = [0.001, 0.03, 0.03]
STOP_STEP = 13

def parse_args():
    """Input arguments"""
    program_description = "Hazard model"
    parser = argparse.ArgumentParser(description=program_description)
    parser.add_argument('g', help='Input network graph')
    parser.add_argument('-d', help='Start date(m/d/y)')

    args = vars(parser.parse_args())
    return args

def get_formated_train_data(data, verbose=False):
    from pandas import DataFrame, Series
    train_data_exog = []
    train_data_endog = []

    if verbose:
        for k, i in data.items():
            train_data_exog.append([k[0], k[1]] + [1] + list(i[1:]) + [i[0]])
            train_data_endog.append(i[0])
        train_data_exog.sort(key=lambda i: (i[0], i[1]))
        train_data_exog = DataFrame(train_data_exog, columns=["NODEID", "SECONDS", "CONSTANT", "ADOPTED_NEIGHBORS", "SENTIMENT", "ADOPTION"])
        logging.info(train_data_exog)

    train_data_exog = []
    train_data_endog = []

    for k, i in data.items():
        train_data_exog.append([1] + list(i[1:]))
        train_data_endog.append(i[0])
    train_data_exog = DataFrame(train_data_exog, columns=["CONSTANT", "ADOPTED_NEIGHBORS", "SENTIMENT"])
    train_data_endog = Series(train_data_endog, name="ADOPTION")

    return train_data_exog, train_data_endog

def main():
    args = parse_args()
    start_date = int(time.mktime(datetime.datetime.strptime(args['d'], "%m/%d/%Y").timetuple()))
    g = get_graphml(args['g'])
    # g = sample(g, 30/len(g))

    g = DynamicNetwork(
            g,
            json.load(open("./sentiment_data/sentiment.json")),
            start_date=start_date,
            intervals=WEEK_IN_SECOND,
            stop_step=STOP_STEP)

    ref_result, real_data = g.generate_train_data(start_date, WEEK_IN_SECOND, stop_step=STOP_STEP)
    logging.info(ref_result)
    logging.info("{} steps".format(len(ref_result)))
    # plot(result)

    exog, endog = get_formated_train_data(real_data)
    # print(stats.norm.fit(exog))

    hazard_model = HazardModel(exog=exog, endog=endog, dist=stats.norm)
    # hazard_model.set_distribution(stats.powerlaw)
    result = hazard_model.fit(method="powell")
    logging.info("MLE loglikelihood")
    print_loglikelihood(exog, endog, result.params)
    sim_model = Hazard.Hazard(g, start_date, WEEK_IN_SECOND, result.params)
    # params = [-1.3810199999999999, 0.087709999999999996, -0.02068]
    # sim_model = Hazard.Hazard(g, start_date, WEEK_IN_SECOND, params)

    # print("Original loglikelihood")
    # print_loglikelihood(exog, endog, FAKE_HAZARD_BETA)

    sim_result, prob_dist = sim_model.hazard(stop_step=STOP_STEP, dist=stats.norm)
    logging.info(sim_result)
    plot({"Reference": ref_result, "MLE result": sim_result}, show=False)
    with open("prob.pickle", 'wb') as f:
        pickle.dump(prob_dist, f)
    # plot_distrubtion({"Prob distrbution": prob_dist}, show=False)

def print_loglikelihood(exogs, endogs, params, dist=stats.norm):
    exogs = np.asarray(exogs)
    endogs = np.asarray(endogs)
    log_likelihood = 0

    for exog, endog in zip(exogs, endogs):
        if endog == 1:
            log_likelihood += dist.logcdf(np.dot(exog, params)).sum()
        elif endog == 0:
            log_likelihood += dist.logcdf(-1 * np.dot(exog, params)).sum()
        else:
            assert False, "Shouldn't run into this line"

    logging.info("{}, {}".format([round(i, 5) for i in params], log_likelihood))

def get_dist():
    pass

if __name__ == "__main__":
    logging.basicConfig(filename="hazard.log", level=logging.NOTSET)
    main()


