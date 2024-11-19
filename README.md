# ArbTrade - Crypto Arbitrage Bot

ArbTrade é um bot de arbitragem de criptomoedas que utiliza a biblioteca **ccxt** para acessar APIs de exchanges e **PyQt5** para uma interface gráfica intuitiva. O objetivo do bot é monitorar as diferenças de preços entre exchanges, calcular oportunidades de arbitragem e exibir os resultados, além de salvar um histórico em CSV.

---

## Funcionalidades
- Interface gráfica elegante e responsiva (GUI) construída com **PyQt5**.
- Conexão com múltiplas exchanges via **ccxt**.
- Exibição de preços (Bid/Ask), taxas e porcentagens de lucro em tempo real.
- Salva histórico de melhores oportunidades de arbitragem em um arquivo CSV.
- Configuração personalizável via arquivo `config.py`.

---

## Requisitos
- **Python 3.9+**
- Sistema operacional: Windows, Linux ou macOS

---

## Instalação

1. Clone este repositório ou baixe os arquivos compactados:
   ```bash
   git clone https://github.com/SEU_USUARIO/ArbTrade.git
   cd ArbTrade
