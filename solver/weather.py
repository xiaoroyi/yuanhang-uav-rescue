"""W1 uniform manual operating scenario. No wind power/time or forecast inference."""

from math import inf
from solver.errors import InputNotReady

LIMITS = [
    ("max_wind_mps", "wind_speed_mps", "风速", "m/s", 1),
    ("max_gust_mps", "gust_mps", "阵风", "m/s", 1),
    ("min_temperature_c", "temperature_c", "最低温度", "°C", -1),
    ("max_temperature_c", "temperature_c", "最高温度", "°C", 1),
    ("max_precipitation_mm_h", "precipitation_mm_h", "降水强度", "mm/h", 1),
]


def window(scenario):
    weather = scenario.get("weather")
    return (
        (weather["valid_from_s"], weather["valid_until_s"]) if weather else (0.0, inf)
    )


def type_checks(scenario):
    """Unqualified types are excluded; a qualified alternative is still usable."""
    weather = scenario.get("weather")
    if not scenario.get("base"):
        return []
    active = {
        d["type_id"]
        for d in scenario["drones"]
        if d["status"] == "available" and d["location_id"] == scenario["base"]["id"]
    }
    if not weather:
        return [{"type_id": t, "allowed": True, "issues": []} for t in sorted(active)]
    rules = {r["type_id"]: r for r in weather["rules"]}
    result = []
    for typ in sorted(active):
        rule = rules.get(typ)
        issues = []
        if rule is None:
            issues.append("未提供该机型的气象作业规则")
        else:
            if not rule["source_ref"].strip():
                issues.append("缺少规则来源")
            if not any(rule[k] is not None for k, _, _, _, _ in LIMITS):
                issues.append("没有配置任何限值")
            for key, variable, label, unit, direction in LIMITS:
                limit = rule[key]
                if limit is None:
                    continue
                value = weather[variable]
                if value is None:
                    issues.append(f"缺少{label}输入，无法检查{limit}{unit}限值")
                elif (value - limit) * direction > 1e-9:
                    issues.append(f"{label}{value}{unit}超出所配置限值{limit}{unit}")
        result.append({"type_id": typ, "allowed": not issues, "issues": issues})
    return result


def eligible_types(scenario):
    return {r["type_id"] for r in type_checks(scenario) if r["allowed"]}


def qualify(scenario):
    if not scenario.get("weather"):
        return
    weather = scenario["weather"]
    if weather["valid_until_s"] <= weather["valid_from_s"]:
        raise InputNotReady("气象作业窗口为空。")
    if not eligible_types(scenario):
        details = "；".join(
            r["type_id"] + ":" + "、".join(r["issues"]) for r in type_checks(scenario)
        )
        raise InputNotReady(
            "当前人工气象情景下没有具备完整作业资格的可用机型。" + details
        )


def check_plan(scenario, plan):
    if not scenario.get("weather"):
        return ["请求气象检查，但快照未包含人工气象情景"]
    problems = []
    if scenario["policy"]["requires_communication"]:
        problems.append("人工气象与联合通信的组合尚未具备独立验证能力")
    checks = {r["type_id"]: r for r in type_checks(scenario)}
    drones = {d["drone_id"]: d for d in scenario["drones"]}
    start, end = window(scenario)
    for sortie in plan["sorties"]:
        typ = drones[sortie["drone_id"]]["type_id"]
        if typ not in checks or not checks[typ]["allowed"]:
            problems.append(f"{sortie['sortie_id']}使用未通过气象资格的机型{typ}")
        if sortie["takeoff_s"] < start - 1e-6 or sortie["return_s"] > end + 1e-6:
            problems.append(f"{sortie['sortie_id']}飞行超出人工气象有效窗口")
    return problems
