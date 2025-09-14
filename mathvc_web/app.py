from flask import Flask, render_template, request, jsonify
import sys
import os

# Add the parent directory to the system path to allow imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from mathvc_system_meta_planner import MATHVCMetaPlannerSystem

app = Flask(__name__)

# Initialize the MATHVC Meta Planner System
# We need to specify the correct path to the 'configs' directory
config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'configs'))
planner = MATHVCMetaPlannerSystem(config_dir=config_path)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/send_message', methods=['POST'])
def send_message():
    user_input = request.json.get('message')
    if not user_input:
        return jsonify({'error': 'No message provided'}), 400

    response = planner.meta_planner_process(user_input)
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)
