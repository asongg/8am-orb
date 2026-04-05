from abc import ABC, abstractmethod

class Broker(ABC):
    @abstractmethod
    def submit_order(self, symbol, side, qty, order_type="market", limit_price=None):
        pass

    @abstractmethod
    def cancel_order(self, broker_order_id):
        pass

    @abstractmethod
    def list_open_orders(self):
        pass

    @abstractmethod
    def get_positions(self):
        pass