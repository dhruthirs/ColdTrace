def calculate_trend(temperatures):
    if len(temperatures) < 3:
        return "INSUFFICIENT_DATA"

    recent = temperatures[-3:]

    if recent[0] < recent[1] < recent[2]:
        return "RISING"

    if recent[0] > recent[1] > recent[2]:
        return "FALLING"

    return "STABLE"


def calculate_rate(temperatures):
    if len(temperatures) < 2:
        return 0.0

    return round(
        temperatures[-1] - temperatures[-2],
        2
    )