def calculate_rug_risk(holders_data):
    top_holder = holders_data['holders'][0]
    pct = top_holder['percentage']
    volume = holders_data['poolInfo']['baseCurrencyAmount']
    risk = 0
    if pct > 90:
        risk += 50
    elif pct > 70:
        risk += 30
    if volume < 10000:
        risk += 30
    if len(holders_data['holders']) < 5:
        risk += 20
    return min(100, risk)
