import json
import csv
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from finsql import Account,AssetItem,FinSQL,ASSET_TABLE

class FinContext:
    def __init__(self, config_path, db_path):
        self.config_path = config_path
        self.db_path = db_path
        with open(config_path) as f:
            self.config = json.load(f)
        self.cat_dict:dict = {}
        self.acc:dict[str,Account] = {}
        self.fsql = FinSQL(self.db_path)

        if "Categories" in self.config:
            self.cat_dict = self.config["Categories"]
        
        if "Accounts" in self.config:
            for i in self.config["Accounts"]:
                self.acc[i["Name"]] = Account(i["Name"])
        
        if "Assets" in self.config:
            for i in self.config["Assets"]:
                acc_name = i["Account"]
                assert(acc_name in self.acc)
                acc = self.acc[acc_name]
                asset = AssetItem(i["Name"], acc)
                if "Category" in i:
                    for cat,type in i["Category"].items():
                        assert(cat in self.cat_dict and type in self.cat_dict[cat])
                        asset.add_cat(cat,type)
                acc.add_asset(asset)
    
    def write_config(self):
        config = {}
        if self.cat_dict:
            config["Categories"] = self.cat_dict
        if self.acc:
            accs = [v.to_json() for k,v in self.acc.items()]
            config["Accounts"] = accs
        
        assets = []
        for k,v in self.acc.items():
            for asset in v.asset_list:
                assets.append(asset.to_json())
        if assets:
            config["Assets"] = assets
            
        with open(self.config_path, 'w') as f:
            json.dump(config, f, indent=4)
    
    def init_db_from_csv(self, csv_path):
        with self.fsql as s:
            s.clear_db()
            s.initial_db()
            s.load_from_csv(csv_path)
    
    def asset_table(self):
        cols = ["DATE", "ACCOUNT", "NAME", "NET_WORTH", "MONTH_INVEST", "MONTH_PROFIT"]
        with self.fsql as s:
            r = s.query_all_asset()
            df = pd.DataFrame(r, columns=cols)

        df["ASSET"] = df['ACCOUNT'] + '-' + df['NAME']
        df = df[["DATE", "ASSET", "NET_WORTH"]]
        return df
    
    def asset_chart(self):
        df = self.asset_table()
        df_sum = df.copy()
        df_sum = df_sum.groupby("DATE")["NET_WORTH"].sum().reset_index()
        fig = px.line(df, x='DATE', y='NET_WORTH', color="ASSET")
        fig.add_bar(x=df_sum["DATE"], y=df_sum["NET_WORTH"], name="TOTAL")
        return fig
    
    def account_df(self):
        cols = ["Account", "Name"]
        cols.extend([k for k in self.cat_dict])
        df = pd.DataFrame(columns=cols)
        for k,v in self.acc.items():
            v.add_to_df(df)
        return df

    def account_from_df(self, df:pd.DataFrame):
        for index, row in df.iterrows():
            acc_name = row["Account"]
            asset_name = row["Name"]
            if acc_name in self.acc:
                acc = self.acc[acc_name]
                for asset in acc.asset_list:
                    if asset.name == asset_name:
                        pass
                
    
    def category_df(self):
        cat = [[k, ','.join(v)] for k,v in self.cat_dict.items()]
        cat_df = pd.DataFrame(cat, columns=["Category", "Labels"])
        return cat_df
    
    def category_from_df(self, df:pd.DataFrame):
        cat_dict = {}
        for index, row in df.iterrows():
            name:str = row["Category"]
            labels:str = row["Labels"]
            cat_dict[name] = labels.split(',')
        self.cat_dict = cat_dict
        self.write_config()
    
    def add_asset(self, acc_name, asset_name, cats:dict):
        if acc_name not in self.acc:
            self.acc[acc_name] = Account(acc_name)
        
        acc = self.acc[acc_name]
        asset = AssetItem(asset_name, acc)
        for k,v in cats.items():
            asset.add_cat(k,v)
        acc.add_asset(asset)
        self.write_config()
            
            
        
        
            
        
        