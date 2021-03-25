def temperature_process(valid_temperature: str) -> float:
    valid_temperature = valid_temperature.replace("℃", "")
    return float(valid_temperature)


def aqi_process(valid_aqi: str) -> float:
    if not valid_aqi:
        return 0.0
    else:
        return float(valid_aqi)
