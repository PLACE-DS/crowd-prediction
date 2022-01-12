library(tidyr)
library(dplyr)
# library(fastDummies)
# library(stringr)
library(tsibble)
library(fpp3)

# load data
df_full <- read.csv('../data/cmsa_combined.csv')

# subset and format data
format_df <- function(df){
  df <- df %>%
    select(c(1,2))
  df$datetime <- as.POSIXct(df$datetime, format="%Y-%m-%d %H:%M:%S", tz="UTC")
  df <- df %>% 
    as_tsibble(index = datetime) %>% 
    filter(datetime < ymd_hms("2021-12-08 00:00:00")) 
  
  return(df)
}

df_11 <- df_full %>%
  select(c(1,2)) %>% 
  format_df()

df_12 <- df_full %>%
  select(c(1,3)) %>% 
  format_df()

df_14 <- df_full %>%
  select(c(1,4)) %>% 
  format_df()

create_train <- function(df){
  train <- df %>% 
    train %>% 
    as_tsibble(index = datetime) %>% 
    filter(datetime < ymd_hms("2021-12-01 00:00:00")) 
  
  return(train)
}

# train_11 <- df_11 
# # train_11$datetime <- as.POSIXct(train_11$datetime, format="%Y-%m-%d %H:%M:%S", tz="UTC")
# train_11 <- train_11 %>% 
#   as_tsibble(index = datetime) %>% 
#   filter(datetime < ymd_hms("2021-12-01 00:00:00")) 

train_11 <- create_train(df_11)
train_12 <- create_train(df_12)
train_14 <- create_train(df_14)

# train_12 <- df_12
# train_12$datetime <- as.POSIXct(train_12$datetime, format="%Y-%m-%d %H:%M:%S", tz="UTC")
# train_12 <- train_12 %>% 
#   as_tsibble(index = datetime) %>% 
#   filter(datetime < ymd_hms("2021-12-01 00:00:00")) 
# 
# train_14 <- df_14
# train_14$datetime <- as.POSIXct(train_14$datetime, format="%Y-%m-%d %H:%M:%S", tz="UTC")
# train_14 <- train_14 %>% 
#   as_tsibble(index = datetime) %>% 
#   filter(datetime < ymd_hms("2021-12-01 00:00:00")) 

fit_11 <- train_11 %>% 
  model(
    `ARIMA` = ARIMA(GAWW.11),
    # `ARIMA-F1` = ARIMA(GAWW.11 ~ fourier(K=1, period=24*4)), 
    # `ARIMA-F2` = ARIMA(GAWW.11 ~ fourier(K=2, period=24*4)),
    # `ARIMA-F3` = ARIMA(GAWW.11 ~ fourier(K=3, period=24*4)),
  )

fc_11 <- fit_11 %>% forecast(h=24*4*7)

acc <- accuracy(fc_11, df_11) 
acc

pred <- fc_11 %>%
  as_tibble %>% 
  select(datetime, `.mean`)

write.csv(pred, "../data/pred_arima_TEST.csv", row.names = FALSE)
