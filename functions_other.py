import pandas as pd

# function to save a list of dataframes with all same column year and different monte-carlo simulations of a parameter (over time) to csv
def list_of_dfs_to_csv(list_of_dfs, system_id, material, substance):
    df_pivoted = pd.DataFrame(columns=[list_of_dfs[0].columns[0]])  # select column year
    df_pivoted[list_of_dfs[0].columns[0]] = list_of_dfs[0][list_of_dfs[0].columns[0]]
    i = 0
    column_name_data = list_of_dfs[0].columns[1]
    for df in list_of_dfs:
        i += 1
        df_data = df[column_name_data]
        df_pivoted = pd.concat([df_pivoted, df_data], axis=1)
    df_pivoted.to_csv(f'{list_of_dfs[0].columns[1]}_{system_id}_{material}_{substance}.csv')

def list_of_dfs_to_csv2(list_of_dfs, system_id, material, substance):
    df_pivoted = pd.DataFrame(columns=[list_of_dfs[0].columns[0], list_of_dfs[0].columns[1]])  # select column year and year_waste_origin
    df_pivoted[list_of_dfs[0].columns[0]] = list_of_dfs[0][list_of_dfs[0].columns[0]]
    df_pivoted[list_of_dfs[0].columns[1]] = list_of_dfs[0][list_of_dfs[0].columns[1]]
    i = 0
    column_name_data = list_of_dfs[0].columns[2]
    for df in list_of_dfs:
        i += 1
        df_data = df[column_name_data]
        df_pivoted = pd.concat([df_pivoted, df_data], axis=1)
    df_pivoted.to_csv(f'waste_age_cohorts_{system_id}_{material}_{substance}.csv')


def calc_average_MC(list_of_dfs, column_name, year_start, year_end, system_id, material):
    df_average = pd.DataFrame(columns=["year", (column_name + "_average")])
    for year_average in range(int(year_start), int(year_end)):  # + 1
        total = 0
        for df_i in list_of_dfs:
            value_year = df_i[column_name][df_i["year"] == year_average].iloc[0]
            total += value_year
        average = total / len(list_of_dfs)
        year_average_value = {
            "year": year_average,
            (column_name + "_average"): average
        }
        df_average = pd.concat([df_average, pd.DataFrame([year_average_value])])
    df_average.to_csv(column_name + f'_average_{system_id}_{material}.csv')