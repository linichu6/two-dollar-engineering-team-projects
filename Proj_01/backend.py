from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any


class TradingSimulationError(Exception):
    pass


class AccountAlreadyExistsError(TradingSimulationError):
    pass


class AccountNotCreatedError(TradingSimulationError):
    pass


class InvalidAmountError(TradingSimulationError):
    pass


class InvalidQuantityError(TradingSimulationError):
    pass


class InsufficientFundsError(TradingSimulationError):
    pass


class InsufficientSharesError(TradingSimulationError):
    pass


class UnknownSymbolError(TradingSimulationError):
    pass


class TransactionType(str, Enum):
    ACCOUNT_CREATED = "ACCOUNT_CREATED"
    DEPOSIT = "DEPOSIT"
    WITHDRAWAL = "WITHDRAWAL"
    BUY = "BUY"
    SELL = "SELL"


@dataclass
class Transaction:
    transaction_id: int
    transaction_type: TransactionType
    timestamp: datetime
    symbol: str | None
    quantity: int | None
    price_per_share: float | None
    cash_amount: float
    cash_balance_after: float
    notes: str


@dataclass
class Holding:
    symbol: str
    quantity: int
    current_price: float
    market_value: float


@dataclass
class PortfolioSummary:
    account_id: str
    owner_name: str
    cash_balance: float
    total_deposited_cash: float
    holdings_value: float
    total_portfolio_value: float
    profit_loss: float


_SUPPORTED_PRICES = {"AAPL": 150.0, "TSLA": 250.0, "GOOGL": 2800.0}


def get_supported_symbols() -> list[str]:
    return ["AAPL", "TSLA", "GOOGL"]


def get_share_price(symbol: str) -> float:
    normalized = symbol.strip().upper()
    if not normalized:
        raise UnknownSymbolError("Symbol cannot be empty.")
    try:
        return _SUPPORTED_PRICES[normalized]
    except KeyError as exc:
        raise UnknownSymbolError(f"Unsupported symbol: {symbol}") from exc


class TradingAccount:
    def __init__(self) -> None:
        self._account_created = False
        self._account_id: str | None = None
        self._owner_name: str | None = None
        self._cash_balance = 0.0
        self._total_deposited_cash = 0.0
        self._holdings: dict[str, int] = {}
        self._transactions: list[Transaction] = []
        self._next_transaction_id = 1

    def _ensure_account_created(self) -> None:
        if not self._account_created:
            raise AccountNotCreatedError("Account has not been created yet.")

    def _normalize_symbol(self, symbol: str) -> str:
        normalized = symbol.strip().upper()
        if not normalized:
            raise UnknownSymbolError("Symbol cannot be empty.")
        if normalized not in _SUPPORTED_PRICES:
            raise UnknownSymbolError(f"Unsupported symbol: {symbol}")
        return normalized

    def _validate_positive_amount(self, amount: float) -> None:
        if not isinstance(amount, (int, float)) or isinstance(amount, bool):
            raise InvalidAmountError("Amount must be numeric.")
        if amount <= 0:
            raise InvalidAmountError("Amount must be greater than 0.")

    def _validate_non_negative_amount(self, amount: float) -> None:
        if not isinstance(amount, (int, float)) or isinstance(amount, bool):
            raise InvalidAmountError("Amount must be numeric.")
        if amount < 0:
            raise InvalidAmountError("Amount must be greater than or equal to 0.")

    def _validate_positive_quantity(self, quantity: int) -> None:
        if not isinstance(quantity, int) or isinstance(quantity, bool):
            raise InvalidQuantityError("Quantity must be an integer.")
        if quantity <= 0:
            raise InvalidQuantityError("Quantity must be greater than 0.")

    def _record_transaction(
        self,
        transaction_type: TransactionType,
        symbol: str | None,
        quantity: int | None,
        price_per_share: float | None,
        cash_amount: float,
        notes: str,
    ) -> Transaction:
        transaction = Transaction(
            transaction_id=self._next_transaction_id,
            transaction_type=transaction_type,
            timestamp=datetime.now(),
            symbol=symbol,
            quantity=quantity,
            price_per_share=price_per_share,
            cash_amount=cash_amount,
            cash_balance_after=self._cash_balance,
            notes=notes,
        )
        self._transactions.append(transaction)
        self._next_transaction_id += 1
        return transaction

    def _calculate_holdings_value(self) -> float:
        total = 0.0
        for symbol, quantity in self._holdings.items():
            total += quantity * get_share_price(symbol)
        return total

    def create_account(self, account_id: str, owner_name: str, initial_deposit: float) -> PortfolioSummary:
        if self._account_created:
            raise AccountAlreadyExistsError("Account already exists.")
        if not isinstance(account_id, str) or not account_id.strip():
            raise InvalidAmountError("Account ID must be a non-empty string.")
        if not isinstance(owner_name, str) or not owner_name.strip():
            raise InvalidAmountError("Owner name must be a non-empty string.")
        self._validate_non_negative_amount(initial_deposit)
        self._account_created = True
        self._account_id = account_id.strip()
        self._owner_name = owner_name.strip()
        self._cash_balance = float(initial_deposit)
        self._total_deposited_cash = float(initial_deposit)
        self._record_transaction(
            TransactionType.ACCOUNT_CREATED,
            None,
            None,
            None,
            float(initial_deposit),
            f"Account created with initial deposit {initial_deposit}.",
        )
        return self.get_portfolio_summary()

    def deposit(self, amount: float) -> PortfolioSummary:
        self._ensure_account_created()
        self._validate_positive_amount(amount)
        self._cash_balance += float(amount)
        self._total_deposited_cash += float(amount)
        self._record_transaction(TransactionType.DEPOSIT, None, None, None, float(amount), f"Deposited {amount}.")
        return self.get_portfolio_summary()

    def withdraw(self, amount: float) -> PortfolioSummary:
        self._ensure_account_created()
        self._validate_positive_amount(amount)
        if float(amount) > self._cash_balance:
            raise InsufficientFundsError("Insufficient cash balance.")
        self._cash_balance -= float(amount)
        self._total_deposited_cash -= float(amount)
        self._record_transaction(TransactionType.WITHDRAWAL, None, None, None, float(amount), f"Withdrew {amount}.")
        return self.get_portfolio_summary()

    def buy(self, symbol: str, quantity: int) -> PortfolioSummary:
        self._ensure_account_created()
        normalized = self._normalize_symbol(symbol)
        self._validate_positive_quantity(quantity)
        price = get_share_price(normalized)
        total_cost = price * quantity
        if total_cost > self._cash_balance:
            raise InsufficientFundsError("Insufficient cash to buy shares.")
        self._cash_balance -= total_cost
        self._holdings[normalized] = self._holdings.get(normalized, 0) + quantity
        self._record_transaction(
            TransactionType.BUY,
            normalized,
            quantity,
            price,
            total_cost,
            f"Bought {quantity} shares of {normalized} at {price}.",
        )
        return self.get_portfolio_summary()

    def sell(self, symbol: str, quantity: int) -> PortfolioSummary:
        self._ensure_account_created()
        normalized = self._normalize_symbol(symbol)
        self._validate_positive_quantity(quantity)
        owned = self._holdings.get(normalized, 0)
        if quantity > owned:
            raise InsufficientSharesError("Insufficient shares to sell.")
        price = get_share_price(normalized)
        proceeds = price * quantity
        self._cash_balance += proceeds
        remaining = owned - quantity
        if remaining:
            self._holdings[normalized] = remaining
        else:
            self._holdings.pop(normalized, None)
        self._record_transaction(
            TransactionType.SELL,
            normalized,
            quantity,
            price,
            proceeds,
            f"Sold {quantity} shares of {normalized} at {price}.",
        )
        return self.get_portfolio_summary()

    def get_holdings(self) -> list[Holding]:
        self._ensure_account_created()
        holdings: list[Holding] = []
        for symbol in sorted(self._holdings):
            price = get_share_price(symbol)
            quantity = self._holdings[symbol]
            holdings.append(Holding(symbol, quantity, price, quantity * price))
        return holdings

    def get_portfolio_summary(self) -> PortfolioSummary:
        self._ensure_account_created()
        holdings_value = self._calculate_holdings_value()
        total_portfolio_value = self._cash_balance + holdings_value
        profit_loss = total_portfolio_value - self._total_deposited_cash
        return PortfolioSummary(
            account_id=self._account_id or "",
            owner_name=self._owner_name or "",
            cash_balance=self._cash_balance,
            total_deposited_cash=self._total_deposited_cash,
            holdings_value=holdings_value,
            total_portfolio_value=total_portfolio_value,
            profit_loss=profit_loss,
        )

    def get_profit_loss(self) -> float:
        return self.get_portfolio_summary().profit_loss

    def get_transactions(self) -> list[Transaction]:
        self._ensure_account_created()
        return list(self._transactions)


def holdings_to_rows(holdings: list[Holding]) -> list[list[str | int | float]]:
    return [[h.symbol, h.quantity, h.current_price, h.market_value] for h in holdings]


def transactions_to_rows(transactions: list[Transaction]) -> list[list[str | int | float | None]]:
    return [
        [
            t.transaction_id,
            t.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            t.transaction_type.value,
            t.symbol,
            t.quantity,
            t.price_per_share,
            t.cash_amount,
            t.cash_balance_after,
            t.notes,
        ]
        for t in transactions
    ]


def portfolio_summary_to_dict(summary: PortfolioSummary) -> dict[str, float | str]:
    return {
        "account_id": summary.account_id,
        "owner_name": summary.owner_name,
        "cash_balance": summary.cash_balance,
        "total_deposited_cash": summary.total_deposited_cash,
        "holdings_value": summary.holdings_value,
        "total_portfolio_value": summary.total_portfolio_value,
        "profit_loss": summary.profit_loss,
    }
