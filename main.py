from queue import Queue
from violas_client import Client
from violas_client.banktypes.bytecode import CodeType
from cache.api import liquidator_api
from consumer.liquidate_borrow import LiquidateBorrowThread
from conf.config import URL, faucet_file


q = Queue()
liquidate = LiquidateBorrowThread(q, URL, faucet_file)
liquidate.liquidate_borrow("ad9d787d68d431d76fc690ec80450213")

client = Client()
addrs = [client.BANK_OWNER_ADDRESS,
         "00000000000000000000000042414E4B",
         "008E290B2104836059B2470B3D7B5A27",
         "54C9B693169248731486981145613FB2",
         "5AC1D3147D23ACAE204DA849C96C3C17",
         "6A192880DAF96E435DEBAC2B5102233D",
         "A083AB80E3580E8842B8AD073BF39AB9",
         "CC4E152E78A9DE212190A8174EA298F3",
         "DC0BC76555E66D13C2AAE803CC3E4CFE",
         "EA242CBD47842BD9D3C420C94D87A9D2",
         "000000000000000000000000000000dd"
         ]
txs = []
for addr in addrs:
    seq = client.get_sequence_number(addr)
    for i in range(seq):
        tx = client.get_account_transaction(addr, i)
        txs.append(tx)
txs.sort(key = lambda tx: tx.get_version())
liquidator_api.set_oracle_price("USD", 4294967296)
liquidator_api.set_oracle_price("EUR", 4998978423)
for tx in txs:
    if tx.get_code_type() == CodeType.LIQUIDATE_BORROW:
        print(tx.get_version())
    liquidator_api.add_tx(tx)
# print(liquidator_api.to_json())
