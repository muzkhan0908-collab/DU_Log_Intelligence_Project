from flask import Flask, request, render_template, jsonify
from collections import defaultdict
import re
import gen_flow_diagram
import log_analyzer

app = Flask(__name__)
analysis_data = {}

# ==========================================
# GLOBAL STORAGE
# ==========================================
parsed_data = defaultdict(lambda: defaultdict(list))

cur_ue = 0
analysis_data = {}

# ==========================================
# COMPILED REGEX (FASTER)
# ==========================================
UE_PATTERN = re.compile(r'UE_ID[:=]([0-9]+)')
TRANS_PATTERN = re.compile(r'TRANS_ID[:=]([A-Za-z0-9_-]+)')
CLEAN_PATTERN = re.compile(r'[^a-zA-Z0-9 _:\-]')

# ==========================================
# HOME PAGE
# ==========================================
@app.route('/', methods=['GET', 'POST'])
def home():
    global parsed_data
    global cur_ue
    global analysis_data

    flow_steps = []

    ue_ids = []
    trans_ids = []

    # ======================================
    # FILE UPLOAD
    # ======================================
    if request.method == 'POST' and 'logfile' in request.files:

        file = request.files['logfile']
        all_log_lines = []

        # CLEAR OLD DATA
        parsed_data.clear()

        # ======================================
        # READ FILE LINE BY LINE (IMPORTANT)
        # ======================================
        for raw_line in file.stream:

            try:
                line = raw_line.decode('utf-8').strip()

            except UnicodeDecodeError:
                continue

            if not line:
                continue
            all_log_lines.append(line)

            # ======================================
            # REGEX SEARCH
            # ======================================
            ue_match = UE_PATTERN.search(line)

            if not ue_match:
                continue

            trans_match = TRANS_PATTERN.search(line)

            ue_id = ue_match.group(1)

            trans_id = (
                trans_match.group(1)
                if trans_match else "UNKNOWN"
            )

            # ======================================
            # CLEAN LINE
            # ======================================
            clean_line = CLEAN_PATTERN.sub('', line)

            # ======================================
            # STORE DATA
            # ======================================
            parsed_data[ue_id][trans_id].append(clean_line)

        # ======================================
        # GET IDS
        # ======================================
        ue_ids = sorted(parsed_data.keys())

        trans_set = set()

        for ue in parsed_data.values():
            trans_set.update(ue.keys())

        trans_ids = sorted(trans_set)
        analysis_data = log_analyzer.analyze_logs(all_log_lines)
        if ue_ids:
         cur_ue = ue_ids[0]

    logs = []

    for trans_logs in parsed_data[cur_ue].values():
        logs.extend(trans_logs)

    if logs:
            flow_steps = gen_flow_diagram.generate_flow_diagram(
                logs,
                cur_ue
            )

            # Flow Intelligence
            analysis_data["flow_steps"] = len(flow_steps)

            analysis_data["modules_involved"] = len(
                set(
                    re.findall(
                        r'APP_UE|RLC_UL_UE|RLC_DL_UE|F1AP|CU|DU_RRM_UE|SS_APP_UE|CMN_TMR|SCH_LVL1_CMN|NRUP|EGTP',
                        "\n".join(flow_steps)
                    )
                )
            )

    # ======================================
    # SEARCH/FILTER
    # ======================================
    elif request.method == 'GET':

        selected_ue = request.args.get('ue_id')

        selected_trans = request.args.get('trans_id')

        ue_ids = sorted(parsed_data.keys())

        trans_set = set()

        for ue in parsed_data.values():
            trans_set.update(ue.keys())

        trans_ids = sorted(trans_set)

        logs = []

        # ======================================
        # FILTER USING UE_ID
        # ======================================
        if selected_ue and selected_ue in parsed_data:
            cur_ue = selected_ue
            for trans_logs in parsed_data[selected_ue].values():
                logs.extend(trans_logs)

        # ======================================
        # FILTER USING TRANS_ID
        # ======================================
        elif selected_trans:

            for trans_logs in parsed_data[cur_ue][selected_trans]:
                logs.append(trans_logs)


        # ======================================
        # GENERATE FLOW
        # ======================================
        if logs:

           flow_steps = gen_flow_diagram.generate_flow_diagram(
            logs,
            cur_ue
        )

    return render_template(
        'index.html',
        ue_ids=ue_ids,
        trans_ids=trans_ids,
        flow=flow_steps,
        analysis=analysis_data
    )

# ======================================
# SEARCH UE
# ======================================
@app.route('/search_users')
def search_users():

    query = request.args.get('q', '').lower()

    results = [
        ue for ue in parsed_data.keys()
        if query in ue.lower()
    ]

    return jsonify(results[:20])

# ======================================
# SEARCH TRANS
# ======================================
@app.route('/search_trans')
def search_trans():

    query = request.args.get('q', '').lower()

    all_trans = set()

    for ue in parsed_data.values():
        all_trans.update(ue.keys())

    results = [
        trans for trans in all_trans
        if query in trans.lower()
    ]

    return jsonify(results[:20])

# ======================================
# RUN APP
# ======================================
if __name__ == '__main__':

    app.run(
        debug=True,
        threaded=True
    )