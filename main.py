from pathlib import Path
from functions_db import return_engine, upload_all_excel_tables, load_system

num_simulations = 1000



# UPLOADING EXCEL TABLES TO DATABASE

# get current working directory (to get the parent directory of the script directory (regardless of the current working directory): project_path = Path(__file__).resolve().parent)
project_path = Path().resolve()

# specify path to excel tables
path_to_excel_tables = str(project_path)+'/tables.xlsx'

# connecting to database
string_engine_connection = input("Please enter the string for the engine connection (e.g. mysql+pymysql://username:password@localhost:3306/mydatabase; without apostrophes)!") # insert connection information for your database storage
db_connection = return_engine(string_engine_connection)

# uploading sheets from excel tables to database
upload_all_excel_tables(path_to_excel_tables, db_connection)



# LOADING AND ASSESSING SYSTEM FROM DATABASE FOR PARAMETER VALUES WITH UNCERTAINTY



# loading system to assess from database
sys1 = load_system('sy1', db_connection)
sys2 = load_system('sy2', db_connection)
sys3 = load_system('sy3', db_connection)
sys4 = load_system('sy4', db_connection)
sys5 = load_system('sy5', db_connection)
sys6 = load_system('sy6', db_connection)
sys7 = load_system('sy7', db_connection)
sys8 = load_system('sy8', db_connection)
sys9 = load_system('sy9', db_connection)
sys10 = load_system('sy10', db_connection)
sys11 = load_system('sy11', db_connection)
sys12 = load_system('sy12', db_connection)
sys16 = load_system('sy16', db_connection)
sys17 = load_system('sy17', db_connection)
sys18 = load_system('sy18', db_connection)
sys19 = load_system('sy19', db_connection)
sys21 = load_system('sy21', db_connection)
sys22 = load_system('sy22', db_connection)
sys24 = load_system('sy24', db_connection)
sys25 = load_system('sy25', db_connection)
sys26 = load_system('sy26', db_connection)
sys27 = load_system('sy27', db_connection)
sys28 = load_system('sy28', db_connection)
sys29 = load_system('sy29', db_connection)
sys31 = load_system('sy31', db_connection)
sys32 = load_system('sy32', db_connection)
sys33 = load_system('sy33', db_connection)
sys35 = load_system('sy35', db_connection)
sys36 = load_system('sy36', db_connection)
sys37 = load_system('sy37', db_connection)
sys38 = load_system('sy38', db_connection)
sys39 = load_system('sy39', db_connection)
sys40 = load_system('sy40', db_connection)
sys41 = load_system('sy41', db_connection)



# mass balance check

sys1.balance_check_material_MC("PVCav_20_log", num_simulations)
sys1.balance_check_material_MC("PVCav_20_wei", num_simulations)
sys1.balance_check_substance_MC("PVCav_20_log", "DEHP", num_simulations)



# calculate material flows

sys1.calc_consumption_waste_material_timeline_MC("PVCav_20_log", num_simulations)
sys1.calc_consumption_waste_material_timeline_MC("PVCav_15_log", num_simulations)
sys1.calc_consumption_waste_material_timeline_MC("PVCav_20_wei", num_simulations)
sys1.calc_consumption_waste_material_timeline_MC("PVCav_30_log", num_simulations)



# calculate substance flows

# Figure 1

sys2.calc_substance_concentration_consumption_waste_timeline_MC("PVCav_20_log", "DEHP", num_simulations)
sys2.calc_substance_concentration_consumption_waste_timeline_MC("PVCav_15_log", "DEHP", num_simulations)
sys2.calc_substance_concentration_consumption_waste_timeline_MC("PVCav_20_wei", "DEHP", num_simulations)
sys2.calc_substance_concentration_consumption_waste_timeline_MC("PVCav_30_log", "DEHP", num_simulations)

sys2.calc_substance_concentration_consumption_waste_timeline_MC("PVCav_20_log", "DiNP", num_simulations)
sys2.calc_substance_concentration_consumption_waste_timeline_MC("PVCav_15_log", "DiNP", num_simulations)
sys2.calc_substance_concentration_consumption_waste_timeline_MC("PVCav_20_wei", "DiNP", num_simulations)
sys2.calc_substance_concentration_consumption_waste_timeline_MC("PVCav_30_log", "DiNP", num_simulations)

sys2.calc_substance_concentration_consumption_waste_timeline_MC("PVCav_20_log", "DEHT", num_simulations)
sys2.calc_substance_concentration_consumption_waste_timeline_MC("PVCav_15_log", "DEHT", num_simulations)
sys2.calc_substance_concentration_consumption_waste_timeline_MC("PVCav_20_wei", "DEHT", num_simulations)
sys2.calc_substance_concentration_consumption_waste_timeline_MC("PVCav_30_log", "DEHT", num_simulations)

# Figure 2

sys6.calc_substance_concentration_consumption_waste_timeline_MC("PVCav_20_log", "DEHP", num_simulations)
sys7.calc_substance_concentration_consumption_waste_timeline_MC("PVCav_20_log", "DEHP", num_simulations)

sys3.calc_substance_concentration_consumption_waste_timeline_MC("PVCav_20_log", "DEHP", num_simulations)
sys4.calc_substance_concentration_consumption_waste_timeline_MC("PVCav_20_log", "DEHP", num_simulations)
sys37.calc_substance_concentration_consumption_waste_timeline_MC("PVCav_20_log", "DEHP", num_simulations)

sys8.calc_substance_concentration_consumption_waste_timeline_MC("PVCav_20_log", "DEHP", num_simulations)
sys9.calc_substance_concentration_consumption_waste_timeline_MC("PVCav_20_log", "DEHP", num_simulations)
sys36.calc_substance_concentration_consumption_waste_timeline_MC("PVCav_20_log", "DEHP", num_simulations)

# Figure 3

sys1.calc_substance_concentration_consumption_waste_timeline_MC("PVCav_20_log", "DEHP", num_simulations)
sys32.calc_substance_concentration_consumption_waste_timeline_MC("PVCav_20_log", "DEHP", num_simulations)

# Figure 4

sys11.calc_substance_concentration_consumption_waste_timeline_MC("PVCav_20_log", "DEHP", num_simulations)

sys12.calc_substance_concentration_consumption_waste_timeline_MC("PVCav_20_log", "DEHP", num_simulations)
sys35.calc_substance_concentration_consumption_waste_timeline_MC("PVCav_20_log", "DEHP", num_simulations)
sys38.calc_substance_concentration_consumption_waste_timeline_MC("PVCav_20_log", "DEHP", num_simulations)

sys33.calc_substance_concentration_consumption_waste_timeline_MC("PVCav_20_log", "DEHP", num_simulations)
sys39.calc_substance_concentration_consumption_waste_timeline_MC("PVCav_20_log", "DEHP", num_simulations)
sys40.calc_substance_concentration_consumption_waste_timeline_MC("PVCav_20_log", "DEHP", num_simulations)

sys21.calc_substance_concentration_consumption_waste_timeline_MC("PVCav_20_log", "DEHP", num_simulations)
sys22.calc_substance_concentration_consumption_waste_timeline_MC("PVCav_20_log", "DEHP", num_simulations)
sys24.calc_substance_concentration_consumption_waste_timeline_MC("PVCav_20_log", "DEHP", num_simulations)

# Figure 5

# no additional scenario

# Figures SI

sys1.calc_substance_concentration_consumption_waste_timeline_MC("PVCav_20_log", "DiNP", num_simulations)
sys6.calc_substance_concentration_consumption_waste_timeline_MC("PVCav_20_log", "DiNP", num_simulations)
sys7.calc_substance_concentration_consumption_waste_timeline_MC("PVCav_20_log", "DiNP", num_simulations)
sys21.calc_substance_concentration_consumption_waste_timeline_MC("PVCav_20_log", "DiNP", num_simulations)
sys22.calc_substance_concentration_consumption_waste_timeline_MC("PVCav_20_log", "DiNP", num_simulations)
sys24.calc_substance_concentration_consumption_waste_timeline_MC("PVCav_20_log", "DiNP", num_simulations)
sys25.calc_substance_concentration_consumption_waste_timeline_MC("PVCav_20_log", "DiNP", num_simulations)
sys26.calc_substance_concentration_consumption_waste_timeline_MC("PVCav_20_log", "DiNP", num_simulations)
sys28.calc_substance_concentration_consumption_waste_timeline_MC("PVCav_20_log", "DiNP", num_simulations)
sys29.calc_substance_concentration_consumption_waste_timeline_MC("PVCav_20_log", "DiNP", num_simulations)
sys31.calc_substance_concentration_consumption_waste_timeline_MC("PVCav_20_log", "DiNP", num_simulations)

sys1.calc_substance_concentration_consumption_waste_timeline_MC("PVCav_20_log", "DEHT", num_simulations)
sys27.calc_substance_concentration_consumption_waste_timeline_MC("PVCav_20_log", "DEHT", num_simulations)
sys41.calc_substance_concentration_consumption_waste_timeline_MC("PVCav_20_log", "DEHT", num_simulations)

# not in figure

sys5.calc_substance_concentration_consumption_waste_timeline_MC("PVCav_20_log", "DEHP", num_simulations)
sys10.calc_substance_concentration_consumption_waste_timeline_MC("PVCav_20_log", "DEHP", num_simulations)
sys16.calc_substance_concentration_consumption_waste_timeline_MC("PVCav_20_log", "DEHP", num_simulations)
sys17.calc_substance_concentration_consumption_waste_timeline_MC("PVCav_20_log", "DEHP", num_simulations)
sys18.calc_substance_concentration_consumption_waste_timeline_MC("PVCav_20_log", "DEHP", num_simulations)
sys19.calc_substance_concentration_consumption_waste_timeline_MC("PVCav_20_log", "DEHP", num_simulations)



# plotting material and substance flows

sys1.plot_substance_flows_MC_separately("PVCav_20_log", "DEHP", num_simulations)








