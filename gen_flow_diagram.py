import re


# ============================================================
# IMPORTANT F1AP SIGNALING MESSAGES
# ============================================================

F1AP_MESSAGES = [
    "UE_CONTEXT_SETUP_REQUEST",
    "UE_CONTEXT_SETUP_RESPONSE",

    "UE_CONTEXT_MODIFICATION_REQUEST",
    "UE_CONTEXT_MODIFICATION_RESPONSE",
    "UE_CONTEXT_MODIFICATION_CONFIRM",
    "UE_CONTEXT_MODIFICATION_REQUIRED",

    "UE_CONTEXT_RELEASE_REQUEST",
    "UE_CONTEXT_RELEASE_COMMAND",
    "UE_CONTEXT_RELEASE_COMPLETE",

    "DL_RRC_MESSAGE_TRANSFER",
    "UL_RRC_MESSAGE_TRANSFER",

    "INITIAL_UL_RRC_MESSAGE",
]


# ============================================================
# TRANSACTION EVENTS
# ============================================================

TRANSACTION_EVENTS = [
    "TRANS_CREATED",
    "TRANS_DONE",
]


# ============================================================
# CHECK SELECTED UE
# ============================================================

def line_belongs_to_ue(line, ue_id):

    ue_id = str(ue_id)

    pattern = (
        r"(?:UE_ID|RRM_UE_ID)"
        r"[:=]"
        + re.escape(ue_id)
        + r"(?:[:\s]|$)"
    )

    return re.search(pattern, line) is not None


# ============================================================
# GET TRANSACTION ID
# ============================================================

def get_transaction_id(line):

    match = re.search(
        r"TRANS_ID[:=]([A-Za-z0-9_-]+)",
        line
    )

    if match:
        return match.group(1)

    return None


# ============================================================
# GET DIRECTION
# ============================================================

def get_direction(line, message):

    # CU -> DU / F1AP
    if "CU:DU" in line:

        return "CU->>F1AP"

    # DU -> CU / F1AP
    if "DU:CU" in line:

        return "F1AP->>CU"

    # Default direction based on message type
    if (
        message.endswith("REQUEST")
        or message.endswith("COMMAND")
        or message.endswith("REQUIRED")
    ):

        return "CU->>F1AP"

    return "F1AP->>CU"


# ============================================================
# CREATE READABLE LABEL
# ============================================================

def create_label(line, message):

    trans_id = get_transaction_id(line)

    label = message

    if trans_id:

        label += " | TRANS_ID: " + trans_id

    return label


# ============================================================
# GENERATE FLOW
# ============================================================

def generate_flow_diagram(log_file_lines, UE_ID):

    flow = []

    # --------------------------------------------------------
    # Mermaid notes
    # --------------------------------------------------------

    flow.append(
        "Note right of CU: External node\n"
    )

    flow.append(
        "Note right of F1AP: F1AP signaling\n"
    )

    # --------------------------------------------------------
    # Prevent duplicate consecutive messages
    # --------------------------------------------------------

    last_message = None

    # --------------------------------------------------------
    # Process log
    # --------------------------------------------------------

    for line in log_file_lines:

        # Only selected UE
        if not line_belongs_to_ue(line, UE_ID):

            continue

        # ====================================================
        # TRANSACTION EVENTS
        # ====================================================

        transaction_found = False

        for event in TRANSACTION_EVENTS:

            if event in line:

                trans_id = get_transaction_id(line)

                # Do not display repeated transaction markers
                current_key = (
                    event,
                    trans_id
                )

                if current_key == last_message:

                    transaction_found = True
                    break

                if event == "TRANS_CREATED":

                    label = "[START] Transaction Created"

                else:

                    label = "[DONE] Transaction Completed"

                if trans_id:

                    label += " | TRANS_ID: " + trans_id

                flow.append(
                    "APP_UE->>APP_UE:" + label + "\n"
                )

                last_message = current_key

                transaction_found = True

                break

        if transaction_found:

            continue

        # ====================================================
        # F1AP SIGNALING
        # ====================================================

        message_found = False

        for message in F1AP_MESSAGES:

            if message not in line:

                continue

            trans_id = get_transaction_id(line)

            current_key = (
                message,
                trans_id
            )

            # Ignore exact consecutive duplicate
            if current_key == last_message:

                message_found = True
                break

            direction = get_direction(
                line,
                message
            )

            label = create_label(
                line,
                message
            )

            flow.append(
                direction
                + ":"
                + label
                + "\n"
            )

            last_message = current_key

            message_found = True

            break

        if message_found:

            continue

    return flow