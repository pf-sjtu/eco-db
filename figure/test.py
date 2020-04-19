# -*- coding: utf-8 -*-

# In[1]:
import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from patsy import dmatrices
from statsmodels.sandbox.regression.predstd import wls_prediction_std
from matplotlib import pyplot as plt

np.random.seed(9876789)

# In[2]:
df = sm.datasets.get_rdataset("Guerry", "HistData", cache=True).data
df2 = df[["Department", "Lottery", "Literacy", "Wealth", "Region"]].dropna()

f = "Lottery ~ Literacy + Wealth + Region"
y, X = dmatrices(f, data=df2, return_type="dataframe")

model = sm.OLS(y, X)
result = model.fit()
print(result.summary())


# In[3]:
nsample = 100
x = np.linspace(0, 10, nsample)
X = np.column_stack((x, x ** 2))
beta = np.array([1, 0.1, 10])
e = np.random.normal(size=nsample)

X = sm.add_constant(X)
y = np.dot(X, beta) + e

model = sm.OLS(y, X)
result = model.fit()
print(result.summary())


# In[4]:
nsample = 50
sig = 0.5
x = np.linspace(0, 20, nsample)
X = np.column_stack((x, np.sin(x), (x - 5) ** 2, np.ones(nsample)))
beta = [0.5, 0.6, -0.02, 5.0]

y_true = np.dot(X, beta)
y = y_true + sig * np.random.normal(size=nsample)

model = sm.OLS(y, X)
result = model.fit()
print(result.summary())
y_pred = result.predict()  # result.fittedvalues

prstd, iv_l, iv_u = wls_prediction_std(result)

fig, ax = plt.subplots(1, 2, figsize=(16, 6))
ax[0].plot(x, y, "o", label="data")
ax[0].plot(x, y_true, "b-", label="True")
ax[0].plot(x, y_pred, "r--", label="OLS")
ax[0].plot(x, iv_l, "r--")
ax[0].plot(x, iv_u, "r--")
ax[0].legend(loc="best")

qq_data = np.column_stack((y_true, y_pred))
qq_data = qq_data[np.argsort(qq_data[:, 0]), :]
ax[1].plot(qq_data[:, 0], qq_data[:, 1], "o")
ax[1].set_xlabel("True")
ax[1].set_ylabel("Predict")


# In[5]:
nsample = 50
groups = np.zeros(nsample, int)
groups[20:40] = 1
groups[40:] = 2
# dummy = (groups[:, None] == np.unique(groups)).astype(float)
dummy = sm.categorical(groups, drop=True)
x = np.linspace(0, 20, nsample)
X = np.column_stack((x, dummy[:, 1:]))
X = sm.add_constant(X, prepend=True)

beta = [1, 3, -3, 10]
y_true = np.dot(X, beta)
e = np.random.normal(size=nsample)
y = y_true + e

model = sm.OLS(y, X)
result = model.fit()
print(result.summary())
y_pred = result.predict()  # result.fittedvalues

prstd, iv_l, iv_u = wls_prediction_std(result)

fig, ax = plt.subplots(1, 2, figsize=(16, 6))
ax[0].plot(x, y, "o", label="data")
ax[0].plot(x, y_true, "b-", label="True")
ax[0].plot(x, y_pred, "r--", label="OLS")
ax[0].plot(x, iv_l, "r--")
ax[0].plot(x, iv_u, "r--")
ax[0].legend(loc="best")

qq_data = np.column_stack((y_true, y_pred))
qq_data = qq_data[np.argsort(qq_data[:, 0]), :]
ax[1].plot(qq_data[:, 0], qq_data[:, 1], "o")
ax[1].set_xlabel("True")
ax[1].set_ylabel("Predict")

R = [[0, 1, 0, 0], [0, 0, 1, 0]]
R2 = np.diag(np.ones(4, dtype=int))
print(result.f_test(R))
print(result.f_test("x2 = x3 = 0"))
