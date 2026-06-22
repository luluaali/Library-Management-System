import gradio as gr
import pandas as pd
import datetime
import os

# File paths
BOOKS_FILE = 'Library_Books_Collection.csv'
MEMBERS_FILE = 'Library_Members.csv'
TRANSACTIONS_FILE = 'transactions.csv'
RETURNS_FILE = 'returns.csv'


def initialize_files():
    if not os.path.exists(TRANSACTIONS_FILE):
        transactions_df = pd.DataFrame(
            columns=['Member Name', 'Member Code', 'Book Code', 'Date of Issue', 'Due Date']
        )
        transactions_df.to_csv(TRANSACTIONS_FILE, index=False)

    if not os.path.exists(RETURNS_FILE):
        returns_df = pd.DataFrame(
            columns=['Member Name', 'Member Code', 'Book Code', 'Due', 'Date of Return']
        )
        returns_df.to_csv(RETURNS_FILE, index=False)


def load_books():
    if os.path.exists(BOOKS_FILE):
        return pd.read_csv(BOOKS_FILE, encoding="utf-8")
    else:
        return pd.DataFrame(columns=[
            'Book Code', 'Book Name', 'Author Name',
            'Availability', 'Amount', 'Late Return Fine'
        ])


def load_members():
    if os.path.exists(MEMBERS_FILE):
        return pd.read_csv(MEMBERS_FILE, encoding="latin1")
    else:
        return pd.DataFrame(columns=[
            "Member Code", "Member Name", "Phone Number", "Email Address",
            "Book Code", "Book Name", "Issue Date", "Return Date",
            "Dues", "Fines"
        ])


def load_transactions():
    if os.path.exists(TRANSACTIONS_FILE):
        return pd.read_csv(TRANSACTIONS_FILE)
    else:
        return pd.DataFrame(columns=[
            'Member Name', 'Member Code', 'Book Code', 'Date of Issue', 'Due Date'
        ])


def load_returns():
    if os.path.exists(RETURNS_FILE):
        return pd.read_csv(RETURNS_FILE)
    else:
        return pd.DataFrame(columns=[
            'Member Name', 'Member Code', 'Book Code', 'Due', 'Date of Return'
        ])


def save_books(df):
    df.to_csv(BOOKS_FILE, index=False)


def save_members(df):
    df.to_csv(MEMBERS_FILE, index=False)


def save_transactions(df):
    df.to_csv(TRANSACTIONS_FILE, index=False)


def save_returns(df):
    df.to_csv(RETURNS_FILE, index=False)


# -------- Helper limits --------
MAX_ACTIVE_BOOKS = 3  # max books a member can have at a time


def count_active_books_for_member(member_code: str) -> int:
    tx = load_transactions()
    if tx.empty:
        return 0
    return (tx["Member Code"] == member_code).sum()


# -------- Basic UI helpers --------
def ui_show_books():
    return load_books()


def ui_filter_books(search_text, availability):
    df = load_books()

    if availability in ["Yes", "No"]:
        df = df[df["Availability"] == availability]

    search_text = search_text.strip()
    if search_text:
        mask = (
            df["Book Code"].astype(str).str.contains(search_text, case=False, na=False) |
            df["Book Name"].astype(str).str.contains(search_text, case=False, na=False) |
            df["Author Name"].astype(str).str.contains(search_text, case=False, na=False)
        )
        df = df[mask]

    return df


def ui_add_book(book_code, book_name, author_name, availability, amount, late_fine):
    books_df = load_books()
    new_book = pd.DataFrame({
        "Book Code": [book_code],
        "Book Name": [book_name],
        "Author Name": [author_name],
        "Availability": [availability],
        "Amount": [amount],
        "Late Return Fine": [late_fine],
    })
    books_df = pd.concat([books_df, new_book], ignore_index=True)
    save_books(books_df)
    return books_df


def ui_show_members():
    df = load_members()
    cols = [
        "Member Code", "Member Name", "Phone Number", "Email Address",
        "Dues", "Fines",
        "Issue Date", "Return Date",
        "Book Code", "Book Name",
    ]
    cols = [c for c in cols if c in df.columns]
    return df[cols]


def ui_add_member(member_code, member_name, phone, email,
                  book_code, book_name, dues, fines):
    members_df = load_members()
    new_member = pd.DataFrame({
        "Member Code": [member_code],
        "Member Name": [member_name],
        "Phone Number": [phone],
        "Email Address": [email],
        "Book Code": [book_code],
        "Book Name": [book_name],
        "Issue Date": [""],
        "Return Date": [""],
        "Dues": [dues],
        "Fines": [fines],
    })
    members_df = pd.concat([members_df, new_member], ignore_index=True)
    save_members(members_df)
    return members_df


def ui_delete_book(book_code):
    df = load_books()
    df = df[df["Book Code"] != book_code]
    save_books(df)
    return df


def ui_update_member(member_code, new_phone, new_dues,
                     new_fines, new_book_code, new_book_name):
    df = load_members()
    mask = df["Member Code"] == member_code
    if new_phone.strip():
        df.loc[mask, "Phone Number"] = new_phone
    if new_dues.strip():
        df.loc[mask, "Dues"] = new_dues
    if new_fines.strip():
        df.loc[mask, "Fines"] = new_fines
    if new_book_code.strip():
        df.loc[mask, "Book Code"] = new_book_code
    if new_book_name.strip():
        df.loc[mask, "Book Name"] = new_book_name
    save_members(df)
    return df


def ui_delete_member(member_code):
    df = load_members()
    df = df[df["Member Code"] != member_code]
    save_members(df)
    return df


# ---- Issue / Return helpers ----
def ui_issue_book(member_name, member_code, book_code, issue_date_str):
    books_df = load_books()
    members_df = load_members()
    transactions_df = load_transactions()

    if member_code not in members_df["Member Code"].values:
        return transactions_df, books_df, f"Member {member_code} not found"

    active_count = count_active_books_for_member(member_code)
    if active_count >= MAX_ACTIVE_BOOKS:
        return transactions_df, books_df, (
            f"Member {member_code} already has {active_count} active books. "
            f"Limit is {MAX_ACTIVE_BOOKS}."
        )

    if book_code not in books_df["Book Code"].values:
        return transactions_df, books_df, f"Book {book_code} not found"

    book_row = books_df[books_df["Book Code"] == book_code]
    if book_row["Availability"].values[0] == "No":
        return transactions_df, books_df, "Book is not available"

    try:
        dat = datetime.datetime.strptime(issue_date_str, "%Y/%m/%d").date()
    except Exception:
        return transactions_df, books_df, "Incorrect issue date format, use YYYY/MM/DD"

    due_date = dat + datetime.timedelta(days=14)

    new_transaction = pd.DataFrame({
        "Member Name": [member_name],
        "Member Code": [member_code],
        "Book Code": [book_code],
        "Date of Issue": [str(dat)],
        "Due Date": [str(due_date)],
    })
    transactions_df = pd.concat([transactions_df, new_transaction], ignore_index=True)
    save_transactions(transactions_df)

    books_df.loc[books_df["Book Code"] == book_code, "Availability"] = "No"
    save_books(books_df)

    return transactions_df, books_df, f"BOOK ISSUED, due on {due_date}"


def ui_return_book(member_name, member_code, book_code, due, return_date_str):
    books_df = load_books()
    members_df = load_members()
    returns_df = load_returns()
    transactions_df = load_transactions()

    if member_code not in members_df["Member Code"].values:
        return returns_df, books_df, transactions_df, f"Member {member_code} not found"

    if book_code not in books_df["Book Code"].values:
        return returns_df, books_df, transactions_df, f"Book {book_code} not found"

    try:
        return_date = datetime.datetime.strptime(return_date_str, "%Y/%m/%d").date()
    except Exception:
        return returns_df, books_df, transactions_df, "Incorrect return date format, use YYYY/MM/DD"

    row = transactions_df[
        (transactions_df["Member Code"] == member_code) &
        (transactions_df["Book Code"] == book_code)
    ]

    auto_due_str = "AED 0.00"
    if not row.empty and "Due Date" in row.columns:
        try:
            due_date = datetime.datetime.strptime(
                row["Due Date"].values[0], "%Y-%m-%d"
            ).date()
            days_late = (return_date - due_date).days
            fine_amount = max(0, days_late) * 1
            auto_due_str = f"AED {fine_amount:.2f}"
        except Exception:
            auto_due_str = "AED 0.00"

    if not due.strip():
        due = auto_due_str

    new_return = pd.DataFrame({
        "Member Name": [member_name],
        "Member Code": [member_code],
        "Book Code": [book_code],
        "Due": [due],
        "Date of Return": [str(return_date)],
    })
    returns_df = pd.concat([returns_df, new_return], ignore_index=True)
    save_returns(returns_df)

    books_df.loc[books_df["Book Code"] == book_code, "Availability"] = "Yes"
    save_books(books_df)

    transactions_df = transactions_df[
        ~((transactions_df["Member Code"] == member_code) &
          (transactions_df["Book Code"] == book_code))
    ]
    save_transactions(transactions_df)

    return returns_df, books_df, transactions_df, f"BOOK RETURNED, fine: {due}"


# ---- Reports helpers ----
def ui_view_issued():
    tx = load_transactions()
    if tx.empty or "Due Date" not in tx.columns:
        return tx

    tx = tx.copy()
    tx["Due Date"] = pd.to_datetime(tx["Due Date"], errors="coerce")
    today = pd.Timestamp.today().normalize()
    tx["Days Late"] = (today - tx["Due Date"]).dt.days

    on_time = tx[tx["Days Late"] <= 0]
    cols = ["Member Name", "Member Code", "Book Code",
            "Date of Issue", "Due Date", "Days Late"]
    cols = [c for c in cols if c in on_time.columns]
    return on_time[cols]


def ui_view_defaulters():
    tx = load_transactions()
    if tx.empty or "Due Date" not in tx.columns:
        return tx

    tx = tx.copy()
    tx["Due Date"] = pd.to_datetime(tx["Due Date"], errors="coerce")
    today = pd.Timestamp.today().normalize()
    tx["Days Late"] = (today - tx["Due Date"]).dt.days
    defaulters = tx[tx["Days Late"] > 0]

    cols = ["Member Name", "Member Code", "Book Code",
            "Date of Issue", "Due Date", "Days Late"]
    cols = [c for c in cols if c in defaulters.columns]
    return defaulters[cols]


# -------- Gradio UI --------
with gr.Blocks() as demo:
    gr.Markdown("# Library Management System")

    # -------- About tab --------
    with gr.Tab("About"):
        gr.Markdown(
            """
            ### About this Library Management System

            This system streamlines day-to-day library operations, from cataloging books
            to managing member borrowing activity.

            **Key capabilities**

            - Centralized catalog of titles, authors, availability status and pricing.
            - Member registry with contact details and outstanding dues.
            - Issuing and returning of books with automatic due-date calculation.
            - Overdue tracking with per-day late fees and defaulter reporting.
            - Real-time visibility of stock and current checkouts.
            - CSV-based data storage for easy backup and migration.
            """
        )

    # -------- Books tab --------
    with gr.Tab("Books"):
        gr.Markdown("### Show Books")

        with gr.Row():
            book_search_in = gr.Textbox(
                label="Search (code / name / author)",
                placeholder="e.g. B009, Jane Eyre, Gabriel",
            )
            book_avail_filter = gr.Dropdown(
                choices=["All", "Yes", "No"],
                value="All",
                label="Availability",
            )

        show_books_btn = gr.Button("Show / Search Books")
        books_table = gr.Dataframe(
            headers=[
                "Book Code", "Book Name", "Author Name",
                "Availability", "Amount", "Late Return Fine"
            ],
            datatype=["str", "str", "str", "str", "str", "str"],
            interactive=False,
            wrap=True,
            column_widths=[110, 260, 200, 120, 110, 140],
        )
        show_books_btn.click(
            ui_filter_books,
            inputs=[book_search_in, book_avail_filter],
            outputs=books_table,
        )

        gr.Markdown("### Add Book")
        with gr.Row():
            book_code_in = gr.Textbox(label="Book Code")
            book_name_in = gr.Textbox(label="Book Name")
        with gr.Row():
            author_in = gr.Textbox(label="Author Name")
            availability_in = gr.Dropdown(
                choices=["Yes", "No"], value="Yes", label="Availability"
            )
        with gr.Row():
            amount_in = gr.Textbox(label="Amount (e.g. AED 50.00)")
            fine_in = gr.Textbox(label="Late Return Fine (e.g. AED 5.00)")

        add_book_btn = gr.Button("Add Book")
        add_book_btn.click(
            ui_add_book,
            inputs=[book_code_in, book_name_in, author_in, availability_in, amount_in, fine_in],
            outputs=books_table,
        )

        gr.Markdown("### Delete Book")
        del_book_code_in = gr.Textbox(label="Book Code to delete")
        del_book_btn = gr.Button("Delete Book")
        del_book_btn.click(ui_delete_book, inputs=del_book_code_in, outputs=books_table)

    # -------- Members tab --------
    with gr.Tab("Members"):
        gr.Markdown("### Show Members")
        show_members_btn = gr.Button("Show Members")
        members_table = gr.Dataframe(
            headers=[
                "Member Code", "Member Name", "Phone Number", "Email Address",
                "Dues", "Fines",
                "Issue Date", "Return Date",
                "Book Code", "Book Name",
            ],
            datatype=["str"] * 10,
            interactive=False,
        )
        show_members_btn.click(ui_show_members, outputs=members_table)

        gr.Markdown("### Add Member")
        with gr.Row():
            mem_code_in = gr.Textbox(label="Member Code")
            mem_name_in = gr.Textbox(label="Member Name")
        with gr.Row():
            phone_in = gr.Textbox(label="Phone Number")
            email_in = gr.Textbox(label="Email Address")
        with gr.Row():
            mem_book_code_in = gr.Textbox(label="Book Code (optional)", value="")
            mem_book_name_in = gr.Textbox(label="Book Name (optional)", value="")
        with gr.Row():
            dues_in = gr.Textbox(label="Dues (e.g. AED 0.00)", value="AED 0.00")
            fines_in = gr.Textbox(label="Fines (e.g. AED 0.00)", value="AED 0.00")

        add_member_btn = gr.Button("Add Member")
        add_member_btn.click(
            ui_add_member,
            inputs=[
                mem_code_in, mem_name_in, phone_in, email_in,
                mem_book_code_in, mem_book_name_in, dues_in, fines_in
            ],
            outputs=members_table,
        )

        gr.Markdown("### Update Member")
        upd_mem_code_in = gr.Textbox(label="Member Code to update")
        upd_phone_in = gr.Textbox(label="New Phone Number (leave blank to keep)")
        upd_dues_in = gr.Textbox(label="New Dues (leave blank to keep)")
        upd_fines_in = gr.Textbox(label="New Fines (leave blank to keep)")
        upd_book_code_in = gr.Textbox(label="New Book Code (leave blank to keep)")
        upd_book_name_in = gr.Textbox(label="New Book Name (leave blank to keep)")

        upd_mem_btn = gr.Button("Update Member")
        upd_mem_btn.click(
            ui_update_member,
            inputs=[
                upd_mem_code_in,
                upd_phone_in,
                upd_dues_in,
                upd_fines_in,
                upd_book_code_in,
                upd_book_name_in,
            ],
            outputs=members_table,
        )

        gr.Markdown("### Delete Member")
        del_mem_code_in = gr.Textbox(label="Member Code to delete")
        del_mem_btn = gr.Button("Delete Member")
        del_mem_btn.click(ui_delete_member, inputs=del_mem_code_in, outputs=members_table)

    # -------- Reports tab --------
    with gr.Tab("Reports"):
        gr.Markdown("### Reports")

        with gr.Row():
            view_issued_btn = gr.Button("View Issued Books")
            view_defaulters_btn = gr.Button("View Defaulters")

        reports_table = gr.Dataframe(
            label="Report",
            headers=[
                "Member Name", "Member Code", "Book Code",
                "Date of Issue", "Due Date", "Days Late"
            ],
            datatype=["str", "str", "str", "str", "str", "number"],
            interactive=False,
            wrap=True,
        )

        view_issued_btn.click(
            ui_view_issued,
            outputs=reports_table,
        )

        view_defaulters_btn.click(
            ui_view_defaulters,
            outputs=reports_table,
        )

    # -------- Transactions tab --------
    with gr.Tab("Transactions"):
        gr.Markdown("### Transactions")

        mode_radio = gr.Radio(
            ["Issue", "Return"],
            label="Choose action",
            value="Issue",
            interactive=True,
        )

        # ----- Issue Book section -----
        issue_section = gr.Column(visible=True)
        with issue_section:
            gr.Markdown("#### Issue Book")
            with gr.Row():
                iss_member_name_in = gr.Textbox(label="Member Name")
                iss_member_code_in = gr.Textbox(label="Member Code")
            with gr.Row():
                iss_book_code_in = gr.Textbox(label="Book Code")
                iss_date_in = gr.Textbox(label="Issue Date (YYYY/MM/DD)")

            issue_status = gr.Textbox(label="Status", interactive=False)
            issue_transactions_table = gr.Dataframe(
                label="Transactions",
                headers=[
                    "Member Name", "Member Code", "Book Code",
                    "Date of Issue", "Due Date"
                ],
                datatype=["str", "str", "str", "str", "str"],
                interactive=False,
                wrap=True,
                column_widths=[160, 120, 120, 150, 150],
            )
            issue_books_table = gr.Dataframe(
                label="Books (availability)",
                headers=[
                    "Book Code", "Book Name", "Author Name",
                    "Availability", "Amount", "Late Return Fine"
                ],
                datatype=["str", "str", "str", "str", "str", "str"],
                interactive=False,
                wrap=True,
                column_widths=[110, 260, 200, 120, 110, 140],
            )

            issue_btn = gr.Button("Issue Book")
            issue_btn.click(
                ui_issue_book,
                inputs=[iss_member_name_in, iss_member_code_in, iss_book_code_in, iss_date_in],
                outputs=[issue_transactions_table, issue_books_table, issue_status],
            )

        # ----- Return Book section -----
        return_section = gr.Column(visible=False)
        with return_section:
            gr.Markdown("#### Return Book")
            with gr.Row():
                ret_member_name_in = gr.Textbox(label="Member Name")
                ret_member_code_in = gr.Textbox(label="Member Code")
            with gr.Row():
                ret_book_code_in = gr.Textbox(label="Book Code")
                ret_due_in = gr.Textbox(label="Due Amount (e.g. AED 0.00)")
            with gr.Row():
                ret_date_in = gr.Textbox(label="Return Date (YYYY/MM/DD)")

            return_status = gr.Textbox(label="Status", interactive=False)
            return_returns_table = gr.Dataframe(
                label="Returns",
                headers=["Member Name", "Member Code", "Book Code", "Due", "Date of Return"],
                datatype=["str", "str", "str", "str", "str"],
                interactive=False,
                wrap=True,
                column_widths=[160, 120, 120, 110, 150],
            )
            return_books_table = gr.Dataframe(
                label="Books (availability)",
                headers=[
                    "Book Code", "Book Name", "Author Name",
                    "Availability", "Amount", "Late Return Fine"
                ],
                datatype=["str", "str", "str", "str", "str", "str"],
                interactive=False,
                wrap=True,
                column_widths=[110, 260, 200, 120, 110, 140],
            )
            return_transactions_table = gr.Dataframe(
                label="Open Transactions",
                headers=[
                    "Member Name", "Member Code", "Book Code",
                    "Date of Issue", "Due Date"
                ],
                datatype=["str", "str", "str", "str", "str"],
                interactive=False,
                wrap=True,
                column_widths=[160, 120, 120, 150, 150],
            )

            return_btn = gr.Button("Return Book")
            return_btn.click(
                ui_return_book,
                inputs=[ret_member_name_in, ret_member_code_in, ret_book_code_in, ret_due_in, ret_date_in],
                outputs=[return_returns_table, return_books_table, return_transactions_table, return_status],
            )

        def toggle_mode(mode):
            if mode == "Issue":
                return gr.Column(visible=True), gr.Column(visible=False)
            else:
                return gr.Column(visible=False), gr.Column(visible=True)

        mode_radio.change(
            toggle_mode,
            inputs=mode_radio,
            outputs=[issue_section, return_section],
        )


if __name__ == "__main__":
    initialize_files()
    demo.launch(share=True)
