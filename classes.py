import numpy as np
import pandas as pd
import scipy
from multiprocessing import Pool, cpu_count
from functions_plotting import plot_df_several_in_one_two_axes, plot_df_several_separately, plot_substance_flows_separately
from functions_other import list_of_dfs_to_csv, list_of_dfs_to_csv2, calc_average_MC


def calc_consumption_waste_MC(seed, year_start, year_end, find_flows, material):
    np.random.seed(seed)

    print(f'calculation status: MFA, consumption, simulation seed {seed}')
    consumption = pd.DataFrame(columns=["year", "material_consumption"])
    for year in range(int(year_start), int(year_end) + 1):
        flow_year = find_flows(material, 'product manufacturing', 'use', year=year)
        if flow_year is None:
            consumption_amount = 0
        elif flow_year.amount == 0:
            consumption_amount = 0
        else:
            consumption_amount = np.random.triangular(left=flow_year.dist_par1, mode=flow_year.amount,
                                                      right=flow_year.dist_par2, size=None)
        consumption_year = {
            "year": year,
            "material_consumption": consumption_amount
        }
        consumption = pd.concat([consumption, pd.DataFrame([consumption_year])])

    print(f'calculation status: MFA, waste, simulation seed {seed}')
    waste = pd.DataFrame(columns=["year", "material_waste"])
    waste_from_year_to_year = pd.DataFrame(columns=["year", "year_waste_origin", "waste_amount"])
    lifetime_dist = find_flows(material, 'product manufacturing', 'use',
                                            year=year_start).material.lifetime_dist
    # print(lifetime_dist)
    for year in range(int(year_start), int(year_end) + 1):
        waste_year = 0
        for year_iter in range(int(year_start), year + 1):
            use_flow_year_iter = find_flows(material, 'product manufacturing', 'use',
                                            year=year_iter)
            if use_flow_year_iter is None:
                continue
            else:
                consumption_flow_amount = \
                    consumption["material_consumption"][
                        consumption["year"] == year_iter].iloc[0]
                if lifetime_dist == "lognormal":
                    waste_from_year_iter_in_year = consumption_flow_amount * \
                                                   scipy.integrate.quad(scipy.stats.lognorm.pdf, (year - 0.5), (year + 0.5),
                                                                        args=(use_flow_year_iter.material.dist_par1,
                                                                              use_flow_year_iter.year,
                                                                              use_flow_year_iter.material.dist_par2))[0]
                elif lifetime_dist == "weibull":
                    waste_from_year_iter_in_year = consumption_flow_amount * \
                                                   scipy.integrate.quad(scipy.stats.weibull_min.pdf, (year - 0.5),
                                                                        (year + 0.5),
                                                                        args=(use_flow_year_iter.material.dist_par1,
                                                                              use_flow_year_iter.year,
                                                                              use_flow_year_iter.material.dist_par2))[
                                                       0]
                waste_from_year_iter_in_year_df = {
                    "year": year,
                    "year_waste_origin": year_iter,
                    "waste_amount": waste_from_year_iter_in_year
                }
                waste_from_year_to_year = pd.concat(
                    [waste_from_year_to_year, pd.DataFrame([waste_from_year_iter_in_year_df])])
                waste_year += waste_from_year_iter_in_year
        waste_year = {
            "year": year,
            "material_waste": waste_year
        }
        waste = pd.concat([waste, pd.DataFrame([waste_year])])

    return consumption, waste, waste_from_year_to_year


def calc_substance_flows_MC(seed, consumption_dfs, waste_from_year_to_year_dfs, composition_in, material, substance, year_start, year_end, TCs_past_in, TCs_future1_in, TCs_future2_in, find_flows, RR_in):

    np.random.seed(seed)

    print(f'calculation status: SFA, simulation seed {seed}')

    # consumption and waste of material_inv in simulation i
    consumption_df = consumption_dfs[seed-1]
    waste_from_year_to_year_df = waste_from_year_to_year_dfs[seed-1]

    substance_concentration_timeline = []  # referring to input to use that year (i.e. before losses of substance during use)
    substance_consumption_timeline = []
    substance_waste_timeline = []
    composition_virgin_timeline = []

    composition = composition_in

    # calc concentration and consumption of substance_inv in start year

    composition_virgin_start_year = composition[
        (composition['material'] == material) & (composition['substance'] == substance) & (
                    composition['year'] == year_start)]
    substance_market_share_year_start = composition_virgin_start_year["substance_market_share"].iloc[0]
    substance_conc_product_year_start = np.random.normal(
        loc=composition_virgin_start_year["substance_conc_product"].iloc[0],
        scale=composition_virgin_start_year["substance_conc_product_dist_par1"].iloc[0], size=None)
    substance_concentration_virgin_year_start = float(substance_conc_product_year_start) * float(
        substance_market_share_year_start)
    composition_virgin_timeline.append((year_start, substance_concentration_virgin_year_start))

    consumption_material_year_start = \
    consumption_df["material_consumption"][consumption_df["year"] == year_start].iloc[0]
    consumption_substance_year_start = consumption_material_year_start * substance_concentration_virgin_year_start
    substance_consumption_timeline.append((year_start, consumption_substance_year_start))
    if consumption_material_year_start > 0:
        substance_concentration_year_start = consumption_substance_year_start / consumption_material_year_start
    else:
        substance_concentration_year_start = 0
    substance_concentration_timeline.append((year_start, substance_concentration_year_start))

    # retrieve TC use for substance and material (same for all years)
    TCs_past = TCs_past_in
    TC_use_past = TCs_past["value"][(TCs_past['process'] == 3) & (TCs_past['material'] == material) & (
                TCs_past['substance'] == substance)].iloc[0]

    TCs_future1 = TCs_future1_in
    TCs_future2 = TCs_future2_in
    TC_use_future1 = TCs_future1["value"][(TCs_future1['process'] == 3) & (TCs_future1['material'] == material) & (
            TCs_future1['substance'] == substance)].iloc[0]
    TC_use_future2 = TCs_future2["value"][(TCs_future2['process'] == 3) & (TCs_future2['material'] == material) & (
            TCs_future2['substance'] == substance)].iloc[0]

    if year_start <= 2024:
        TC_use = TC_use_past
    elif year_start <= 2060:
        TC_use = TC_use_future1
    else:
        TC_use = TC_use_future2
    # waste of material_inv from year_iter_waste in year
    waste_from_year_start_in_year_start = waste_from_year_to_year_df["waste_amount"][
        (waste_from_year_to_year_df["year_waste_origin"] == year_start) & (
                    waste_from_year_to_year_df["year"] == year_start)].iloc[0]
    substance_waste_from_year_start_in_year_start = waste_from_year_start_in_year_start * substance_concentration_year_start * TC_use
    substance_waste_timeline.append((year_start, substance_waste_from_year_start_in_year_start))

    # calc concentration and consumption in following years

    # calc recycling amount of substance in year

    rec_df = pd.DataFrame(columns=["year", "year_waste_origin", "substance_concentration_waste", "recycling_amount", "recycling_amount_substance"])
    rec_overview_df = pd.DataFrame(columns=["year", "material_amount_virgin", "material_amount_recycled", "substance_concentration_waste", "substance_amount_virgin", "substance_amount_recycled"])

    TC_rec_past = TCs_past["value"][
        (TCs_past['process'] == 5) & (TCs_past['material'] == material) & (
                    TCs_past['substance'] == substance)].iloc[0]

    TC_rec_future1 = TCs_future1["value"][
        (TCs_future1['process'] == 5) & (TCs_future1['material'] == material) & (
                    TCs_future1['substance'] == substance)].iloc[0]

    TC_rec_future2 = TCs_future2["value"][
        (TCs_future2['process'] == 5) & (TCs_future2['material'] == material) & (
                    TCs_future2['substance'] == substance)].iloc[0]

    for year in range(year_start + 1, year_end + 1):

        recycling_amount = 0
        recycling_amount_substance = 0

        # composition_virgin_timeline use
        use_flow_year = find_flows(material, 'product manufacturing', 'use', year=year)
        composition_virgin = composition[
            (composition['material'] == material) & (composition['substance'] == substance) & (
                        composition['year'] == year) & (composition['inflow_to_process'] == 3)]

        # substance concentration in virgin material in year
        if composition_virgin.empty:
            substance_concentration_year = 0
        else:
            substance_market_share_year = composition_virgin["substance_market_share"].iloc[0]
            substance_conc_product_year = np.random.normal(loc=composition_virgin["substance_conc_product"].iloc[0],
                                                           scale=
                                                           composition_virgin["substance_conc_product_dist_par1"].iloc[
                                                               0], size=None)
            substance_concentration_year = float(substance_conc_product_year) * float(substance_market_share_year)

        composition_virgin_timeline.append((year, substance_concentration_year))

        # get RR in previous year
        RR = RR_in
        try:
            RR_previousyear = RR["value"][(RR["material"] == material) & (RR["year"] == year - 1)].iloc[0]
        except:
            print(f"no RR for material {material} and year {year - 1}")
            RR_previousyear = 0

        if year <= (2024+1):  # until (incl.) 2024 TC_past, but as TC_rec of previous year is relevant, because recycled waste stems from previous year, still for sec mat in 2025 the TC_rec is TC_rec_past
            TC_use = TC_use_past  # same for past and future
            TC_rec = TC_rec_past
        elif year <= (2060+1):
            TC_use = TC_use_future1  # same for past and future
            TC_rec = TC_rec_future1
        else:
            TC_use = TC_use_future2  # same for past and future
            TC_rec = TC_rec_future2

        # for each year prior to year assessed, calculate waste amount or material_inv arising in year before year assessed and amount of it that is recycled
        waste_year_total = 0
        substance_in_waste_year_total = 0
        for year_iter in range(year_start,
                               year):  # only in loop until year-1; no recycling of waste of consumption flow into in year of consumption (only recycling from previous years)

            # waste amount in previous year (from which it is recycled to next year) = waste arising of flow to use in each year before assessed year (calculated via integration of PDF over one year with location of use year + average lifetime)
            waste_from_year_iter_in_previousyear = waste_from_year_to_year_df["waste_amount"][
                (waste_from_year_to_year_df["year_waste_origin"] == year_iter) & (
                            waste_from_year_to_year_df["year"] == year - 1)].iloc[0]

            waste_from_year_iter_in_year1 = waste_from_year_to_year_df["waste_amount"][
                (waste_from_year_to_year_df["year_waste_origin"] == year_iter) & (
                        waste_from_year_to_year_df["year"] == year)].iloc[0]
            waste_year_total += waste_from_year_iter_in_year1

            # recycling amount from waste from year_iter in previous year going into use phase in year
            recycling_amount_from_year_iter_in_year = waste_from_year_iter_in_previousyear * RR_previousyear
            recycling_amount += recycling_amount_from_year_iter_in_year

            # substance concentration in waste flow from year_iter
            substance_concentration_year_iter = substance_concentration_timeline[year_iter - year_start][1]

            substance_in_waste_year_total += waste_from_year_iter_in_year1 * substance_concentration_year_iter

            # calculate amount recycled of substance = material recycling amount from year_iter consumption to year * substance concentration in recycled waste - considering losses during use phase (TC_use) * recycling efficiency substance - considering losses during recycling e.g. by release to water during washing (recycling efficiency material considered in RR)
            substance_recycling_amount_from_year_iter_in_year = recycling_amount_from_year_iter_in_year * substance_concentration_year_iter * TC_use * TC_rec
            recycling_amount_substance += substance_recycling_amount_from_year_iter_in_year

            rec_df = pd.concat([rec_df, pd.DataFrame([[year, year_iter, substance_concentration_year_iter, recycling_amount_from_year_iter_in_year,
                                                       substance_recycling_amount_from_year_iter_in_year]],
                                                     columns=rec_df.columns)], ignore_index=True)
        substance_waste_concentration_year_overall = substance_in_waste_year_total / waste_year_total

        # calc total consumption and concentration of substance_inv in year (add virgin to recycled)

        if use_flow_year is None or use_flow_year.amount == 0:
            substance_amount_total = 0
            substance_concentration_year = 0

            virgin_material_amount_year = 0
            recycling_amount = 0    # redundant with above?
            substance_amount_virgin_material = 0
            recycling_amount_substance = 0


        else:

            # calc virgin amount of material_inv by subtracting recycled amount from total consumption amount
            consumption_year_total = consumption_df["material_consumption"][consumption_df["year"] == year].iloc[0]
            virgin_material_amount_year = consumption_year_total - recycling_amount

            # calc total virgin substance consumption
            substance_amount_virgin_material = virgin_material_amount_year * substance_concentration_year

            # calc total consumption substance year as sum of recycled amount and virgin amount
            substance_amount_total = recycling_amount_substance + substance_amount_virgin_material

            # calc concentration substance year via total consumption substance and consumption material in year
            substance_concentration_year = substance_amount_total / consumption_year_total

        rec_overview_df = pd.concat([rec_overview_df, pd.DataFrame(
                [[year, virgin_material_amount_year, recycling_amount, substance_waste_concentration_year_overall, substance_amount_virgin_material, recycling_amount_substance]],
                columns=rec_overview_df.columns)], ignore_index=True)


        substance_consumption_timeline.append((year, substance_amount_total))
        substance_concentration_timeline.append((year, substance_concentration_year))

        # calc waste of substance_inv in all years

        waste_substance = 0
        # calc waste amount from consumption flow of each previous year arising in year
        for year_iter_waste in range(year_start, year + 1):  # waste also arises in same year of consumption

            # waste of material_inv from year_iter_waste in year
            waste_from_year_iter_in_year = waste_from_year_to_year_df["waste_amount"][
                (waste_from_year_to_year_df["year_waste_origin"] == year_iter_waste) & (
                            waste_from_year_to_year_df["year"] == year)].iloc[0]

            # waste of substance_inv
            substance_concentration_year_iter = substance_concentration_timeline[year_iter_waste - year_start][1]
            substance_waste_from_year_iter_in_year = waste_from_year_iter_in_year * substance_concentration_year_iter * TC_use
            waste_substance += substance_waste_from_year_iter_in_year

        substance_waste_timeline.append((year, waste_substance))

    # convert lists of concentration, consumption, and waste of substance_inv and year to dataframes

    df_substance_concentration_timeline = pd.DataFrame(substance_concentration_timeline,
                                                       columns=["year", "substance_concentration"])
    df_substance_consumption_timeline = pd.DataFrame(substance_consumption_timeline,
                                                     columns=["year", "substance_consumption"])
    df_substance_waste_timeline = pd.DataFrame(substance_waste_timeline, columns=["year", "substance_waste"])
    df_composition_virgin_timeline = pd.DataFrame(composition_virgin_timeline,
                                                  columns=["year", "substance_concentration_virgin"])

    return df_substance_concentration_timeline, df_substance_consumption_timeline, df_substance_waste_timeline, df_composition_virgin_timeline, rec_df, rec_overview_df






class Scenario:
    def __init__(
            self,
            id_in: str,
            TCs_past_in: pd.DataFrame,
            TCs_future1_in: pd.DataFrame,
            TCs_future2_in: pd.DataFrame,
            RR_in: pd.DataFrame,
            composition_in: pd.DataFrame

    ):
        self.id = id_in
        self.TCs_past = TCs_past_in
        self.TCs_future1 = TCs_future1_in
        self.TCs_future2 = TCs_future2_in
        self.RR = RR_in
        self.composition = composition_in






class Process:
    def __init__(
            self,
            id_in: str,
            name_in: str
    ):
        self.id = id_in,
        self.name = name_in






class Material:
    def __init__(
            self,
            id_in: str,
            product_in: str,
            type_in: str,
            lifetime_in: float,
            lifetime_dist_in: str,
            dist_par1_in: float,
            dist_par2_in: float
    ):
        self.id = id_in
        self.product = product_in
        self.type = type_in
        self.lifetime = lifetime_in
        self.lifetime_dist = lifetime_dist_in
        self.dist_par1 = dist_par1_in
        self.dist_par2 = dist_par2_in

    def match(self, **kwargs):
        return all(getattr(self, key) == val for (key, val) in kwargs.items())  # is true if input key == input val for an instance investigated






class Flow:
    def __init__(
            self,
            year_in: int,
            origin_in: str,
            destination_in: str,
            amount_in: float,
            amount_dist_in: str,
            dist_par1_in: float,
            dist_par2_in: float,
            material_in: str
    ):
        self.year = year_in
        self.origin = origin_in
        self.destination = destination_in
        self.amount = amount_in
        self.amount_dist = amount_dist_in
        self.dist_par1 = dist_par1_in
        self.dist_par2 = dist_par2_in
        self.material = material_in

    def match(self, **kwargs):
        return all(getattr(self, key) == val for (key, val) in kwargs.items())  # is true if input key == input val for an instance investigated






class System:
    def __init__(
            self,
            id_in: str,
            location_in: str,
            year_start_in: int,
            year_end_in: int,
            processes_in: pd.DataFrame,
            mat_flows_in: list,
            scenario_in: Scenario,
            unit_in: str
    ):
        self.id = id_in
        self.location = location_in
        self.year_start = year_start_in
        self.year_end = year_end_in
        self.processes = processes_in
        self.flows = mat_flows_in
        self.scenario = scenario_in
        self.unit = unit_in



    # AUXILIARY


    def findFlows(self, **kwargs) -> list:
        flows = []
        for flow in self.flows:
            if flow.match(**kwargs):
                flows.append(flow)
        return flows


    def findFlows_material(self, material_inv, **kwargs) -> Flow:

        # find flows of year_inv
        flows_year = self.findFlows(**kwargs)

        # from flows of year_inv, select only flow of investigated material
        flows_year_material = []
        for flow in flows_year:
            if flow.material.id == material_inv:
                flows_year_material.append(flow)
        if len(flows_year_material) > 1:
            print(f"more than 1 flow of {kwargs.items()} and material {material_inv} -> correct input data")
            return
        else:
            try:
                flow_year_material = flows_year_material[0]
                return flow_year_material
            except:
                print(f"no flow of {kwargs.items()} and material {material_inv} -> correct input data")


    def findFlows_material_process(self, material_inv, process_origin, process_destination, **kwargs) -> Flow:

        # find flows matching **kwargs
        flows_kwargs = self.findFlows(**kwargs)

        # from flows matching **kwargs, select only flow of investigated material
        flows_kwargs_material = []
        for flow in flows_kwargs:
            if flow.material.id == material_inv:
                flows_kwargs_material.append(flow)
        flows_kwargs_material_process = []
        for flow in flows_kwargs_material:
            if flow.origin.name == process_origin and flow.destination.name == process_destination:
                flows_kwargs_material_process.append(flow)
        if len(flows_kwargs_material_process) > 1:
            print(f"more than 1 flow of {kwargs.items()} and material {material_inv} from {process_origin} to {process_destination} -> correct input data")
            return
        else:
            try:
                flow_kwargs_material_process = flows_kwargs_material_process[0]
                return flow_kwargs_material_process
            except:
                print(f"no flow of {kwargs.items()} and material {material_inv} from {process_origin} to {process_destination} -> correct input data")






    # FLOWS CALCULATION


    def calc_consumption_waste_material_timeline_MC(self, material_inv, num_simulations_inp) -> list:




        total_simulations = num_simulations_inp
        # print("total_simulations", total_simulations)
        batch_size = cpu_count()    # corresponds to number processes
        # print("batch_size", batch_size)
        # Choose as many distinct seeds as number of simulations
        all_seeds = list(range(1, total_simulations + 1))
        # print("all_seeds", all_seeds)
        # Split the seeds into batches
        seed_batches = [all_seeds[i:i + batch_size] for i in range(0, len(all_seeds), batch_size)]
        # print("seed_batches", seed_batches)




        consumption_MC = []
        waste_MC = []
        waste_MC_from_year_to_year = []

        # for each Monte Carlo simulation, calc consumption for each year and store in dataframe (dataframes containing consumption amounts for individual MC run are stored in a list)
        with Pool(processes=batch_size) as pool:
            for seeds in seed_batches:
                function_inputs = []
                for seed in seeds:
                    function_input = (seed, self.year_start, self.year_end, self.findFlows_material_process, material_inv)
                    function_inputs.append(function_input)
                batch_results = pool.starmap(calc_consumption_waste_MC, function_inputs)
                for consumption, waste, waste_from_year_to_year in batch_results:
                    consumption_MC.append(consumption)
                    waste_MC.append(waste)
                    waste_MC_from_year_to_year.append(waste_from_year_to_year)

        list_of_dfs_to_csv(consumption_MC, self.id, material_inv, "NA")
        list_of_dfs_to_csv(waste_MC, self.id, material_inv, "NA")
        #list_of_dfs_to_csv2(waste_MC_from_year_to_year, self.id, material_inv, "NA")   # results in very big file




        # calculate average consumption amount (for all model years) of all MC runs and store in dataframe
        consumption_average = pd.DataFrame(columns=["year", "material_consumption_average"])
        for year_average in range(int(self.year_start), int(self.year_end)+1):
            consumption_total = 0
            for consumption_i in consumption_MC:
                consumption_year_average_amount = consumption_i["material_consumption"][consumption_i["year"] == year_average].iloc[0]
                consumption_total += consumption_year_average_amount
            average_consumption_year_average = consumption_total / num_simulations_inp
            consumption_year_average = {
                "year": year_average,
                "material_consumption_average": average_consumption_year_average
            }
            consumption_average = pd.concat([consumption_average, pd.DataFrame([consumption_year_average])])
        consumption_average.to_csv(f'material_consumption_average_{self.id}_{material_inv}.csv')


        # calculate average waste amount (for all model years) of all MC runs and store in dataframe
        waste_average = pd.DataFrame(columns=["year", "material_waste_average"])
        for year_average_waste in range(int(self.year_start), int(self.year_end) + 1):
            waste_total = 0
            for waste_i in waste_MC:
                waste_year_average_amount = \
                waste_i["material_waste"][waste_i["year"] == year_average_waste].iloc[0]
                waste_total += waste_year_average_amount
            average_waste_year_average = waste_total / num_simulations_inp
            waste_year_average = {
                "year": year_average_waste,
                "material_waste_average": average_waste_year_average
            }
            waste_average = pd.concat([waste_average, pd.DataFrame([waste_year_average])])
        waste_average.to_csv(f'material_waste_average_{self.id}_{material_inv}.csv')

        return consumption_MC, waste_MC, waste_MC_from_year_to_year, consumption_average, waste_average



    def calc_substance_concentration_consumption_waste_timeline_MC(self, material_inv, substance_inv, num_simulations_inp) -> pd.DataFrame:



        # calc consumption and waste of material_inv

        consumption_waste_material_timeline_MC = self.calc_consumption_waste_material_timeline_MC(material_inv, num_simulations_inp)
        consumption_dfs = consumption_waste_material_timeline_MC[0]
        waste_from_year_to_year_dfs = consumption_waste_material_timeline_MC[2]



        # calc flows of substance_inv

        total_simulations = num_simulations_inp
        # print("total_simulations", total_simulations)
        batch_size = cpu_count()  # corresponds to number processes
        # print("batch_size", batch_size)
        # Choose as many distinct seeds as number of simulations
        all_seeds = list(range(1, total_simulations + 1))
        # print("all_seeds", all_seeds)
        # Split the seeds into batches
        seed_batches = [all_seeds[i:i + batch_size] for i in range(0, len(all_seeds), batch_size)]
        # print("seed_batches", seed_batches)

        substance_concentration_timeline_MC = []  # referring to input to use that year (i.e. before losses of substance during use)
        substance_consumption_timeline_MC = []
        substance_waste_timeline_MC = []
        composition_virgin_timeline_MC = []
        df_rec_MC = []
        df_rec_overview_MC = []

        with Pool(processes=batch_size) as pool:
            for seeds in seed_batches:
                function_inputs = []
                for seed in seeds:
                    function_input = (seed, consumption_dfs, waste_from_year_to_year_dfs, self.scenario.composition,
                                material_inv, substance_inv, self.year_start, self.year_end, self.scenario.TCs_past,
                                self.scenario.TCs_future1, self.scenario.TCs_future2, self.findFlows_material_process, self.scenario.RR)
                    function_inputs.append(function_input)
                batch_results = pool.starmap(calc_substance_flows_MC, function_inputs)
                for df_substance_concentration_timeline, df_substance_consumption_timeline, df_substance_waste_timeline, df_composition_virgin_timeline, df_rec, df_rec_overview in batch_results:
                    substance_concentration_timeline_MC.append(df_substance_concentration_timeline)  # referring to input to use that year (i.e. before losses of substance during use)
                    substance_consumption_timeline_MC.append(df_substance_consumption_timeline)
                    substance_waste_timeline_MC.append(df_substance_waste_timeline)
                    composition_virgin_timeline_MC.append(df_composition_virgin_timeline)
                    df_rec_MC.append(df_rec)
                    df_rec_overview_MC.append(df_rec_overview)

        list_of_dfs_to_csv(substance_consumption_timeline_MC, self.id, material_inv, substance_inv)
        list_of_dfs_to_csv(substance_waste_timeline_MC, self.id, material_inv, substance_inv)
        list_of_dfs_to_csv(substance_concentration_timeline_MC, self.id, material_inv, substance_inv)
        list_of_dfs_to_csv(composition_virgin_timeline_MC, self.id, material_inv, substance_inv)

        # calc average of MC runs for rec_df values
        rec_df_average = pd.DataFrame(columns=["year", "year_waste_origin", "substance_concentration_waste_average", "recycling_amount_average",
                                       "recycling_amount_substance_average"])
        year_average = []
        year_waste_origin_average = []
        substance_concentration_waste_total = []
        recycling_amount_total = []
        recycling_amount_substance_total = []
        for index, row in df_rec_MC[0].iterrows():
            year_average.append(row["year"])
            year_waste_origin_average.append(row["year_waste_origin"])
            substance_concentration_waste_total.append(0)
            recycling_amount_total.append(0)
            recycling_amount_substance_total.append(0)
        # print(len(year_average), len(year_waste_origin_average), len(substance_concentration_waste_total), len(recycling_amount_total), len(recycling_amount_substance_total))
        for df_i in df_rec_MC:
            for index, row in df_i.iterrows():
                # print(index)
                substance_concentration_waste_total[index] += row["substance_concentration_waste"]
                recycling_amount_total[index] += row["recycling_amount"]
                recycling_amount_substance_total[index] += row["recycling_amount_substance"]

        for n in range(len(year_average)):
            year_average_values = {
                "year": year_average[n],
                "year_waste_origin": year_waste_origin_average[n],
                ("substance_concentration_waste" + "_average"): substance_concentration_waste_total[n] / len(df_rec_MC),
                ("recycling_amount" + "_average"): recycling_amount_total[n] / len(df_rec_MC),
                ("recycling_amount_substance" + "_average"): recycling_amount_substance_total[n] / len(df_rec_MC),
            }
            rec_df_average = pd.concat([rec_df_average, pd.DataFrame([year_average_values])])
        rec_df_average.to_csv(f'rec_df_average_{self.id}_{material_inv}_{substance_inv}.csv')


        rec_overview_df_average = pd.DataFrame(columns=["year", "material_amount_virgin_average", "material_amount_recycled_average", "substance_concentration_waste_average", "substance_amount_virgin_average", "substance_amount_recycled_average"])
        for year_average in range(int(self.year_start)+1, int(self.year_end)+1):  # + 1
            material_amount_virgin_total = 0
            material_amount_recycled_total = 0
            substance_concentration_waste_total = 0
            substance_amount_virgin_total = 0
            substance_amount_recycled_total = 0
            # print(df_rec_overview_MC[0])
            # print(year_average)
            for df_i in df_rec_overview_MC:
                material_amount_virgin_total += df_i["material_amount_virgin"][df_i["year"] == year_average].iloc[0]
                material_amount_recycled_total += df_i["material_amount_recycled"][df_i["year"] == year_average].iloc[0]
                substance_concentration_waste_total += df_i["substance_concentration_waste"][df_i["year"] == year_average].iloc[0]
                substance_amount_virgin_total += df_i["substance_amount_virgin"][df_i["year"] == year_average].iloc[0]
                substance_amount_recycled_total += df_i["substance_amount_recycled"][df_i["year"] == year_average].iloc[0]
            material_amount_virgin_average = material_amount_virgin_total / len(df_rec_overview_MC)
            material_amount_recycled_average = material_amount_recycled_total / len(df_rec_overview_MC)
            substance_concentration_waste_average = substance_concentration_waste_total / len(df_rec_overview_MC)
            substance_amount_virgin_average = substance_amount_virgin_total / len(df_rec_overview_MC)
            substance_amount_recycled_average = substance_amount_recycled_total / len(df_rec_overview_MC)
            year_average_values = {
                "year": year_average,
                "material_amount_virgin_average": material_amount_virgin_average,
                "material_amount_recycled_average": material_amount_recycled_average,
                "substance_concentration_waste_average": substance_concentration_waste_average,
                "substance_amount_virgin_average": substance_amount_virgin_average,
                "substance_amount_recycled_average": substance_amount_recycled_average
            }
            rec_overview_df_average = pd.concat([rec_overview_df_average, pd.DataFrame([year_average_values])])
        rec_overview_df_average.to_csv(f'rec_overview_df_average_{self.id}_{material_inv}_{substance_inv}.csv')


        # calculate average concentration, consumption, and waste of substance_inv (for all model years) of all MC runs and store in dataframe  # may cause the code to crash -> potentially calculate average in a different way
        # calc_average_MC(substance_concentration_timeline_MC, "substance_concentration", self.year_start,
        #                 self.year_end,
        #                 self.id, material_inv)
        # calc_average_MC(substance_consumption_timeline_MC, "substance_consumption", self.year_start, self.year_end,
        #                 self.id,
        #                 material_inv)
        # calc_average_MC(substance_waste_timeline_MC, "substance_waste", self.year_start, self.year_end, self.id,
        #                 material_inv)
        # calc_average_MC(composition_virgin_timeline_MC, "substance_concentration_virgin", self.year_start,
        #                 self.year_end,
        #                 self.id, material_inv)

        return substance_concentration_timeline_MC, substance_consumption_timeline_MC, substance_waste_timeline_MC, composition_virgin_timeline_MC, df_rec_MC





    # PLOTTING


    # plot consumption Monte Carlo and related waste
    def plot_material_flows_MC(self, material_inv, num_sim):
        lists_consumption_waste = self.calc_consumption_waste_material_timeline_MC(material_inv, num_sim)
        dfs_left = []
        # print(lists_consumption_waste[0])
        for df in lists_consumption_waste[0]:
            dfs_left.append(df)
        for df in lists_consumption_waste[1]:
            dfs_left.append(df)
        dfs_right = []
        plot_df_several_in_one_two_axes(dfs_left, dfs_right)





    def plot_substance_flows_MC_separately(self, material_inv, substance_inv, num_sim) -> None:
        dfs_conc_cons_waste_MC = self.calc_substance_concentration_consumption_waste_timeline_MC(material_inv,
                                                                                                 substance_inv, num_sim)
        dfs_concentration = dfs_conc_cons_waste_MC[0]
        dfs_consumption = dfs_conc_cons_waste_MC[1]
        dfs_waste = dfs_conc_cons_waste_MC[2]
        dfs_concentration_virgin = dfs_conc_cons_waste_MC[3]

        df_RR = self.scenario.RR
        df_RR_plot = pd.DataFrame(columns=["year", "RR"])
        for year in range(self.year_start, self.year_end+1):
            exists = 0
            for index, row in df_RR.iterrows():
                if row["material"] == material_inv and row["year"] == year:
                    df_RR_plot = pd.concat([df_RR_plot, pd.DataFrame([[year, row["value"]]], columns=df_RR_plot.columns)], ignore_index=True)
                    exists = 1
            if exists == 0:
                df_RR_plot = pd.concat([df_RR_plot, pd.DataFrame([[year, 0]], columns=df_RR_plot.columns)], ignore_index=True)
        dfs_RR_plot = []
        for i in range(len(dfs_concentration)):
            dfs_RR_plot.append(df_RR_plot)

        dfs_concentration_to_one_df = pd.DataFrame(columns=[dfs_concentration[0].columns[0]]) # select column year
        dfs_concentration_to_one_df[dfs_concentration[0].columns[0]] = dfs_concentration[0][dfs_concentration[0].columns[0]]
        i = 0
        for df in dfs_concentration:
            i+=1
            dfs_concentration_to_one_df[f'{dfs_concentration[0].columns[1]}_{i}'] = df[dfs_concentration[0].columns[1]]
        dfs_concentration_to_one_df.to_csv(f'concentration_{self.id}_{material_inv}_{substance_inv}.csv')

        list_of_dfs_to_csv(dfs_RR_plot, self.id, material_inv, substance_inv)
        df_RR_plot.to_csv(f'RR_{self.id}_{material_inv}.csv')

        name_plot = f'{self.id}_{material_inv}_{substance_inv}'

        plot_substance_flows_separately(dfs_concentration_virgin, dfs_concentration, dfs_consumption, dfs_waste, dfs_RR_plot, name_plot)




    # BALANCE CHECK


    # ATTENTION: calc duration (set via start and end year of system) needs to be sufficiently long (alternatively, code would need to be adapted so to calculate waste till inf)
    def balance_check_material_MC(self, material_inv, num_sim):
        cons_waste = self.calc_consumption_waste_material_timeline_MC(material_inv, num_sim)
        consumption_dfs = cons_waste[0]
        waste_dfs = cons_waste[1]

        consumption_MCruns = []
        waste_MCruns = []

        for i in range(num_sim):

            consumption_MCrun = 0
            for index, row in consumption_dfs[i].iterrows():
                consumption_MCrun += row["material_consumption"]
            consumption_MCruns.append(consumption_MCrun)

            waste_MCrun = 0
            for index, row in waste_dfs[i].iterrows():
                waste_MCrun += row["material_waste"]
            waste_MCruns.append(waste_MCrun)

        for i in range(num_sim):
            print(
                f"consumption run {i + 1} - check: consumption ({consumption_MCruns[i]}) = waste ({waste_MCruns[i]})?")

        return consumption_MCruns, waste_MCruns


    # ATTENTION: calc duration (set via start and end year of system) needs to be sufficiently long (alternatively, code would need to be adapted so to calculate waste till inf)
    def balance_check_substance_MC(self, material_inv, substance_inv, num_sim):

        dfs_conc_cons_waste = self.calc_substance_concentration_consumption_waste_timeline_MC(material_inv,
                                                                                              substance_inv,
                                                                                              num_sim)
        print(dfs_conc_cons_waste)

        consumption_tot_MC = []
        waste_tot_MC = []
        losses_use_MC = []
        rec_substance_total_losses_MC = []
        rec_substance_total_losses_check_MC = []

        for i in range(num_sim):

            df_consumption = dfs_conc_cons_waste[1][i]
            df_waste = dfs_conc_cons_waste[2][i]
            df_rec = dfs_conc_cons_waste[4][i]

            consumption_tot = 0
            print(df_consumption, "df_consumption")
            for index, row in df_consumption.iterrows():
                consumption_tot += row["substance_consumption"]
            consumption_tot_MC.append((consumption_tot))

            waste_tot = 0
            print(df_waste, "df_waste")
            for index, row in df_waste.iterrows():
                waste_tot += row["substance_waste"]
            waste_tot_MC.append((waste_tot))

            # retrieve TC use
            TCs = self.scenario.TCs_past    # TC_use same for past and future
            print(TCs)
            TC_use = TCs["value"][(TCs['process'] == 3) & (TCs['material'] == material_inv) & (TCs['substance'] == substance_inv)].iloc[0]
            print(TC_use)
            # calc substance losses during use
            losses_use = consumption_tot * (1 - TC_use)
            losses_use_MC.append(losses_use)



            rec_substance_total_losses = 0  # corresponds to recycling amount substance (after losses) calculated with model (summed up over all years), over all years, for 1 MC run
            for index, row in df_rec.iterrows():
                rec_substance_total_losses += row["recycling_amount_substance"]
                print(row["recycling_amount_substance"], row["year"])

            rec_substance_total_losses_check = 0   # corresponds to recycling amount substance (after losses) calculated via waste amount (after use losses) and RR and TC_rec in year, over all years, for 1 MC run
            for year_iter_rec in range(self.year_start, self.year_end+1):
                print(year_iter_rec)
                waste_year = df_waste["substance_waste"][(df_waste['year'] == year_iter_rec)].iloc[0]
                print(waste_year)

                # retrieve TC rec for year
                if year_iter_rec <= 2024:
                    TCs_rec = self.scenario.TCs_past
                elif year_iter_rec <= 2060:
                    TCs_rec = self.scenario.TCs_future1
                else:
                    TCs_rec = self.scenario.TCs_future2

                TC_rec_year = TCs_rec["value"][(TCs['process'] == 5) & (TCs['material'] == material_inv) & (TCs['substance'] == substance_inv)].iloc[0]
                print(TC_rec_year)

                RR_entity = self.scenario.RR
                RR_year = RR_entity["value"][(RR_entity['year'] == year_iter_rec) & (RR_entity['material'] == material_inv)].iloc[0]
                print(RR_year)

                rec_substance_after_losses_year = waste_year * RR_year * TC_rec_year
                print(rec_substance_after_losses_year)
                rec_substance_total_losses_check += rec_substance_after_losses_year

            rec_substance_total_losses_MC.append(rec_substance_total_losses)
            rec_substance_total_losses_check_MC.append(rec_substance_total_losses_check)

        for i in range(num_sim):
            print(f"simulation number substance {i + 1}: consumption_tot_substance ({consumption_tot_MC[i]}) = waste_tot_substance ({waste_tot_MC[i]}) + losses_use_substance ({losses_use_MC[i]}) = {waste_tot_MC[i] + losses_use_MC[i]}?")
            print(f"simulation number {i + 1}: recycling_amount_substance_total_after_losses from model ({rec_substance_total_losses_MC[i]}) = recycling_amount_substance_total_after_losses calculated via waste amount and RR and TC rec in each year ({rec_substance_total_losses_check_MC[i]})")

        return consumption_tot_MC, waste_tot_MC, losses_use_MC, rec_substance_total_losses_MC, rec_substance_total_losses_check_MC