import time

from bs4 import BeautifulSoup
import requests
import pandas as pd
from datetime import datetime

scrape = requests.get('https://www.mse.mk/mk/stats/symbolhistory/kmb')
soup = BeautifulSoup(scrape.text, 'html.parser')


def get_data_for(code, startDate, endDate):
    url = 'https://www.mse.mk/mk/stats/symbolhistory/' + code
    data = {
        'FromDate': startDate.strftime('%d.%m.%Y'),
        'ToDate': endDate.strftime('%d.%m.%Y'),
        'Code': code
    }

    response = requests.post(url, data=data)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        # наслови на колоните
        headers = [th.text.strip() for th in soup.find_all('th')]

        # најди ги сите редови во табелата и прескокни го првиот
        column_row = soup.findAll('tr')[1:]

        table = soup.find('table')

        if table:
            rows = []
            for row in column_row:
                row_data = row.find_all('td')  # најди ги сите полиња во редот
                if row_data:
                    individual_row_data = [pole.text.strip() for pole in row_data]
                    individual_row_data.insert(0, code)
                    rows.append(individual_row_data)

            df = pd.DataFrame(rows, columns=['Име'] + headers)
            return df
        else:
            print('No data for', code)
            return pd.DataFrame()
    else:
        print('Error')
        return pd.DataFrame()


end = datetime.now()
# почетокот е 10 години пред
start = end.replace(year=end.year - 10)

# имиња на сите издавачи филтрирани без тие со броеви
names = [option.text for option in soup.find_all('option') if not any(char.isdigit() for char in option.text)]

all_data = pd.DataFrame()

startTime = time.time()

for year in range(10):
    start_date = start.replace(year=start.year + year)
    end_date = start.replace(year=start.year + year + 1)

    for name in names:
        df = get_data_for(name, start_date, end_date)
        all_data = pd.concat([all_data, df], ignore_index=True)

all_data.to_csv('data.csv', index=False)

print('Data written to csv file')

print(f"Execution completed in {time.time() - startTime:.2f} seconds.")