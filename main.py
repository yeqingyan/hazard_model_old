import argparse
import time
import datetime
import Hazard
from Utils.NetworkUtils import *
from Utils.Plot import *
from DynamicNetwork import DynamicNetwork
from HazardMLE import *

WEEK_IN_SECOND = 7 * 24 * 60 * 60

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

    for i in fake_data.values():
        train_data_exog.append([1] + list(i[1:]))
        train_data_endog.append(i[0])
    train_data_exog = DataFrame(train_data_exog, columns=["CONSTANT", "ADOPTED_NEIGHBORS", "SENTIMENT"])
    train_data_endog = Series(train_data_endog, name="ADOPTION")
    return train_data_exog, train_data_endog

def main():
    args = parse_args()
    start_date = int(time.mktime(datetime.datetime.strptime(args['d'], "%m/%d/%Y").timetuple()))
    g = get_graphml(args['g'])
    graph_info(g)
    g = DynamicNetwork(g)
    model = Hazard.Hazard(g, start_date, WEEK_IN_SECOND, [0.3, 0.3, 0.3])
    ref_result, fake_data = model.hazard()
    print(ref_result)
    print("{} steps".format(len(ref_result)))
    # plot(result)

    exog, endog = fake_train_data(fake_data)
    # g.generate_train_data(start_date, WEEK_IN_SECOND, fake_data)
    result = HazardModel(exog=exog, endog=endog).fit()
    print(result)
    print(result.params)

    sim_model = Hazard.Hazard(g, start_date, WEEK_IN_SECOND, result.params)
    sim_result, _ = sim_model.hazard()
    plot([ref_result, sim_result])
    return

if __name__ == "__main__":
    main()


