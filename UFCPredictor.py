import csv
import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

from keras.models import Sequential
from keras.layers import Dense
from keras.layers import Dropout
from keras import regularizers

import pydot
from IPython.display import SVG
from keras.utils.vis_utils import model_to_dot
from keras.utils import plot_model

def process_file(file_name):
    f = open(file_name, newline='')
    reader = csv.reader(f, delimiter=',')
    headers = next(reader)
    all = []
    for row in reader:
        single = {}
        for i in range(0, len(row)):
            single[str(headers[i])] = row[i]
        all.append(single)
    return all

# Fetch data
nn_data = pd.read_csv('stats/NeuralNetworkData.csv', index_col = 0)


X, y = nn_data.iloc[:, 1:], nn_data.iloc[:, 0]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.1, random_state=0)

# Normalization
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

model = Sequential()
model.add(Dense(20, input_dim=X_train_scaled.shape[1],activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(20, activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(10, activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(1, activation='sigmoid'))
model.compile(loss='binary_crossentropy', optimizer='Adam', metrics=['accuracy'])

#print(SVG(model_to_dot(model).create(prog='dot', format='svg')))

model.fit(x=X_train_scaled, y=y_train, epochs=500, verbose=0)
test_results = model.evaluate(x = X_test_scaled, y = y_test, verbose=0)
print("Test Accuracy = {}".format(test_results[1]))
train_results = model.evaluate(x = X_train_scaled, y = y_train, verbose=0)
print("Train Accuracy = {}".format(train_results[1]))