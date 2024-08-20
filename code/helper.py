import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import re


# clean df function
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

    2) 'CNT' - Consecutive Negative tests - counts number of consecutive weeks of negative tests

    3) 'responder' - A responder is defined as a patient who successfully meets the abstinence window
    with 4 consecutive clean urine tests at the final 4 weeks of treatment

    4) 'NTR' - Negative Test Rate - counts the number of negative tests per patient

    Parameters:
    df (pandas.DataFrame): The DataFrame containing the opiates data.

    Returns:
    pandas.DataFrame: The processed DataFrame.
    """
    # create df for opiates tests
    tests = df.loc[
        :, ["patdeid"] + [col for col in df.columns if "test_opiate300" in col]
    ]

    # remove the prefix from the column names
    # tests.columns = tests.columns.str.replace("test_Opiate300_", "")

    # null values will be treated as positive urine tests and filled with 1.0
    tests = tests.fillna(1.0)

    # create column tnt (total negative tests) counts total negative tests for each patient
    tests["TNT"] = (tests.iloc[:, 1:] == 0.0).astype(int).sum(axis=1)

    # create NTR column - negative test rate
    tests["NTR"] = tests.TNT / 25

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
    df["meds_methadone"] = df.loc[df.medication == 1.0]["avg_daily_dose"]
    df["meds_buprenorphine"] = df.loc[df.medication == 2.0]["avg_daily_dose"]

    # fill null values with 0
    df.meds_methadone.fillna(0, inplace=True)
    df.meds_buprenorphine.fillna(0, inplace=True)

    # drop original columns to remove redundancy
    df = df.drop(columns=["avg_daily_dose", "medication"])

    return df


def series_func(df, group, agg="mean"):
    """
    Create series from wide dataset, by specifying the
    data category your are looking for.

    Parameters:
    df: pandas dataframe, data to be aggregated
    group: str, data category
    agg: str, aggregation function

    Returns:

    """
    # subset columns for data group specified
    df = df[[col for col in df.columns if group in col]]

    # remove the prefix and feature name from the column names
    df.columns = [
        "_".join(col.split("_")[2:]) if len(col.split("_")) > 2 else col
        for col in df.columns
    ]

    # create condition for aggregation
    if agg == "mean":
        series = df.mean()
    elif agg == "sum":
        series = df.sum()

    return series


def plot_func(series, title, ylabel, xlabel):
    """
    Plot the data series.

    Parameters:
    series: pandas series, data series to plot
    title: str, title of the plot

    Returns:

    """
    fig = plt.figure(figsize=(14, 4))
    # take input to plot in a loop with subplots
    sns.barplot(x=series.index, y=series.values.flatten(), color="gray")
    plt.axhline(y=series.mean(), color="black", linestyle="--")
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)


def df_value_counts(df):
    """
    This function takes a DataFrame and returns a DataFrame with the value counts of each column.

    Parameters:
    df: pandas DataFrame


    Returns:
    pandas DataFrame

    """

    # Use a different variable name to avoid confusion
    count_dfs = [df[col].value_counts().reset_index(name="count") for col in df.columns]

    # Process each DataFrame in count_dfs
    for temp_df in count_dfs:
        temp_df["percentage"] = (temp_df["count"] / temp_df["count"].sum()).round(2)
        temp_df.rename(columns={"index": "value"}, inplace=True)

    # Instantiate a new DataFrame for the result
    result_df = pd.DataFrame()

    # Append the processed DataFrames to result_df
    for i, temp_df in enumerate(count_dfs):
        # Use pd.concat instead of append
        result_df = pd.concat(
            [
                result_df,
                pd.DataFrame(
                    {
                        "column": [df.columns[i]] * temp_df.shape[0],
                        "value": temp_df.iloc[:, 0],
                        "count": temp_df["count"],
                        "percentage": temp_df["percentage"],
                    }
                ),
            ],
            ignore_index=True,
        )

    return result_df


def plot_weekly_data(df, drug_dict, group):
    """
    This function plots the weekly data for each drug class.

    Parameters:
    df: pandas DataFrame, data to be plotted
    drug_dict: dict, dictionary with drug acronyms as keys and drug names as values

    Returns:

    """
    # iterate through list of drug test names (9 totla)
    for i, col in enumerate(df.columns):
        # next 4 steps make variables available for each plot
        drug_names = df.columns[i]  # this is a list available for plotting
        # create condition for survey vs. tests
        if group == "survey_":
            title = f"{drug_dict[col].capitalize()} Monthly Instance of Self Reported Drug Use"  # title argument for plot_func()
        else:
            title = f"{drug_dict[col].capitalize()} Drug Screen: Positive Test Rate"  # title argument for plot_func()
        ylabel = "Number of Positive Tests"  # ylabel argument for plot_func()
        xlabel = "Week of Treatment"  # xlabel argument for plot_func()

        # the next 5 steps create the plot, apply annotation to project the insights to the user
        if group == "survey_":
            fig = plt.figure(figsize=(14, 4))
            sns.barplot(
                x=df.index, y=col, data=df, color="gray"
            )  # use seaborn to create a barplot
            plt.axhline(
                df[col].mean(), color="red", linestyle="--", linewidth=1
            )  # Add mean to show change from central tendency
            plt.annotate(  # create a small text box showing a float with positive test rate
                # create conditions for survey vs. tests
                f"Monthly average of {df[col].mean().round(2)} reported instances of {drug_dict[col].capitalize()} use",
                xy=(0.5, 0.5),
                xycoords="axes fraction",
                ha="center",
                va="center",
                fontsize=12,
                color="black",
                backgroundcolor="white",
            )
        else:
            fig = plt.figure(figsize=(14, 4))
            sns.barplot(
                x=df.index, y=col, data=df, color="gray"
            )  # use seaborn to create a barplot
            plt.axhline(
                df[col].mean(), color="red", linestyle="--", linewidth=1
            )  # Add mean to show change from central tendency
            plt.annotate(  # create a small text box showing a float with positive test rate
                # create conditions for survey vs. tests
                f"Weekly average {df[col].mean().round(2)} positive test rate",
                xy=(0.5, 0.5),
                xycoords="axes fraction",
                ha="center",
                va="center",
                fontsize=12,
                color="black",
                backgroundcolor="white",
            )
        # Add plot titles and labels
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)

        plt.show()  # Display the plot


def agg_weekly_data(df, group, agg):
    """
    This function aggregates the weekly data for a specified group of data.
    The aggregated data will be organized in a dataframe, ideal for plotting
    and extracting meaningful insights.

    Parameters:
    df: pandas DataFrame, data to be aggregated
    group: str, data category e.g 'test', 'meds'
    agg: str, aggregation function e.g. 'sum', 'mean'

    Returns:
    pandas DataFrame

    """
    # create a series for each drug class
    import re

    # subset data
    weekly_data = df[[col for col in df.columns if col.startswith(group)]]

    # Pull out the drug names for plotting

    # set conditions for survey, vs. tests
    if group == "survey_":
        drug_cols = weekly_data.iloc[:, :10]
    else:
        drug_cols = weekly_data.iloc[:, :9]

    # trim the column names to remove prefix and suffix
    # the list comprehension uses regex to remove prefix and suffix
    # an example would be transform test_Opiate300_1 to Opiate300
    drug_cols = [re.sub(r"^.*?_(.*?)_.*$", r"\1", s) for s in drug_cols.columns]

    # create acronyms for drugs in dataframe for easier reading
    # an example would be transform Opiate300 to opi
    # provides easier reading for the dataframe
    acronym_cols = [col.lower()[:3] for col in drug_cols]

    print("Series created for each drug class:")
    # create a series for each drug class
    for i in range(len(drug_cols)):
        acronym = acronym_cols[i]  # get the acronym for the drug
        drug = drug_cols[i]  # get the drug name
        # set condition for survey vs. tests
        if group == "survey_":
            globals()[acronym] = series_func(df, "survey_" + drug, agg="sum").round(2)
        else:
            globals()[acronym] = series_func(df, group + drug, agg).round(2)

        globals()[acronym] = globals()[acronym].to_frame(acronym)
        print(acronym, "created with shape of:", globals()[acronym].shape)

    # merge all series into one dataframe
    merged_df = pd.concat([pro, amp, can, ben, mme, oxy, coc, met, opi], axis=1)

    # create dict with full drug names and acronyms
    drug_dict = dict(zip(acronym_cols, drug_cols))
    print("Series created for each drug class:")
    print()
    print("drug_tests Dataframe:  Positive test rate per drug class")

    plot_weekly_data(merged_df, drug_dict, group)

    return merged_df, drug_dict


def search_suffix(col_name):
    """
    Function to check if the suffix of the column name is numerically <= 4
    The suffix represents the week of treatment
    we only want columns that include data from the first 4 weeks of treat

    Parameters:
    col_name (str): The column name to check

    Returns:
    bool: True if the suffix is <= 4, False

    """
    # Use the re module to search for a pattern at the end of the string
    match = re.search(
        r"(\d+)$", col_name
    )  # Look for one or more digits at the end of the string
    if match:
        return (
            int(match.group(1)) <= 4
        )  # Convert the found digits to an integer and check if <= 4
    return False


def feature_selection(df, prefix, feature_list):
    """
    Selects features from tests and survey data to form granualar level data quality
    when building data models for machine learning

    Parameters:
    df (pandas.DataFrame): The DataFrame containing the tests and survey data.
    feature_list (list): A list of drug names to select from the DataFrame.

    Returns:
    pandas.DataFrame: The selected features from the DataFrame.

    """

    matching_columns = [
        col
        for col in df.columns
        if any(
            col.startswith(prefix + drug) and search_suffix(col)
            for drug in feature_list
        )
    ]

    # Use the matching_columns list to select the columns from the DataFrame
    tests = df[matching_columns]

    print("Shape of tests DataFrame:", tests.shape)
    display(tests)

    return tests


import lifelines


def cindex(y_true, scores):
    """
    Calculate the concordance index for the given true values and predicted scores.
    Parameters:
    y_true (array-like): The true values.
    scores (array-like): The predicted scores.
    Returns:
    float: The concordance index.
    """
    return lifelines.utils.concordance_index(y_true, scores)


# create a function to plot confusionmatrixdisplay for each classifier
def plot_confusion_matrix(
    y_true, y_pred, classes, normalize=False, title=None, cmap=plt.cm.Blues
):
    """
    This function prints and plots the confusion matrix.
    Normalization can be applied by setting `normalize=True`.
    """
    from sklearn.metrics import confusion_matrix

    if not title:
        if normalize:
            title = "Normalized confusion matrix"
        else:
            title = "Confusion matrix, without normalization"

    # Compute confusion matrix
    cm = confusion_matrix(y_true, y_pred)
    if normalize:
        cm = cm.astype("float") / cm.sum(axis=1)[:, np.newaxis]
    else:
        pass
    fig, ax = plt.subplots()
    im = ax.imshow(cm, interpolation="nearest", cmap=cmap)
    ax.figure.colorbar(im, ax=ax)
    # We want to show all ticks...
    ax.set(
        xticks=np.arange(cm.shape[1]),
        yticks=np.arange(cm.shape[0]),
        # ... and label them with the respective list entries
        xticklabels=classes,
        yticklabels=classes,
        title=title,
        ylabel="True label",
        xlabel="Predicted label",
    )

    # Rotate the tick labels and set their alignment.
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")

    # Loop over data dimensions and create text annotations.
    fmt = ".2f" if normalize else "d"
    thresh = cm.max() / 2.0
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            ax.text(
                j,
                i,
                format(cm[i, j], fmt),
                ha="center",
                va="center",
                color="white" if cm[i, j] > thresh else "black",
            )
    fig.tight_layout()
    return ax


def plot_feature_importance(model, preprocessor, X, metric="gain", num_features=25):
    """
    Plot the feature importance of a model.

    Parameters:
    - model: The trained model.
    - preprocessor: The preprocessing ColumnTransformer.
    - X: The input features.
    - metric: The feature importance metric to use (default: 'gain').
    - num_features: The number of top features to plot (default: 25).

    Returns:
    - None (plots the feature importance).
    """
    # Get feature importances
    importances = model.get_booster().get_score(importance_type=metric)

    # Extract feature names from the preprocessor
    feature_names = []

    for name, transformer, columns in preprocessor.transformers_:
        if hasattr(transformer, "categories_"):
            # OneHotEncoder case
            for i, cat in enumerate(transformer.categories_):
                feature_names.extend([f"{columns[i]}_{category}" for category in cat])
        else:
            feature_names.extend(columns)

    # Map feature indices to feature names
    importances_named = {feature_names[int(k[1:])]: v for k, v in importances.items()}

    # Round importances
    importances_rounded = {k: round(v, 2) for k, v in importances_named.items()}

    # Sort features by importance
    sorted_importances = sorted(
        importances_rounded.items(), key=lambda x: x[1], reverse=True
    )[:num_features]

    # Create DataFrame for plotting
    importance_df = pd.DataFrame(sorted_importances, columns=["Feature", "Importance"])

    # Plot the feature importances
    plt.figure(figsize=(10, 6))
    bars = plt.barh(importance_df["Feature"], importance_df["Importance"])
    plt.xlabel("Importance")
    plt.ylabel("Feature")
    plt.title(f"Feature Importance - Gain")
    plt.gca().invert_yaxis()  # Invert y-axis to have the most important feature at the top

    # Annotate the bars with the importance values
    for bar in bars:
        plt.text(
            bar.get_width(),
            bar.get_y() + bar.get_height() / 2,
            f"{bar.get_width():.2f}",
            va="center",
        )

    plt.show()

    return importance_df


def plot_dependence(feature1, feature2, feature3, feature4, shap_values, X_test):
    """
    create a pair of SHAP dependence plots for the given features.

    Parameters:
    - feature1: The name of the first feature.
    - feature2: The name of the second feature.
    - feature3: The name of the third feature.
    - feature4: The name of the fourth feature.

    - X_test: The test set.
    - shap_values: The SHAP values for the test set.

    Returns:
    - None: This function displays a pair of SHAP dependence plots.

    """
    import shap

    # Extract SHAP values for the dependence plot

    # Create a figure with subplots
    fig, axes = plt.subplots(1, 2, figsize=(15, 5))

    # Plot the first SHAP dependence plot
    shap.dependence_plot(
        feature1,
        shap_values,
        X_test,
        interaction_index=feature2,
        show=False,
        ax=axes[0],
    )
    axes[0].set_title(f"Dependence Plot for {feature1}")

    # Plot the second SHAP dependence plot
    shap.dependence_plot(
        feature3,
        shap_values,
        X_test,
        interaction_index=feature4,
        show=False,
        ax=axes[1],
    )
    axes[1].set_title(f"Dependence Plot for {feature3}")

    # Show the plots
    plt.tight_layout()
    plt.show()

