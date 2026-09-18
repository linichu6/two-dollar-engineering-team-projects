import gradio as gr

from backend import (
    AccountNotCreatedError,
    TradingAccount,
    TradingSimulationError,
    holdings_to_rows,
    portfolio_summary_to_dict,
    transactions_to_rows,
)


PALETTE = {
    "gold": "#ecad0a",
    "blue": "#209dd7",
    "purple": "#753991",
    "bg": "#f8fafc",
    "bg_dark": "#111827",
    "surface": "#ffffff",
    "surface_dark": "#1f2937",
    "text": "#0f172a",
    "text_dark": "#e5e7eb",
    "muted": "#64748b",
    "muted_dark": "#9ca3af",
}


def format_money(value: float) -> str:
    return f"${value:,.2f}"


def format_summary_markdown(account: TradingAccount) -> str:
    try:
        summary = account.get_portfolio_summary()
    except AccountNotCreatedError:
        return "No account created yet. Create one to begin tracking cash, holdings, and performance."
    data = portfolio_summary_to_dict(summary)
    pnl_color = "#16a34a" if data["profit_loss"] >= 0 else "#dc2626"
    return (
        f"**Account ID:** `{data['account_id']}`\n\n"
        f"**Owner Name:** {data['owner_name']}\n\n"
        f"**Cash Balance:** {format_money(data['cash_balance'])}\n\n"
        f"**Total Deposited Cash:** {format_money(data['total_deposited_cash'])}\n\n"
        f"**Holdings Value:** {format_money(data['holdings_value'])}\n\n"
        f"**Total Portfolio Value:** {format_money(data['total_portfolio_value'])}\n\n"
        f"**Profit/Loss:** <span style='color:{pnl_color}; font-weight:700'>{format_money(data['profit_loss'])}</span>"
    )


def build_view(account: TradingAccount):
    try:
        summary_markdown = format_summary_markdown(account)
        holdings_rows = holdings_to_rows(account.get_holdings())
        transaction_rows = transactions_to_rows(account.get_transactions())
        return summary_markdown, holdings_rows, transaction_rows
    except AccountNotCreatedError:
        return "No account created yet. Create an account to view holdings and transactions.", [], []


def _status_ok(message: str) -> str:
    return f"<div style='padding:12px 14px;border-radius:12px;background:rgba(32,157,215,0.10);border:1px solid rgba(32,157,215,0.25);color:var(--body-text-color);'><strong>Success:</strong> {message}</div>"


def _status_error(message: str) -> str:
    return f"<div style='padding:12px 14px;border-radius:12px;background:rgba(220,38,38,0.10);border:1px solid rgba(220,38,38,0.25);color:var(--body-text-color);'><strong>Error:</strong> {message}</div>"


def _handle_operation(account: TradingAccount, fn, *args):
    try:
        fn(*args)
        summary, holdings, transactions = build_view(account)
        return account, _status_ok("Operation completed successfully."), summary, holdings, transactions
    except TradingSimulationError as exc:
        summary, holdings, transactions = build_view(account)
        return account, _status_error(str(exc)), summary, holdings, transactions


def handle_create_account(account, account_id, owner_name, initial_deposit):
    try:
        account.create_account(account_id, owner_name, float(initial_deposit or 0))
        summary, holdings, transactions = build_view(account)
        return account, _status_ok("Account created successfully."), summary, holdings, transactions
    except TradingSimulationError as exc:
        summary, holdings, transactions = build_view(account)
        return account, _status_error(str(exc)), summary, holdings, transactions


def handle_deposit(account, amount):
    return _handle_operation(account, account.deposit, float(amount or 0))


def handle_withdraw(account, amount):
    return _handle_operation(account, account.withdraw, float(amount or 0))


def handle_buy(account, symbol, quantity):
    return _handle_operation(account, account.buy, symbol, int(quantity or 0))


def handle_sell(account, symbol, quantity):
    return _handle_operation(account, account.sell, symbol, int(quantity or 0))


def handle_refresh(account):
    summary, holdings, transactions = build_view(account)
    return account, _status_ok("Portfolio refreshed."), summary, holdings, transactions


css = f"""
:root {{
  --gold: {PALETTE['gold']};
  --blue: {PALETTE['blue']};
  --purple: {PALETTE['purple']};
}}
.gradio-container {{
  max-width: 1250px !important;
}}
.hero {{
  border: 1px solid rgba(125, 125, 125, 0.18);
  border-radius: 24px;
  padding: 28px;
  background: linear-gradient(135deg, rgba(32,157,215,0.12), rgba(117,57,145,0.10), rgba(236,173,10,0.10));
  box-shadow: 0 12px 30px rgba(15,23,42,0.08);
}}
.card {{
  border: 1px solid rgba(125, 125, 125, 0.18);
  border-radius: 18px;
  padding: 18px;
  background: var(--background-fill-primary);
}}
.small-note {{ color: var(--body-text-color-subdued); font-size: 0.95rem; }}
"""


def build_demo():
    with gr.Blocks(title="Trading Simulation Account Manager", css=css, theme=gr.themes.Soft(primary_hue="blue", secondary_hue="purple")) as demo:
        gr.Markdown(
            "# Trading Simulation Account Manager\n"
            "<div class='hero'>"
            "A polished single-user demo for creating an account, managing cash, trading supported symbols, and reviewing portfolio performance in real time."
            "</div>"
        )

        account_state = gr.State(TradingAccount())
        status_output = gr.Markdown()
        # summary_output = gr.Markdown(value="No account created yet. Create one to begin tracking cash, holdings, and performance.")

        with gr.Row():
            with gr.Column(scale=1):
                with gr.Group(elem_classes=["card"]):
                    gr.Markdown("## Account Setup")
                    account_id_input = gr.Textbox(label="Account ID", placeholder="Example: ACC-001", interactive=True)
                    owner_name_input = gr.Textbox(label="Owner Name", placeholder="Example: Jane Doe", interactive=True)
                    initial_deposit_input = gr.Number(label="Initial Deposit", value=10000, minimum=0, interactive=True)
                    create_account_button = gr.Button("Create Account", variant="primary")

                with gr.Group(elem_classes=["card"]):
                    gr.Markdown("## Cash Operations")
                    cash_amount_input = gr.Number(label="Cash Amount", value=1000, minimum=0, interactive=True)
                    with gr.Row():
                        deposit_button = gr.Button("Deposit")
                        withdraw_button = gr.Button("Withdraw")

            with gr.Column(scale=1):
                with gr.Group(elem_classes=["card"]):
                    gr.Markdown("## Trading Operations")
                    symbol_input = gr.Dropdown(
                        choices=["AAPL", "TSLA", "GOOGL"],
                        value="AAPL",
                        label="Symbol",
                        interactive=True,
                    )
                    quantity_input = gr.Number(label="Quantity", value=1, minimum=1, precision=0, interactive=True)
                    with gr.Row():
                        buy_button = gr.Button("Buy", variant="primary")
                        sell_button = gr.Button("Sell")
                    refresh_button = gr.Button("Refresh Portfolio")

                with gr.Group(elem_classes=["card"]):
                    gr.Markdown("## Quick Guidance")
                    gr.Markdown(
                        "- Supported symbols: AAPL, TSLA, GOOGL\n"
                        "- Withdrawals cannot exceed cash balance\n"
                        "- Buys cannot exceed available cash\n"
                        "- Sells cannot exceed owned shares"
                    )

        #with gr.Group(elem_classes=["card"]):
        #    gr.Markdown("## Portfolio Summary")
        #    summary_output.render()
        with gr.Group(elem_classes=["card"]):
            gr.Markdown("## Portfolio Summary")
            summary_output = gr.Markdown(
                value="No account created yet. Create one to begin tracking cash, holdings, and performance."
            )

        with gr.Row():
            with gr.Column():
                with gr.Group(elem_classes=["card"]):
                    gr.Markdown("## Holdings")
                    holdings_table = gr.Dataframe(
                        headers=["Symbol", "Quantity", "Current Price", "Market Value"],
                        datatype=["str", "number", "number", "number"],
                        value=[],
                        interactive=False,
                    )
            with gr.Column():
                with gr.Group(elem_classes=["card"]):
                    gr.Markdown("## Transaction History")
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
                        datatype=["number", "str", "str", "str", "number", "number", "number", "number", "str"],
                        value=[],
                        interactive=False,
                    )

        create_account_button.click(
            fn=handle_create_account,
            inputs=[account_state, account_id_input, owner_name_input, initial_deposit_input],
            outputs=[account_state, status_output, summary_output, holdings_table, transactions_table],
        )
        deposit_button.click(
            fn=handle_deposit,
            inputs=[account_state, cash_amount_input],
            outputs=[account_state, status_output, summary_output, holdings_table, transactions_table],
        )
        withdraw_button.click(
            fn=handle_withdraw,
            inputs=[account_state, cash_amount_input],
            outputs=[account_state, status_output, summary_output, holdings_table, transactions_table],
        )
        buy_button.click(
            fn=handle_buy,
            inputs=[account_state, symbol_input, quantity_input],
            outputs=[account_state, status_output, summary_output, holdings_table, transactions_table],
        )
        sell_button.click(
            fn=handle_sell,
            inputs=[account_state, symbol_input, quantity_input],
            outputs=[account_state, status_output, summary_output, holdings_table, transactions_table],
        )
        refresh_button.click(
            fn=handle_refresh,
            inputs=[account_state],
            outputs=[account_state, status_output, summary_output, holdings_table, transactions_table],
        )

    return demo


demo = build_demo()


if __name__ == "__main__":
    demo.launch()
