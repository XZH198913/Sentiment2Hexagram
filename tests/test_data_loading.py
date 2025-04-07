import unittest
from src.data_loader import load_gua_data

class TestDataLoading(unittest.TestCase):
    def setUp(self):
        self.test_data_path = "../data/64_gua.csv"

    def test_load_valid_csv(self):
        df = load_gua_data(self.test_data_path)
        self.assertIsNotNone(df)
        self.assertEqual(len(df), 64)
        self.assertIn('卦名', df.columns)

    def test_missing_file(self):
        with self.assertRaises(FileNotFoundError):
            load_gua_data("nonexistent.csv")

if __name__ == '__main__':
    unittest.main()