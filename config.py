# Configurações de API para cada exchange
API_KEYS = {
    'okx': {'apiKey': '', 'secret': ''},
    'mercado': {'apiKey': '', 'secret': ''},
    'novadax': {'apiKey': '', 'secret': ''},
    'binance': {'apiKey': '', 'secret': ''},
    'kucoin': {'apiKey': '', 'secret': ''}
}

# Símbolo padrão para arbitragem
DEFAULT_SYMBOL = 'ETH/BRL'

# Intervalo de atualização (em milissegundos)
UPDATE_INTERVAL = 10000  # 10 segundos

# Exchanges usadas no programa
EXCHANGES = ['okx', 'mercado', 'novadax', 'binance', 'kucoin']

# Valor disponível para arbitragem (em reais, BRL)
ARBITRAGE_AMOUNT = 5000.0  # Valor em BRL para cálculo do lucro

# Taxas padrão (em formato decimal) caso a exchange não forneça
DEFAULT_FEES = {
    'maker': 0.0002,  # Taxa Maker: 0.02%
    'taker': 0.0003   # Taxa Taker: 0.03%
}
