import time
import copy

from .util import new_mantissa, safe_sub, mantissa_mul, mantissa_div
from violas_client.banktypes.bytecode import CodeType
from violas_client.vlstypes.view import TransactionView
from violas_client.oracle_client.bytecodes import CodeType as OracleCodeType


class TokenInfo():
    def __init__(self, **kwargs):
        self.currency_code = kwargs.get("currency_code")
        self.total_supply = kwargs.get("total_supply")
        self.total_reserves = kwargs.get("total_reserves")
        self.total_borrows = kwargs.get("total_borrows")
        self.borrow_index = kwargs.get("borrow_index")

        self.oracle_price = 0
        self.price = kwargs.get("price")

        self.collateral_factor = kwargs.get("collateral_factor")
        self.base_rate = kwargs.get("base_rate")
        self.rate_multiplier = kwargs.get("rate_multiplier")
        self.rate_jump_multiplier = kwargs.get("rate_jump_multiplier")
        self.rate_kink = kwargs.get("rate_kink")
        self.last_minute = kwargs.get("last_minute")

        # resource struct T
        self.index = kwargs.get("index")
        self.contract_value = kwargs.get("contract_value")

        #更新
        self.exchange_rate = self.update_exchange_rate()

    @classmethod
    def empty(cls, **kwargs):
        return cls(currency_code=kwargs.get("currency_code"),
                   owner = kwargs.get("owner"),
                   total_supply=0,
                   total_reserves=0,
                   total_borrows=0,
                   borrow_index=new_mantissa(1, 1),
                   price=0,
                   collateral_factor=kwargs.get("collateral_factor"),
                   base_rate=kwargs.get("base_rate"),
                   rate_multiplier = kwargs.get("rate_multiplier"),
                   rate_jump_multiplier = kwargs.get("rate_jump_multiplier"),
                   rate_kink = kwargs.get("rate_kink"),
                   last_minute = kwargs.get("last_minute"),
                   data = kwargs.get("data"),
                   bulletin_first = "",
                   bulletins = "")

    def accrue_interest(self):
        borrow_rate = self.get_borrow_rate()
        minute = int(time.time() + 10) // 60
        cnt = safe_sub(minute, self.last_minute)
        if cnt == 0:
            return self
        borrow_rate = borrow_rate *cnt
        self.last_minute = minute
        interest_accumulated = mantissa_mul(self.total_borrows, borrow_rate)
        self.total_borrows = self.total_borrows + interest_accumulated
        reserve_factor = new_mantissa(1, 2)
        self.total_reserves = self.total_reserves +mantissa_mul(interest_accumulated, reserve_factor)
        self.interest_index = self.interest_index + mantissa_mul(self.interest_index, borrow_rate)

        self.exchange_rate = self.update_exchange_rate()
        return self

    def get_forecast(self, time_sec):
        ret = copy.deepcopy(self)
        borrow_rate = ret.get_borrow_rate()
        minute = time_sec // 60
        cnt = safe_sub(minute, ret.last_minute)
        if cnt == 0:
            return ret
        borrow_rate = borrow_rate * cnt
        ret.last_minute = minute
        interest_accumulated = mantissa_mul(ret.total_borrows, borrow_rate)
        ret.total_borrows = ret.total_borrows + interest_accumulated
        reserve_factor = new_mantissa(1, 2)
        ret.total_reserves = ret.total_reserves + mantissa_mul(interest_accumulated, reserve_factor)
        ret.interest_index = ret.interest_index + mantissa_mul(ret.interest_index, borrow_rate)
        return ret

    def get_borrow_rate(self):
        if self.total_borrows == 0:
            util = 0
        else:
            util = new_mantissa(self.total_borrows, self.total_borrows + safe_sub(self.contract_value, self.total_reserves))

        if util < self.rate_kink:
            return mantissa_mul(self.rate_multiplier, util) + self.base_rate
        normal_rate = mantissa_mul(self.rate_multiplier, self.rate_kink) + self.base_rate
        excess_util = util - self.rate_kink
        return mantissa_mul(self.rate_jump_multiplier, excess_util) + normal_rate

    def update_exchange_rate(self):
        if self.total_supply == 0:
            return new_mantissa(1, 100)
        return new_mantissa(self.contract_value + self.total_borrows - self.total_reserves, self.total_supply)

    def add_lock(self, tx):
        amount = tx.get_amount()
        self.contract_value += amount
        tokens = mantissa_div(amount, self.exchange_rate)
        self.total_supply += self.total_supply + tokens

    def add_borrow(self, tx):
        amount = tx.get_amount()
        self.total_borrows += amount
        self.contract_value -= amount

    def add_redeem(self, tx):
        amount = tx.get_amount()
        self.total_supply = safe_sub(self.total_supply, amount)
        self.contract_value -= amount

    def add_repay_borrow(self, tx):
        amount = tx.get_amount()
        self.total_borrows = safe_sub(self.total_borrows, amount)
        self.contract_value += amount

    def add_update_price_from_oracle(self):
        pass

    def add_update_exchange_rate(self, price):
        self.oracle_price = price

