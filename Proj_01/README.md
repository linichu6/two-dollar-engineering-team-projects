\# Trading Simulation Account Manager



A Python trading simulation application generated collaboratively by four AI engineering agents:



\* `engineering\_lead`

\* `backend\_engineer`

\* `frontend\_engineer`

\* `test\_engineer`



The project demonstrates a small multi-agent software development workflow in which different agents are responsible for system design, backend implementation, frontend development, and automated testing.



The application provides a Gradio-based interface for creating a simulated trading account, managing cash, buying and selling supported stocks, and reviewing portfolio performance and transaction history.



\## Features



\* Create a trading account

\* Make an initial cash deposit

\* Deposit and withdraw cash

\* Buy supported stocks

\* Sell owned shares

\* Prevent purchases when cash is insufficient

\* Prevent sales when shares are not owned

\* Prevent withdrawals that exceed available cash

\* Track current holdings

\* Calculate portfolio value

\* Calculate profit and loss

\* Maintain transaction history

\* Validate account and transaction inputs

\* Interactive Gradio web interface

\* Automated backend unit tests



\## Supported Symbols



The simulation currently uses fixed prices for three symbols:



| Symbol | Simulated Price |

| ------ | --------------: |

| AAPL   |         $150.00 |

| TSLA   |         $250.00 |

| GOOGL  |       $2,800.00 |



This project does not connect to a live brokerage or market-data provider.



\## Multi-Agent Development Model



This project was generated using four specialized engineering agents.



\### Engineering Lead



The `engineering\_lead` defines the overall architecture and engineering approach.



Responsibilities include:



\* Analyzing the application requirements

\* Designing the system structure

\* Defining responsibilities between components

\* Defining domain models and business rules

\* Coordinating work between the other engineering agents



The resulting architecture and design decisions are documented in `design.md`.



\### Backend Engineer



The `backend\_engineer` implements the core business logic in `backend.py`.



Responsibilities include:



\* Trading account management

\* Cash balance management

\* Deposits and withdrawals

\* Buy and sell operations

\* Portfolio calculations

\* Holdings management

\* Transaction history

\* Business-rule validation

\* Domain-specific exceptions



The backend does not depend on Gradio and can be used independently from the UI.



\### Frontend Engineer



The `frontend\_engineer` implements the Gradio application in `app.py`.



Responsibilities include:



\* Account creation interface

\* Cash-operation controls

\* Trading controls

\* Portfolio summary display

\* Holdings table

\* Transaction-history table

\* User-facing success and error messages



The frontend delegates business operations to the backend instead of implementing trading logic itself.



\### Test Engineer



The `test\_engineer` implements automated tests in `test\_backend.py`.



The tests cover behavior including:



\* Account creation

\* Duplicate account prevention

\* Deposits

\* Withdrawals

\* Invalid amounts

\* Buying stocks

\* Selling stocks

\* Insufficient cash

\* Insufficient shares

\* Invalid quantities

\* Unsupported symbols

\* Portfolio calculations

\* Transaction ordering

\* Transaction IDs



\## Service Architecture



```text

&#x20;                 ┌───────────────────────┐

&#x20;                 │        User           │

&#x20;                 └───────────┬───────────┘

&#x20;                             │

&#x20;                             ▼

&#x20;                 ┌───────────────────────┐

&#x20;                 │      Gradio UI        │

&#x20;                 │       app.py          │

&#x20;                 │                       │

&#x20;                 │ Account Setup         │

&#x20;                 │ Cash Operations       │

&#x20;                 │ Trading Operations    │

&#x20;                 │ Portfolio Summary     │

&#x20;                 │ Holdings              │

&#x20;                 │ Transaction History   │

&#x20;                 └───────────┬───────────┘

&#x20;                             │

&#x20;                             ▼

&#x20;                 ┌───────────────────────┐

&#x20;                 │   TradingAccount      │

&#x20;                 │     backend.py        │

&#x20;                 │                       │

&#x20;                 │ create\_account()      │

&#x20;                 │ deposit()             │

&#x20;                 │ withdraw()            │

&#x20;                 │ buy()                 │

&#x20;                 │ sell()                │

&#x20;                 │ get\_holdings()        │

&#x20;                 │ get\_transactions()    │

&#x20;                 │ get\_portfolio\_summary │

&#x20;                 └───────────┬───────────┘

&#x20;                             │

&#x20;            ┌────────────────┼────────────────┐

&#x20;            ▼                ▼                ▼

&#x20;     Cash Balance       Holdings State   Transactions

&#x20;                             │

&#x20;                             ▼

&#x20;                    Simulated Prices

&#x20;                 AAPL / TSLA / GOOGL

```



The project currently stores all account information \*\*in memory\*\*.



There is no external database, brokerage API, or persistent storage.



Restarting the application resets the simulated account.



\## Project Structure



```text

Proj\_01/

│

├── app.py

│   Gradio frontend and UI event handlers

│

├── backend.py

│   Trading domain models and business logic

│

├── design.md

│   Architecture and implementation design produced by the engineering lead

│

├── test\_backend.py

│   Backend unit tests

│

├── test\_summary.md

│   Test-engineering notes and test summary

│

├── \_validate.py

│   Supporting validation script

│

└── pyproject.toml

&#x20;   Python project configuration and dependencies

```



\## Backend Domain Model



The main backend class is:



```python

TradingAccount

```



It manages:



```text

TradingAccount

│

├── Account information

│   ├── Account ID

│   └── Owner name

│

├── Cash

│   ├── Current cash balance

│   └── Total deposited cash

│

├── Holdings

│   └── Symbol → quantity

│

└── Transactions

&#x20;   ├── Account creation

&#x20;   ├── Deposit

&#x20;   ├── Withdrawal

&#x20;   ├── Buy

&#x20;   └── Sell

```



The backend also defines these domain models:



```python

Transaction

Holding

PortfolioSummary

TransactionType

```



\## Portfolio Calculation



Portfolio value is calculated as:



```text

Portfolio Value

=

Cash Balance

\+

Value of All Holdings

```



Holdings value is:



```text

Σ(quantity × current simulated share price)

```



Profit/loss is calculated as:



```text

Profit/Loss

=

Total Portfolio Value

\-

Total Deposited Cash

```



Deposits increase contributed capital, while withdrawals reduce it.



Buying and selling shares do not directly change contributed capital.



\## Requirements



\* Python 3.13 or later

\* `uv`

\* Gradio 6.28 or later



The dependency is defined in `pyproject.toml`:



```toml

dependencies = \[

&#x20;   "gradio>=6.28.0",

]

```



\## Installation



Clone the repository:



```bash

git clone https://github.com/linichu6/two-dollar-engineering-team-projects.git

```



Move into the project directory:



```bash

cd two-dollar-engineering-team-projects/Proj\_01

```



Install/synchronize the environment with `uv`:



```bash

uv sync

```



\## Run the Application



From the `Proj\_01` directory:



```bash

uv run app.py

```



Gradio will start a local web server.



Open the local URL displayed in the terminal, typically:



```text

http://127.0.0.1:7860

```



\## Using the Application



\### 1. Create an Account



Enter:



\* Account ID

\* Owner name

\* Initial deposit



Then select:



```text

Create Account

```



\### 2. Deposit or Withdraw Cash



Enter an amount under \*\*Cash Operations\*\* and select:



```text

Deposit

```



or:



```text

Withdraw

```



Withdrawals cannot exceed the available cash balance.



\### 3. Buy Shares



Select one of the supported symbols:



```text

AAPL

TSLA

GOOGL

```



Enter the quantity and select:



```text

Buy

```



The purchase is rejected if there is not enough available cash.



\### 4. Sell Shares



Select a symbol, enter the quantity, and select:



```text

Sell

```



The application prevents selling more shares than the account owns.



\### 5. Review the Portfolio



The interface displays:



\* Cash balance

\* Total deposited cash

\* Holdings value

\* Total portfolio value

\* Profit/loss

\* Current holdings

\* Complete transaction history



\## Run the Tests



Run the backend unit tests with:



```bash

uv run python -m unittest test\_backend.py

```



Or use unittest discovery:



```bash

uv run python -m unittest discover

```



\## Example Workflow



```text

Create Account

&#x20;   │

&#x20;   │ Initial Deposit: $10,000

&#x20;   ▼

Cash Balance: $10,000

&#x20;   │

&#x20;   │ Buy 10 AAPL @ $150

&#x20;   ▼

Cash Balance: $8,500

AAPL Holdings: 10 shares

Holdings Value: $1,500

&#x20;   │

&#x20;   │ Buy 2 TSLA @ $250

&#x20;   ▼

Cash Balance: $8,000

Holdings Value: $2,000

Portfolio Value: $10,000

```



Because the simulation currently uses fixed prices, buying and immediately valuing the same stocks normally produces no investment profit or loss.



\## Validation and Error Handling



The backend defines custom exceptions for common business-rule failures:



```text

TradingSimulationError

├── AccountAlreadyExistsError

├── AccountNotCreatedError

├── InvalidAmountError

├── InvalidQuantityError

├── InsufficientFundsError

├── InsufficientSharesError

└── UnknownSymbolError

```



The Gradio frontend catches these domain errors and displays them to the user without duplicating backend validation logic.



\## Current Limitations



This is an educational trading simulation rather than a production brokerage platform.



Current limitations include:



\* Single simulated user/account per application session

\* In-memory state only

\* No database persistence

\* Fixed stock prices

\* Only AAPL, TSLA, and GOOGL are supported

\* No real brokerage integration

\* No authentication or authorization

\* No market-data API

\* No commissions or fees

\* No order types such as limit or stop orders

\* No asynchronous order execution



\## Possible Future Enhancements



Potential extensions include:



\* Persist accounts and transactions in a database

\* Add real-time market-data APIs

\* Add additional securities

\* Support multiple accounts

\* Add authentication

\* Add REST APIs around the trading backend

\* Add charting and portfolio analytics

\* Add realized and unrealized P/L

\* Add average cost basis

\* Add limit and stop orders

\* Add Docker support

\* Add CI/CD with GitHub Actions

\* Add integration and UI tests



\## Purpose



This project demonstrates both a simple trading application and an \*\*AI-assisted multi-agent engineering workflow\*\*.



Rather than asking one agent to generate the entire application, responsibilities are separated in a way similar to a software engineering team:



```text

Engineering Lead

&#x20;      │

&#x20;      ├───────────────┬────────────────┐

&#x20;      ▼               ▼                ▼

Backend Engineer  Frontend Engineer  Test Engineer

&#x20;      │               │                │

&#x20;      ▼               ▼                ▼

&#x20; backend.py         app.py       test\_backend.py

&#x20;      │               │                │

&#x20;      └───────────────┴────────────────┘

&#x20;                      │

&#x20;                      ▼

&#x20;               Working Application

```



This structure demonstrates how specialized AI agents can collaborate across planning, implementation, user-interface development, and software testing.



