import pandas as pd
import unittest
from pandas.testing import assert_frame_equal
from pipeline.convert_csv import remove_commas, remove_mixed_commercial_apartment, add_cadastre

class TestRemoveMixedCommercialApartment(unittest.TestCase):
    
    def test_empty_col(self):
        data = [
            {"Date mutation": "2024-06-27", "Valeur fonciere": 255000000.0, "Code postal": "75008", "Voie": "MONTAIGNE", "Type local": None}
        ]
        df = pd.DataFrame(data)
        result = remove_mixed_commercial_apartment(df)
        
        expected_data = [
            {"Date mutation": "2024-06-27", "Valeur fonciere": 255000000.0, "Code postal": "75008", "Voie": "MONTAIGNE", "Type local": None}
        ]
        expected = pd.DataFrame(expected_data)

        # Check that we removed only the mixed "Appartement" row
        assert_frame_equal(result, expected, check_like=True)
    
    def test_remove_mixed_transaction_apartment_only_remains(self):
        data = [
            # Mixed transaction (should remove the Appartement)
            {"Date mutation": "2024-06-27", "Valeur fonciere": 255000000.0, "Code postal": "75008", "Voie": "MONTAIGNE", "Type local": "Local industriel. commercial ou assimilé"},
            {"Date mutation": "2024-06-27", "Valeur fonciere": 255000000.0, "Code postal": "75008", "Voie": "MONTAIGNE", "Type local": "Appartement"},
            # Pure apartment transaction (should keep it)
            {"Date mutation": "2024-06-28", "Valeur fonciere": 300000.0, "Code postal": "75015", "Voie": "LECOURBE", "Type local": "Appartement"},
            # Pure commercial transaction (should keep it too)
            {"Date mutation": "2024-06-29", "Valeur fonciere": 500000.0, "Code postal": "75010", "Voie": "LAFAYETTE", "Type local": "Local industriel. commercial ou assimilé"},
        ]
        df = pd.DataFrame(data)
        result = remove_mixed_commercial_apartment(df)
        
        expected_data = [
            {"Date mutation": "2024-06-27", "Valeur fonciere": 255000000.0, "Code postal": "75008", "Voie": "MONTAIGNE", "Type local": "Local industriel. commercial ou assimilé"},
            {"Date mutation": "2024-06-28", "Valeur fonciere": 300000.0, "Code postal": "75015", "Voie": "LECOURBE", "Type local": "Appartement"},
            {"Date mutation": "2024-06-29", "Valeur fonciere": 500000.0, "Code postal": "75010", "Voie": "LAFAYETTE", "Type local": "Local industriel. commercial ou assimilé"},
        ]
        expected = pd.DataFrame(expected_data, index=[0, 2, 3])

        # Check that we removed only the mixed "Appartement" row
        assert_frame_equal(result, expected, check_like=True)

    def test_removes_apartment_in_mixed_transaction(self):
        data = [
            {"Date mutation": "2024-06-27", "Valeur fonciere": 255000000.0, "Code postal": "75008", "Voie": "MONTAIGNE", "Type local": "Local industriel. commercial ou assimilé"},
            {"Date mutation": "2024-06-27", "Valeur fonciere": 255000000.0, "Code postal": "75008", "Voie": "MONTAIGNE", "Type local": "Appartement"},
            {"Date mutation": "2024-06-28", "Valeur fonciere": 300000.0, "Code postal": "75015", "Voie": "LECOURBE", "Type local": "Appartement"},
        ]
        df = pd.DataFrame(data)
        result = remove_mixed_commercial_apartment(df)
        
        expected_data = [
            {"Date mutation": "2024-06-27", "Valeur fonciere": 255000000.0, "Code postal": "75008", "Voie": "MONTAIGNE", "Type local": "Local industriel. commercial ou assimilé"},
            {"Date mutation": "2024-06-28", "Valeur fonciere": 300000.0, "Code postal": "75015", "Voie": "LECOURBE", "Type local": "Appartement"}
            ]
        
        expected = pd.DataFrame(expected_data, index=[0, 2])

        # The mixed transaction apartment should be removed
        assert_frame_equal(result, expected, check_like=True)

    def test_keeps_clean_apartment(self):
        data = [
            {"Date mutation": "2024-06-28", "Valeur fonciere": 300000.0, "Code postal": "75015", "Voie": "LECOURBE", "Type local": "Appartement"},
        ]
        df = pd.DataFrame(data)
        result = remove_mixed_commercial_apartment(df)
        expected = pd.DataFrame(data)
        assert_frame_equal(result, expected, check_like=True)

    def test_keeps_clean_commercial(self):
        data = [
            {"Date mutation": "2024-06-29", "Valeur fonciere": 500000.0, "Code postal": "75010", "Voie": "LAFAYETTE", "Type local": "Local industriel. commercial ou assimilé"},
        ]
        df = pd.DataFrame(data)
        result = remove_mixed_commercial_apartment(df)
        expected = pd.DataFrame(data)
        assert_frame_equal(result, expected, check_like=True)
    
    def test_no_effect_on_clean_data(self):
        data = [
            {"Date mutation": "2024-05-10", "Valeur fonciere": 200000.0, "Code postal": "75001", "Voie": "RIVOLI", "Type local": "Appartement"},
            {"Date mutation": "2024-05-10", "Valeur fonciere": 500000.0, "Code postal": "75001", "Voie": "RIVOLI", "Type local": "Local industriel. commercial ou assimilé"},
        ]
        df = pd.DataFrame(data)
        result = remove_mixed_commercial_apartment(df)
        expected = pd.DataFrame(data)
        assert_frame_equal(result, expected, check_like=True)
        
        
class TestRemoveCommas(unittest.TestCase):
    
    def test_basic_string_replacement(self):
        df = pd.DataFrame({
            "col1": ["1,23", "4,56"],
            "col2": ["7,89", "0,12"]
        })
        expected = pd.DataFrame({
            "col1": ["1.23", "4.56"],
            "col2": ["7.89", "0.12"]
        })
        result = remove_commas(df)
        assert_frame_equal(result, expected)

    def test_mixed_types(self):
        df = pd.DataFrame({
            "str_col": ["1,5", "2,6"],
            "float_col": [1.5, 2.6],
            "int_col": [1, 2]
        })
        expected = pd.DataFrame({
            "str_col": ["1.5", "2.6"],
            "float_col": [1.5, 2.6],
            "int_col": [1, 2]
        })
        result = remove_commas(df)
        assert_frame_equal(result, expected)

    def test_handles_empty_strings_and_nan(self):
        df = pd.DataFrame({
            "col": ["1,23", "", None]
        })
        expected = pd.DataFrame({
            "col": ["1.23", "", None]
        })
        result = remove_commas(df)
        assert_frame_equal(result, expected)

    def test_no_commas(self):
        df = pd.DataFrame({
            "col": ["1.23", "4.56"]
        })
        expected = df.copy()
        result = remove_commas(df)
        assert_frame_equal(result, expected)
    

class TestAddCadastre(unittest.TestCase):

    def test_basic_case(self):
        df = pd.DataFrame({
            "Code departement": [1],
            "Code commune": [4],
            "Section": ["AH"]
        })
        result = add_cadastre(df)
        self.assertIn("Cadastre", result.columns)
        self.assertEqual(result.loc[0, "Cadastre"], "01004AH")

    def test_padding_behavior(self):
        df = pd.DataFrame({
            "Code departement": [75, 3],
            "Code commune": [1, 21],
            "Section": ["AX", "B"]
        })
        result = add_cadastre(df)
        expected_cadastre = ["75001AX", "03021B"]
        self.assertEqual(list(result["Cadastre"]), expected_cadastre)

    def test_existing_string_columns(self):
        df = pd.DataFrame({
            "Code departement": ["09", "75"],
            "Code commune": ["007", "001"],
            "Section": ["C", "D"]
        })
        result = add_cadastre(df)
        expected_cadastre = ["09007C", "75001D"]
        self.assertEqual(list(result["Cadastre"]), expected_cadastre)

    def test_preserves_other_columns(self):
        df = pd.DataFrame({
            "Code departement": [75],
            "Code commune": [1],
            "Section": ["X"],
            "Other": ["test"]
        })
        result = add_cadastre(df)
        self.assertEqual(result.loc[0, "Other"], "test")


if __name__ == '__main__':
    unittest.main()