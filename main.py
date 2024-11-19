import ccxt
import csv
from datetime import datetime
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QLabel, QWidget, QTableWidget, QTableWidgetItem
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QFont
import sys
import config  # Importa as configurações do arquivo config.py


class CryptoExchange:
    def __init__(self, exchange_id, api_key=None, secret=None):
        self.exchange = getattr(ccxt, exchange_id)({
            'apiKey': api_key,
            'secret': secret
        })

    def get_price(self, symbol):
        try:
            ticker = self.exchange.fetch_ticker(symbol)
            bid = ticker.get('bid', None)
            ask = ticker.get('ask', None)
            diff_24h = ticker.get('percentage', None)
            return bid, ask, diff_24h
        except Exception as e:
            print(f"Erro ao obter preços na exchange {self.exchange.id}: {e}")
            return None, None, None

    def get_fees(self):
        maker_fee = config.DEFAULT_FEES['maker']
        taker_fee = config.DEFAULT_FEES['taker']
        try:
            if hasattr(self.exchange, 'fees') and 'trading' in self.exchange.fees:
                maker_fee = self.exchange.fees['trading'].get(
                    'maker', maker_fee)
                taker_fee = self.exchange.fees['trading'].get(
                    'taker', taker_fee)
        except Exception as e:
            print(f"Erro ao obter taxas na exchange {self.exchange.id}: {e}")
        return maker_fee, taker_fee


class ArbitrageApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Crypto Arbitrage Bot")
        self.setGeometry(100, 100, 1200, 600)

        # Configuração das Exchanges com chaves de API do arquivo config
        self.exchanges = [
            CryptoExchange(
                exchange_id, config.API_KEYS[exchange_id]['apiKey'], config.API_KEYS[exchange_id]['secret']
            ) for exchange_id in config.EXCHANGES
        ]

        # Elementos da UI
        layout = QVBoxLayout()

        self.label = QLabel("Atualizando dados...")
        layout.addWidget(self.label)

        self.table = QTableWidget()
        self.table.setRowCount(len(self.exchanges))
        self.table.setColumnCount(10)
        self.table.setHorizontalHeaderLabels([
            "Nome Corretora", "Best Bid (R$)", "Best Ask (R$)", "Bid após Taxas (R$)", "Ask após Taxas (R$)",
            "Diferença (%) Compra-Venda", "Diferença 24h (%)", "Taxa Maker (%)", "Taxa Taker (%)", "Ação"
        ])

        layout.addWidget(self.table)

        # Label para exibir a melhor oportunidade de arbitragem
        self.best_opportunity_label = QLabel(
            "Melhor oportunidade de arbitragem: Aguardando dados..."
        )
        self.best_opportunity_label.setFont(QFont("Arial", 10, QFont.Bold))
        layout.addWidget(self.best_opportunity_label)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Aplicando o estilo escuro
        self.set_dark_mode()

        # Timer para atualizações automáticas
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_data)
        self.timer.start(config.UPDATE_INTERVAL)

        # Inicializa o arquivo CSV
        self.init_csv()

    def set_dark_mode(self):
        dark_stylesheet = """
        QMainWindow {
            background-color: #000000;
            color: #FFFFFF;
        }
        QLabel, QTableWidget {
            background-color: #000000;
            color: #FFFFFF;
        }
        QHeaderView::section {
            background-color: #333333;
            color: #FFFFFF;
        }
        QTableWidget::item {
            background-color: #000000;
            color: #FFFFFF;
        }
        """
        self.setStyleSheet(dark_stylesheet)

    def init_csv(self):
        # Cria o arquivo CSV com cabeçalhos se ainda não existir
        with open("arbitrage_history.csv", "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([
                "Data/Hora", "Exchange Compra", "Preço Compra (Sem Taxa)", "Preço Compra (Com Taxa)",
                "Exchange Venda", "Preço Venda (Sem Taxa)", "Preço Venda (Com Taxa)", "Quantidade (ETH)",
                "Total Investido (R$)", "Total Recebido (R$)", "Lucro Líquido (R$)", "Lucro (%)"
            ])

    def update_data(self):
        symbol = config.DEFAULT_SYMBOL
        arbitrage_amount = config.ARBITRAGE_AMOUNT

        best_ask_exchange = None
        best_bid_exchange = None
        best_ask_price_after_fees = None
        best_bid_price_after_fees = None
        best_ask_maker_fee = None
        best_bid_taker_fee = None
        lowest_ask = float('inf')
        highest_bid = float('-inf')

        for row, ex in enumerate(self.exchanges):
            bid, ask, diff_24h = ex.get_price(symbol)
            maker_fee, taker_fee = ex.get_fees()

            bid_after_fee = bid * (1 - taker_fee) if bid else None
            ask_after_fee = ask * (1 + maker_fee) if ask else None

            if ask and ask < lowest_ask:
                lowest_ask = ask
                best_ask_exchange = ex.exchange.id
                best_ask_price_after_fees = ask_after_fee
                best_ask_maker_fee = maker_fee

            if bid and bid > highest_bid:
                highest_bid = bid
                best_bid_exchange = ex.exchange.id
                best_bid_price_after_fees = bid_after_fee
                best_bid_taker_fee = taker_fee

            # Atualizando a tabela
            self.table.setItem(row, 0, QTableWidgetItem(ex.exchange.id))
            self.table.setItem(row, 1, QTableWidgetItem(
                f"R$ {bid:,.2f}" if bid else "N/A"))
            self.table.setItem(row, 2, QTableWidgetItem(
                f"R$ {ask:,.2f}" if ask else "N/A"))
            self.table.setItem(row, 3, QTableWidgetItem(
                f"R$ {bid_after_fee:,.2f}" if bid_after_fee else "N/A"))
            self.table.setItem(row, 4, QTableWidgetItem(
                f"R$ {ask_after_fee:,.2f}" if ask_after_fee else "N/A"))
            self.table.setItem(row, 5, QTableWidgetItem(
                f"{((bid - ask) / ask) * 100:.2f}%" if bid and ask else "N/A"))
            self.table.setItem(row, 6, QTableWidgetItem(
                f"{diff_24h:.2f}%" if diff_24h else "N/A"))
            self.table.setItem(row, 7, QTableWidgetItem(
                f"{maker_fee * 100:.2f}%"))
            self.table.setItem(row, 8, QTableWidgetItem(
                f"{taker_fee * 100:.2f}%"))
            self.table.setItem(row, 9, QTableWidgetItem("Neutro"))

        if best_ask_exchange and best_bid_exchange:
            eth_amount = arbitrage_amount / best_ask_price_after_fees
            total_invested = eth_amount * best_ask_price_after_fees
            total_received = eth_amount * best_bid_price_after_fees
            profit = total_received - total_invested
            profit_percent = (profit / total_invested) * 100

            self.best_opportunity_label.setText(
                f"Melhor oportunidade da rodada:\n"
                f"Comprar na {best_ask_exchange}: {eth_amount:.4f} ETH a R$ {
                    best_ask_price_after_fees:,.2f} "
                f"(Maker: {best_ask_maker_fee * 100:.2f}%)\n"
                f"Vender na {best_bid_exchange}: {eth_amount:.4f} ETH a R$ {
                    best_bid_price_after_fees:,.2f} "
                f"(Taker: {best_bid_taker_fee * 100:.2f}%)\n"
                f"Investimento: R$ {arbitrage_amount:,.2f}\n"
                f"Lucro Líquido: R$ {profit:,.2f} ({profit_percent:.2f}%)"
            )

            # Salva a melhor oportunidade no CSV
            self.save_to_csv(
                best_ask_exchange, best_bid_exchange, lowest_ask, best_ask_price_after_fees,
                highest_bid, best_bid_price_after_fees, eth_amount, total_invested, total_received,
                profit, profit_percent
            )

    def save_to_csv(self, buy_exchange, sell_exchange, buy_price_no_fee, buy_price_with_fee, sell_price_no_fee,
                    sell_price_with_fee, eth_amount, total_invested, total_received, profit, profit_percent):
        with open("arbitrage_history.csv", "a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                buy_exchange, f"{buy_price_no_fee:.2f}", f"{
                    buy_price_with_fee:.2f}",
                sell_exchange, f"{sell_price_no_fee:.2f}", f"{
                    sell_price_with_fee:.2f}",
                f"{eth_amount:.4f}", f"{
                    total_invested:.2f}", f"{total_received:.2f}",
                f"{profit:.2f}", f"{profit_percent:.2f}"
            ])


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ArbitrageApp()
    window.show()
    sys.exit(app.exec_())
