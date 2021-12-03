# Crowd prediction based on simple ARMA model, using sample data

import pandas as pd
import numpy as np
from statsmodels.tsa.arima_model import ARIMA
import warnings
from data_loading import sensor1

# Specify to ignore warning messages
warnings.filterwarnings("ignore")

# Training set
train = sensor1[-100:]

# Fit ARIMA
arima_fit = ARIMA(train["count"].values, order=(1,0,1)).fit()
# Forecast the next 100 datetime points
fc, se, conf  = arima_fit.forecast(100, alpha=0.05)  # 95% conf

# Create a df with forecast intervals of the next 100 datetime points
dt = [train.iloc[-1:]["Datetime"].values[0] + np.timedelta64(15*i,'m') for i in range(100)]
forecasts = pd.DataFrame({"datetime": dt})
forecasts["forecast"] = fc 
forecasts["lower_bound"] = conf[:, 0]
forecasts["upper_bound"] = conf[:, 1]

forecasts.to_csv("sensor1_forecast.csv")