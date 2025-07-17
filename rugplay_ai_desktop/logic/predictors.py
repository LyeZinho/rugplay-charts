import plotly.graph_objects as go

def generate_candlestick_chart(candles):
    fig = go.Figure(data=[go.Candlestick(
        x=[c['time'] for c in candles],
        open=[c['open'] for c in candles],
        high=[c['high'] for c in candles],
        low=[c['low'] for c in candles],
        close=[c['close'] for c in candles]
    )])
    fig.update_layout(title='Candle Chart', xaxis_title='Time', yaxis_title='Price')
    return fig
