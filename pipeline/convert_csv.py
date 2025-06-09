import pandas as pd
from utils.constants import file_to_csv, col_to_drop

def remove_commas(df):
    """
    Replace commas with dots in all string columns of a dataframe
    
    Parameters
    ----------
    df : pandas.DataFrame
        The dataframe to convert
        
    Returns
    -------
    pandas.DataFrame
        The converted dataframe
    """
    return df.applymap(lambda x: x.replace(',', '.') if isinstance(x, str) else x)

def add_cadastre(df):
    """
    Add a "Cadastre" column to a dataframe by concatenating several existing columns
    
    Parameters
    ----------
    df : pandas.DataFrame
        The dataframe to modify
        
    Returns
    -------
    pandas.DataFrame
        The modified dataframe
    """
    
    
    df["Code departement"] = df["Code departement"].astype(str).str.zfill(2)
    df["Code commune"] = df["Code commune"].astype(str).str.zfill(3)

    df["Cadastre"] = (
        df["Code departement"] +
        df["Code commune"] +
        df["Section"]
    )
    return df

def remove_mixed_commercial_apartment(df):
    # Define transaction keys (adjust if needed)
    """
    Remove apartment rows from a dataframe that are part of transactions that contain both apartments and commercial properties.

    Parameters
    ----------
    df : pandas.DataFrame
        The dataframe to clean
        
    Returns
    -------
    pandas.DataFrame
        The cleaned dataframe
    """

    transaction_cols = ["Date mutation", "Valeur fonciere", "Code postal", "Voie"]

    # Identify transaction groups that contain both apartment and commercial
    grouped = df.groupby(transaction_cols)["Type local"].agg(set).reset_index()
    mixed = grouped[grouped["Type local"].apply(lambda x: {"Appartement", "Local industriel. commercial ou assimilé"}.issubset(x))]

    # Merge back to original df to flag matching transactions
    mixed["flag"] = True
    df = df.merge(mixed[transaction_cols + ["flag"]], on=transaction_cols, how="left")

    # Remove apartment rows that are part of mixed transactions
    df = df[~((df["flag"] == True) & (df["Type local"] == "Appartement"))]

    # Drop the flag column
    df = df.drop(columns=["flag"])
    return df


def remove_useless(df, col_to_drop):
    """
    Remove useless columns and rows from a dataframe
    
    Parameters
    ----------
    df : pandas.DataFrame
        The dataframe to clean
    
    Returns
    -------
    pandas.DataFrame
        The cleaned dataframe
    """
    
    df = df.drop(col_to_drop, axis=1)
    df = df[df["Type local"] == "Appartement"]
    return df

def merge_rows(df):
    """
    Aggregate rows in the dataframe by summing 'Surface reelle bati'.

    Parameters
    ----------
    df : pandas.DataFrame
        The dataframe to process.

    Returns
    -------
    pandas.DataFrame
        A dataframe with rows grouped by all columns except 'Surface reelle bati',
        where 'Surface reelle bati' values are summed.
    """

    group_cols = df.columns.difference(['Surface reelle bati']).tolist()
    return df.groupby(group_cols, dropna=False, as_index=False)['Surface reelle bati'].sum()


def convert_txt(file_to_csv):
    """
    Convert multiple text files to CSV files by applying a series of transformations

    Parameters
    ----------
    file_to_csv : dict
        A dictionary mapping the input file paths to the output file paths

    Returns
    -------
    None

    Notes
    -----
    The following transformations are applied:

    1. Remove commas from string columns
    2. Add the 'Cadastre' column
    3. Convert columns to numeric if possible
    4. Remove useless columns and rows
    5. Merge rows by summing 'Surface reelle bati'
    6. Write the resulting dataframe to a CSV file
    """
    for file in file_to_csv.keys():
        df = pd.read_csv(file, sep="|", encoding="utf-8")
        df = remove_commas(df)
        df = add_cadastre(df)
        df = df.apply(pd.to_numeric, errors='ignore')
        df = remove_mixed_commercial_apartment(df)
        df = remove_useless(df, col_to_drop)
        df = merge_rows(df)
        df.to_csv(file_to_csv[file], index=False, sep=",", encoding="utf-8")

if __name__ == "__main__":
    convert_txt(file_to_csv)
    print("Conversion complete.")
