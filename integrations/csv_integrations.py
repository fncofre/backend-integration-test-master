"""This is the module for .csv integrations.

This module have all the necessary methods for prepare 
the data to be used in the api_integration and ingestion.
"""

import re
import os

import pandas as pd
import numpy as np


def open_csv_url(url: str) -> pd.DataFrame:
    """Read the .csv directly from the URL

    Separated by '|', and 'nan' transformed to ''
    Return: a Pandas.DataFrame or False
    """
    try:
        return pd.read_csv(url, sep='|', na_filter=False)
    except Exception:
        return False


def save_csv(df: pd.DataFrame, name: str):
    """Save the DataFrame in data folder as .csv

    Separated by '|', and without index
    Return: True
    """
    path = './data'
    if not os.path.exists(path):
        os.mkdir(path)
    df.to_csv(f'./data/{name}.csv', index=None, sep='|')
    return True


def merge_df_byfield(df1: pd.DataFrame, df2: pd.DataFrame, field: str):
    """Return: a Merged DataFrame by field"""
    return pd.merge(df1, df2, on=field)


def filter_df_bycolumn(df: pd.DataFrame, column: str, filters: list):
    """Filter the DataFrame 

    Cheking if the values from a 'column' exist in the filters
    Return: filtered DataFrame
    """
    filt = df[column].isin(filters)
    return df.loc[filt]


def filter_df_byamount(df: pd.DataFrame, column: str, n: int):
    """Filter the DataFrame 

    Cheking if the values from a 'column' are bigger than 'n'
    Return: filtered DataFrame
    """
    filt = df[column] > n
    return df.loc[filt]


def remove_df_duplicates(df: pd.DataFrame, column: str):
    """Remove duplicates from DataFrame 

    Remove rows where the values from a 'column' are repeated
    (Keeps the first match)
    Return: DataFrame without duplicates
    """
    filt = df[column].duplicated(keep='first')
    return df.loc[~filt]


def clean_df_tags(df: pd.DataFrame, column: str):
    """Clean the 'column' values of DataFrame 

    Erasing HTML tags from the values of 'column'
    Return: Cleaned DataFrame
    """
    cleanr = re.compile('<.*?>')
    df[column] = [re.sub(cleanr, '', x) for x in df[column]]
    return df


def update_df_prices(df: pd.DataFrame):
    """Transform the structure of 'prices_df' DataFrame 

    From: SKU|BRANCH|PRICE|STOCK - To: SKU|BRANCH_PRODUCTS
    BRANCH_PRODUCTS: [{BRANCH|PRICE|STOCK}, ...] 
    Return: new DataFrame
    """
    product_data = {}
    for row in df.itertuples():
        key = str(row[1])
        value = {
            'branch': row[2],
            'stock': row[4],
            'price': row[3]
        }
        if key not in product_data:
            product_data[key] = [value]
        else:
            product_data[key].append(value)
    df = pd.DataFrame(list(product_data.items()),
                      columns=['SKU', 'BRANCH_PRODUCTS'])
    df['SKU'] = pd.to_numeric(df['SKU'])
    return df


def update_df_package(df: pd.DataFrame):
    """Fill the package with null values of DataFrame 

    Filling the field with corresponding package value from item_description
    Return: DataFrame without null package values
    """
    key_words = ['UN', 'PZ', 'CC', 'LT']
    for row in df.itertuples():
        for word in key_words:
            if word in row.ITEM_DESCRIPTION:
                package = 'UN'
                break
            else:
                package = 'KG'
        if row.BUY_UNIT == '':
            df.at[row.Index, 'BUY_UNIT'] = package
    return df


def join_df_columns(df: pd.DataFrame, column: str, drop_columns: list, sep: str):
    """Join the columns of the DataFrame 

    Joining the columns with the drop ones separated by 'sep'
    Return: DataFrame with new 'column' and dropped 'drop_columns'
    """
    df[column] = df[column].str.cat(df[drop_columns], sep=sep)
    df[column] = df[column].str.lower()
    for col in drop_columns:
        df.drop(col, inplace=True, axis=1)
    return df


def select_df_n_highest_branch(df: pd.DataFrame, n: int, column: str):
    """Select n highest values from 'column' for each branch

    Return: ranked DataFrame
    """
    return df.sort_values(column, ascending=False).groupby('BRANCH').head(n)
