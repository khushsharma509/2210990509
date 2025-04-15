from flask import Flask, request, jsonify
import requests
from collections import deque
import time

app = Flask(__name__)

WINDOW_SIZE = 10
TIMEOUT = 0.5

number_servers = {
    'p': 'http://20.244.56.144/evaluation-service/primes',
    'f': 'http://20.244.56.144/evaluation-service/fibo', 
    'e': 'http://20.244.56.144/evaluation-service/even',
    'r': 'http://20.244.56.144/evaluation-service/rand'
}

number_storage = {
    'p': deque(maxlen=WINDOW_SIZE),
    'f': deque(maxlen=WINDOW_SIZE),
    'e': deque(maxlen=WINDOW_SIZE),
    'r': deque(maxlen=WINDOW_SIZE)
}

def get_numbers_from_server(number_type):
    try:
        response = requests.get(number_servers[number_type], timeout=TIMEOUT)
        if response.ok:
            return response.json().get('numbers', [])
    except:
        return []
    return []

def compute_average(nums):
    return sum(nums)/len(nums) if nums else 0

@app.route('/numbers/<string:num_type>')
def process_numbers(num_type):
    start = time.time()
    
    if num_type not in number_servers:
        return jsonify({"error": "Invalid number type"}), 400
    
    previous_numbers = list(number_storage[num_type])
    fresh_numbers = get_numbers_from_server(num_type)
    
    for num in fresh_numbers:
        if num not in number_storage[num_type]:
            number_storage[num_type].append(num)
    
    current_numbers = list(number_storage[num_type])
    average = round(compute_average(current_numbers), 2)
    
    if time.time() - start > TIMEOUT:
        return jsonify({"error": "Processing took too long"}), 500
    
    return jsonify({
        "windowPrevState": previous_numbers,
        "windowCurrState": current_numbers,
        "numbers": fresh_numbers,
        "avg": average
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9876)