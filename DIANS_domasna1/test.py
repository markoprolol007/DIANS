from bs4 import BeautifulSoup
import requests
import pandas as pd
import csv
from datetime import datetime

scrape = requests.get('https://www.mse.mk/mk/stats/symbolhistory/ADIN')
soup = BeautifulSoup(scrape.text, 'html.parser')
# имиња на сите издавачи филтрирани без тие со броеви
names = [option.text for option in soup.find_all('option') if not any(char.isdigit() for char in option.text)]
# print(names)


def get_data_for(name, start_date, end_date):
    url = 'https://www.mse.mk/mk/stats/symbolhistory/' + name
    data = {
        'Name': name,
        'StartDate': start_date.strftime('%d.%m.%Y'),
        'EndDate': end_date.strftime('%d.%m.%Y')
    }

    page = requests.post(url, data=data)

    if page.status_code == 200:
        # наслови на колоните
        headers = [th.text.strip() for th in soup.find_all('th')]

        table = soup.findAll('table')

        titles = soup.findAll('th')

        # најди ги сите редови во табелата и прескокни го првиот
        column_row = soup.findAll('tr')[1:]
        rows = []

        if table:
            for row in column_row:
                row_data = row.find_all('td')  # најди ги сите полиња во редот
                individual_row_data = [pole.text.strip() for pole in row_data]
                individual_row_data.insert(0, name)
                rows.append(individual_row_data)

            df = pd.DataFrame(rows, columns=['Name'] + headers)

            return df
        else:
            print('No data for ', name)
            return pd.DataFrame()
    else:
        print('Error')
        return pd.DataFrame()


end = datetime.now()
# почетокот е 10 години пред
start = end.replace(year=end.year - 10)

all_data = pd.DataFrame()

for temp in range(10):
    start_date = start.replace(year=start.year + temp)
    end_date = start.replace(year=start.year + temp + 1)

    for name in names:
        data = get_data_for(name, start_date, end_date)
        all_data = pd.concat([all_data, data], ignore_index=True)


all_data.to_csv('data.csv', index=False)

print('Data written to csv file')
