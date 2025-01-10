# data_store.py
import pandas as pd

class DataStore:
    def __init__(self):
        self.df = None

    def load_data(self, file_path):
        self.df = pd.read_csv(file_path)
        self.df['date'] = pd.to_datetime(self.df['date'])
        return self.df

# Create a global instance
data_store = DataStore()