from flask import Flask, request, render_template, jsonify
import re
import gen_flow_diagram

app = Flask(__name__)

# Store parsed logs globally
parsed_data = {}

@app.route('/', methods=['GET', 'POST'])
def home():
    global parsed_data

    flow_steps = []
    ue_ids = []

    # 🔹 Step 1: Handle file upload
    if request.method == 'POST' and 'logfile' in request.files:
        file = request.files['logfile']
        content = file.read().decode('utf-8')
        print(f"======/ uploaded name========== :{file}")
        parsed_data = {}

        lines = content.splitlines()

        for line in lines:
            # Flexible regex
            match = re.search(r"UE_ID[:=]([0-9]+)", line)

            if match:
                ue = match.group(1)

                if ue not in parsed_data:
                    parsed_data[ue] = []

                # Clean text for Mermaid
                clean_line = re.sub(r'[^a-zA-Z0-9 _-]', '', line)
                parsed_data[ue].append(clean_line)
        ue_ids = list(parsed_data.keys())
        print(f"======ue_ids========: {ue_ids}")

    # 🔹 Step 2: Handle UE selection (GET method)
    elif request.method == 'GET' and 'ue_id' in request.args:
        selected_ue = request.args.get('ue_id')

        ue_ids = list(parsed_data.keys())
        flow_steps = gen_flow_diagram.generate_flow_diagram(parsed_data.get(selected_ue, []), selected_ue)

    else:
        ue_ids = list(parsed_data.keys())

    return render_template('index.html', ue_ids=ue_ids, flow=flow_steps)


# 🔹 Search API
@app.route('/search_users')
def search_users():
    query = request.args.get('q', '').lower()

    results = [u for u in parsed_data.keys() if query in u.lower()]

    return jsonify(results[:10])


if __name__ == '__main__':
    app.run(debug=True)