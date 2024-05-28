import pandas as pd

# Загрузка данных из CSV
file_path = 'КАРТОЧКИ ВИЛЛЫ.csv'
data = pd.read_csv(file_path, delimiter=',')

# Печать всех столбцов
print(data.columns)
