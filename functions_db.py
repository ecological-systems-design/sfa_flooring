import pandas as pd
import sqlalchemy as sa
import mysql.connector
from classes import Scenario, Process, Material, Flow, System
import matplotlib
matplotlib.use('Agg', force=True)



def return_engine(db_connection_string: str) -> sa.engine:
    """
    Returns a sqlalchemy engine object for a given database connection string. Sets isolation level to 'AUTOCOMMIT' (to avoid errors when creating schemas).
    """

    engine = sa.create_engine(db_connection_string)
    return engine



def upload_to_database(df: pd.DataFrame, table_name: str, schema_name: str, db_engine) -> None:
    """
    Uploads a dataframe to the specified database.
    """

    df.to_sql(table_name, db_engine, schema=schema_name, if_exists='replace', index=False)


    return None



def upload_all_excel_tables(excel_storage_location: str, db_engine: sa.engine) -> None:

    # Read data from Excel
    xl = pd.ExcelFile(excel_storage_location)

    for sheet_name in xl.sheet_names:  # in xl.sheet_names[:31]
        table_df = pd.read_excel(excel_storage_location, sheet_name=sheet_name)

        # Upload data to database
        try:
            upload_to_database(table_df, sheet_name, 'sfa', db_engine)
            print("Upload to database successful")
        except:
            print('Error: Could not upload data to database.')

    return None



def upload_one_excel_table(excel_storage_location: str, excel_sheet_name: str, db_engine: sa.engine) -> None:

    # Read data from Excel
    table_df = pd.read_excel(excel_storage_location, sheet_name = excel_sheet_name)

    # Upload data to database
    try:
        upload_to_database(table_df, excel_sheet_name, 'sfa', db_engine)

    except:
        print('Error: Could not upload GWR data to database.')


    print("Upload to database successful")

    return None



def query_db_to_df(sql: str, engine: sa.engine) -> pd.DataFrame:
    """
    Returns a dataframe from a sql query.
    """

    # Execute sql query
    with engine.connect() as conn:
        df = pd.read_sql_query(sql, conn)
        conn.close()
    return df



def load_system(id, db_engine) -> System:

    # get system parameters

    sql = f'SELECT * FROM system WHERE id = "{id}"'
    system_df = query_db_to_df(sql=sql, engine=db_engine)



    # create entity Scenario for scenario of system

    # get scenario parameters

    system_scenario_id = system_df["scenario"][0]
    sql = f'SELECT * FROM scenarios WHERE id = "{system_scenario_id}"'
    system_scenario_df = query_db_to_df(sql=sql, engine=db_engine)

        # derive RRs, TCs and composition for scenario

    RRs_table_name = system_scenario_df["RR"][0]
    sql = f'SELECT * FROM {RRs_table_name};'
    RR_df = query_db_to_df(sql=sql, engine=db_engine)

    TCs_past_table_name = system_scenario_df["TCs_past"][0]
    sql = f'SELECT * FROM {TCs_past_table_name};'
    TCs_past_df = query_db_to_df(sql=sql, engine=db_engine)

    TCs_future1_table_name = system_scenario_df["TCs_future1"][0]
    sql = f'SELECT * FROM {TCs_future1_table_name};'
    TCs_future1_df = query_db_to_df(sql=sql, engine=db_engine)

    TCs_future2_table_name = system_scenario_df["TCs_future2"][0]
    sql = f'SELECT * FROM {TCs_future2_table_name};'
    TCs_future2_df = query_db_to_df(sql=sql, engine=db_engine)

    composition_table_name = system_scenario_df["composition"][0]
    sql = f'SELECT * FROM {composition_table_name};'
    composition_df = query_db_to_df(sql=sql, engine=db_engine)

    scenario = Scenario(system_scenario_id, TCs_past_df, TCs_future1_df, TCs_future2_df, RR_df, composition_df)




    flows_table_name = system_df["mat_flows"][0]
    sql = f'SELECT * FROM {flows_table_name};'
    flows_df = query_db_to_df(sql=sql, engine=db_engine)

    flows = []
    i=0
    for index, row_flows in flows_df.iterrows():
        i+=1
        # retrieve material of flow for all flows of system
        material_flow = row_flows["material"]



        # create entity Material from database data on material of flow and composition (list of Composition entities)
        sql = f'SELECT * FROM materials WHERE id = "{material_flow}";'
        material_df = query_db_to_df(sql=sql, engine=db_engine)

        try:
            material = Material(
                material_df["id"][0],
                material_df["product"][0],
                material_df["type"][0],
                material_df["lifetime"][0],
                material_df["lifetime_dist"][0],
                material_df["dist_par1"][0],
                material_df["dist_par2"][0]
            )

        except:
            print(f"material {material_flow} does not exist")

        processes_table_name =system_df["processes"][0]

        # derive flow's origin process for scenario
        sql = f'SELECT * FROM {processes_table_name} where id = {row_flows["origin"]};'
        process_df = query_db_to_df(sql=sql, engine=db_engine)
        for index, process in process_df.iterrows():
            process_origin = Process(process["id"], process["name"])

        # derive flow's destination process with TCs for scenario
        sql = f'SELECT * FROM {processes_table_name} where id = {row_flows["destination"]};'
        process_df = query_db_to_df(sql=sql, engine=db_engine)
        for index, process in process_df.iterrows():
            process_destination = Process(process["id"], process["name"])

        # create entity Flow from database data on flow and Material entity
        flow = Flow(
            row_flows["year"],
            process_origin,
            process_destination,
            row_flows["amount"],
            row_flows["amount_dist"],
            row_flows["dist_par1"],
            row_flows["dist_par2"],
            material
        )
        flows.append(flow)

    sql = f'SELECT * FROM {processes_table_name};'
    processes_system_df = query_db_to_df(sql=sql, engine=db_engine)

    
    system = System(
        system_df["id"][0],
        system_df["location"][0],
        system_df["year_start"][0],
        system_df["year_end"][0],
        processes_system_df,
        flows,
        scenario,
        system_df["unit"][0]
    )

    return system





