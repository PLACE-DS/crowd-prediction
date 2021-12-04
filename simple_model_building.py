# Crowd prediction based on simple ARMA model and XGBoost, using sample data

import pandas as pd
import numpy as np
from statsmodels.tsa.arima_model import ARIMA
from xgboost import XGBRegressor
import warnings
from data_loading import kloveniersburgwal

# Specify to ignore warning messages
warnings.filterwarnings("ignore")

# Prepare the data
data = kloveniersburgwal

# Training-test set split
# split a univariate dataset into train/test sets
def train_test_split(data, n_test):
	return data[:-n_test, :], data[-n_test:, :]

train, test = train_test_split(data, 400)

# Fit ARIMA
arima_fit = ARIMA(train["count"].values, order=(6,0,3)).fit()
# Forecast the next 100 datetime points
fc, se, conf  = arima_fit.forecast(800, alpha=0.05)  # 95% conf

# Create a df with forecast intervals of the next 100 datetime points

# Get the following datetime (after the last point of training set)
dt = [train.iloc[-1:]["datetime"].values[0] + np.timedelta64(15*i,'m') for i in range(100)]

# Extract the forecasts
forecasts = pd.DataFrame({"datetime": dt})
forecasts["forecast"] = fc 
forecasts["lower_bound"] = conf[:, 0]
forecasts["upper_bound"] = conf[:, 1]

# Result file - just to test the workflow

# Future work: extract objectnummer, location, threshold into forecast file 
forecasts["objectnummer"] = "CMSA-GAWW-22"
forecasts["location"] = "Kloveniersburgwal"
forecasts["threshold"] = 182.5 #wrong number
forecasts = forecasts.reindex(columns=["objectnummer", "location", "datetime", "forecast", "lower_bound", "upper_bound", "threshold"])

forecasts.to_csv("result/sensor1_forecast.csv")

# XGBoost

# Prepare features
def create_time_features(df, label=None):
    """
    Creates time series features from datetime index
    """
    df['hour'] = df['datetime'].dt.hour
    df['dayofweek'] = df['datetime'].dt.dayofweek
    df['quarter'] = df['datetime'].dt.quarter
    df['month'] = df['datetime'].dt.month
    df['year'] = df['datetime'].dt.year
    df['dayofyear'] = df['datetime'].dt.dayofyear
    df['dayofmonth'] = df['datetime'].dt.day
    df['weekofyear'] = df['datetime'].dt.weekofyear
    
    X = df[['hour','dayofweek','quarter','month','year',
           'dayofyear','dayofmonth','weekofyear']]
    if label:
        y = df[label]
        return X, y
    return X

y_train = train[["count"]]
X_train = train.drop(["count"], axis=1)
X_train = create_time_features(X_train)

xgboost = XGBRegressor(n_estimators=1000)
xgboost_fit = xgboost.fit(X_train, y_train)