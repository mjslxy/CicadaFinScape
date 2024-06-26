from __future__ import annotations
import sqlite3
import copy
import csv
import pandas as pd
from st_utils import FinLogger

class SQLColDef:
    def __init__(self, name:str = "", type:str = "", constraint:str = ""):
        self.name:str = name
        self.type = type
        self.constraint = constraint
    def col_def_str(self):
        return f"{self.name} {self.type} {self.constraint}"

class SQLTableDef:
    def __init__(self, name:str = "", cols:list[SQLColDef] = [], ex_cols:list[SQLColDef] = []):
        self._name:str = name
        self._ess_cols = cols
        self._ex_cols = ex_cols
    
    def name(self):
        return self._name
    
    def ess_cols(self) -> list[SQLColDef]:
        return copy.copy(self._ess_cols)
    
    def ex_cols(self) -> list[SQLColDef]:
        return copy.copy(self._ex_cols)
    
    def cols_str(self):
        ess_cols_str = ',\n'.join([x.name for x in self.ess_cols()])
        return ess_cols_str
    
    def cols_name(self):
        return [x.name for x in self.ess_cols()]
    
    def create_table_str(self):
        ess_col_def = ',\n'.join([x.col_def_str() for x in self.ess_cols()])
        ex_col_def = ',\n'.join([x.col_def_str() for x in self.ex_cols()])
        if ex_col_def:
            col_def = ',\n'.join([ess_col_def, ex_col_def])
        else:
            col_def = ess_col_def

        return f"CREATE TABLE {self.name()} ({col_def});"

COL_DATE = SQLColDef("DATE", "TEXT", "NOT NULL")
COL_ACCOUNT = SQLColDef("ACCOUNT", "TEXT", "NOT NULL")
COL_NAME = SQLColDef("NAME", "TEXT", "NOT NULL")
COL_NET_WORTH = SQLColDef("NET_WORTH", "REAL", "NOT NULL")
COL_MONTH_INVESTIGATION = SQLColDef("MONTH_INVESTIGATION", "REAL", "NOT NULL")
COL_MONTH_PROFIT = SQLColDef("MONTH_PROFIT", "REAL", "NOT NULL")
ASSET_TABLE = SQLTableDef("ASSET", [COL_DATE, COL_ACCOUNT, COL_NAME, COL_NET_WORTH, COL_MONTH_INVESTIGATION, COL_MONTH_PROFIT])

class AssetItem:
    def __init__(self, name:str, acc:Account):
        self.acc = acc
        self.name = name
        self.cats:dict[str,str] = {}
        self.ex_cols:list[SQLColDef] = []
    def add_cat(self, cat:str, type:str):
        self.cats[cat] = type
    def to_json(self):
        return {
            "Name" : self.name,
            "Account": self.acc.name,
            "Category" : self.cats
        }
    def to_df(self):
        data = {
            "Account" : self.acc.name,
            "Name" : self.name,
        }
        data.update(self.cats)
        data = {k:[v] for k,v in data.items()}
        return pd.DataFrame.from_dict(data)
    def add_to_df(self, df:pd.DataFrame):
        data = {
            "Account" : self.acc.name,
            "Name" : self.name,
        }
        data.update(self.cats)
        data = [data[x] if x in data else None for x in df.columns]
        df.loc[len(df)] = data

class Account:
    def __init__(self, name:str):
        self.name = name
        self.asset_list:list[AssetItem] = []
    def add_asset(self, asset:AssetItem):
        self.asset_list.append(asset)
    def to_json(self):
        return {"Name" : self.name}
    def to_df(self):
        df = pd.DataFrame()
        for asset in self.asset_list:
            df = pd.concat([df, asset.to_df()])
        print(df)
        return df
    def add_to_df(self, df:pd.DataFrame):
        for asset in self.asset_list:
            asset.add_to_df(df)
    def asset(self, asset_name):
        asset = next(filter(lambda x: x.name == asset_name, self.asset_list), None)
        return asset
            

class AssetTable:
    def __init__(self, accounts:list[Account]):
        self.accounts = accounts

class FinSQL:
    def __init__(self, db_path:str):
        self.db_path = db_path
        self.db:sqlite3.Connection = None
    
    def __enter__(self):
        print(self.db_path)
        self.db = sqlite3.connect(self.db_path)
        return self
    
    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.db.close()

    def _get_tables(self):
        return self.exec("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
    
    def exec(self, exec_str):
        print(exec_str)
        return self.db.execute(exec_str)
    
    def clear_db(self):
        tables = self._get_tables()
        for table in tables:
            self.exec(f"DROP TABLE IF EXISTS {table[0]}")
        self.db.commit()

    def initial_db(self):
        tables = self._get_tables()
        if tables:
            print("db is not empty, can not initialize, please clear db first")
            return
        self.exec(ASSET_TABLE.create_table_str())
        self.db.commit()
    
    def validate_db(self):
        tables = self._get_tables()
        for table in tables:
            if not table[0] == ASSET_TABLE.name():
                FinLogger.warn(f"Database contain unknown table {table[0]} !")
                
        if ASSET_TABLE.name() not in [x[0] for x in tables]:
            return False

        return True
     
    def insert_asset(self, data:dict):
        insert_keys = []
        insert_values = []
        for c in ASSET_TABLE.ess_cols():
            k = c.name
            assert k in data, f"{k} is not in {data}"
            insert_keys.append(k)
            if c.type == "TEXT":
                insert_values.append(f"'{data[k]}'")
            else:
                insert_values.append(str(data[k]))
        for k in ASSET_TABLE.ex_cols():
            if k in data:
                insert_keys.append(data[k])
        key_str = ', '.join(insert_keys)
        value_str = ', '.join(insert_values)
        execute_str = f"INSERT INTO {ASSET_TABLE.name()} ({key_str}) VALUES ({value_str});"
        self.exec(execute_str)
    
    def commit(self):
        self.db.commit()
    
    def load_from_csv(self, csv_path):
        with open(csv_path, 'r') as f:
            reader = csv.reader(f)
            csv_data = list(reader)
        assert(len(csv_data[0]) == len(ASSET_TABLE.ess_cols()))

        for data in csv_data[1:]:
            insert_data = {x.name:y for x,y in zip(ASSET_TABLE.ess_cols(), data)}
            self.insert_asset(insert_data)
        self.db.commit()

    def query_asset(self, acc_name, name):
        results = self.exec(f'''SELECT * from {ASSET_TABLE.name()} WHERE ACCOUNT = "{acc_name}" and NAME = "{name}"''')
        return results
    
    def query_all_asset(self):
        results = self.exec(f"SELECT * from {ASSET_TABLE.name()}").fetchall()
        return results
    
    def query_date(self, date):
        results = self.exec(f'''SELECT * from {ASSET_TABLE.name()} WHERE DATE = "{date}"''').fetchall()
        return results

    def delete_asset(self, acc_name, name):
        self.exec(f'''DELETE FROM {ASSET_TABLE.name()} WHERE ACCOUNT = "{acc_name}" and NAME = "{name}"''')
    
    def query_col(self, cols):
        col_str = ", ".join(cols)
        results = self.exec(f'''SELECT {col_str} from {ASSET_TABLE.name()}''').fetchall()
        return results
    
            
        
            
        