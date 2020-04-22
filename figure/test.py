# -*- coding: utf-8 -*-

# In[1]:
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from patsy import dmatrices
import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.sandbox.regression.predstd import wls_prediction_std
from scipy.linalg import toeplitz


np.random.seed(9876789)


# In[2]:
df = sm.datasets.get_rdataset("Guerry", "HistData", cache=True).data
df2 = df[["Department", "Lottery", "Literacy", "Wealth", "Region"]].dropna()

f = "Lottery ~ Literacy + Wealth + Region"
y, X = dmatrices(f, data=df2, return_type="dataframe")

model = sm.OLS(y, X)
result = model.fit()
print(result.summary())
print(result.f_test("Literacy = 0"))


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


# In[6]
# condition number over 20 is worrisome
df = sm.datasets.longley.load_pandas()
y = df.endog
X = df.exog
X = sm.add_constant(X)
model = sm.OLS(y, X)
result = model.fit()
print(result.summary())


# In[6]
# compute condition number value manually
norm_x = np.zeros_like(X)
for i, name in enumerate(X):
    if name == "const":
        norm_x[:, i] = X[name]
    else:
        norm_x[:, i] = X[name] / np.linalg.norm(X[name])
norm_xtx = np.dot(norm_x.T, norm_x)
eigs = np.linalg.eigvals(norm_xtx)
condition_number = np.sqrt(eigs.max() / eigs.min())
result2 = sm.OLS(y.iloc[:14], X.iloc[:14]).fit()
print(result2.summary())
print(
    "Percentage change %4.2f%%\n"
    * 7
    % tuple([i for i in (result2.params - result.params) / result.params * 100])
)


# In[6]
infl = result.get_influence()
# DEBTAS in abs value greater than 2/sqrt(N) to be influential observations
debtas_thd = 2 / len(X) ** 0.5
debtas = infl.summary_frame().filter(regex="dfb").abs()
t = debtas > debtas_thd
i = t.sum(axis=1) == 0
result3 = sm.OLS(y.loc[i], X.loc[i, :]).fit()
print(t)


# In[7]
data = sm.datasets.longley.load(as_pandas=False)
data.exog = sm.add_constant(data.exog)
ols_resid = sm.OLS(data.endog, data.exog).fit().resid
resid_fit = sm.OLS(ols_resid[1:], ols_resid[:-1]).fit()
rho = resid_fit.params[0]
order = toeplitz(range(len(ols_resid)))
sigma = rho ** order
gls_result = sm.GLS(data.endog, data.exog, sigma=sigma).fit()
gls_sum = gls_result.summary()
print(gls_sum)


glsar_model = sm.GLSAR(data.endog, data.exog, 1)
glsar_result = glsar_model.iterative_fit(1)
print(glsar_result.summary())

print(gls_result.params)
print(glsar_result.params)
print(gls_result.bse)
print(glsar_result.bse)


# In[8]
# quantile regression

# LAD
data = sm.datasets.engel.load_pandas().data
model = smf.quantreg("foodexp ~ income", data)
# result = model.fit(q=0.5)
# print(result.summary())

quantiles = np.arange(0.05, 0.96, 0.1)


def fit_model(q):
    res = model.fit(q=q)
    return [q, res.params["Intercept"], res.params["income"]] + res.conf_int().loc[
        "income"
    ].tolist()


models = [fit_model(x) for x in quantiles]
models = pd.DataFrame(models, columns=["q", "a", "b", "lb", "ub"])

ols = smf.ols("foodexp ~ income", data).fit()
ols_ci = ols.conf_int().loc["income"].tolist()
ols = {
    "a": ols.params["Intercept"],
    "b": ols.params["income"],
    "lb": ols_ci[0],
    "ub": ols_ci[1],
}
lad = smf.quantreg("foodexp ~ income", data).fit()
lad_ci = lad.conf_int().loc["income"].tolist()
lad = {
    "a": lad.params["Intercept"],
    "b": lad.params["income"],
    "lb": lad_ci[0],
    "ub": lad_ci[1],
}

# print(models)
# print(ols)

x = np.arange(data["income"].min(), data["income"].max(), 50)
get_y = lambda a, b: a + b * x
fig, ax = plt.subplots(figsize=(8, 6))
for i in range(models.shape[0]):
    y = get_y(models.a[i], models.b[i])
    ax.plot(x, y, linestyle="dotted", color="grey")

ax.plot(x, get_y(ols["a"], ols["b"]), color="red", label="OLS")
ax.plot(x, get_y(lad["a"], lad["b"]), color="green", label="LAD")
ax.scatter(data["income"], data["foodexp"], alpha=0.2)
ax.set_xlim((240, 3000))
ax.set_ylim((240, 2000))
legend = ax.legend()
ax.set_xlabel("Income", fontsize=16)
ax.set_ylabel("Food expenditure", fontsize=16)


# In[9]:
moore = sm.datasets.get_rdataset("Moore", "carData", cache=True)
data = moore.data
data = data.rename(columns={i: i.replace(".", "_") for i in data.columns})
f= 'conformity ~ C(fcategory, Sum) * C(partner_status, Sum)'
# y, X = dmatrices(f, data=data, return_type="dataframe")
moore_lm = smf.ols(f,data=data).fit()
table1 = sm.stats.anova_lm(moore_lm, typ=1)
table2 = sm.stats.anova_lm(moore_lm, typ=2)
table3 = sm.stats.anova_lm(moore_lm, typ=3)
