import pandas as pd

df = pd.read_csv("data/sample.csv", index_col="Unnamed: 0")
crowd_sample = df.iloc[:, 0:4]

crowd_sample["Datetime"] = pd.to_datetime(crowd_sample['Time'])
crowd_sample.set_index(["Datetime"], inplace=True)
crowd_sample = crowd_sample.drop(["Time"], axis=1)

# CMSA-GAWW-22
crowd_sample["CMSA-GAWW-22 Kloveniersburgwal"].to_csv("data/CMSA-GAWW-22-Kloveniersburgwal.csv")
sensor1 = pd.read_csv("data/CMSA-GAWW-22-Kloveniersburgwal.csv")
sensor1["objectnummer"] = "CMSA-GAWW-22"
sensor1["location"] = "Kloveniersburgwal"
sensor1["Datetime"] = pd.to_datetime(sensor1['Datetime'])
sensor1 = sensor1.rename(columns={"CMSA-GAWW-22 Kloveniersburgwal": "count", "Datetime": "datetime"})
sensor1 = sensor1.reindex(columns=["objectnummer", "location", "datetime", "count"])