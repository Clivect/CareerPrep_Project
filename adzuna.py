import requests

def get_job_listings(query):
    api_url = 'https://api.adzuna.com/v1/api/jobs/us/search/1'
    params = {
        'app_id': '7e5637e9',
        'app_key': '3ae6973897f268f1bd9eb002e21193fc',
        'results_per_page': 100,
        'what': query,
        'where': 'USA' 
    }
    response = requests.get(api_url, params=params)
    return response.json().get('results', [])

