import matplotlib
from matplotlib.ticker import FormatStrFormatter
matplotlib.use('Agg', force=True)
from matplotlib import pyplot as plt
import numpy as np
import seaborn as sns



# plot some data given in dataframe of which first column is year and second column is anything (y values)
def plot_df(df_year):
    x = []
    for index, row in df_year.iterrows():
        year = row["year"]
        x.append(year)
    y = []
    for index, row in df_year.iterrows():
        y_value = row[df_year.columns[1]]
        y.append(y_value)

    fig, ax = plt.subplots(nrows=1, ncols=1, sharex=True, figsize=(12, 6))

    ax.set_title(df_year.columns[1])
    # ax.set_xlim(xmin=self.year_start, xmax=self.year_end)
    ax.set_xlim(xmin=1950, xmax=2050)

    plt.show()
    plt.savefig('plot_df.png')



def plot_df_several_separately(list_df_year):
    x = []
    y = []
    for df in list_df_year:
        x_df = []
        y_df = []
        titles = []
        for index, row in df.iterrows():
            year = row["year"]
            x_df.append(year)
        for index, row in df.iterrows():
            y_value = row[df.columns[1]]
            y_df.append(y_value)
        x.append(x_df)
        y.append(y_df)
        titles.append(df.columns[1])

    fig, ax = plt.subplots(nrows=1, ncols=1, sharex=True, figsize=(12, 6))

    axes_list = []
    i = 0
    for y_numbers in y:
        ax.set_title(titles[i])
        axes_list.append(ax)
        i += 1

    plt.show()
    plt.savefig('plot_df_several_separately.png')



def plot_df_several_in_one(list_df_year):
    x = []
    y = []
    titles = []
    for df in list_df_year:
        print(df)
        x_df = []
        y_df = []
        for index, row in df.iterrows():
            year = row["year"]
            x_df.append(year)
        for index, row in df.iterrows():
            y_value = row[df.columns[1]]
            y_df.append(y_value)
        x.append(x_df)
        y.append(y_df)
        titles.append(df.columns[1])
    print(x)
    print(y)
    print(titles)
    i = 0
    for y_numbers in y:
        print(y_numbers)
        plt.plot(x[0], y_numbers, label=titles[i])  # could also be x[i], all the same
        i += 1

    plt.show()
    plt.legend()
    plt.savefig('plot_df_several_in_one.png')



def plot_df_several_in_one_two_axes(list_df_left, list_df_right):


    fig, ax1 = plt.subplots()


    colors = sns.color_palette("Set2") + sns.color_palette("Set1") + sns.color_palette("Set3")


    # left axis

    x = []
    y = []
    titles = []
    for df in list_df_left:
        x_df = []
        y_df = []
        for index, row in df.iterrows():
            year = row["year"]
            x_df.append(year)
        for index, row in df.iterrows():
            y_value = row[df.columns[1]]
            y_df.append(y_value)
        x.append(x_df)
        y.append(y_df)
        titles.append(df.columns[1])

    ax1.set_xlabel('time')
    ax1.tick_params(axis='y')
    i = 0
    for y_numbers in y:
        ax1.plot(x[0], y_numbers, label=titles[i], color=colors[i])  # could also be x[i], all the same
        i += 1
    imax = i
    ax1.set_ylabel("mass flow")
    ax1.legend(loc='upper left')


    # right axis

    ax2 = ax1.twinx()

    x = []
    y = []
    titles = []
    for df in list_df_right:
        x_df = []
        y_df = []
        for index, row in df.iterrows():
            year = row["year"]
            x_df.append(year)
        for index, row in df.iterrows():
            y_value = row[df.columns[1]]
            y_df.append(y_value)
        x.append(x_df)
        y.append(y_df)
        titles.append(df.columns[1])

    ax2.set_ylabel("mass flow")  #  x-label already handled with ax1
    ax2.tick_params(axis='y')
    i = 0
    for y_numbers in y:
        print(x[0])
        print(y_numbers)
        print(titles[i])
        print(colors[imax + i])
        ax2.plot(x[0], y_numbers, label=titles[i], color=colors[imax+i])  # could also be x[i], all the same
        i += 1
    ax2.set_ylabel("mass flow")
    ax2.legend(loc='upper right')


    fig.tight_layout()
    plt.show()
    plt.savefig('plot_df_several_in_one_two_axes.png')
    plt.savefig('plot_df_several_in_one_two_axes.svg')



def plot_df_several_separately(list_dfs):

    colors = sns.color_palette("Set2") + sns.color_palette("Set1") + sns.color_palette("Set3")

    n_row = 2
    n_col = round(len(list_dfs)/n_row + 0.5)
    print(n_row, n_col)
    fig, axs = plt.subplots(int(n_row), int(n_col))
    print(axs)
    i = 0
    row = 0
    for row in range(n_row):
        col = 0
        for col in range(n_col):

            df = list_dfs[i]
            x_df = []
            y_df = []
            for index, row in df.iterrows():
                year = row["year"]
                x_df.append(year)
            for index, row in df.iterrows():
                y_value = row[df.columns[1]]
                y_df.append(y_value)

            print(axs[int(row), int(col)])
            axs[int(row), int(col)].plot(x_df, y_df)
            axs[int(row), int(col)].set_xlabel('Year')
            axs[int(row), int(col)].set_ylabel(df.columns[1])
            axs[int(row), int(col)].legend()

            i += 1
            col += 1
    row +=1

    fig.suptitle('Substance Flows')
    plt.show()
    plt.savefig('plot_df_several_separately.png')



def plot_substance_flows_separately(conc_virgin, conc, cons, waste, RR, name):  # each of them is a list of dataframes
    colors = sns.color_palette("Set2") + sns.color_palette("Set1") + sns.color_palette("Set3")

    list_dfs = []
    list_dfs.append(conc_virgin)
    list_dfs.append(conc)
    list_dfs.append(cons)
    list_dfs.append(waste)
    list_dfs.append(RR)

    n_rows = 2
    n_cols = 3
    fig, axs = plt.subplots(n_rows, n_cols)
    ax = axs.flatten()
    i = 0
    for a in range(n_rows):
        for b in range(n_cols):

            try:
                dfs = list_dfs[i]
                for df in dfs:
                    x = []
                    y = []
                    for index, row in df.iterrows():
                        year = int(row["year"])
                        x.append(year)
                    for index, row in df.iterrows():
                        y_value = row[df.columns[1]]
                        y.append(y_value)

                    axs[a, b].plot(x, y, label=df.columns[1])

                    axs[a, b].set_xlabel('Year')
                    axs[a, b].xaxis.set_major_formatter(FormatStrFormatter('%.0f'))

                    axs[a, b].set_ylabel(df.columns[1])

            except:
                print("not all axes full")

            i += 1
            b += 1
        a += 1

    fig.suptitle(f'substance_flows_{name}')
    plt.show()

    for i in range(6):
        ax = axs.flatten()[i]
        plt.setp(ax.get_xticklabels(), rotation=90, horizontalalignment='center', )
    plt.tight_layout()


    plt.savefig(f'plot_df_several_in_one_two_axes_{name}.svg')
    plt.savefig(f'plot_df_several_in_one_two_axes_{name}.png')