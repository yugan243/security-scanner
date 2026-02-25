```python
from flask import Flask, request, jsonify
from ast import literal_eval

app = Flask(__name__)

@app.route('/')
def index():
    # Get the user input from the URL
    user_input = request.args.get('input', '')

    # Check if the user input is empty
    if not user_input:
        return jsonify({"error": "No input provided."}), 400

    try:
        # Safely evaluate the user input as Python code
        result = literal_eval(user_input)
    except (ValueError, SyntaxError):
        return jsonify({"error": "Invalid input."}), 400

    # Return the result of the evaluation
    return jsonify({"result": result})

if __name__ == '__main__':
    app.run()
```