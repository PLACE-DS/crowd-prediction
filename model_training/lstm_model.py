import tensorflow as tf
from collections import deque
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import math


mpl.rcParams['figure.figsize'] = (30, 6)
mpl.rcParams['axes.grid'] = False

# Check for TensorFlow GPU access
print(f"TensorFlow has access to the following devices:\n{tf.config.list_physical_devices()}")

# See TensorFlow version
print(f"TensorFlow version: {tf.__version__}")

df = pd.read_csv('../data/cmsa_combined.csv', index_col="datetime")
df = df.iloc[:, 1:]
df.columns

date_time = pd.to_datetime(df.index, format='%Y-%m-%d %H:%M:%S')

df = df[['GAWW-11', 'checkin_dam', 'checkin_nieuwmarkt', 'hotel_overnachtingen']]

timestamp_s = date_time.map(pd.Timestamp.timestamp)

day = 24*60*60
day2 = (2)*day
day3_5 = (3.5)*day
day4 = (4)*day
week = (7)*day
week2 = (14)*day
month = (13)*day
year = (365)*day

df['Day sin'] = np.sin(timestamp_s * (2 * np.pi / day))
df['Day cos'] = np.cos(timestamp_s * (2 * np.pi / day))
df['2 Day sin'] = np.sin(timestamp_s * (2 * np.pi / day2))
df['2 Day cos'] = np.cos(timestamp_s * (2 * np.pi / day2))
df['3.5 Day sin'] = np.sin(timestamp_s * (2 * np.pi / day3_5))
df['3.5 Day cos'] = np.cos(timestamp_s * (2 * np.pi / day3_5))
df['4 Day sin'] = np.sin(timestamp_s * (2 * np.pi / day4))
df['4 Day cos'] = np.cos(timestamp_s * (2 * np.pi / day4))
df['Week sin'] = np.sin(timestamp_s * (2 * np.pi / week))
df['Week cos'] = np.cos(timestamp_s * (2 * np.pi / week))
df['2 Weeks sin'] = np.sin(timestamp_s * (2 * np.pi / week2))
df['2 Weeks cos'] = np.cos(timestamp_s * (2 * np.pi / week2))
df['Month sin'] = np.sin(timestamp_s * (2 * np.pi / month))
df['Month cos'] = np.cos(timestamp_s * (2 * np.pi / month))
df['Year sin'] = np.sin(timestamp_s * (2 * np.pi / year))
df['Year cos'] = np.cos(timestamp_s * (2 * np.pi / year))

column_indices = {name: i for i, name in enumerate(df.columns)}

history = 96
shift = 96
prediction_window = 1

train_df = df[0:43825+shift-2]
val_df = df[43825-history-shift-1:44497+shift-2]
test_df = df[44497-history-shift-1:45169+shift-2]

num_features = df.shape[1]
print(num_features)

train_mean = train_df.mean()
train_std = train_df.std()

train_df = (train_df - train_mean) / train_std
val_df = (val_df - train_mean) / train_std
test_df = (test_df - train_mean) / train_std


def transform_data(dataframe, label, history, shift, prediction_window):
    if prediction_window > history:
        raise ValueError(
            "This transformation function can't handle transformations "
            "that require a prediction_window larger then history.")

    df_copy = dataframe.copy()
    y_df = df_copy[label][history+shift:]
    df_copy["target"] = df_copy[label].shift(-history-shift)
    df_copy = df_copy[:-history-shift]

    # -- transform 2D data into 3D data with history dimension --
    # create deque (first in first out queue) with length of history
    # cycle through sample data, put previous samples in a deque as history for said sample.
    # when enough history is available in deque "len(deq) == history":
    # start adding ( history x features ) matrices for each sample to a 3d array.
    deq = deque(maxlen=history)
    array = np.array(df_copy)
    data = list()
    for k, sample in enumerate(array):
        deq.append(sample)
        if len(deq) == history:
            data.append(np.array(deq))
    np_data = np.array(data)

    # slice only x data, remove "target" or label
    x_data = np_data[:, :, :-1]

    # slice only "target" or label
    # possibly prediction_window =/= history, take only prediction_window length as y label vector
    y_data = np_data[:, 0:prediction_window, -1:][:, :, 0]  # follow with a reshape

    return x_data, y_data, y_df[:len(y_data)]


print(train_df.shape)

train_x, train_y, train_y_df = transform_data(train_df, "GAWW-11", history, shift, prediction_window)
val_x, val_y, val_y_df = transform_data(val_df, "GAWW-11", history, shift, prediction_window)
test_x, test_y, test_y_df = transform_data(test_df, "GAWW-11", history, shift, prediction_window)

print("train_x shape: ", train_x.shape)
print("train_y shape: ", train_y.shape)
print("val_x shape: ", val_x.shape)
print("val_y shape: ", val_y.shape)
print("test_x shape: ", test_x.shape)
print("test_y shape: ", test_y.shape)

model = tf.keras.models.Sequential([
    tf.keras.layers.LSTM(units=32, dropout=0.2),
    tf.keras.layers.Dense(units=prediction_window, activation='linear')
])

early_stopping = tf.keras.callbacks.EarlyStopping(
    monitor='val_loss', patience=2,
    mode='min', restore_best_weights=True
)

reduce_lr = tf.keras.callbacks.ReduceLROnPlateau(
    monitor='val_loss', factor=0.2, patience=1, verbose=0,
    mode='auto', min_delta=0.0001, cooldown=0, min_lr=0
)

model.compile(loss=tf.losses.MeanSquaredError(),
              optimizer=tf.optimizers.Adam(learning_rate=1e-2),
              metrics=[tf.metrics.MeanAbsoluteError()])

print("Training model, this takes a while.")
history = model.fit(x=train_x, y=train_y, epochs=20, batch_size=18,
                    validation_data=(val_x, val_y),
                    callbacks=[early_stopping, reduce_lr])


print(model.summary())

# summarize history for loss
plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title('model loss')
plt.ylabel('loss')
plt.xlabel('epoch')
plt.legend(['train', 'val'], loc='upper left')
plt.show()

print("Predicting train, val and test data, this might take a while.")
train_pred = model.predict(train_x)
val_pred = model.predict(val_x)
test_pred = model.predict(test_x)

print("train_pred shape: ", train_pred.shape)
print("val_pred shape: ", val_pred.shape)
print("test_pred shape: ", test_pred.shape)

# inverse scale predictions and ground truths
train_pred_inv_scale = train_pred * train_std["GAWW-11"] + train_mean["GAWW-11"]
val_pred_inv_scale = val_pred * train_std["GAWW-11"] + train_mean["GAWW-11"]
test_pred_inv_scale = test_pred * train_std["GAWW-11"] + train_mean["GAWW-11"]

train_y_inv_scale = train_y * train_std["GAWW-11"] + train_mean["GAWW-11"]
val_y_inv_scale = val_y * train_std["GAWW-11"] + train_mean["GAWW-11"]
test_y_inv_scale = test_y * train_std["GAWW-11"] + train_mean["GAWW-11"]

# calculate rmse
train_mse = np.square(np.subtract(train_y_inv_scale, train_pred_inv_scale)).mean()
train_rmse = math.sqrt(train_mse)
val_mse = np.square(np.subtract(val_y_inv_scale, val_pred_inv_scale)).mean()
val_rmse = math.sqrt(val_mse)
test_mse = np.square(np.subtract(test_y_inv_scale, test_pred_inv_scale)).mean()
test_rmse = math.sqrt(test_mse)

print("Train RMSE:", train_rmse)
print("Validation RMSE:", val_rmse)
print("Test RMSE:", test_rmse)

train_pred_series = pd.Series(train_pred_inv_scale.flatten(), name='train_prediction').reset_index()
val_pred_series = pd.Series(val_pred_inv_scale.flatten(), name='val_prediction').reset_index()
test_pred_series = pd.Series(test_pred_inv_scale.flatten(), name='test_prediction').reset_index()

train_actual_series = pd.Series(train_y_inv_scale.flatten(), name='train_actual').reset_index()
val_actual_series = pd.Series(val_y_inv_scale.flatten(), name='val_actual').reset_index()
test_actual_series = pd.Series(test_y_inv_scale.flatten(), name='test_actual').reset_index()

train_datetime = pd.Series(df[0:43825+672-2].index[:-671], name='datetime').reset_index()
val_datetime = pd.Series(df[43825-672-672-1:44497+672-2].index[672*2:-671], name='datetime').reset_index()
test_datetime = pd.Series(df[44497-672-672-1:45169+672-2].index[672*2:-671], name='datetime').reset_index()

train_pred_df = pd.concat([train_datetime, train_actual_series, train_pred_series], axis=1)[['datetime', 'train_actual', 'train_prediction']]
val_pred_df = pd.concat([val_datetime, val_actual_series, val_pred_series], axis=1)[['datetime', 'val_actual', 'val_prediction']]
test_pred_df = pd.concat([test_datetime, test_actual_series, test_pred_series], axis=1)[['datetime', 'test_actual', 'test_prediction']]

train_pred_df.to_csv('../data/train_pred_lstm.csv', index=False)
val_pred_df.to_csv('../data/val_pred_lstm.csv', index=False)
test_pred_df.to_csv('../data/test_pred_lstm.csv', index=False)

train_pred_df[-672*3:-672*2].plot(x='datetime', y=["train_actual", "train_prediction"])
plt.show()
val_pred_df.plot(x='datetime', y=["val_actual", "val_prediction"])
plt.show()
test_pred_df.plot(x='datetime', y=["test_actual", "test_prediction"])
plt.show()

