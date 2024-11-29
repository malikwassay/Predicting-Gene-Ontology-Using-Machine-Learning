import requests

url = 'http://127.0.0.1:5000/predict'

data = {
    'sequence': 'MTEYKLVVVGAGGVGKSALTIQLIQY'  # Example protein sequence
}

response = requests.post(url, json=data)

print(response.json())  # Expected response: {'predicted_function': 'Function_A'}