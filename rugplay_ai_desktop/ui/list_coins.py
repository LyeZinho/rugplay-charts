import requests
import os
from dotenv import load_dotenv
import plotly.graph_objects as go
import plotly.io as pio
import numpy as np

def fetch_top_coins(api_key):
    url = "https://rugplay.com/api/v1/top"
    headers = {"Authorization": f"Bearer {api_key}"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()["coins"]

def generate_coins_html(coins):
    html = """
    <html>
    <head>
        <title>Lista de Moedas - RugPlay</title>
        <script src=\"https://cdn.plot.ly/plotly-latest.min.js\"></script>
        <style>
            body { font-family: Arial, sans-serif; background: #181a20; color: #eaeaea; }
            table { border-collapse: collapse; width: 100%; background: #23262f; color: #eaeaea; }
            th, td { border: 1px solid #333; padding: 8px; text-align: center; }
            th { background: #222; color: #fff; }
            img { width: 32px; height: 32px; }
            .card {
                background: #23262f;
                border-radius: 12px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.18);
                padding: 24px;
                margin: 24px auto;
                max-width: 900px;
                color: #eaeaea;
            }
            .card h3 { margin-top: 0; color: #fff; }
            .tips { color: #2ecc40; font-weight: bold; }
        </style>
    </head>
    <body>
        <h2 style='color:#fff;'>Lista de Moedas</h2>
        <div class=\"card\">
            <h3>Predições e Dicas de Investimento</h3>
    """
    html += predictions_card_html(coins)
    html += """
        </div>
        <div id=\"tree_map\" style=\"width:100%;max-width:900px;height:500px;margin:auto;\"></div>
        <div id=\"growth_charts\" style=\"width:100%;max-width:900px;margin:auto;\"></div>
        <table>
            <tr>
                <th>Ícone</th>
                <th>Nome</th>
                <th>Símbolo</th>
                <th>Preço</th>
                <th>Variação 24h</th>
                <th>Market Cap</th>
                <th>Volume 24h</th>
            </tr>
    """
    for coin in coins:
        html += f"""
            <tr>
                <td><img src='https://rugplay.com/{coin['icon']}' alt='{coin['symbol']}'></td>
                <td>{coin['name']}</td>
                <td>{coin['symbol']}</td>
                <td>${coin['price']:.2f}</td>
                <td>{coin['change24h']:.2f}</td>
                <td>${coin['marketCap']:.2f}</td>
                <td>${coin['volume24h']:.2f}</td>
            </tr>
        """
    html += """
        </table>
    """
    # Gerar o código do gráfico tree map
    tree_map_html = generate_tree_map_html(coins)
    html += tree_map_html
    # Gerar gráficos de crescimento
    growth_charts_html = generate_growth_charts_html(coins)
    html += growth_charts_html
    html += """
    </body>
    </html>
    """
    return html

def predictions_card_html(coins):
    # Top 3 moedas por crescimento 24h
    top_growth = sorted(coins, key=lambda c: c['change24h'], reverse=True)[:3]
    tips = []
    for coin in top_growth:
        if coin['change24h'] > 0:
            tips.append(f"<span class='tips'>Dica: {coin['name']} ({coin['symbol']}) está em alta (+{coin['change24h']:.2f}%)! </span>")
    # Predição simples: próximo preço estimado (usando variação 24h)
    preds = [coin['price'] * (1 + coin['change24h']/100) for coin in top_growth]
    preds_html = "<ul>"
    for coin, pred in zip(top_growth, preds):
        preds_html += f"<li>Próximo preço estimado de <b>{coin['name']}</b>: <b>${pred:.2f}</b></li>"
    preds_html += "</ul>"
    # Predição geral do mercado
    avg_pred = np.mean([coin['price'] * (1 + coin['change24h']/100) for coin in coins])
    card = f"{''.join(tips)}<br><br><b>Predições das top moedas:</b> {preds_html}<br><b>Predição geral do mercado:</b> ${avg_pred:.2f}"
    return card

def generate_growth_charts_html(coins):
    # Gráfico de linha dos preços das top 3 moedas
    top3 = sorted(coins, key=lambda c: c['marketCap'], reverse=True)[:3]
    fig_line = go.Figure()
    for coin in top3:
        # Simular histórico de preço (usando preço atual e variação 24h)
        price_yesterday = coin['price'] / (1 + coin['change24h']/100) if coin['change24h'] != -100 else 0
        fig_line.add_trace(go.Scatter(x=["Ontem", "Hoje"], y=[price_yesterday, coin['price']], mode="lines+markers", name=coin['name']))
    fig_line.update_layout(
        title="Crescimento das Top 3 Moedas (24h)",
        xaxis_title="Dia",
        yaxis_title="Preço",
        template='plotly_dark',
        paper_bgcolor='#181a20',
        plot_bgcolor='#23262f',
        font=dict(color='#eaeaea')
    )
    line_html = pio.to_html(fig_line, include_plotlyjs=False, full_html=False, div_id="growth_line_chart")

    # Gráfico de barras do crescimento percentual das top 5 moedas
    top5 = sorted(coins, key=lambda c: c['change24h'], reverse=True)[:5]
    fig_bar = go.Figure(go.Bar(
        x=[coin['name'] for coin in top5],
        y=[coin['change24h'] for coin in top5],
        marker_color="#2ecc40"
    ))
    fig_bar.update_layout(
        title="Top 5 Crescimentos Percentuais (24h)",
        xaxis_title="Moeda",
        yaxis_title="% Crescimento 24h",
        template='plotly_dark',
        paper_bgcolor='#181a20',
        plot_bgcolor='#23262f',
        font=dict(color='#eaeaea')
    )
    bar_html = pio.to_html(fig_bar, include_plotlyjs=False, full_html=False, div_id="growth_bar_chart")

    return f"<div>{line_html}</div><div>{bar_html}</div>"

def generate_tree_map_html(coins):
    labels = [coin['name'] for coin in coins]
    values = [coin['marketCap'] for coin in coins]
    customdata = [f"{coin['symbol']}<br>Market Cap: ${coin['marketCap']:.2f}" for coin in coins]
    fig = go.Figure(go.Treemap(
        labels=labels,
        parents=[""]*len(labels),
        values=values,
        customdata=customdata,
        hovertemplate="%{label}<br>%{customdata}<extra></extra>",
        marker=dict(colorscale="Blues")
    ))
    fig.update_layout(
        margin=dict(t=0, l=0, r=0, b=0),
        template='plotly_dark',
        paper_bgcolor='#181a20',
        font=dict(color='#eaeaea')
    )
    # Exportar apenas o div do gráfico
    tree_map_html = pio.to_html(fig, include_plotlyjs=False, full_html=False, div_id="tree_map")
    return tree_map_html

def main():
    load_dotenv()
    api_key = os.getenv("KEY")
    if not api_key:
        print("API KEY não encontrada. Verifique o arquivo .env e a variável KEY.")
        return
    coins = fetch_top_coins(api_key)
    html = generate_coins_html(coins)
    output_dir = "output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    output_path = os.path.join(output_dir, "coins_list.html")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Página gerada em {output_path}")

if __name__ == "__main__":
    main()
