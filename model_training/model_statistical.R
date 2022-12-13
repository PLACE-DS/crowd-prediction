library(tidyr)
library(dplyr)
library(fastDummies)
library(stringr)
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
    filter(datetime < ymd_hms("2021-12-16 00:00:00")) 
  
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
    as_tsibble(index = datetime) %>% 
    filter(datetime < ymd_hms("2021-12-01 12:00:00")) 
  
  return(train)
}

train_11 <- create_train(df_11)
train_12 <- create_train(df_12)
train_14 <- create_train(df_14)

train_11 <- train_11 %>% rename(value = GAWW.11) %>% as_tsibble()
train_12 <- train_12 %>% rename(value = GAWW.12) %>% as_tsibble()
train_14 <- train_14 %>% rename(value = GAWW.14) %>% as_tsibble()

# modeling
fit_11_k20 <- train_11 %>% 
  model(
    `ARIMA` = ARIMA(value),
    `ARIMA-F20` = ARIMA(value ~ fourier(K=20, period=24*4)),
    `ARIMA-F1` = ARIMA(value ~ fourier(K=2, period=24*4)),
    `ARIMA-F2` = ARIMA(value ~ fourier(K=2, period=24*4)),
    `ARIMA-F3` = ARIMA(value ~ fourier(K=3, period=24*4)),
  )

fc_11_k20 <- fit_11_k20 %>% forecast(h=24*4*7)

df_11 <- df_11 %>% rename(value = GAWW.11) %>% as_tsibble()

acc_11_k20 <- accuracy(fc_11_k20, df_11) 
acc_11_k20

pred_k20 <- fc_11_k20 %>%
  as_tibble %>% 
  filter(.model=="ARIMA") %>% 
  select(datetime, `.mean`) 

test <- df_11 %>%
  filter(datetime > ymd_hms("2021-11-30 00:00:00")) %>%
  as_tsibble()

fc_11_k20 %>% autoplot(test, level=FALSE)

# test <- df_11 %>% 
#   filter(datetime > ymd_hms("2021-11-01 00:00:00")) %>% 
#   as_tsibble()
# 
# autoplot(test)

write.csv(pred, "../data/pred_arima_TEST.csv", row.names = FALSE)




# Careful this takes forever
fit_11 <- model(train_11,
             `K = 01` = ARIMA(value ~ fourier(K=1, period=24*4)),
             `K = 02` = ARIMA(value ~ fourier(K=2, period=24*4)),
             `K = 03` = ARIMA(value ~ fourier(K=3, period=24*4)),
             `K = 04` = ARIMA(value ~ fourier(K=4, period=24*4)),
             `K = 05` = ARIMA(value ~ fourier(K=5, period=24*4)),
             `K = 06` = ARIMA(value ~ fourier(K=6, period=24*4)),
             `K = 07` = ARIMA(value ~ fourier(K=7, period=24*4)),
             `K = 08` = ARIMA(value ~ fourier(K=8, period=24*4)),
             `K = 09` = ARIMA(value ~ fourier(K=9, period=24*4)),
             `K = 10` = ARIMA(value ~ fourier(K=10, period=24*4)),
             `K = 11` = ARIMA(value ~ fourier(K=11, period=24*4)),
             `K = 12` = ARIMA(value ~ fourier(K=12, period=24*4)),
             `K = 13` = ARIMA(value ~ fourier(K=13, period=24*4)),
             `K = 14` = ARIMA(value ~ fourier(K=14, period=24*4)),
             `K = 15` = ARIMA(value ~ fourier(K=15, period=24*4)),
             `K = 16` = ARIMA(value ~ fourier(K=16, period=24*4)),
             `K = 17` = ARIMA(value ~ fourier(K=17, period=24*4)),
             `K = 18` = ARIMA(value ~ fourier(K=18, period=24*4)),
             `K = 19` = ARIMA(value ~ fourier(K=19, period=24*4)),
             `K = 20` = ARIMA(value ~ fourier(K=20, period=24*4)),
             `K = 21` = ARIMA(value ~ fourier(K=21, period=24*4)),
             `K = 22` = ARIMA(value ~ fourier(K=22, period=24*4)),
             `K = 23` = ARIMA(value ~ fourier(K=23, period=24*4)),
             `K = 24` = ARIMA(value ~ fourier(K=24, period=24*4)),
             `K = 25` = ARIMA(value ~ fourier(K=25, period=24*4)),
             `K = 26` = ARIMA(value ~ fourier(K=26, period=24*4))
)
library(gt)
library(gridExtra)

fit_11 %>% glance() %>% # if you want to plot the accuracies table, this one works
  select(-c(ar_roots,ma_roots)) %>%
  gt() %>%
  tab_header(
    title = md("**HR w/ Fouriers comparison**")
  ) %>% opt_align_table_header(align = "center")

g <- fit_11 %>% glance() %>% select(AICc)
g <- data.frame(AICc = g$AICc, K = seq(1,26,1))

p1 <- ggplot(g, aes(x=K, y=AICc, group =1)) + geom_path()+
  geom_point() + labs(title = "AICc of HR with K Fourier terms")

p2 <- train_11 %>% autoplot(value) + #plot
  geom_line(data = fitted(fit_11 %>% select("K = 20")),
            aes(y = .fitted, colour = .model), size = 1, alpha = 0.5) +
  labs(title = "K = 20 harmonic regression fit") +
  theme(legend.position = "none")

grid.arrange(p1,p2, ncol=2)