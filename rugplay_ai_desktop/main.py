
from api.rugplay_client import get_coin_info, get_holders, get_market_top
from logic.rug_detector import calculate_rug_risk
from logic.predictors import generate_candlestick_chart
from logic.predict_ai import predict_next_close
from logic.alerts import big_holders_alert, big_buyers_alert
from ui.template import generate_html
import plotly.io as pio
import os, json

def save_candles_cache(symbol, candles):
    cache_dir = "data"
    cache_path = os.path.join(cache_dir, "candles_cache.json")
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)
    try:
        with open(cache_path, "r", encoding="utf-8") as f:
            cache = json.load(f)
    except Exception:
        cache = {}
    cache[symbol] = candles
    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2)

if __name__ == "__main__":
    import sys
    print("Digite o símbolo da moeda para gerar o relatório:")
    symbol = input("Symbol: ").strip().upper() if len(sys.argv) == 1 else sys.argv[1].upper()
    coin_data = get_coin_info(symbol)
    holders_data = get_holders(symbol)
    candles = coin_data['candlestickData']
    save_candles_cache(symbol, candles)
    risk_score = calculate_rug_risk(holders_data)
    import plotly.graph_objects as go
    import numpy as np
    # Gráfico de velas com linhas de tendência e predição
    x_vals = [c['time'] for c in candles]
    open_vals = [c['open'] for c in candles] if 'open' in candles[0] else [c['close'] for c in candles]
    high_vals = [c['high'] for c in candles] if 'high' in candles[0] else [c['close'] for c in candles]
    low_vals = [c['low'] for c in candles] if 'low' in candles[0] else [c['close'] for c in candles]
    close_vals = [c['close'] for c in candles]
    fig = go.Figure(data=[go.Candlestick(
        x=x_vals,
        open=open_vals,
        high=high_vals,
        low=low_vals,
        close=close_vals
    )])
    # Linha de tendência (regressão linear)
    times = np.arange(len(close_vals)).reshape(-1, 1)
    closes_np = np.array(close_vals).reshape(-1, 1)
    from sklearn.linear_model import LinearRegression
    model = LinearRegression()
    model.fit(times, closes_np)
    trend = model.predict(times).flatten()
    fig.add_trace(go.Scatter(x=x_vals, y=trend, mode='lines', name='Tendência', line=dict(color='blue', dash='dash')))
    # Linha de predição IA
    pred_steps = 1
    future_times = np.arange(len(close_vals), len(close_vals)+pred_steps).reshape(-1, 1)
    pred_vals = model.predict(future_times).flatten()
    fig.add_trace(go.Scatter(x=x_vals + [x_vals[-1]+1], y=list(trend) + [pred_vals[0]], mode='lines+markers', name='Predição IA', line=dict(color='orange', dash='dot')))
    fig.update_layout(
        title='Candle Chart com Tendência e Predição',
        xaxis_title='Time',
        yaxis_title='Price',
        template='plotly_dark',
        paper_bgcolor='#181a20',
        plot_bgcolor='#23262f',
        font=dict(color='#eaeaea')
    )
    chart_html = pio.to_html(fig, full_html=False)
    chart_html = pio.to_html(fig, full_html=False)

    # Gráfico de linha do volume de compras
    volume_data = coin_data.get('volumeData', [])
    if volume_data and len(volume_data) > 1:
        import plotly.graph_objects as go
        times = [v['time'] for v in volume_data]
        volumes = [v['volume'] for v in volume_data]
        fig_vol = go.Figure()
        fig_vol.add_trace(go.Scatter(x=times, y=volumes, mode='lines+markers', name='Volume de Compras'))
        fig_vol.update_layout(
            title='Volume de Compras ao Longo do Tempo',
            xaxis_title='Time',
            yaxis_title='Volume',
            template='plotly_dark',
            paper_bgcolor='#181a20',
            plot_bgcolor='#23262f',
            font=dict(color='#eaeaea')
        )
        volume_html = pio.to_html(fig_vol, full_html=False)
        # Adiciona o gráfico de volume abaixo do gráfico de candle
        chart_html += '<div style="margin-top:2em;">' + volume_html + '</div>'
    # Predição de IA (próximo preço de fechamento)
    pred = predict_next_close(candles, steps=1)[0]
    # Alertas
    holder_alerts = big_holders_alert(holders_data)
    buyer_alerts = big_buyers_alert(holders_data)

    # Classificação de risco colorida
    if risk_score > 70:
        risk_label = "Altíssima"
        risk_color = "red"
    elif risk_score > 30:
        risk_label = "Média"
        risk_color = "orange"
    else:
        risk_label = "Baixa"
        risk_color = "green"

    # Spread de holders
    top_holder_pct = holders_data['holders'][0]['percentage']
    spread = "Concentração muito alta" if top_holder_pct > 70 else ("Concentração média" if top_holder_pct > 30 else "Concentração saudável")

    # Crescimento/queda suspeitos
    closes = [c['close'] for c in candles]
    if len(closes) > 2:
        last_change = (closes[-1] - closes[-2]) / closes[-2] * 100 if closes[-2] != 0 else 0
    else:
        last_change = 0
    if last_change > 50:
        growth_alert = "Crescimento vertiginoso suspeito!"
    elif last_change < -30:
        growth_alert = "Queda abrupta detectada!"
    else:
        growth_alert = "Variação normal."

    # Card extra HTML
    extra_card = f"""
    <div style='background:#23262f;border-radius:12px;box-shadow:0 2px 8px rgba(0,0,0,0.18);padding:24px;margin:24px 0;color:#eaeaea;'>
        <h3>Risco de Rugpull: <span style='color:{risk_color};'>{risk_label} ({risk_score}%)</span></h3>
        <p>Spread de holders: <b>{spread}</b></p>
        <p>{growth_alert}</p>
        <p>Predição IA (próximo fechamento): <b>${pred:.6f}</b></p>
        <p>Alertas de big holders:</p>
        <ul>{''.join([f'<li>{a}</li>' for a in holder_alerts])}</ul>
        <p>Alertas de big buyers:</p>
        <ul>{''.join([f'<li>{a}</li>' for a in buyer_alerts])}</ul>
    </div>
    """

    # Tabela de holders
    holders_table = """
    <div style='margin:32px 0;'>
    <h3 style='color:#fff;'>Lista de Holders</h3>
    <table border='1' cellpadding='6' style='border-collapse:collapse;width:100%;background:#23262f;color:#eaeaea;'>
        <tr style='background:#222;color:#fff;'>
            <th>Rank</th><th>Nome</th><th>Quantidade</th><th>% do Supply</th><th>Valor de Liquidação</th>
        </tr>
    """
    for h in holders_data['holders']:
        holders_table += f"<tr><td>{h['rank']}</td><td>{h['name']}</td><td>{h['quantity']:.2f}</td><td>{h['percentage']:.2f}%</td><td>${h['liquidationValue']:.2f}</td></tr>"
    holders_table += "</table></div>"

    # Gráfico de pizza do share entre holders
    import plotly.graph_objects as go
    pie_labels = [h['name'] for h in holders_data['holders']]
    pie_values = [h['percentage'] for h in holders_data['holders']]
    fig_pie = go.Figure(go.Pie(labels=pie_labels, values=pie_values, hole=0.3))
    fig_pie.update_layout(
        title='Distribuição de Shares entre Holders',
        width=1000,
        height=500,
        template='plotly_dark',
        paper_bgcolor='#181a20',
        font=dict(color='#eaeaea')
    )
    pie_html = pio.to_html(fig_pie, full_html=False, div_id="holders_pie_chart")
    holders_table += f"<div id='holders_pie_chart' style='margin:32px auto;max-width:620px;'>{pie_html}</div>"

    # Gerar HTML final com card extra e tabela de holders
    html = generate_html(coin_data, risk_score, chart_html)
    # Inserir o card extra antes do gráfico
    html = html.replace('<div class="chart">', extra_card + '<div class="chart">')
    # Adicionar tabela e gráfico de pizza dos holders ao final
    html = html.replace('</body>', holders_table + '</body>')

    with open(os.path.join("output", "report.html"), "w", encoding="utf-8") as f:
        f.write(html)
    print("Relatório gerado em output/report.html")
    print(f"Predição IA (próximo fechamento): {pred:.6f}")
    print(f"Risco de rugpull: {risk_label} ({risk_score}%)")
    print(f"Spread de holders: {spread}")
    print(growth_alert)
    print("Alertas de big holders:")
    for a in holder_alerts:
        print("-", a)
    print("Alertas de big buyers:")
    for a in buyer_alerts:
        print("-", a)
