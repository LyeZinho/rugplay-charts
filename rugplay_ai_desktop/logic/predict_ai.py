from sklearn.linear_model import LinearRegression
import numpy as np

def predict_next_close(candles, steps=1):
    # candles: lista de dicts com 'close' e 'time'
    closes = np.array([c['close'] for c in candles]).reshape(-1, 1)
    times = np.arange(len(closes)).reshape(-1, 1)
    model = LinearRegression()
    model.fit(times, closes)
    future_times = np.arange(len(closes), len(closes)+steps).reshape(-1, 1)
    preds = model.predict(future_times)
    return preds.flatten().tolist()
