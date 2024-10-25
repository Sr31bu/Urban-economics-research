import pandas_datareader.data as web
import statsmodels.api as sm
import pandas as pd

# Load Fama-French factors from Kenneth French's data library via pandas_datareader
ff_data = web.DataReader("F-F_Research_Data_Factors", "famafrench", start='1926-07-01', end='2024-09-01')[0]

# Display the first few rows to check data
print(ff_data.head())

# Step (a): CAPM Beta - Regress MKT_RF on SMB
X_capm = sm.add_constant(ff_data['SMB'])  # SMB is the size factor
y_capm = ff_data['Mkt-RF']  # MKT_RF is the market premium

capm_model = sm.OLS(y_capm, X_capm).fit()

# Step (b): Fama-French Three-Factor Model - Regress MKT_RF on MKT_RF, SMB, and HML
X_ff = sm.add_constant(ff_data[['Mkt-RF', 'SMB', 'HML']])  # Include three factors
y_ff = ff_data['Mkt-RF']  # MKT_RF as the dependent variable

ff_model = sm.OLS(y_ff, X_ff).fit()

# Print the results
print("CAPM Model Results:")
print(capm_model.summary())

print("\nFama-French Three-Factor Model Results:")
print(ff_model.summary())
