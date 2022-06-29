import pandas as pd

stations = pd.read_csv('C:/Users/lml6626/Documents/urban_malaria/emodtrials/data/Ibadan_ward_pop.csv')
stations.head()
list(stations.columns)

points = pd.read_csv('data/points.csv')
points.head()