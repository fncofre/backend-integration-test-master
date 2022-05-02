"""This is the ingestion module.

This module imports api_integrations and csv_integrations,
to be able to do all the required tasks.
Needs to read "credentials.json" which contains
the client credentials Global variables for OAuth2,
and the BASE_URL of the API.
"""

import numpy as np
import pandas as pd
import json
import os

import integrations.csv_integrations as ci
import integrations.api_integrations as ai


def process_csv_files(n: int, branches_names: list):
    """Does all the required processing to the .csv

    Imports all the necessary methods from
    csv_integrations to perform the assigned tasks.
    Return: store_df and save it on .data/
    """
    prices_url = 'https://cornershop-scrapers-evaluation.s3.amazonaws.com/public/PRICES-STOCK.csv'
    products_url = 'https://cornershop-scrapers-evaluation.s3.amazonaws.com/public/PRODUCTS.csv'
    prices_df = ci.open_csv_url(prices_url)
    products_df = ci.open_csv_url(products_url)

    prices_df = ci.filter_df_bycolumn(prices_df, 'BRANCH', branches_names)
    prices_df = ci.filter_df_byamount(prices_df, 'STOCK', 0)
    prices_df = ci.select_df_n_highest_branch(prices_df, n, 'PRICE')

    prices_df = ci.update_df_prices(prices_df)
    store_df = ci.merge_df_byfield(products_df, prices_df, 'SKU')
    del prices_df, products_df
    store_df = ci.clean_df_tags(store_df, 'ITEM_DESCRIPTION')
    store_df = ci.join_df_columns(
        store_df, 'CATEGORY', ['SUB_CATEGORY', 'SUB_SUB_CATEGORY'], '|')
    store_df = ci.update_df_package(store_df)

    ci.save_csv(store_df, 'store_products')
    return store_df


def process_api_calls(df: pd.DataFrame, from_n: int, to_n: int):
    """Does all the required API calls

    Imports all the necessary methods from
    api_integrations to perform the assigned tasks.
    """
    token, BASE_URL = ai.get_credentials()
    stores_dict = ai.get_stores_ids(token, BASE_URL)
    richard_id = ai.get_merchant_id(stores_dict, "Richard's")
    beauty_id = ai.get_merchant_id(stores_dict, 'Beauty')

    merch_data = {
        'can_be_deleted': False,
        'can_be_updated': True,
        'id': richard_id,
        'is_active': True,
        'name': "Richard's"
    }

    ai.update_merchant(
        token, BASE_URL, f'/api/merchants/{richard_id}', merch_data)
    ai.delete_merchant(token, BASE_URL, f'/api/merchants/{beauty_id}')
    ai.post_products(token, BASE_URL, richard_id, df, from_n, to_n)
