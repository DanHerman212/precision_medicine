import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


# bulk_data_loader.py
def load_dataframes(data_dict, path):
    """
    Loads data from files specified in a DataFrame and assigns each to a DataFrame,
    returned in a dictionary with keys being the variable names.

    Parameters:
    - data_dict (pandas.DataFrame): DataFrame with columns 'Variable' and 'File Name'.
    - path (str): Base path to the data files.

    Returns:
    dict: A dictionary with variable names as keys and loaded DataFrames as values.
    """
    data_frames = {}
    for _, row in data_dict.iterrows():
        variable_name = row["Variable"].lower()
        file_name = row["File Name"]
        try:
            full_path = f"{path}{file_name}"
            df = pd.read_csv(full_path)
            data_frames[variable_name] = df
            print(f"{variable_name} loaded successfully.")
        except FileNotFoundError:
            print(f"File {file_name} not found at {path}.")
        except Exception as e:
            print(f"An error occurred while loading {file_name}: {e}")

    return data_frames


# create helper function
def clean_df(df, keep_cols, rename_cols):
    """
    Clean the given DataFrame by dropping unnecessary columns, renaming columns, and reordering columns.

    Parameters:
    df (pandas.DataFrame): The DataFrame to be cleaned.
    keep_cols (list): A list of column names to keep in the DataFrame.
    rename_cols (dict): A dictionary mapping old column names to new column names.

    Returns:
    pandas.DataFrame: The cleaned DataFrame.
    """
    # drop columns that are not on keep_cols list
    df = df.drop(columns=[col for col in df.columns if col not in keep_cols])

    # cleans the VISIT column, removing text and converting to integers for ordinal value
    if "VISIT" in df.columns:
        # remove 'VISIT' from VISIT column
        df["VISIT"] = df["VISIT"].str.replace("VISIT", "")

        # if VISIT column contains 'BASELINE' replace with 0
        df["VISIT"] = df["VISIT"].str.replace("BASELINE", "0")

        # remove WK in visit column then convert to int
        df["VISIT"] = df["VISIT"].str.replace("WK", "")

        # change VISIT column to int
        df["VISIT"] = df["VISIT"].astype(int)
    else:
        pass

    # rename columns
    df = df.rename(columns=rename_cols)

    # bring 'patdeid' column to 0 index at axis=1
    df = pd.concat([df["patdeid"], df.drop(columns="patdeid")], axis=1)

    return df


def backfill_nulls(df, cols):
    """
    Backfill null values in the given columns with the last non-null value.

    Parameters:
    df (pandas.DataFrame): The DataFrame to be cleaned.
    cols (list): A list of column names to backfill.

    Returns:
    pandas.DataFrame: The cleaned DataFrame.
    """
    for col in cols:
        df[col] = df[col].fillna(method="bfill")
    return df


def flatten_dataframe(df, start, stop, step):
    """
    Flattens a dataframe by creating separate dataframes for each week of clinical data,
    renaming columns with the corresponding week number, and merging all dataframes into one,
    reshaping dataframe to 1 row per patient, with all clinical data properly encoded into columns.

    Args:
        df (pandas.DataFrame): The input dataframe.
        start (int): The starting week number.
        stop (int): The stopping week number.
        step (int): The step size between weeks.

    Returns:
        pandas.DataFrame: The flattened dataframe.

    """
    # create a new dataframe for every week of clinical data
    # the name of the dataframe will be VISIT+number of visit
    for i in range(start, stop + 1, step):
        globals()["VISIT%s" % i] = df[df["VISIT"] == i]

    # for each dataframe beteween start and stop
    # add the value in VISIT to the end of the name of each column +"_"+"visit"
    for i in range(start, stop + 1, step):
        for col in globals()["VISIT%s" % i].columns:
            if col != "patdeid":
                globals()["VISIT%s" % i][col + "_" + str(i)] = globals()["VISIT%s" % i][
                    col
                ]
                # after columns are annoted, drop original columns
                globals()["VISIT%s" % i] = globals()["VISIT%s" % i].drop(columns=col)
            else:
                pass

    # merge all dfs using left merge on patdeid
    for i in range(start, stop + 1, step):
        if i == start:
            df = pd.merge(
                globals()["VISIT%s" % i],
                globals()["VISIT%s" % (i + step)],
                on="patdeid",
                how="left",
            )
        elif i < stop:
            df = pd.merge(
                df, globals()["VISIT%s" % (i + step)], on="patdeid", how="left"
            )
        else:
            pass

            # drop erroneous visit columns, as the visit is encoded in each column
            df = df.drop(
                columns=[col for col in df.columns if col.startswith("VISIT")], axis=1
            )

            return df


# create function to merge dataframes using functools reduce
def merge_dfs(dfs):
    """
    Merge the given list of DataFrames into one DataFrame.

    Parameters:
    dfs (list): A list of DataFrames to be merged.

    Returns:
    pandas.DataFrame: The merged DataFrame.
    """
    from functools import reduce

    df = reduce(
        lambda left, right: pd.merge(left, right, on="patdeid", how="left"), dfs
    )
    return df


def uds_features(df):
    """
    Creates metrics used to measure outcomes from opiate test data, listed as follows:
    1) 'TNT' - Total Negative tests - counts total negative tests per patient

    3) 'CNT' - Consecutive Negative tests - counts number of consecutive weeks of negative tests

    2) 'responder' - A responder is defined as a patient who successfully meets the abstinence window
    with 4 consecutive clean urine tests at the final 4 weeks of treatment

    Parameters:
    df (pandas.DataFrame): The DataFrame containing the opiates data.

    Returns:
    pandas.DataFrame: The processed DataFrame.
    """
    # create df for opiates tests
    tests = df.loc[
        :, ["patdeid"] + [col for col in df.columns if "test_Opiate300" in col]
    ]

    # remove the prefix from the column names
    # tests.columns = tests.columns.str.replace("test_Opiate300_", "")

    # null values will be treated as positive urine tests and filled with 1.0
    tests = tests.fillna(1.0)

    # create column tnt (total negative tests) counts total negative tests for each patient
    tests["TNT"] = (tests.iloc[:, 1:] == 0.0).astype(int).sum(axis=1)

    # create column 'CNT' (consecutive negative tests)
    tests["CNT"] = None

    # convert each column into a list and test results into key value pairs
    # to analyze the number of consecutive negative tests
    # count how many times 0.0 occurs consecutively
    # update the count in tests['CNT'] column

    # import itertools library
    import itertools

    for i in range(0, tests.shape[0]):
        values = [
            len(list(v)) for k, v in itertools.groupby(tests.iloc[i, 1:26]) if k == 0.0
        ]
        tests["CNT"][i] = max(values) if values else 0

    # create column 'responder' - defined as a patient that reaches abstinent window
    # observe the number in columns 21 - 24 if the sum is equal to zero then value in responder column is 1.0 else 0.0
    tests["responder"] = np.where(
        (tests.iloc[:, 21:26].sum(axis=1) == 0), 1.0, 0.0
    ).astype(int)

    return tests


def med_features(df):
    """
    Process the medication dataframe by creating separate columns for methadone dose and buprenorphine dose,
    filling null values with 0, and dropping unnecessary columns.

    Parameters:
    df (pandas.DataFrame): The medication dataframe.

    Returns:
    pandas.DataFrame: The processed dataframe.
    """

    # create new columns for methadone and buprenorphine dose
    df["meds_methadone"] = df.loc[df.medication == 1.0]["total_dose"]
    df["meds_buprenorphine"] = df.loc[df.medication == 2.0]["total_dose"]

    # fill null values with 0
    df.meds_methadone.fillna(0, inplace=True)
    df.meds_buprenorphine.fillna(0, inplace=True)

    # drop original columns to remove redundancy
    df = df.drop(columns=["total_dose", "medication"])

    return df


# store markdown as local variable
markdown_table = """
    | File Name | Table Name | Variable |Description |
    | :--- | :--- | :--- | :--- |
    | T_FRRSA.csv | Research Session Attendance|RSA |Records attendence for each week of treatment |
    | T_FRDEM.csv | Demographics|DEM |Sex, Ethnicity, Race |
    | T_FRUDSAB.csv | Urine Drug Screen| UDS  |Drug test for 8 different drug classes, taken weekly for 24 weeks |
    | T_FRDSM.csv | DSM-IV Diagnosis|DSM |Tracks 6 different conditions|
    | T_FRMDH.csv | Medical and Psychiatric History|MDH |Tracks 24 different Conditions|
    | T_FRPEX.csv | Physical Exam|PEX |Tracks 12 different physical observations|
    | T_FRPBC.csv | Pregnancy and Birth Control|PBC |Tracks 2 different conditions|
    | T_FRTFB.csv | Timeline Follow Back Survey|TFB |Surveys for self reported drug use, collected every 4 weeks, includes previous 30 days of use|
    | T_FRABZ.csv | Alcohol Breathalyzer |ABZ |Breathalyzer test for alcohol, taken weekly for 24 weeks|
    |T_FRDOS.csv | Dose Record |DOS |Records the dose of medication taken each week for 24 weeks|
    |SAE.csv | Serious Adverse Events |SAE |Records any serious adverse events that occur during the study|
    """


def markdown_table_to_df(markdown_table):
    """
    Converts a Markdown table string into a pandas DataFrame.

    Parameters:
    - markdown_table (str): The Markdown table as a string.

    Returns:
    - pd.DataFrame: DataFrame representation of the Markdown table.
    """

    # Split the table into rows and remove any empty lines
    rows = [row.strip() for row in markdown_table.strip().split("\n") if row]

    # Extract column names from the first row
    columns = [col.strip() for col in rows[0].split("|") if col]

    # Initialize an empty list to hold row data
    data = []

    # Iterate over the remaining rows
    for row in rows[2:]:  # Skip the header and separator rows
        values = [value.strip() for value in row.split("|") if value]
        row_data = dict(zip(columns, values))
        data.append(row_data)

    # Convert the list of dictionaries to a DataFrame
    df = pd.DataFrame(data)

    return df
