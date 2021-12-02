import pandas as pd

df = pd.read_csv("data/sample.csv", index_col="Unnamed: 0")
crowd_sample = df.iloc[:, 0:4]