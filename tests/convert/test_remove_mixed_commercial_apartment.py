import pandas as pd
import unittest
from pandas.testing import assert_frame_equal
from pipeline.convert_csv import remove_mixed_commercial_apartment  # replace with actual path

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


if __name__ == '__main__':
    unittest.main()