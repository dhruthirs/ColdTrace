def detect_anomaly(temperatures):
    if len(temperatures) < 2:
        return False

    # Temperature rising too quickly
    rate = temperatures[-1] - temperatures[-2]

    if rate >= 0.4:
        return True

    return False


def detect_cooling_failure(temperatures, cooling):
    if not cooling or len(temperatures) < 3:
        return False

    recent = temperatures[-3:]

    # Cooling is ON but temperature keeps rising
    if recent[0] < recent[1] < recent[2]:
        return True

    return False