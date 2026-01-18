import requests
import matplotlib.pyplot as plt


def load_data():
    """ Load data from PRIS113 dataset """
    url = "https://api.statbank.dk/v1/data"
    response = requests.post(url, json={
        "table": "PRIS113",
        "format": "CSV",
        "variables": [
            {
                "code": "Tid",
                "placement": "Stub",
                "values": [
                    "*"
                ]
            }
        ]        
    })    
    data = {}
    for line in response.text.splitlines()[1:]:  # Skip header
        fields = line.split(';')
        datemonth = fields[0].split('M')
        year = datemonth[0]
        month = datemonth[1].lstrip('0') or '0'  # Remove leading zero
        if year not in data:
            data[year] = {'values': {}}

        monthIntValue = float(fields[1].replace(',', '.'))
        data[year]['values'][month] = {'value': monthIntValue}

    return data


def process_data(data):
    """ Process the loaded data """

    # Calculate year totals
    for key, value in data.items():
        yearTotal = 0
        for month, month_data in value['values'].items():
            yearTotal += month_data['value']
        data[key]['total'] = yearTotal

    # Calculate consumer price index (base year 2000)
    cpi_base_value = data['2000']['total'] / 12
    for key, value in data.items():
        for month, month_data in value['values'].items():
            month_data['cpi'] = month_data['value'] / cpi_base_value * 100

    # Calculate inflation rates
    for key, value in data.items():
        for month, month_data in value['values'].items():
            last_month_data = None
            last_year = str(int(key) - 1)

            # Previous month
            if month == '1':
                if last_year in data:
                    last_month_data = data[last_year]['values'].get('12')
            else:
                last_month_data = data[key]['values'].get(str(int(month) - 1))

            # Month-to-month inflation
            if last_month_data:
                month_data['month_to_month_inflation'] = month_data['cpi'] / last_month_data['cpi'] - 1

            # 12-month inflation
            if last_year in data and month in data[last_year]['values']:
                last_year_data = data[last_year]['values'][month]
                month_data['12_month_inflation'] = month_data['cpi'] / last_year_data['cpi'] - 1
                
    