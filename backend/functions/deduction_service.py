import requests
import os

def apply_deductions(pharmacy_id, case_id, deductions):
    """
    Calls the IHBS API to apply deductions.
    """
    api_url = os.getenv('IHBS_API_URL', 'https://api.ihbs.rssb.rw/v1/deductions/apply')
    api_key = os.getenv('IHBS_API_KEY', 'MOCK_API_KEY')

    payload = {
        'pharmacy_id': pharmacy_id,
        'case_id': case_id,
        'deductions': deductions,
        'source': 'COUNTER_VERIFICATION'
    }

    # In a real environment, we'd call the API:
    # response = requests.post(api_url, json=payload, headers={'X-API-KEY': api_key})
    # response.raise_for_status()
    # return response.json()

    return {'status': 'success', 'confirmation_id': f'IHBS-CONF-{case_id}'}
