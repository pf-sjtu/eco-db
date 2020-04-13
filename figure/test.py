# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
# from sklearn import datasets

# iris = datasets.load_iris()
# dat = pd.DataFrame(data=iris.data, columns=["sl", "sw", "pl", "pw"])

# model = smf.ols('pw ~ sw + sl', data=dat).fit()
# t = model.summary()
# fig = sm.qqplot(model.resid, line="s")
# ax = fig.axes[0]
# fig.show()

# dat2 = pd.DataFrame(data=np.random.rand(100, 2), columns=["a", "b"])
# model2 = sm.OLS(dat2["a"], dat2["b"]).fit()
# t2 = model2.summary()

# model3 = smf.ols('a ~ b', data=dat2).fit()
# t3 = model2.summary()

# fig = sm.qqplot(model3.resid, line="s")
# ax = fig.axes[0]
# fig.show()

# import statsmodels.api as sm
# import pandas as pd
# from patsy import dmatrices

# df = pd.DataFrame(data=iris.data, columns=["sl", "sw", "pl", "pw"])。
df = sm.datasets.get_rdataset("Guerry", "HistData", cache=True).data


# import urllib

# url = 'https://raw.githubusercontent.com/vincentarelbundock/Rdatasets/master/csv/HistData/Guerry.csv'
# headers = {'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:75.0) Gecko/20100101 Firefox/75.0'}
# request = urllib.request.Request(url, headers=headers)
# r_open = urllib.request.urlopen(request, timeout=3)
# content = r_open.read()#读取，一般会在这里报异常
# r_open.close()#记得要关闭
