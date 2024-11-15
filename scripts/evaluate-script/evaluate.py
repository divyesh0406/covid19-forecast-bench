import os
import pandas as pd
import numpy as np
import datetime
import threading


DAY_ZERO = datetime.datetime(2020,1,22)
FORECASTS_NAMES = "scripts/evaluate-script/forecasts_filenames.txt"
MODEL_NAMES = "scripts/evaluate-script/models.txt"
US_DEATH_URL = "https://raw.githubusercontent.com/scc-usc/ReCOVER-COVID-19/master/results/forecasts/us_deaths.csv"
US_DEATH_FORECASTS_DIR = "../../formatted-forecasts/US-COVID/state-death/"
US_CASE_URL = "https://raw.githubusercontent.com/scc-usc/ReCOVER-COVID-19/master/results/forecasts/us_data.csv"
US_CASE_FORECASTS_DIR = "../../formatted-forecasts/US-COVID/state-case/"

def datetime_to_str(date):
    return date.strftime("%Y-%m-%d")

def str_to_datetime(date_str):
    return datetime.datetime.strptime(date_str,"%Y-%m-%d")

def get_inc_truth(url):
    # Fetch observed data.
    cum_truth = pd.read_csv(url, index_col="id")

    # Calculate incident data.
    inc_truth = cum_truth.drop(columns=["Country"])
    inc_truth = inc_truth.diff(axis=1)

    # Format week intervals.
    date_col1 = list(inc_truth.columns)
    date_col1.pop()
    date_col2 = list(inc_truth.columns)
    date_col2.pop(0)

    end_date = date_col2

    # Assign new column names.
    inc_truth = inc_truth.drop(columns=["2020-01-25"])
    inc_truth.columns = date_col2

    # Add region names.
    inc_truth.insert(0, "State", cum_truth["Country"])
    return inc_truth

def get_model_reports_mapping(model_names, forecasts_names):
    mapping = {}
    with open(model_names) as f:
        for model in f:
            mapping[model.strip()] = []

    with open(forecasts_names) as f:
        for filename in f:
            model = filename[:-9].strip()
            if model in mapping:
                mapping[model].append(filename.strip())
    return mapping

def get_evaluation_df(foreast_type, metric, inc_truth, regions, models):
    wk_intervals = list(inc_truth.columns)[22:]
    model_evals = {}

    for region in regions:
        model_evals[region] = []
        for i in range(0, 4):
            path = "../../evaluation/US-COVID/{0}_eval/{1}_{2}_weeks_ahead_{3}.csv".format(foreast_type, metric, i+1, region)
            if os.path.exists(path):
                df = pd.read_csv(path, index_col=0);
                model_evals[region].append(pd.DataFrame(df, columns=wk_intervals))
            else:
                empty_array = np.empty((len(models), len(wk_intervals)))
                empty_array[:] = np.nan
                model_evals[region].append(pd.DataFrame(empty_array, columns=wk_intervals, index=models))

    return model_evals

def evaluate(inc_truth, model_name, metric, reports, regions, model_evals, forecasts_dir):
    for report in reports:
        path = forecasts_dir + "{}/{}".format(model_name, report)
        if not os.path.exists(path):
            continue

        # Fetch report data.
        print("Evaluating " + report)
        pred = pd.read_csv(path, index_col=0)
        pred = pred.drop(columns=[pred.columns[1]])

        # Assign each column name to be week intervals.
        cols = list(pred.columns)
        for i in range(1, len(cols)):
            epi_day = int(cols[i])
            end_date = datetime_to_str(DAY_ZERO + datetime.timedelta(days=epi_day))
            cols[i] = end_date
        pred.columns = cols

        if metric == "mae":
            # Calculate MAE for each state.
            pred_num = pred.drop(columns=["State"])
            pred_num = pred_num[sorted(pred_num.columns)]
            observed_wks = 4;
            for i in range(0, 4):
                if i >= len(pred_num.columns) or pred_num.columns[i] > inc_truth.columns[-1]:
                    observed_wks -= 1
            pred_num = pred_num.drop(columns=pred_num.columns[observed_wks:])  # Only look at first 4 observed weeks.
            mae_df = np.abs((pred_num - inc_truth[pred_num.columns]))
            mae_df.insert(0, "State", regions[:-1])

            # Calculate the mean MAE as the overall error.
            overall_mae = mae_df.mean()
            overall_mae['State'] = "states"

            mae_df = mae_df.append(overall_mae, ignore_index=True)
            for i in range(0, observed_wks):
                interval = mae_df.columns[i+1]
                if interval in model_evals["states"][i].columns:
                    for region in regions:
                        model_evals[region][i].loc[model_name, interval] = mae_df[interval][mae_df["State"] == region].tolist()[0]
        elif metric == "mape":
            pred_num = pred.drop(columns=["State"])
            pred_num = pred_num[sorted(pred_num.columns)]
            observed_wks = 4;
            for i in range(0, 4):
                if i >= len(pred_num.columns) or pred_num.columns[i] > inc_truth.columns[-1]:
                    observed_wks -= 1
            pred_num = pred_num.drop(columns=pred_num.columns[observed_wks:])
            mape_df = np.abs((pred_num - inc_truth[pred_num.columns])) / inc_truth[pred_num.columns]
            mape_df.replace([np.inf, -np.inf], np.nan, inplace=True)
            mape_df.fillna(0)
            mape_df.insert(0, "State", regions[:-1])

            # Calculate the mean MAE as the overall error.
            overall_mape = mape_df.mean()
            overall_mape['State'] = "states"

            mape_df = mape_df.append(overall_mape, ignore_index=True)
            for i in range(0, observed_wks):
                interval = mape_df.columns[i+1]
                if interval in model_evals["states"][i].columns:
                    for region in regions:
                        model_evals[region][i].loc[model_name, interval] = mape_df[interval][mape_df["State"] == region].tolist()[0]

# Adding a Bogus Error Metric (BEM)
       

def generate_average_evals(regions, model_evals):
    average_evals = {}
    for region in regions:
        week_ahead_4 = model_evals[region][3]
        week_ahead_3 = model_evals[region][2]
        week_ahead_2 = model_evals[region][1]
        week_ahead_1 = model_evals[region][0]

        # Make sure the forecast made in the same forecast report are named under the same column.
        week_ahead_4 = week_ahead_4[week_ahead_4.columns[3:]]
        week_ahead_3 = week_ahead_3[week_ahead_3.columns[2:-1]]
        week_ahead_2 = week_ahead_2[week_ahead_2.columns[1:-2]]
        week_ahead_1 = week_ahead_1[week_ahead_1.columns[:-3]]

        week_ahead_3.columns = week_ahead_4.columns
        week_ahead_2.columns = week_ahead_4.columns
        week_ahead_1.columns = week_ahead_4.columns

        average = (week_ahead_4 + week_ahead_3 + week_ahead_2 + week_ahead_1) / 4
        average_evals[region] = average
    return average_evals

def run():
    model_reports_mapping = get_model_reports_mapping(MODEL_NAMES, FORECASTS_NAMES)

    # Death eval - MAE
    output_dir = "./output/state_death_eval/"
    os.mkdir(output_dir)
    inc_truth = get_inc_truth(US_DEATH_URL)
    state_col = list(inc_truth["State"])
    state_col.append("states")

    model_evals = get_evaluation_df("state_death", "mae", inc_truth, state_col, model_reports_mapping.keys())
    for model in model_reports_mapping:
        reports = model_reports_mapping[model]
        evaluate(inc_truth, model, "mae", reports, state_col, model_evals, US_DEATH_FORECASTS_DIR)

    for state in model_evals:
        for i in range(len(model_evals[state])):
            model_evals[state][i].to_csv(output_dir + "mae_{0}_weeks_ahead_{1}.csv".format(i+1, state))

    average_evals = generate_average_evals(state_col, model_evals)
    for state in average_evals:
        average_evals[state].to_csv(output_dir + "mae_avg_{1}.csv".format(i+1, state))

    # Death eval - MAPE
    model_evals = get_evaluation_df("state_death", "mape", inc_truth, state_col, model_reports_mapping.keys())
    for model in model_reports_mapping:
        reports = model_reports_mapping[model]
        evaluate(inc_truth, model, "mape", reports, state_col, model_evals, US_DEATH_FORECASTS_DIR)

    for state in model_evals:
        for i in range(len(model_evals[state])):
            model_evals[state][i].to_csv(output_dir + "mape_{0}_weeks_ahead_{1}.csv".format(i+1, state))

    average_evals = generate_average_evals(state_col, model_evals)
    for state in average_evals:
        average_evals[state].to_csv(output_dir + "mape_avg_{1}.csv".format(i+1, state))

    # Case eval - MAE
    output_dir = "./output/state_case_eval/"
    os.mkdir(output_dir)
    inc_truth = get_inc_truth(US_CASE_URL)
    state_col = list(inc_truth["State"])
    state_col.append("states")

    model_evals = get_evaluation_df("state_case", "mae", inc_truth, state_col, model_reports_mapping.keys())
    for model in model_reports_mapping:
        reports = model_reports_mapping[model]
        evaluate(inc_truth, model, "mae", reports, state_col, model_evals, US_CASE_FORECASTS_DIR)

    for state in model_evals:
        for i in range(len(model_evals[state])):
            model_evals[state][i].to_csv(output_dir + "mae_{0}_weeks_ahead_{1}.csv".format(i+1, state))

    average_evals = generate_average_evals(state_col, model_evals)
    for state in average_evals:
        average_evals[state].to_csv(output_dir + "mae_avg_{1}.csv".format(i+1, state))

    # Case eval - MAPE
    model_evals = get_evaluation_df("state_case", "mape", inc_truth, state_col, model_reports_mapping.keys())
    for model in model_reports_mapping:
        reports = model_reports_mapping[model]
        evaluate(inc_truth, model, "mape", reports, state_col, model_evals, US_CASE_FORECASTS_DIR)

    for state in model_evals:
        for i in range(len(model_evals[state])):
            model_evals[state][i].to_csv(output_dir + "mape_{0}_weeks_ahead_{1}.csv".format(i+1, state))

    average_evals = generate_average_evals(state_col, model_evals)
    for state in average_evals:
        average_evals[state].to_csv(output_dir + "mape_avg_{1}.csv".format(i+1, state))

    #Bogus Eval


if __name__ == "__main__":
    run()