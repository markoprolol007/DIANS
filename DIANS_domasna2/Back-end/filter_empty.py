import pandas as pd

df = pd.read_csv('data.csv')
filtered = df[df['Количина'] != 0]

filtered.to_csv('filtered.csv', index=False)
print('Data written to filtered.csv file')