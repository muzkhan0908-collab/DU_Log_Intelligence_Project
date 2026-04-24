from flask import Flask, request, render_template, jsonify
import re

app = Flask(__name__)

parsed_data = {}
ue_ids = []

@app.route('/', methods=['GET', 'POST'])
def home():
    global parsed_data, ue_ids

    ue_ids = []
    flow_steps = []



    # 🔸 Step 1: Upload log file
    if request.method == 'POST' and 'logfile' in request.files:
       
        file = request.files['logfile']
        content = file.read().decode('utf-8')

        parsed_data = {}

        # 🔸 Step 2: Extract ue ids + steps
        lines = content.splitlines()

        for line in lines:
            pattern = r":UE_ID:([^:]+):"
            match = re.search(pattern, line)
            if match:
                ue = match.group(1)

                if ue not in parsed_data:
                    parsed_data[ue] = []

                # Add log line as step
                parsed_data[ue].append(line.strip())

        ue_ids = list(parsed_data.keys())

    # 🔸 Step 3: Dropdown selection
    if request.method == 'POST' and "ue_id" in request.form:
        selected_ue = request.form.get("ue_id")
        flow_steps = parsed_data.get(selected_ue, [])
        ue_ids = list(parsed_data.keys())
    
   
    return render_template('index.html', ue_ids=ue_ids, flow=flow_steps)

@app.route('/search_users')
def search_users():
    query = request.args.get('q', '').lower()

    # Filter based on query
    results = [u for u in ue_ids if query in u.lower()]

    return jsonify(results[:10])  # limit results

if __name__ == '__main__':
    app.run(debug=True)