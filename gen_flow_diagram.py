import os
import re
import string
cwd = os.getcwd()+"\\"

# print(cwd)
# print("Enter the du_log file name: ")
file_name = "du_26_02_09_08_21_48_part_2.log"
# print("Enter the UE ID to extracted: ")
UE_ID = 19863

# file_output = UE_ID + ".txt"
# UE_ID = "UE_ID:"+UE_ID

# UE_file = open(file_output, "w")
# DU_file = open(cwd+file_name, "r")

ue_flow = []

modules = ["SS_APP_UE", "CMN_TMR", "RLC_UL_UE", "DU_RRM_UE", "F1AP", "SCH_LVL1_CMN", "NRUP", "EGTP", "RLC_DL_UE", "SCH_LVL2_CMN","SS_MAC_UL_UE"]

f1ap_recv_messages = ["UE_CONTEXT_SETUP_REQ", "DL_RRC_MESSAGE_TRANSFER", "UE_CONTEXT_RELEASE_REQ", 
                      "UE_CONTEXT_RELEASE_COMMAND" ,"UE_CONTEXT_MODIFICATION_REQUEST", "UE_CONTEXT_MODIFICATION_CONFIRM"]
f1ap_send_messages = ["INITIAL_UL_", "UE_CONTEXT_SETUP_RES", "UL_RRC_MESSAGE_TRANSFER", "UE_CONTEXT_RELEASE_COMP", 
                      "UE_CONTEXT_MODIFICATION_RES", "UE_CONTEXT_MODIFICATION_REQUIRED"]

trans_messages = ["TRANS_CREATED", "TRANS_DONE"]


main_module = "SS_APP_UE"


def process_trans(message, line):
    words = re.split(r":", line)
    for word in words:
        trans_split = word.split("]")
        for trans_word in trans_split:
            if message in trans_word:
                note = "Note right of APP_UE: "+trans_word
                note = note + line[line.find(":TRANS_ID"):]+"\n"
                ue_flow.append(note)
                break

def process_modules(modules, line):
    if main_module in line:
        app_loc = line.find(main_module)
        evt_loc = line.find("EVT_")
        module_name_found = False
        for module_name in modules[1:]:
            if module_name in line:
                module_name_found = True
                module_loc = line.find(module_name)
                if app_loc < module_loc:
                    ue_flow.append("APP_UE"+"->>"+module_name+":"+line[evt_loc:]+"\n")
                else:
                    ue_flow.append(module_name+"->>APP_UE"+":"+line[evt_loc:]+"\n")
                break
        if line.count(main_module) > 1:
            ue_flow.append("APP_UE->>APP_UE:"+line[evt_loc:]+"\n")

def process_f1ap_recv_message(message, line):
    ue_flow.append("CU->>F1AP:"+line[line.find(message):]+"\n")

def process_f1ap_send_message(message, line):
    ue_flow.append("F1AP->>CU:"+line[line.find(message):]+"\n")


def generate_flow_diagram(log_file_lines, UE_ID):

    title = "title Call flow for "+UE_ID+"\n"
    # ue_flow.append("DU Log Parser")

    cu_note = "Note right of CU: External node\n"
    ue_flow.append(cu_note)

    f1ap_note = "Note right of F1AP: F1AP SCTP send/recv\n"
    ue_flow.append(f1ap_note)


    for line in log_file_lines:
        if UE_ID in line:
            for message in trans_messages:
                if message in line:
                    process_trans(message, line)
            for module_name in modules:
                if module_name in line:
                    process_modules(modules, line)
                    break
            for message in f1ap_recv_messages:
                if message in line:
                    process_f1ap_recv_message(message, line)
                    break
            for message in f1ap_send_messages:
                if message in line:
                    process_f1ap_send_message(message, line)
                    break
    print(ue_flow)
    return ue_flow


if __name__ == '__main__':
    
    DU_file = open(cwd+file_name, "r")
    temp_ue_flow = generate_flow_diagram(DU_file, UE_ID)
    DU_file.close()
    print(temp_ue_flow)