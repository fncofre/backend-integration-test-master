import unittest
import requests
import json

import pandas as pd

import integrations.api_integrations as ai
import integrations.csv_integrations as ci


class integrations_test(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.auth = ai.read_credentials()
        path_url = f'/oauth/token?client_id={self.auth["CLIENT_ID"]}&client_secret={self.auth["CLIENT_SECRET"]}&grant_type={self.auth["GRAND_TYPE"]}'
        r = requests.post(self.auth['BASE_URL']+path_url)
        content_dict = json.loads(r.content.decode('utf-8'))
        self.token = f"Bearer {content_dict['access_token']}"
        self.url = self.auth['BASE_URL']

    def test_get_stores_id(self):
        """Test method 'get_stores_ids()' from api_integrations.py

        Check if the value returned is the dict with ids.
        """
        result = ai.get_stores_ids(self.token, self.url)
        self.assertEqual(type(result), dict)

    def test_update_merchant(self):
        """Test method 'update_merchant()' from api_integrations.py

        Check if the value returned from an update with 'merch_data',
        Returns a 'status_code' equals to 200.
        """
        richard_id = 'ae9c81fe-163e-4546-8349-19dbf63715c7'
        merch_data = {
            'can_be_deleted': False,
            'can_be_updated': True,
            'id': richard_id,
            'is_active': True,
            'name': "Richard's"
        }
        result = ai.update_merchant(
            self.token, self.url, f'/api/merchants/{richard_id}', merch_data)
        self.assertEqual(merch_data, result)

    def test_delete_merchant(self):
        """Test method 'delete_merchant()' from api_integrations.py

        Check if the value returned from a delete for 'beauty_id',
        Returns a 'status_code' equals to 200.
        """
        beauty_id = '9001976c-a9e7-4b95-b133-9ac8ba213fb2'
        result = ai.delete_merchant(
            self.token, self.url, f'/api/merchants/{beauty_id}')
        self.assertEqual(result, 200)

    def test_post_product(self):
        """Test method 'post_products()' from api_integrations.py

        Check if the value returned from a POST with 'product',
        Returns no errors on the response array.
        """
        path = '/api/products'
        richard_id = 'ae9c81fe-163e-4546-8349-19dbf63715c7'
        product = {
            "merchant_id": richard_id,
            "sku": "123456789",
            "barcodes": ["95281231"],
            "brand": "COCA-COLA",
            "name": "MONSTER",
            "description": "BEBIDA ENERGETICA 500ML",
            "package": "UN",
            "image_url": f"{self.url}/images/123456789",
            "category": "Bebestibles|gaseosas|bebidas energeticas",
            "url": f'{self.url+path}/95281231',
            "branch_products": [{"branch": "MM", "stock": 20, "price": 82}]
        }
        df = pd.DataFrame([product], columns=product.keys())
        result = ai.post_products(
            self.token, self.url, richard_id, df, 0, len(df))
        # If result[1] has no elements, all df was upload correctly
        self.assertEqual(len(result[1]), 0)

    def test_amount_filter(self):
        """Test method 'filter_df_byamount()' from csv_integrations.py

        Select the elements higher than n from the column of df,
        Cheking if the 'result' is equals to a df with the 'stock' bigger than 0.
        """
        products = {'ID': [1, 2, 3, 4],
                    'STOCK': [0, 2, -3, 1]}
        df = pd.DataFrame(data=products)
        df = ci.filter_df_byamount(df, 'STOCK', 0)
        prices = df['STOCK'].tolist()
        self.assertEqual(prices, [2, 1])

    def test_clean_tags(self):
        """Test method 'clean_df_tags()' from csv_integrations.py

        Remove HTML tags of the values from the column of df,
        Cheking if the 'result' is equals to a previously cleaned df.
        """
        products = {'ID': [1, 2],
                    'DESCRIPTION': ["<p>BEBIDA</p>", "<p>RAMITAS</p>"]}
        df = pd.DataFrame(data=products)
        df = ci.clean_df_tags(df, 'DESCRIPTION')
        description = df['DESCRIPTION'].tolist()
        self.assertEqual(description, ['BEBIDA', 'RAMITAS'])

    def test_remove_duplicates(self):
        """Test method 'remove_df_duplicates()' from csv_integrations.py

        Remove all values with that have the same value in 'column' keeping the first one.
        Cheking if the 'result' is equals to a list without the duplicate values.
        """
        products = {'ID': [1, 2, 1],
                    'PRICE': [100, 200, 300]}
        df = pd.DataFrame(data=products)
        df = ci.remove_df_duplicates(df, 'ID')
        price = df['ID'].tolist()
        self.assertEqual(price, [1, 2])

    def test_update_package(self):
        """Test method 'update_df_package()' from csv_integrations.py

        ADD package information to the BUY_UNIT column, extracting it from 'ITEM_DESCRIPTION'
        Cheking if the result is equals to a previously filled df with package.
        """
        products = {'ID': [1, 2, 3],
                    'ITEM_DESCRIPTION': ["DULCE 1UN", "GASEOSA", "CARNE 1KG"],
                    'BUY_UNIT': ['', 'UN', '']}
        df = pd.DataFrame(data=products)
        df = ci.update_df_package(df)
        package = df['BUY_UNIT'].tolist()
        self.assertEqual(package, ['UN', 'UN', 'KG'])

    def test_join_columns(self):
        """Test method 'join_df_columns()' from csv_integrations.py

        Join the given columns separated by '|', dropping each one from df except the first one
        Cheking if the result is equals to a previously joined 'categories' columns.
        """
        products = {'ID': [1, 2],
                    'CATEGORY': ["SNACKS", "BEBESTIBLES"],
                    'SUBCATEGORY': ["SALADOS", "GASEOSAS"],
                    'SUBSUBCATEGORY': ["PAPAS", "COLA"]}
        df = pd.DataFrame(data=products)
        df = ci.join_df_columns(
            df, 'CATEGORY', ['SUBCATEGORY', 'SUBSUBCATEGORY'], '|')
        package = df['CATEGORY'].tolist()
        self.assertEqual(
            package, ['snacks|salados|papas', 'bebestibles|gaseosas|cola'])

    def test_merge_byfield(self):
        """Test method 'merge_df_byfield()' from csv_integrations.py

        Merge 2 differents DataFrames by their 'field' column,
        Cheking if both DataFrames were intersected getting all columns.
        """
        products_price = {'ID': [1, 3, 2],
                          'PRICE': [100, 200, 300]}
        df_price = pd.DataFrame(data=products_price)
        products_name = {'ID': [3, 2, 1],
                         'NAME': ["DULCE", "PAPA", "BEBIDA"]}
        df_name = pd.DataFrame(data=products_name)
        df = ci.merge_df_byfield(df_price, df_name, 'ID')
        self.assertEqual(df.iloc[0]["NAME"], 'BEBIDA')

    def test_select_higest(self):
        """Test method 'select_df_n_highest_branch()' from csv_integrations.py

        Select the first n highest values from the column of df for each group,
        Cheking if the 'result' is equals to a df with the highest prices for each branch.
        """
        products = {'ID': [1, 2, 3],
                    'PRICE': [100, 200, 300],
                    'BRANCH': ["MM", "SR", "MM"]}
        df = pd.DataFrame(data=products)
        df = ci.select_df_n_highest_branch(df, 1, 'PRICE')
        id_higher = df['ID'].tolist()
        self.assertEqual(id_higher, [3, 2])


if __name__ == "__main__":
    unittest.main()
