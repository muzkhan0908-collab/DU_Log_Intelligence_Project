import re


def analyze_logs(log_lines):
    """
    Analyze DU log lines and calculate basic
    statistics, errors, warnings and timeouts.
    """

    total_lines = len(log_lines)

    ue_ids = set()
    trans_ids = set()

    errors = []
    warnings = []
    timeouts = []

    for line in log_lines:

        # Find UE ID
        ue_match = re.search(r'UE_ID[:=]\s*([0-9]+)', line)

        if ue_match:
            ue_ids.add(ue_match.group(1))

        # Find Transaction ID
        trans_match = re.search(
            r'TRANS_ID[:=]\s*([A-Za-z0-9_-]+)',
            line
        )

        if trans_match:
            trans_ids.add(trans_match.group(1))

        # Convert line to uppercase
        upper_line = line.upper()

        # Detect errors
        if (
            "ERROR" in upper_line
            or "FAILED" in upper_line
            or "FAIL" in upper_line
        ):
            errors.append(line.strip())

        # Detect warnings
        if (
            "WARNING" in upper_line
            or "WARN" in upper_line
        ):
            warnings.append(line.strip())

        # Detect timeouts
        if (
            "TIMEOUT" in upper_line
            or "TIMED OUT" in upper_line
        ):
            timeouts.append(line.strip())

    # Calculate health score
    health_score = 100

    health_score -= len(errors) * 3
    health_score -= len(warnings)
    health_score -= len(timeouts) * 2

    # Keep score between 0 and 100
    health_score = max(0, min(100, health_score))

    # Determine health status
    if health_score >= 80:
        health_status = "HEALTHY"
    elif health_score >= 50:
        health_status = "WARNING"
    else:
        health_status = "CRITICAL"

    return {
        "total_lines": total_lines,

        "total_ues": len(ue_ids),

        "total_transactions": len(trans_ids),

        "error_count": len(errors),
        "errors": errors,

        "warning_count": len(warnings),
        "warnings": warnings,

        "timeout_count": len(timeouts),
        "timeouts": timeouts,

        "health_score": health_score,
        "health_status": health_status
    }
if __name__ == "__main__":
    test_logs = [
        "UE_ID:1234 TRANS_ID:abc-001 SUCCESS",
        "UE_ID:1234 TRANS_ID:abc-001 WARNING connection slow",
        "UE_ID:5678 TRANS_ID:def-002 ERROR connection failed",
        "UE_ID:5678 TRANS_ID:def-002 TIMEOUT"
    ]

    result = analyze_logs(test_logs)

    print("Total UEs:", result["total_ues"])
    print("Total Transactions:", result["total_transactions"])
    print("Errors:", result["error_count"])
    print("Warnings:", result["warning_count"])
    print("Timeouts:", result["timeout_count"])
    print("Health Score:", result["health_score"])
    print("Health Status:", result["health_status"])