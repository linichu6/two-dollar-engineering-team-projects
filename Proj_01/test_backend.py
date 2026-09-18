import unittest

from backend import (
    AccountAlreadyExistsError,
    AccountNotCreatedError,
    InsufficientFundsError,
    InsufficientSharesError,
    InvalidAmountError,
    InvalidQuantityError,
    Holding,
    PortfolioSummary,
    TransactionType,
    TradingAccount,
    UnknownSymbolError,
    get_share_price,
)


class TestBackend(unittest.TestCase):
    def test_get_share_price_known_symbols(self) -> None:
        self.assertEqual(get_share_price("AAPL"), 150.0)
        self.assertEqual(get_share_price("TSLA"), 250.0)
        self.assertEqual(get_share_price("GOOGL"), 2800.0)

    def test_get_share_price_normalizes_symbol(self) -> None:
        self.assertEqual(get_share_price("aapl"), 150.0)
        self.assertEqual(get_share_price(" tsla "), 250.0)

    def test_get_share_price_unknown_symbol_raises(self) -> None:
        with self.assertRaises(UnknownSymbolError):
            get_share_price("MSFT")

    def test_create_account_sets_initial_state(self) -> None:
        account = TradingAccount()
        summary = account.create_account("ACC-1", "Jane Doe", 1000)
        self.assertEqual(summary.account_id, "ACC-1")
        self.assertEqual(summary.owner_name, "Jane Doe")
        self.assertAlmostEqual(summary.cash_balance, 1000)
        self.assertAlmostEqual(summary.total_deposited_cash, 1000)
        self.assertAlmostEqual(summary.total_portfolio_value, 1000)
        self.assertAlmostEqual(summary.profit_loss, 0)
        self.assertEqual(len(account.get_transactions()), 1)

    def test_create_account_twice_raises(self) -> None:
        account = TradingAccount()
        account.create_account("ACC-1", "Jane Doe", 0)
        with self.assertRaises(AccountAlreadyExistsError):
            account.create_account("ACC-2", "John Doe", 0)

    def test_create_account_negative_initial_deposit_raises(self) -> None:
        account = TradingAccount()
        with self.assertRaises(InvalidAmountError):
            account.create_account("ACC-1", "Jane Doe", -1)

    def test_deposit_increases_cash_and_total_deposited(self) -> None:
        account = TradingAccount()
        account.create_account("ACC-1", "Jane Doe", 100)
        summary = account.deposit(50)
        self.assertAlmostEqual(summary.cash_balance, 150)
        self.assertAlmostEqual(summary.total_deposited_cash, 150)
        self.assertEqual(len(account.get_transactions()), 2)

    def test_deposit_before_account_creation_raises(self) -> None:
        account = TradingAccount()
        with self.assertRaises(AccountNotCreatedError):
            account.deposit(10)

    def test_deposit_non_positive_amount_raises(self) -> None:
        account = TradingAccount()
        account.create_account("ACC-1", "Jane Doe", 0)
        with self.assertRaises(InvalidAmountError):
            account.deposit(0)
        with self.assertRaises(InvalidAmountError):
            account.deposit(-1)

    def test_withdraw_decreases_cash_and_total_deposited(self) -> None:
        account = TradingAccount()
        account.create_account("ACC-1", "Jane Doe", 100)
        summary = account.withdraw(40)
        self.assertAlmostEqual(summary.cash_balance, 60)
        self.assertAlmostEqual(summary.total_deposited_cash, 60)
        self.assertEqual(len(account.get_transactions()), 2)

    def test_withdraw_more_than_cash_raises(self) -> None:
        account = TradingAccount()
        account.create_account("ACC-1", "Jane Doe", 100)
        with self.assertRaises(InsufficientFundsError):
            account.withdraw(101)

    def test_withdraw_non_positive_amount_raises(self) -> None:
        account = TradingAccount()
        account.create_account("ACC-1", "Jane Doe", 100)
        with self.assertRaises(InvalidAmountError):
            account.withdraw(0)
        with self.assertRaises(InvalidAmountError):
            account.withdraw(-1)

    def test_buy_shares_updates_cash_and_holdings(self) -> None:
        account = TradingAccount()
        account.create_account("ACC-1", "Jane Doe", 1000)
        summary = account.buy("AAPL", 2)
        self.assertAlmostEqual(summary.cash_balance, 700)
        holdings = account.get_holdings()
        self.assertEqual(holdings, [Holding("AAPL", 2, 150.0, 300.0)])
        self.assertAlmostEqual(summary.holdings_value, 300)
        self.assertAlmostEqual(summary.total_portfolio_value, 1000)
        self.assertEqual(len(account.get_transactions()), 2)

    def test_buy_without_enough_cash_raises(self) -> None:
        account = TradingAccount()
        account.create_account("ACC-1", "Jane Doe", 100)
        with self.assertRaises(InsufficientFundsError):
            account.buy("AAPL", 1)

    def test_buy_invalid_quantity_raises(self) -> None:
        account = TradingAccount()
        account.create_account("ACC-1", "Jane Doe", 1000)
        with self.assertRaises(InvalidQuantityError):
            account.buy("AAPL", 0)
        with self.assertRaises(InvalidQuantityError):
            account.buy("AAPL", -1)
        with self.assertRaises(InvalidQuantityError):
            account.buy("AAPL", 1.5)  # type: ignore[arg-type]

    def test_buy_unknown_symbol_raises(self) -> None:
        account = TradingAccount()
        account.create_account("ACC-1", "Jane Doe", 1000)
        with self.assertRaises(UnknownSymbolError):
            account.buy("MSFT", 1)

    def test_sell_shares_updates_cash_and_holdings(self) -> None:
        account = TradingAccount()
        account.create_account("ACC-1", "Jane Doe", 1000)
        account.buy("AAPL", 3)
        summary = account.sell("AAPL", 1)
        self.assertAlmostEqual(summary.cash_balance, 700)
        self.assertEqual(account.get_holdings(), [Holding("AAPL", 2, 150.0, 300.0)])
        self.assertEqual(len(account.get_transactions()), 3)

    def test_selling_all_shares_removes_holding(self) -> None:
        account = TradingAccount()
        account.create_account("ACC-1", "Jane Doe", 1000)
        account.buy("AAPL", 1)
        account.sell("AAPL", 1)
        self.assertEqual(account.get_holdings(), [])

    def test_sell_more_than_owned_raises(self) -> None:
        account = TradingAccount()
        account.create_account("ACC-1", "Jane Doe", 1000)
        account.buy("AAPL", 1)
        with self.assertRaises(InsufficientSharesError):
            account.sell("AAPL", 2)

    def test_sell_invalid_quantity_raises(self) -> None:
        account = TradingAccount()
        account.create_account("ACC-1", "Jane Doe", 1000)
        with self.assertRaises(InvalidQuantityError):
            account.sell("AAPL", 0)
        with self.assertRaises(InvalidQuantityError):
            account.sell("AAPL", -1)
        with self.assertRaises(InvalidQuantityError):
            account.sell("AAPL", 1.2)  # type: ignore[arg-type]

    def test_portfolio_value_with_multiple_holdings(self) -> None:
        account = TradingAccount()
        account.create_account("ACC-1", "Jane Doe", 10000)
        account.buy("AAPL", 10)
        account.buy("TSLA", 2)
        summary = account.get_portfolio_summary()
        self.assertAlmostEqual(summary.cash_balance, 8000)
        self.assertAlmostEqual(summary.holdings_value, 2000)
        self.assertAlmostEqual(summary.total_portfolio_value, 10000)
        self.assertAlmostEqual(summary.profit_loss, 0)

    def test_profit_loss_after_withdrawal(self) -> None:
        account = TradingAccount()
        account.create_account("ACC-1", "Jane Doe", 1000)
        summary = account.withdraw(200)
        self.assertAlmostEqual(summary.cash_balance, 800)
        self.assertAlmostEqual(summary.total_deposited_cash, 800)
        self.assertAlmostEqual(summary.total_portfolio_value, 800)
        self.assertAlmostEqual(summary.profit_loss, 0)

    def test_transactions_are_chronological(self) -> None:
        account = TradingAccount()
        account.create_account("ACC-1", "Jane Doe", 1000)
        account.deposit(100)
        account.buy("AAPL", 1)
        account.sell("AAPL", 1)
        account.withdraw(50)
        types = [t.transaction_type for t in account.get_transactions()]
        self.assertEqual(
            types,
            [
                TransactionType.ACCOUNT_CREATED,
                TransactionType.DEPOSIT,
                TransactionType.BUY,
                TransactionType.SELL,
                TransactionType.WITHDRAWAL,
            ],
        )

    def test_transaction_ids_increment(self) -> None:
        account = TradingAccount()
        account.create_account("ACC-1", "Jane Doe", 1000)
        account.deposit(100)
        account.buy("AAPL", 1)
        ids = [t.transaction_id for t in account.get_transactions()]
        self.assertEqual(ids, [1, 2, 3])

    def test_get_transactions_returns_copy(self) -> None:
        account = TradingAccount()
        account.create_account("ACC-1", "Jane Doe", 1000)
        txns = account.get_transactions()
        txns.append(txns[0])
        self.assertEqual(len(account.get_transactions()), 1)


if __name__ == "__main__":
    unittest.main()
