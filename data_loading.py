import pandas as pd

df = pd.read_csv("data/sample.csv", index_col="Unnamed: 0")
crowd_sample = df.iloc[:, 0:4]

crowd_sample["Datetime"] = pd.to_datetime(crowd_sample['Time'])
crowd_sample.set_index(["Datetime"], inplace=True)
crowd_sample = crowd_sample.drop(["Time"], axis=1)

# CMSA-GAWW-22
crowd_sample["CMSA-GAWW-22 Kloveniersburgwal"].to_csv("data/CMSA-GAWW-22-Kloveniersburgwal.csv")
kloveniersburgwal = pd.read_csv("data/CMSA-GAWW-22-Kloveniersburgwal.csv")
kloveniersburgwal["objectnummer"] = "CMSA-GAWW-22"
kloveniersburgwal["location"] = "Kloveniersburgwal"
kloveniersburgwal["Datetime"] = pd.to_datetime(kloveniersburgwal['Datetime'])
kloveniersburgwal = kloveniersburgwal.rename(columns={"CMSA-GAWW-22 Kloveniersburgwal": "count", "Datetime": "datetime"})
kloveniersburgwal = kloveniersburgwal.reindex(columns=["objectnummer", "location", "datetime", "count"])