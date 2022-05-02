"""This is the module for the API integration.

This module have all the necessary methods to 
communicate with the API, and Authentication.
"""

import requests
import json
import os

import pandas as pd


def get_credentials():
    """Get the credentials for Authentication

    r.POST client credentials to get token
    Return: (access token, BASE_URL) or status_code
    """
    creds = read_credentials()
    path_url = f'/oauth/token?client_id={creds["CLIENT_ID"]}&client_secret={creds["CLIENT_SECRET"]}&grant_type={creds["GRAND_TYPE"]}'
    r = requests.post(creds['BASE_URL']+path_url)
    if r.status_code == 200:
        content = deserialize_bytes(r.content)
        return (f"Bearer {content['access_token']}", creds['BASE_URL'])
    else:
        return r.status_code


def read_credentials():
    """Search 'credentials.json' file to get API-credentials

    Return: Dictionary with all the variables from 'credentials.json'
    """
    if not os.path.isfile("credentials.json"):
        print("'credentials.json' not found! Please add it and try again.")
        return False
    else:
        with open("credentials.json") as file:
            return json.load(file)


def get_stores_ids(token: str, BASE_URL: str):
    """Get the dictionary with all merchants from API

    Return: merchants dictionary or status_code
    """
    path_url = '/api/merchants'
    r = requests.get(BASE_URL+path_url, headers={'token': token})
    if r.status_code == 200:
        return deserialize_bytes(r.content)
    else:
        return r.status_code


def deserialize_bytes(content: bytes):
    """Return: dictionary transformed from bytes"""
    return json.loads(content.decode('utf-8'))


def get_merchant_id(stores: dict, name: str):
    """Get the id of the 'name' merchant from list

    Return: merchant id or false
    """
    for merchant in stores['merchants']:
        if merchant['name'] == name:
            return merchant['id']
    return False


def update_merchant(token: str, BASE_URL: str, path: str, merch_data: dict):
    """Update the selected merchant ('path') from API

    Replacing the old one with 'merch_data' 
    Return: merchant dictionary updated or status_code
    """
    headers = {'token': token}
    r = requests.put(BASE_URL+path, headers=headers, json=merch_data)
    if r.status_code == 200:
        return deserialize_bytes(r.content)
    else:
        return r.status_code


def delete_merchant(token: str, BASE_URL: str, path: str):
    """Delete the selected merchant from API

    Return: status_code
    """
    headers = {'token': token}
    r = requests.delete(BASE_URL+path, headers=headers)
    return r.status_code


def post_products(token: str, BASE_URL: str, merchant_id: str, df: pd.DataFrame, from_n: int, to_n: int):
    """Post the DataFrame of products into the API

    r.POST iterating each product from the DataFrame
    <from_n - to_n> used for limit larger DataFrames,
    where it's len is bigger than max API requests
    Return: access token or status_code
    """
    path = '/api/products'
    headers = {'token': token}
    error_products = []
    not_uploaded = to_n - 1 - from_n
    for row in df.itertuples():
        if row.Index <= from_n:
            continue
        if from_n >= to_n:
            break
        product = {
            "merchant_id": merchant_id,
            "sku": str(row.SKU),
            "barcodes": [str(row.EAN)],
            "brand": row.BRAND_NAME,
            "name": row.ITEM_NAME,
            "description": row.ITEM_DESCRIPTION,
            "package": row.BUY_UNIT,
            "image_url": row.ITEM_IMG,
            "category": row.CATEGORY,
            "url": f'{BASE_URL+path}/{row.EAN}',
            "branch_products": row.BRANCH_PRODUCTS
        }
        r = requests.post(BASE_URL+path, headers=headers, json=product)
        if r.status_code != 200:
            error_products.append(row.SKU)
        else:
            not_uploaded -= 1
        from_n += 1
    return (not_uploaded, error_products)
