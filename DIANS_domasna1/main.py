import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import time

scrape = requests.get('https://www.mse.mk/mk/stats/symbolhistory/kmb')
soup = BeautifulSoup(scrape.text, 'html.parser')
names = [option.text for option in soup.find_all('option') if not any(char.isdigit() for char in option.text)]


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


def load_existing_data(filename='data.csv'):
    try:
        existing_data = pd.read_csv(filename, parse_dates=['Датум'], dayfirst=True)
        print("Existing data loaded.")
        return existing_data
    except FileNotFoundError:
        print("No existing data found. Getting data for the last 10 years.")
        return pd.DataFrame()


def update_data_for_issuers():
    existing_data = load_existing_data()
    latest_data = pd.DataFrame()
    today = datetime.now()

    for name in names:
        if not existing_data.empty and name in existing_data['Име'].values:
            issuer_data = existing_data[existing_data['Име'] == name]
            last_date = issuer_data['Датум'].max()
            if last_date < today - timedelta(days=1):
                start_date = last_date + timedelta(days=1)
                print(f"Updating {name} data from {start_date.strftime('%d.%m.%Y')} to {today.strftime('%d.%m.%Y')}")
                new_data = get_data_for(name, start_date, today)
                latest_data = pd.concat([latest_data, new_data], ignore_index=True)
            else:
                print(f"{name} data is up to date.")
        else:
            start_date = today - timedelta(days=365 * 10)
            print(f"No existing data for {name}. Retrieving data since {start_date.strftime('%d.%m.%Y')}")
            new_data = get_data_for(name, start_date, today)
            latest_data = pd.concat([latest_data, new_data], ignore_index=True)

    if not latest_data.empty:
        save_filtered_data(latest_data)


def save_filtered_data(new_data, filename='data.csv'):
    filtered_data = new_data[new_data['Количина'] != '0']
    if not filtered_data.empty:
        append_mode = 'a' if pd.io.common.file_exists(filename) else 'w'
        filtered_data.to_csv(filename, mode=append_mode, index=False, header=append_mode == 'w')
        print(f"Filtered data has been saved to '{filename}'.")
    else:
        print("No new data to save.")


def main():
    start = time.time()
    update_data_for_issuers()
    print(f"Execution completed in {time.time() - start:.2f} seconds.")


if __name__ == "__main__":
    main()
