import time
from bs4 import BeautifulSoup
import requests
import pandas as pd
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

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
        headers = [th.text.strip() for th in soup.find_all('th')]
        column_row = soup.findAll('tr')[1:]
        table = soup.find('table')

        if table:
            rows = []
            for row in column_row:
                row_data = row.find_all('td')
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

def fetch_data_for_year(year, names, start, end):
    start_date = start.replace(year=start.year + year)
    end_date = start.replace(year=start.year + year + 1)
    data_frames = []

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(get_data_for, name, start_date, end_date) for name in names]
        for future in futures:
            df = future.result()
            if not df.empty:
                data_frames.append(df)

    return data_frames

end = datetime.now()
start = end.replace(year=end.year - 10)
scrape = requests.get('https://www.mse.mk/mk/stats/symbolhistory/kmb')
soup = BeautifulSoup(scrape.text, 'html.parser')
names = [option.text for option in soup.find_all('option') if not any(char.isdigit() for char in option.text)]

all_data = []
startTime = time.time()

for year in range(10):
    all_data.extend(fetch_data_for_year(year, names, start, end))

final_df = pd.concat(all_data, ignore_index=True)
final_df.to_csv('data.csv', index=False)

print('Data written to csv file')
print(f"Execution completed in {time.time() - startTime:.2f} seconds.")
