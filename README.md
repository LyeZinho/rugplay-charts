# rugplay-charts

Graficos, relatórios e predições para moedas do RugPlay.

[https://rugplay.com/](https://rugplay.com/)

## Propósito
Este projeto coleta, analisa e visualiza dados de moedas do RugPlay, permitindo gerar relatórios, gráficos, e treinar modelos de IA para prever movimentações de mercado.

## Estrutura
- `rugplay_ai_desktop/`
  - Scripts principais, coleta de dados, geração de relatórios, treinamento de IA.
- `dataset/`
  - Arquivos JSON com histórico diário de cada moeda.
- `output/`
  - Relatórios HTML gerados.

## Como usar
### 1. Coletar dados diariamente
Execute para cada símbolo desejado:
```powershell
python rugplay_ai_desktop/dataset_collector.py SYMBOL
```
Exemplo:
```powershell
python rugplay_ai_desktop/dataset_collector.py NVDA
```
Os dados serão salvos em `dataset/SYMBOL.json`.

### 2. Treinar modelos de IA
Após coletar dados:
```powershell
python rugplay_ai_desktop/train_predictor.py train
```
Para treinar mesmo com poucos dados:
```powershell
python rugplay_ai_desktop/train_predictor.py train --ignore-check
```

### 3. Fazer predições
Para prever o próximo preço de fechamento:
```powershell
python rugplay_ai_desktop/train_predictor.py predict SYMBOL
```

### 4. Gerar relatórios HTML
Execute:
```powershell
python rugplay_ai_desktop/main.py
```
Siga as instruções para informar o símbolo. O relatório será gerado em `output/report.html`.

### 5. Listar moedas e visualizar dicas
Execute:
```powershell
python rugplay_ai_desktop/ui/list_coins.py
```
A página será gerada em `output/coins_list.html`.

## Requisitos
- Python 3.11+
- Instalar dependências:
```powershell
pip install -r requirements.txt
```
- Adicione sua chave da API RugPlay no arquivo `.env`:
```
KEY=seu_token_aqui
```

## Objetivo
- Facilitar análise de risco, tendências e predições para moedas do RugPlay.
- Gerar datasets históricos para treinar modelos de IA.
- Visualizar dados de forma clara e moderna (tema escuro).

## Autor
LyeZinho

## Licença
MIT
