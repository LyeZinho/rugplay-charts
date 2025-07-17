def big_holders_alert(holders_data, threshold=10):
    alerts = []
    for h in holders_data['holders']:
        if h['percentage'] > threshold:
            alerts.append(f"Holder {h['name']} detém {h['percentage']:.2f}% do supply!")
    return alerts

def big_buyers_alert(holders_data, min_liquidation=100000):
    alerts = []
    for h in holders_data['holders']:
        if h['liquidationValue'] > min_liquidation:
            alerts.append(f"Comprador {h['name']} com liquidez de {h['liquidationValue']:.2f}!")
    return alerts
