from jinja2 import Template
import os

def generate_html(coin_data, risk_score, chart_html):
    template_path = os.path.join(os.path.dirname(__file__), "template.html")
    with open(template_path, encoding="utf-8") as f:
        tmpl = Template(f.read())
    return tmpl.render(
        coin=coin_data['coin'],
        risk_score=risk_score,
        chart_html=chart_html
    )
