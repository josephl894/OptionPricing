from datetime import datetime,date
from fredapi import Fred
# Quoting market yield on US Treasury Security as the risk-free interest rate
def get_series_id_for_duration(duration_in_days):
    if duration_in_days <= 30:
        return 'DGS1MO'
    elif duration_in_days <= 90:
        return 'DGS3MO'
    elif duration_in_days <= 180:
        return 'DGS6MO'
    elif duration_in_days <= 365:
        return 'DGS1'
    elif duration_in_days <= 730:
        return 'DGS2'
    elif duration_in_days <= 1095:
        return 'DGS3'
    elif duration_in_days <= 1460:
        return 'DGS4'
    elif duration_in_days <= 1825:
        return 'DGS5'
    else:
        raise ValueError("Duration too long for available series IDs")

def fetch_gov_yield(expiration_date):
    today = datetime.today()
    duration = (expiration_date - today).days
    series_id = get_series_id_for_duration(duration)

    fred = Fred(api_key='c255ca831a82e6ff54c571429f101c45')
    yield_data = fred.get_series_latest_release(series_id)
    
    return yield_data[-1] / 100
