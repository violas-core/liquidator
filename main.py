from violas_client import Client
from bank import Bank
import copy
from network import get_liquidator_account


client = Client("violas_testnet")
addr = "92401c8a5a6713c033fcc6b15bbb2aff"

# account = get_liquidator_account()
# client.bank_liquidate_borrow(account, addr, "vBTC", "vBTC", 634)
print(client.bank_get_total_collateral_value(addr) - client.bank_get_total_borrow_value(addr))
# print(client.bank_get_total_borrow_value(addr))


