import pandas as pd
import unittest
import os
import tempfile
from pandas.testing import assert_frame_equal
from pipeline.convert_csv import remove_commas, remove_mixed_commercial_apartment, add_cadastre, remove_useless, merge_rows, convert_txt
from utils.constants import col_to_drop

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

class TestRemoveUseless(unittest.TestCase):

    def test_removes_columns_and_filters_rows(self):
        df = pd.DataFrame({
            "Type local": ["Appartement", "Maison", "Appartement"],
            "Valeur fonciere": [100000, 200000, 150000],
            "ToRemove": ["a", "b", "c"],
            "Extra": [1, 2, 3]
        })
        drop = ["ToRemove", "Extra"]
        result = remove_useless(df, drop)

        expected = pd.DataFrame({
            "Type local": ["Appartement", "Appartement"],
            "Valeur fonciere": [100000, 150000]
        }, index=[0, 2])

        assert_frame_equal(result.reset_index(drop=True), expected.reset_index(drop=True))


    def test_removes_all_if_no_appartement(self):
        df = pd.DataFrame({
            "Type local": ["Maison", "Commerce"],
            "Valeur fonciere": [300000, 400000],
            "ToRemove": ["x", "y"],
            "Extra": [5, 6]
        })
        drop = ["ToRemove"]
        result = remove_useless(df, drop)
        self.assertTrue(result.empty)

    def test_raises_keyerror_if_columns_missing(self):
        drop = ["NonexistentColumn"]
        df = pd.DataFrame({
            "Type local": ["Appartement"],
            "Valeur fonciere": [500000]
        })

        with self.assertRaises(KeyError):
            remove_useless(df, drop)


class TestMergeRows(unittest.TestCase):

    def test_merges_duplicate_rows(self):
        df = pd.DataFrame({
            "Cadastre": ["01001AB", "01001AB", "01001AC"],
            "Valeur fonciere": [100000, 100000, 150000],
            "Surface reelle bati": [50.0, 70.0, 80.0]
        })

        result = merge_rows(df)

        expected = pd.DataFrame({
            "Cadastre": ["01001AB", "01001AC"],
            "Valeur fonciere": [100000, 150000],
            "Surface reelle bati": [120.0, 80.0]
        })

        assert_frame_equal(
            result.sort_values(by="Cadastre").reset_index(drop=True),
            expected.sort_values(by="Cadastre").reset_index(drop=True)
        )

    def test_no_merge_when_rows_differ(self):
        df = pd.DataFrame({
            "Cadastre": ["01001AB", "01001AB"],
            "Valeur fonciere": [100000, 120000],
            "Surface reelle bati": [50.0, 70.0]
        })

        result = merge_rows(df)

        expected = df.copy()

        assert_frame_equal(
            result.sort_values(by=["Cadastre", "Valeur fonciere"]).reset_index(drop=True),
            expected.sort_values(by=["Cadastre", "Valeur fonciere"]).reset_index(drop=True)
        )

    def test_handles_missing_values(self):
        df = pd.DataFrame({
            "Cadastre": ["01001AB", "01001AB"],
            "Valeur fonciere": [None, None],
            "Surface reelle bati": [10.0, 20.0]
        })

        result = merge_rows(df)

        expected = pd.DataFrame({
            "Cadastre": ["01001AB"],
            "Valeur fonciere": [None],
            "Surface reelle bati": [30.0]
        })

        assert_frame_equal(result.reset_index(drop=True), expected.reset_index(drop=True))

    def test_empty_input(self):
        df = pd.DataFrame(columns=["Cadastre", "Valeur fonciere", "Surface reelle bati"])
        result = merge_rows(df)
        self.assertTrue(result.empty)


class TestConvertTxt(unittest.TestCase):

    def test_end_to_end_conversion(self):
        
        with open("tests/data/convert/input.txt", "r", encoding="utf-8") as f:
            raw_data = f.read()
    
        expected_df = pd.read_csv("tests/data/convert/expected_output.csv")

        # Create temporary input and output files
        with tempfile.NamedTemporaryFile(mode="w+", delete=False, suffix=".txt") as infile, \
             tempfile.NamedTemporaryFile(mode="r", delete=False, suffix=".csv") as outfile:

            infile.write(raw_data)
            infile.flush()

            file_mapping = {infile.name: outfile.name}

            convert_txt(file_mapping)
            result = pd.read_csv(outfile.name)

            assert_frame_equal(
                result.sort_index(axis=1).sort_values(by=result.columns.tolist()).reset_index(drop=True),
                expected_df.sort_index(axis=1).sort_values(by=expected_df.columns.tolist()).reset_index(drop=True)
            )

        # Clean up temp files
        os.remove(infile.name)
        os.remove(outfile.name)


if __name__ == '__main__':
    unittest.main()