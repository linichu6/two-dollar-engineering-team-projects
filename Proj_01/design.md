# Design: Trading Simulation Account Management System

## 1. Overview

Build a simple single-user trading simulation platform with:

- Account creation
- Deposits and withdrawals
- Buy and sell share transactions
- Portfolio holdings reporting
- Portfolio value calculation
- Profit/loss reporting
- Transaction history listing
- Validation to prevent:
  - Negative cash balance
  - Buying shares without enough cash
  - Selling shares not owned

The implementation will be split into:

| Engineer | Responsibility |
|---|---|
| `backend_engineer` | Core account, portfolio, transaction, pricing, and validation logic |
| `frontend_engineer` | Gradio UI app |
| `test_engineer` | Unit tests for backend behavior |

All files must live in the same directory. No packages/subdirectories.

---

## 2. File Structure

All files are in the project root:

```text
backend.py
app.py
test_backend.py
README.md
```

### File Ownership

| File | Owner | Purpose |
|---|---|---|
| `backend.py` | `backend_engineer` | Core trading/account system |
| `app.py` | `frontend_engineer` | Gradio app using backend |
| `test_backend.py` | `test_engineer` | Unit tests for backend |
| `README.md` | Shared | Optional usage notes |

---

## 3. Backend Design

### File: `backend.py`

The backend should contain all business logic and should not depend on Gradio.

Use only Python standard library.

Recommended standard library imports:

```text
dataclasses
datetime
enum
typing
copy
```

Do not use third-party packages.

---

## 4. Domain Concepts

### Account

Represents a trading account.

Tracks:

- Account ID
- Owner name
- Cash balance
- Total deposited cash
- Holdings by symbol
- Transaction history

### Holding

Represents the quantity of a specific stock symbol owned by the user.

### Transaction

Represents an action taken by the user, such as:

- Account creation
- Deposit
- Withdrawal
- Buy
- Sell

### Portfolio Value

Calculated as:

```text
cash_balance + sum(quantity_owned * current_share_price)
```

### Profit/Loss

Calculated as:

```text
portfolio_value - total_deposited_cash
```

Important: `total_deposited_cash` should be updated as follows:

| Action | Effect on `total_deposited_cash` |
|---|---|
| Deposit | Increase |
| Withdrawal | Decrease |
| Buy | No change |
| Sell | No change |

This makes profit/loss represent gain or loss compared to net contributed capital.

---

## 5. Backend Classes and Functions

### 5.1 `TransactionType`

Use an enum for transaction types.

```python
class TransactionType(str, Enum):
    ACCOUNT_CREATED = "ACCOUNT_CREATED"
    DEPOSIT = "DEPOSIT"
    WITHDRAWAL = "WITHDRAWAL"
    BUY = "BUY"
    SELL = "SELL"
```

---

### 5.2 `Transaction`

Dataclass representing a transaction.

```python
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
```

#### Field Meaning

| Field | Description |
|---|---|
| `transaction_id` | Sequential transaction ID |
| `transaction_type` | Type of transaction |
| `timestamp` | When transaction occurred |
| `symbol` | Stock symbol for buy/sell, otherwise `None` |
| `quantity` | Share quantity for buy/sell, otherwise `None` |
| `price_per_share` | Share price for buy/sell, otherwise `None` |
| `cash_amount` | Cash amount moved or trade value |
| `cash_balance_after` | Cash balance after transaction |
| `notes` | Human-readable description |

---

### 5.3 `Holding`

Dataclass representing owned shares.

```python
@dataclass
class Holding:
    symbol: str
    quantity: int
    current_price: float
    market_value: float
```

---

### 5.4 `PortfolioSummary`

Dataclass representing account-level portfolio information.

```python
@dataclass
class PortfolioSummary:
    account_id: str
    owner_name: str
    cash_balance: float
    total_deposited_cash: float
    holdings_value: float
    total_portfolio_value: float
    profit_loss: float
```

---

### 5.5 Exceptions

Define clear custom exceptions for validation failures.

```python
class TradingSimulationError(Exception):
    pass
```

```python
class AccountAlreadyExistsError(TradingSimulationError):
    pass
```

```python
class AccountNotCreatedError(TradingSimulationError):
    pass
```

```python
class InvalidAmountError(TradingSimulationError):
    pass
```

```python
class InvalidQuantityError(TradingSimulationError):
    pass
```

```python
class InsufficientFundsError(TradingSimulationError):
    pass
```

```python
class InsufficientSharesError(TradingSimulationError):
    pass
```

```python
class UnknownSymbolError(TradingSimulationError):
    pass
```

---

## 6. Share Price Function

The system has access to a function:

```python
def get_share_price(symbol: str) -> float:
    ...
```

For this implementation, include the required test implementation with fixed prices:

| Symbol | Price |
|---|---:|
| `AAPL` | `150.00` |
| `TSLA` | `250.00` |
| `GOOGL` | `2800.00` |

### Required Signature

```python
def get_share_price(symbol: str) -> float:
    ...
```

### Behavior

- Normalize `symbol` using uppercase and stripping whitespace.
- Return fixed prices for `AAPL`, `TSLA`, and `GOOGL`.
- Raise `UnknownSymbolError` for unsupported symbols.

---

## 7. Main Backend Class

### 7.1 `TradingAccount`

This class owns the account state and performs all operations.

```python
class TradingAccount:
    def __init__(self) -> None:
        ...
```

The account starts uncreated. The user must call `create_account(...)` first.

---

### 7.2 Account State Fields

The class should maintain the following internal fields:

```python
_account_created: bool
_account_id: str | None
_owner_name: str | None
_cash_balance: float
_total_deposited_cash: float
_holdings: dict[str, int]
_transactions: list[Transaction]
_next_transaction_id: int
```

---

### 7.3 Public Methods

#### Create Account

```python
def create_account(self, account_id: str, owner_name: str, initial_deposit: float) -> PortfolioSummary:
    ...
```

Behavior:

- Can only be called once.
- `account_id` must not be empty.
- `owner_name` must not be empty.
- `initial_deposit` must be greater than or equal to `0`.
- Sets cash balance to `initial_deposit`.
- Sets total deposited cash to `initial_deposit`.
- Records an `ACCOUNT_CREATED` transaction.
- If `initial_deposit > 0`, the account creation transaction may include that initial cash amount.
- Returns a `PortfolioSummary`.

Raises:

```python
AccountAlreadyExistsError
InvalidAmountError
```

---

#### Deposit Funds

```python
def deposit(self, amount: float) -> PortfolioSummary:
    ...
```

Behavior:

- Account must exist.
- `amount` must be greater than `0`.
- Increase cash balance by `amount`.
- Increase total deposited cash by `amount`.
- Record a `DEPOSIT` transaction.
- Return updated `PortfolioSummary`.

Raises:

```python
AccountNotCreatedError
InvalidAmountError
```

---

#### Withdraw Funds

```python
def withdraw(self, amount: float) -> PortfolioSummary:
    ...
```

Behavior:

- Account must exist.
- `amount` must be greater than `0`.
- Cash balance after withdrawal must not be negative.
- Decrease cash balance by `amount`.
- Decrease total deposited cash by `amount`.
- Record a `WITHDRAWAL` transaction.
- Return updated `PortfolioSummary`.

Raises:

```python
AccountNotCreatedError
InvalidAmountError
InsufficientFundsError
```

---

#### Buy Shares

```python
def buy(self, symbol: str, quantity: int) -> PortfolioSummary:
    ...
```

Behavior:

- Account must exist.
- Normalize `symbol`.
- `quantity` must be a positive integer.
- Get current price using `get_share_price(symbol)`.
- Calculate total cost:

```text
total_cost = price * quantity
```

- Reject if `total_cost > cash_balance`.
- Decrease cash balance by `total_cost`.
- Increase holding quantity for symbol.
- Record a `BUY` transaction.
- Return updated `PortfolioSummary`.

Raises:

```python
AccountNotCreatedError
InvalidQuantityError
InsufficientFundsError
UnknownSymbolError
```

---

#### Sell Shares

```python
def sell(self, symbol: str, quantity: int) -> PortfolioSummary:
    ...
```

Behavior:

- Account must exist.
- Normalize `symbol`.
- `quantity` must be a positive integer.
- User must own at least `quantity` shares.
- Get current price using `get_share_price(symbol)`.
- Calculate proceeds:

```text
proceeds = price * quantity
```

- Increase cash balance by `proceeds`.
- Decrease holding quantity.
- Remove the symbol from holdings if quantity becomes `0`.
- Record a `SELL` transaction.
- Return updated `PortfolioSummary`.

Raises:

```python
AccountNotCreatedError
InvalidQuantityError
InsufficientSharesError
UnknownSymbolError
```

---

#### Get Holdings

```python
def get_holdings(self) -> list[Holding]:
    ...
```

Behavior:

- Account must exist.
- Return holdings sorted alphabetically by symbol.
- Each holding should include:
  - Symbol
  - Quantity
  - Current price
  - Market value

Raises:

```python
AccountNotCreatedError
UnknownSymbolError
```

---

#### Get Portfolio Summary

```python
def get_portfolio_summary(self) -> PortfolioSummary:
    ...
```

Behavior:

- Account must exist.
- Calculate:
  - Cash balance
  - Total deposited cash
  - Holdings value
  - Total portfolio value
  - Profit/loss
- Return `PortfolioSummary`.

Raises:

```python
AccountNotCreatedError
UnknownSymbolError
```

---

#### Get Profit/Loss

```python
def get_profit_loss(self) -> float:
    ...
```

Behavior:

- Account must exist.
- Return:

```text
get_portfolio_summary().profit_loss
```

Raises:

```python
AccountNotCreatedError
UnknownSymbolError
```

---

#### Get Transactions

```python
def get_transactions(self) -> list[Transaction]:
    ...
```

Behavior:

- Account must exist.
- Return transaction history in chronological order.
- Return a defensive copy so callers cannot mutate internal state.

Raises:

```python
AccountNotCreatedError
```

---

#### Get Supported Symbols

```python
def get_supported_symbols() -> list[str]:
    ...
```

Behavior:

- Return:

```text
["AAPL", "TSLA", "GOOGL"]
```

This can be a module-level function rather than a class method.

---

## 8. Backend Helper Methods

Inside `TradingAccount`, use private helper methods.

### Ensure Account Exists

```python
def _ensure_account_created(self) -> None:
    ...
```

Raises `AccountNotCreatedError` if account has not been created.

---

### Normalize Symbol

```python
def _normalize_symbol(self, symbol: str) -> str:
    ...
```

Behavior:

- Strip whitespace.
- Convert to uppercase.
- Reject empty symbols.

May raise:

```python
UnknownSymbolError
```

---

### Validate Positive Amount

```python
def _validate_positive_amount(self, amount: float) -> None:
    ...
```

Behavior:

- Ensure amount is numeric.
- Ensure amount is greater than `0`.

Raises:

```python
InvalidAmountError
```

---

### Validate Non-Negative Amount

```python
def _validate_non_negative_amount(self, amount: float) -> None:
    ...
```

Behavior:

- Used for initial deposit.
- Ensure amount is numeric.
- Ensure amount is greater than or equal to `0`.

Raises:

```python
InvalidAmountError
```

---

### Validate Positive Quantity

```python
def _validate_positive_quantity(self, quantity: int) -> None:
    ...
```

Behavior:

- Quantity must be an integer.
- Quantity must be greater than `0`.

Raises:

```python
InvalidQuantityError
```

---

### Record Transaction

```python
def _record_transaction(
    self,
    transaction_type: TransactionType,
    symbol: str | None,
    quantity: int | None,
    price_per_share: float | None,
    cash_amount: float,
    notes: str,
) -> Transaction:
    ...
```

Behavior:

- Create a `Transaction`.
- Assign the next transaction ID.
- Use current timestamp.
- Store cash balance after the transaction.
- Append to `_transactions`.
- Increment `_next_transaction_id`.
- Return the created transaction.

---

### Calculate Holdings Value

```python
def _calculate_holdings_value(self) -> float:
    ...
```

Behavior:

- For each symbol in `_holdings`, call `get_share_price(symbol)`.
- Sum `quantity * price`.

---

## 9. Data Formatting Helpers for Frontend

The backend can expose lightweight helper functions that return primitive structures useful for the UI.

These should still live in `backend.py`.

### Holdings as Rows

```python
def holdings_to_rows(holdings: list[Holding]) -> list[list[str | int | float]]:
    ...
```

Return rows in this order:

```text
Symbol, Quantity, Current Price, Market Value
```

---

### Transactions as Rows

```python
def transactions_to_rows(transactions: list[Transaction]) -> list[list[str | int | float | None]]:
    ...
```

Return rows in this order:

```text
ID, Timestamp, Type, Symbol, Quantity, Price, Cash Amount, Cash Balance After, Notes
```

Timestamp should be formatted as a readable string.

---

### Portfolio Summary as Dict

```python
def portfolio_summary_to_dict(summary: PortfolioSummary) -> dict[str, float | str]:
    ...
```

Return keys:

```text
account_id
owner_name
cash_balance
total_deposited_cash
holdings_value
total_portfolio_value
profit_loss
```

---

## 10. Frontend Design

### File: `app.py`

Owner: `frontend_engineer`

Build a Gradio app using `gradio`.

The app should:

- Create one in-memory `TradingAccount` instance.
- Allow the user to:
  - Create account
  - Deposit funds
  - Withdraw funds
  - Buy shares
  - Sell shares
  - Refresh portfolio view
- Display:
  - Portfolio summary
  - Holdings table
  - Transaction history table
  - User-facing status/error messages

This is a simple single-session app. No persistence is required.

---

## 11. Gradio 6 API Guidance

Use modern Gradio Blocks style.

### Imports

```python
import gradio as gr
from backend import TradingAccount, holdings_to_rows, transactions_to_rows
```

---

### App Construction

Use:

```python
with gr.Blocks(title="Trading Simulation Account Manager") as demo:
    ...
```

Then launch with:

```python
if __name__ == "__main__":
    demo.launch()
```

---

### Important Gradio 6 Notes

The frontend engineer should follow these conventions:

1. Use `gr.Blocks`, not the older `gr.Interface`, because this app has multiple workflows.
2. Prefer `gr.Textbox`, `gr.Number`, `gr.Dropdown`, `gr.Button`, `gr.Markdown`, and `gr.Dataframe`.
3. Use event handlers with `.click(...)`.
4. In Gradio 6, event handlers should be registered with:
   ```python
   button.click(
       fn=handler_function,
       inputs=[...],
       outputs=[...],
   )
   ```
5. Do not use deprecated positional-only assumptions from older Gradio examples.
6. Use `value=...` instead of older dynamic default patterns.
7. Use `interactive=True` for user-editable components.
8. Use `interactive=False` for output-only fields.
9. For `gr.Dataframe`, use `headers=[...]`, `datatype=[...]`, `value=[...]`, and `interactive=False`.
10. Avoid relying on deprecated `Dataframe.update(...)` patterns. Event handlers should return the full new value for the dataframe output.
11. Avoid using deprecated `gr.update(...)` unless necessary. Returning direct primitive/component values is preferred.
12. Use `gr.State` only if the account object must be session-specific. For a simple single-process app, either module-level state or `gr.State` is acceptable. Prefer `gr.State` if possible.

---

## 12. Frontend State Model

Recommended approach:

```python
account_state = gr.State(TradingAccount())
```

Each event handler should accept the current account object as its first or last input and return it as one of the outputs if using `gr.State`.

Example handler signature shape:

```python
def handle_deposit(account: TradingAccount, amount: float) -> tuple[TradingAccount, str, str, list[list], list[list]]:
    ...
```

The returned tuple should include:

1. Updated account state
2. Status message
3. Portfolio summary markdown
4. Holdings table rows
5. Transaction table rows

---

## 13. Frontend Components

### Account Creation Inputs

```python
account_id_input = gr.Textbox(
    label="Account ID",
    placeholder="Example: ACC-001",
    interactive=True,
)
```

```python
owner_name_input = gr.Textbox(
    label="Owner Name",
    placeholder="Example: Jane Doe",
    interactive=True,
)
```

```python
initial_deposit_input = gr.Number(
    label="Initial Deposit",
    value=10000,
    minimum=0,
    interactive=True,
)
```

```python
create_account_button = gr.Button("Create Account", variant="primary")
```

---

### Cash Operation Inputs

```python
cash_amount_input = gr.Number(
    label="Cash Amount",
    value=1000,
    minimum=0,
    interactive=True,
)
```

```python
deposit_button = gr.Button("Deposit")
withdraw_button = gr.Button("Withdraw")
```

---

### Trade Inputs

```python
symbol_input = gr.Dropdown(
    choices=["AAPL", "TSLA", "GOOGL"],
    value="AAPL",
    label="Symbol",
    interactive=True,
)
```

```python
quantity_input = gr.Number(
    label="Quantity",
    value=1,
    minimum=1,
    precision=0,
    interactive=True,
)
```

```python
buy_button = gr.Button("Buy")
sell_button = gr.Button("Sell")
```

---

### Refresh Button

```python
refresh_button = gr.Button("Refresh Portfolio")
```

---

### Status Output

```python
status_output = gr.Markdown()
```

---

### Portfolio Summary Output

Use Markdown for a clear summary.

```python
summary_output = gr.Markdown()
```

Display format should include:

```text
Account ID
Owner Name
Cash Balance
Total Deposited Cash
Holdings Value
Total Portfolio Value
Profit/Loss
```

---

### Holdings Output

```python
holdings_table = gr.Dataframe(
    headers=["Symbol", "Quantity", "Current Price", "Market Value"],
    datatype=["str", "number", "number", "number"],
    value=[],
    interactive=False,
)
```

---

### Transactions Output

```python
transactions_table = gr.Dataframe(
    headers=[
        "ID",
        "Timestamp",
        "Type",
        "Symbol",
        "Quantity",
        "Price",
        "Cash Amount",
        "Cash Balance After",
        "Notes",
    ],
    datatype=[
        "number",
        "str",
        "str",
        "str",
        "number",
        "number",
        "number",
        "number",
        "str",
    ],
    value=[],
    interactive=False,
)
```

---

## 14. Frontend Handler Functions

All handlers should catch backend exceptions and return a user-friendly status message instead of crashing.

### Format Summary Markdown

```python
def format_summary_markdown(account: TradingAccount) -> str:
    ...
```

Behavior:

- If account does not exist, return a message like:
  ```text
  No account created yet.
  ```
- Otherwise return a Markdown summary.

---

### Build Full View State

```python
def build_view(account: TradingAccount) -> tuple[str, list[list], list[list]]:
    ...
```

Returns:

```text
summary_markdown, holdings_rows, transaction_rows
```

Behavior:

- If account does not exist, return empty/default values.
- Otherwise:
  - Get portfolio summary
  - Get holdings
  - Get transactions
  - Convert holdings and transactions to table rows.

---

### Handle Create Account

```python
def handle_create_account(
    account: TradingAccount,
    account_id: str,
    owner_name: str,
    initial_deposit: float,
) -> tuple[TradingAccount, str, str, list[list], list[list]]:
    ...
```

Outputs:

```text
updated account
status markdown
summary markdown
holdings rows
transaction rows
```

Behavior:

- Call `account.create_account(...)`.
- On success, return success status.
- On failure, return error status and current view.

---

### Handle Deposit

```python
def handle_deposit(
    account: TradingAccount,
    amount: float,
) -> tuple[TradingAccount, str, str, list[list], list[list]]:
    ...
```

Behavior:

- Call `account.deposit(amount)`.
- Return updated view.

---

### Handle Withdraw

```python
def handle_withdraw(
    account: TradingAccount,
    amount: float,
) -> tuple[TradingAccount, str, str, list[list], list[list]]:
    ...
```

Behavior:

- Call `account.withdraw(amount)`.
- Return updated view.

---

### Handle Buy

```python
def handle_buy(
    account: TradingAccount,
    symbol: str,
    quantity: int | float,
) -> tuple[TradingAccount, str, str, list[list], list[list]]:
    ...
```

Behavior:

- Convert Gradio `Number` value to `int`.
- Call `account.buy(symbol, quantity)`.
- Return updated view.

---

### Handle Sell

```python
def handle_sell(
    account: TradingAccount,
    symbol: str,
    quantity: int | float,
) -> tuple[TradingAccount, str, str, list[list], list[list]]:
    ...
```

Behavior:

- Convert Gradio `Number` value to `int`.
- Call `account.sell(symbol, quantity)`.
- Return updated view.

---

### Handle Refresh

```python
def handle_refresh(
    account: TradingAccount,
) -> tuple[TradingAccount, str, str, list[list], list[list]]:
    ...
```

Behavior:

- Return unchanged account.
- Return refreshed summary, holdings, and transactions.

---

## 15. Frontend Event Wiring

Each button should wire to the corresponding handler.

### Create Account Button

```python
create_account_button.click(
    fn=handle_create_account,
    inputs=[
        account_state,
        account_id_input,
        owner_name_input,
        initial_deposit_input,
    ],
    outputs=[
        account_state,
        status_output,
        summary_output,
        holdings_table,
        transactions_table,
    ],
)
```

---

### Deposit Button

```python
deposit_button.click(
    fn=handle_deposit,
    inputs=[
        account_state,
        cash_amount_input,
    ],
    outputs=[
        account_state,
        status_output,
        summary_output,
        holdings_table,
        transactions_table,
    ],
)
```

---

### Withdraw Button

```python
withdraw_button.click(
    fn=handle_withdraw,
    inputs=[
        account_state,
        cash_amount_input,
    ],
    outputs=[
        account_state,
        status_output,
        summary_output,
        holdings_table,
        transactions_table,
    ],
)
```

---

### Buy Button

```python
buy_button.click(
    fn=handle_buy,
    inputs=[
        account_state,
        symbol_input,
        quantity_input,
    ],
    outputs=[
        account_state,
        status_output,
        summary_output,
        holdings_table,
        transactions_table,
    ],
)
```

---

### Sell Button

```python
sell_button.click(
    fn=handle_sell,
    inputs=[
        account_state,
        symbol_input,
        quantity_input,
    ],
    outputs=[
        account_state,
        status_output,
        summary_output,
        holdings_table,
        transactions_table,
    ],
)
```

---

### Refresh Button

```python
refresh_button.click(
    fn=handle_refresh,
    inputs=[
        account_state,
    ],
    outputs=[
        account_state,
        status_output,
        summary_output,
        holdings_table,
        transactions_table,
    ],
)
```

---

## 16. Suggested UI Layout

Use `gr.Markdown` headings and `gr.Row` / `gr.Column`.

Recommended layout:

```text
# Trading Simulation Account Manager

[Status Message]

Account Setup
- Account ID
- Owner Name
- Initial Deposit
- Create Account Button

Cash Operations
- Cash Amount
- Deposit Button
- Withdraw Button

Trading Operations
- Symbol Dropdown
- Quantity Number
- Buy Button
- Sell Button

Portfolio Summary

Holdings Table

Transaction History Table
```

The exact layout is flexible as long as all functionality is available.

---

## 17. Testing Design

### File: `test_backend.py`

Owner: `test_engineer`

Use Python standard library `unittest`.

Do not use `pytest`.

Tests should import from `backend.py`.

---

## 18. Required Unit Test Coverage

### 18.1 Share Price Tests

#### Test Known Symbols

```python
def test_get_share_price_known_symbols(self) -> None:
    ...
```

Verify:

```text
AAPL -> 150.00
TSLA -> 250.00
GOOGL -> 2800.00
```

#### Test Symbol Normalization

```python
def test_get_share_price_normalizes_symbol(self) -> None:
    ...
```

Verify:

```text
"aapl" -> 150.00
" tsla " -> 250.00
```

#### Test Unknown Symbol

```python
def test_get_share_price_unknown_symbol_raises(self) -> None:
    ...
```

Verify `UnknownSymbolError`.

---

### 18.2 Account Creation Tests

#### Test Create Account

```python
def test_create_account_sets_initial_state(self) -> None:
    ...
```

Verify:

- Account ID
- Owner name
- Cash balance
- Total deposited cash
- Portfolio value
- Profit/loss initially `0`
- One transaction exists

#### Test Cannot Create Account Twice

```python
def test_create_account_twice_raises(self) -> None:
    ...
```

Verify `AccountAlreadyExistsError`.

#### Test Negative Initial Deposit Rejected

```python
def test_create_account_negative_initial_deposit_raises(self) -> None:
    ...
```

Verify `InvalidAmountError`.

---

### 18.3 Deposit Tests

#### Test Deposit Increases Cash

```python
def test_deposit_increases_cash_and_total_deposited(self) -> None:
    ...
```

Verify:

- Cash balance increases.
- Total deposited cash increases.
- Transaction recorded.

#### Test Deposit Before Account Creation Fails

```python
def test_deposit_before_account_creation_raises(self) -> None:
    ...
```

Verify `AccountNotCreatedError`.

#### Test Deposit Non-Positive Amount Fails

```python
def test_deposit_non_positive_amount_raises(self) -> None:
    ...
```

Verify zero and negative amounts.

---

### 18.4 Withdrawal Tests

#### Test Withdraw Decreases Cash

```python
def test_withdraw_decreases_cash_and_total_deposited(self) -> None:
    ...
```

Verify:

- Cash balance decreases.
- Total deposited cash decreases.
- Transaction recorded.

#### Test Cannot Withdraw More Than Cash

```python
def test_withdraw_more_than_cash_raises(self) -> None:
    ...
```

Verify `InsufficientFundsError`.

#### Test Withdraw Non-Positive Amount Fails

```python
def test_withdraw_non_positive_amount_raises(self) -> None:
    ...
```

Verify `InvalidAmountError`.

---

### 18.5 Buy Tests

#### Test Buy Shares

```python
def test_buy_shares_updates_cash_and_holdings(self) -> None:
    ...
```

Example:

- Create account with `1000`.
- Buy `2` AAPL at `150`.
- Cash should become `700`.
- Holdings should show `2` AAPL.
- Holdings market value should be `300`.
- Portfolio value should remain `1000` if prices are unchanged.
- Transaction recorded.

#### Test Cannot Buy Without Enough Cash

```python
def test_buy_without_enough_cash_raises(self) -> None:
    ...
```

Example:

- Create account with `100`.
- Try to buy `1` AAPL.
- Verify `InsufficientFundsError`.

#### Test Buy Invalid Quantity Fails

```python
def test_buy_invalid_quantity_raises(self) -> None:
    ...
```

Verify:

- Quantity `0`
- Negative quantity
- Non-integer quantity

#### Test Buy Unknown Symbol Fails

```python
def test_buy_unknown_symbol_raises(self) -> None:
    ...
```

Verify `UnknownSymbolError`.

---

### 18.6 Sell Tests

#### Test Sell Shares

```python
def test_sell_shares_updates_cash_and_holdings(self) -> None:
    ...
```

Example:

- Create account with `1000`.
- Buy `3` AAPL.
- Sell `1` AAPL.
- Cash should be:
  ```text
  1000 - 450 + 150 = 700
  ```
- Holdings should show `2` AAPL.
- Transaction recorded.

#### Test Selling All Shares RemovesHolding

```python
def test_selling_all_shares_removes_holding(self) -> None:
    ...
```

Verify symbol no longer appears in holdings.

#### Test Cannot Sell Shares NotOwned

```python
def test_sell_more_than_owned_raises(self) -> None:
    ...
```

Verify `InsufficientSharesError`.

#### Test Sell Invalid Quantity Fails

```python
def test_sell_invalid_quantity_raises(self) -> None:
    ...
```

Verify `InvalidQuantityError`.

---

### 18.7 Portfolio Calculation Tests

#### Test Portfolio Value With Multiple Holdings

```python
def test_portfolio_value_with_multiple_holdings(self) -> None:
    ...
```

Example:

- Create account with `10000`.
- Buy:
  - `10` AAPL = `1500`
  - `2` TSLA = `500`
- Cash = `8000`
- Holdings value = `2000`
- Total portfolio value = `10000`
- Profit/loss = `0`

#### Test Profit Loss After Withdrawal

```python
def test_profit_loss_after_withdrawal(self) -> None:
    ...
```

Example:

- Create account with `1000`.
- Withdraw `200`.
- Cash = `800`
- Total deposited cash = `800`
- Portfolio value = `800`
- Profit/loss = `0`

#### Test Profit Loss Uses Current Prices

```python
def test_profit_loss_uses_current_prices(self) -> None:
    ...
```

Because the provided price function is fixed, this test can verify unchanged price behavior.

Optional if backend allows dependency injection for price function, but not required.

---

### 18.8 Transaction History Tests

#### Test Transactions Are Chronological

```python
def test_transactions_are_chronological(self) -> None:
    ...
```

Perform:

- Create account
- Deposit
- Buy
- Sell
- Withdraw

Verify transaction types are in order.

#### Test Transaction IDs Increment

```python
def test_transaction_ids_increment(self) -> None:
    ...
```

Verify IDs are sequential starting from `1`.

#### Test Get Transactions Returns Copy

```python
def test_get_transactions_returns_copy(self) -> None:
    ...
```

Verify mutating the returned list does not mutate the backend internal transaction list.

---

## 19. Backend Implementation Notes

### Floating Point Handling

Use `float` for money because this is a simulation.

To reduce display noise:

- Backend calculations may use raw floats.
- Frontend formatting should display money with two decimal places.

Example display:

```text
$1,234.56
```

Tests should use `assertAlmostEqual(...)` when comparing floats.

---

### Validation Rules

| Input | Rule |
|---|---|
| `account_id` | Non-empty string |
| `owner_name` | Non-empty string |
| `initial_deposit` | Numeric and `>= 0` |
| `deposit amount` | Numeric and `> 0` |
| `withdraw amount` | Numeric and `> 0` |
| `symbol` | Non-empty, supported symbol |
| `quantity` | Integer and `> 0` |

---

### Transaction Cash Amount Semantics

Use positive `cash_amount` values for the size of the transaction.

Examples:

| Transaction Type | `cash_amount` |
|---|---:|
| Account created with initial deposit `1000` | `1000` |
| Deposit `500` | `500` |
| Withdrawal `200` | `200` |
| Buy `2` AAPL at `150` | `300` |
| Sell `1` TSLA at `250` | `250` |

The direction is already represented by `transaction_type`.

---

## 20. Engineer Assignments

## backend_engineer

Implement `backend.py`.

### Required Deliverables

- `TransactionType`
- `Transaction`
- `Holding`
- `PortfolioSummary`
- All custom exceptions
- `get_share_price(symbol)`
- `get_supported_symbols()`
- `TradingAccount`
- Formatting helpers:
  - `holdings_to_rows(...)`
  - `transactions_to_rows(...)`
  - `portfolio_summary_to_dict(...)`

### Backend Acceptance Criteria

The backend is complete when:

- Account can be created.
- Deposits and withdrawals update cash correctly.
- Withdrawals cannot make cash negative.
- Buys cannot exceed available cash.
- Sells cannot exceed owned shares.
- Holdings are accurately reported.
- Portfolio value is accurately calculated.
- Profit/loss is accurately calculated.
- Transactions are recorded in order.
- All specified exceptions are raised appropriately.
- Unit tests pass.

---

## frontend_engineer

Implement `app.py`.

### Required Deliverables

- Gradio Blocks app
- Account creation UI
- Deposit/withdraw UI
- Buy/sell UI
- Portfolio summary display
- Holdings table
- Transactions table
- Error/status messages
- Event handlers wired to backend

### Frontend Acceptance Criteria

The frontend is complete when:

- User can create an account.
- User can deposit funds.
- User can withdraw funds.
- User can buy supported shares.
- User can sell owned shares.
- Invalid operations show friendly error messages.
- Summary updates after every operation.
- Holdings table updates after every trade.
- Transaction history updates after every operation.
- App runs with:

```bash
uv run python app.py
```

---

## test_engineer

Implement `test_backend.py`.

### Required Deliverables

- Standard library `unittest` test suite
- Tests for account creation
- Tests for deposits
- Tests for withdrawals
- Tests for buying
- Tests for selling
- Tests for holdings
- Tests for portfolio value
- Tests for profit/loss
- Tests for transaction history
- Tests for validation and exceptions

### Test Acceptance Criteria

The tests are complete when:

- They can be run with:

```bash
uv run python -m unittest test_backend.py
```

- They cover all required backend behaviors.
- They pass against the completed backend implementation.

---

## 21. End-to-End Acceptance Criteria

The full system is accepted when:

1. Backend unit tests pass.
2. Gradio app launches successfully.
3. User can create an account with an initial deposit.
4. User can deposit and withdraw funds.
5. User cannot withdraw more cash than available.
6. User can buy AAPL, TSLA, and GOOGL if enough cash is available.
7. User cannot buy unsupported symbols.
8. User cannot buy shares without enough cash.
9. User can sell shares they own.
10. User cannot sell shares they do not own.
11. Holdings are displayed correctly.
12. Transaction history is displayed correctly.
13. Portfolio value is calculated correctly.
14. Profit/loss is calculated correctly.
15. All files are in the same directory.
16. No unsupported third-party dependencies are used.