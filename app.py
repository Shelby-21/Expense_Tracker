import streamlit as st
import sqlite3
from datetime import datetime
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from database import create_tables

create_tables()

conn = sqlite3.connect("finance.db", check_same_thread=False)
cursor = conn.cursor()

# ================= PAGE LAYOUT =================
st.set_page_config(layout="wide", page_title="Finance Analytics Pro")

# ================= USER FUNCTIONS =================

def create_user(username, password):
    try:
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, password)
        )

        conn.commit()

        cursor.execute(
            "SELECT id FROM users WHERE username=?",
            (username,)
        )

        user_id = cursor.fetchone()[0]

        load_default_categories(user_id)

        return True

    except:
        return False

def login_user(username, password):
    cursor.execute("SELECT id FROM users WHERE username=? AND password=?", (username, password))
    return cursor.fetchone()

# ================= CATEGORY FUNCTIONS =================

def load_default_categories(user_id):
    category_data = [
        ("Salary","Base Salary","Income"),
        ("Salary","Bonus","Income"),
        ("Salary","Incentives","Income"),
        ("Business","Freelance","Income"),
        ("Business","Consulting","Income"),
        ("Business","Side Hustle","Income"),
        ("Returns","Interest Income","Income"),
        ("Returns","Dividends","Income"),
        ("Returns","Capital Gains","Income"),
        ("Returns","Rental Income","Income"),
        ("Returns","Business Profit Withdrawal","Income"),
        ("Refund","Tax Refund","Income"),
        ("Refund","Purchase Refund","Income"),
        ("Other Income","Gifts Received","Income"),
        ("Other Income","Misc Income","Income"),
        ("Other Income","Reimbursements","Income"),

        ("Food","Groceries","Expense"),
        ("Food","Dining Out","Expense"),
        ("Food","Snacks","Expense"),
        ("Food","Coffee","Expense"),
        ("Food","Food Delivery","Expense"),

        ("Housing","Rent","Expense"),
        ("Housing","Maintenance","Expense"),
        ("Housing","Repairs","Expense"),
        ("Housing","Furniture","Expense"),
        ("Housing","Appliances","Expense"),

        ("Utilities","Electricity","Expense"),
        ("Utilities","Water","Expense"),
        ("Utilities","Internet","Expense"),
        ("Utilities","Mobile Recharge","Expense"),
        ("Utilities","Gas","Expense"),
        ("Utilities","DTH / Cable","Expense"),
        ("Utilities","Society Charges","Expense"),

        ("Transport","Fuel","Expense"),
        ("Transport","Cab","Expense"),
        ("Transport","Metro","Expense"),
        ("Transport","Bus","Expense"),
        ("Transport","Parking","Expense"),
        ("Transport","Vehicle Maintenance","Expense"),
        ("Transport","Toll","Expense"),
        ("Transport","Insurance Renewal","Expense"),

        ("Shopping","Clothes","Expense"),
        ("Shopping","Shoes","Expense"),
        ("Shopping","Gadgets","Expense"),
        ("Shopping","Accessories","Expense"),
        ("Shopping","Household Items","Expense"),

        ("Entertainment","Movies","Expense"),
        ("Entertainment","OTT Subscriptions","Expense"),
        ("Entertainment","Events","Expense"),
        ("Entertainment","Games","Expense"),
        ("Entertainment","Music","Expense"),

        ("Travel","Flights","Expense"),
        ("Travel","Hotels","Expense"),
        ("Travel","Local Travel","Expense"),
        ("Travel","Travel Food","Expense"),
        ("Travel","Travel Shopping","Expense"),

        ("Health","Doctor Visit","Expense"),
        ("Health","Medicines","Expense"),
        ("Health","Tests","Expense"),
        ("Health","Gym","Expense"),
        ("Health","Supplements","Expense"),
        ("Health","Therapy / Counseling","Expense"),

        ("Family","Gifts","Expense"),
        ("Family","Support","Expense"),
        ("Family","Celebrations","Expense"),
        ("Family","Functions","Expense"),

        ("Education","Courses","Expense"),
        ("Education","Books","Expense"),
        ("Education","Certifications","Expense"),
        ("Education","Workshops","Expense"),

        ("Insurance","Health Insurance","Expense"),
        ("Insurance","Vehicle Insurance","Expense"),
        ("Insurance","Life Insurance","Expense"),

        ("Loan","Home Loan EMI","Expense"),
        ("Loan","Personal Loan EMI","Expense"),
        ("Loan","Education Loan EMI","Expense"),
        ("Loan","Credit Card Bill","Expense"),

        ("Personal Care","Haircut","Expense"),
        ("Personal Care","Grooming","Expense"),
        ("Personal Care","Cosmetics","Expense"),
        ("Personal Care","Hygiene","Expense"),

        ("Equity","Stocks","Investment"),
        ("Equity","Mutual Funds","Investment"),
        ("Equity","ETFs","Investment"),
        ("Retirement","PPF","Investment"),
        ("Retirement","NPS","Investment"),
        ("Debt","Bonds","Investment"),
        ("Debt","Fixed Deposit","Investment"),
        ("Debt","Liquid Funds","Investment"),
        ("Gold","Digital Gold","Investment"),
        ("Gold","Physical Gold","Investment"),
        ("Alternative","REITs","Investment"),
        ("Alternative","InvITs","Investment"),
        ("Crypto","Crypto","Investment"),

        ("Transfer","Bank Transfer","Transfer"),
        ("Transfer","Wallet Transfer","Transfer"),
        ("Transfer","Cash Withdrawal","Transfer"),
        ("Transfer","Investment Transfer","Transfer"),
    ]

    for category, subcategory, type_ in category_data:
        cursor.execute("""
            SELECT 1 FROM categories
            WHERE user_id=? AND category=? AND subcategory=?
        """, (user_id, category, subcategory))

        if not cursor.fetchone():
            cursor.execute("""
                INSERT INTO categories (user_id, category, subcategory, type)
                VALUES (?, ?, ?, ?)
            """, (user_id, category, subcategory, type_))
    conn.commit()

def get_categories(user_id, type_):
    cursor.execute("SELECT DISTINCT category FROM categories WHERE user_id=? AND type=?", (user_id, type_))
    return [x[0] for x in cursor.fetchall()]

def get_subcategories(user_id, category):
    cursor.execute("SELECT subcategory FROM categories WHERE user_id=? AND category=?", (user_id, category))
    return [x[0] for x in cursor.fetchall()]

# ================= ACCOUNT FUNCTIONS =================
def get_accounts(user_id):
    cursor.execute("SELECT id, account_name, opening_balance FROM accounts WHERE user_id=?", (user_id,))
    return cursor.fetchall()

def add_account(user_id, name, type_, balance, include_networth):
    cursor.execute("""
        INSERT INTO accounts (user_id, account_name, account_type, opening_balance, include_in_networth)
        VALUES (?, ?, ?, ?, ?)""", (user_id, name, type_, balance, include_networth))
    conn.commit()

def update_balance(account_id, new_balance):
    cursor.execute("UPDATE accounts SET opening_balance=? WHERE id=?", (new_balance, account_id))
    conn.commit()

# ================= TRANSACTION ENGINE =================
def add_transaction(user_id, date, type_, category, subcategory, account_id, amount, notes):
    signed_amount = -amount if type_ in ["Expense", "Investment"] else amount
    cursor.execute("""
        INSERT INTO transactions (user_id,date,type,category,subcategory,account,amount,signed_amount,tag,notes,created_at)
        VALUES (?,?,?,?,?,?,?,?,?,?,?)""", (user_id,date,type_,category,subcategory,account_id,amount,signed_amount,"",notes,datetime.now()))
    cursor.execute("SELECT opening_balance FROM accounts WHERE id=?", (account_id,))
    balance = cursor.fetchone()[0]
    update_balance(account_id, balance + signed_amount)
    conn.commit()

def delete_transaction(transaction_id):
    cursor.execute("SELECT account, signed_amount FROM transactions WHERE id=?", (transaction_id,))
    account_id, signed_amount = cursor.fetchone()
    cursor.execute("SELECT opening_balance FROM accounts WHERE id=?", (account_id,))
    balance = cursor.fetchone()[0]
    update_balance(account_id, balance - signed_amount)
    cursor.execute("DELETE FROM transactions WHERE id=?", (transaction_id,))
    conn.commit()

def get_transactions(user_id):
    cursor.execute("SELECT id, date, type, category, subcategory, account, amount, notes FROM transactions WHERE user_id=? ORDER BY date DESC", (user_id,))
    return cursor.fetchall()

# ================= BUDGET FUNCTIONS =================
def set_budget(user_id, category, amount):
    cursor.execute("SELECT id FROM budgets WHERE user_id=? AND category=?", (user_id, category))
    if cursor.fetchone():
        cursor.execute("UPDATE budgets SET monthly_budget=? WHERE user_id=? AND category=?", (amount, user_id, category))
    else:
        cursor.execute("INSERT INTO budgets (user_id, category, monthly_budget) VALUES (?, ?, ?)", (user_id, category, amount))
    conn.commit()

def get_budgets(user_id):
    cursor.execute("SELECT category, monthly_budget FROM budgets WHERE user_id=?", (user_id,))
    return cursor.fetchall()

# ================= SESSION =================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_id" not in st.session_state:
    st.session_state.user_id = None

st.title("📊 Personal Finance Analytics App")

# ================= LOGIN / NAVIGATION =================
if not st.session_state.logged_in:
    menu = st.sidebar.selectbox("Menu", ["Login", "Create Account"])
    if menu == "Create Account":
        st.subheader("Create Account")
        u = st.text_input("Username"); p = st.text_input("Password", type="password")
        if st.button("Signup"):
            if create_user(u, p): st.success("Account created")
            else: st.error("Username exists")
    else:
        st.subheader("Login")
        u = st.text_input("Username"); p = st.text_input("Password", type="password")
        if st.button("Login"):
            res = login_user(u, p)
            if res:
                st.session_state.logged_in = True
                st.session_state.user_id = res[0]
                st.rerun()
            else: st.error("Invalid credentials")
else:
    user_id = st.session_state.user_id
    menu = st.sidebar.radio("Navigation", [
        "Dashboard",
        "Add Transaction",
        "View Transactions",
        "Add Account",
        "View Accounts",
        "Add Category",
        "Set Budgets",
        "View Budgets"
    ])

    if menu == "Add Transaction":
        st.subheader("Add Transaction")
        c1, c2 = st.columns(2)
        with c1:
            date = st.date_input("Date")
            type_ = st.selectbox("Type", ["Income", "Expense", "Investment"])
        with c2:
            category = st.selectbox("Category", get_categories(user_id, type_))
            subcategory = st.selectbox("Subcategory", get_subcategories(user_id, category))
        acc_dict = {x[1]: x[0] for x in get_accounts(user_id)}
        account = st.selectbox("Account", list(acc_dict.keys()))
        amount = st.number_input("Amount", min_value=0.0)
        notes = st.text_input("Notes")
        if st.button("Save"):
            add_transaction(user_id, date, type_, category, subcategory, acc_dict[account], amount, notes)
            st.success("Saved")

    elif menu == "View Transactions":
        st.subheader("History")
        for txn in get_transactions(user_id):
            col1, col2 = st.columns([6,1])
            col1.write(f"{txn[1]} | {txn[2]} | {txn[3]} → {txn[4]} | ₹{txn[6]:,.0f}")
            if col2.button("Del", key=f"del_{txn[0]}"):
                delete_transaction(txn[0])
                st.rerun()

    elif menu == "Add Account":
        st.subheader("Add Account")
        name = st.text_input("Name")
        type_ = st.selectbox("Type", ["Savings Account", "Cash", "Credit Card", "Investment"])
        balance = st.number_input("Balance")
        include = st.checkbox("Net Worth?", value=True)
        if st.button("Save"):
            add_account(user_id, name, type_, balance, int(include))
            st.success("Added")

    elif menu == "View Accounts":
        for acc in get_accounts(user_id):
            c1, c2 = st.columns([3,1])
            new_bal = c1.number_input(acc[1], value=float(acc[2]), key=f"bal_{acc[0]}")
            if c2.button("Update", key=f"btn_{acc[0]}"):
                update_balance(acc[0], new_bal); st.success("Done")

    elif menu == "Add Category":

        st.subheader("Add Custom Category")

        type_ = st.selectbox("Type", ["Income", "Expense", "Investment", "Transfer"])

        existing_categories = get_categories(user_id, type_)

        category = st.text_input("New Category Name")

        if existing_categories:
            parent_category = st.selectbox("Or Select Existing Category", ["None"] + existing_categories)
        else:
            parent_category = "None"

        subcategory = st.text_input("Subcategory Name")

        if st.button("Save Category"):

            final_category = category if parent_category == "None" else parent_category

            cursor.execute("""
                SELECT 1 FROM categories
                WHERE user_id=? AND category=? AND subcategory=?
            """, (user_id, final_category, subcategory))

            if cursor.fetchone():

                st.error("This category + subcategory already exists.")

            else:

                cursor.execute("""
                    INSERT INTO categories (user_id, category, subcategory, type)
                    VALUES (?, ?, ?, ?)
                """, (user_id, final_category, subcategory, type_))

                conn.commit()

                st.success("Category added successfully.")

    elif menu == "Set Budgets":
        cat = st.selectbox("Category", get_categories(user_id, "Expense"))
        amt = st.number_input("Budget")
        if st.button("Save"):
            set_budget(user_id, cat, amt); st.success("Saved")

    elif menu == "View Budgets":
        for b in get_budgets(user_id): st.write(f"{b[0]} → ₹{b[1]:,.0f}")

    # ================= DASHBOARD =================
    elif menu == "Dashboard":
        st.subheader("📊 Financial Dashboard")

        # COLORS
        main_color = '#6366f1'   # Indigo
        warning_color = '#ef4444' # Warning Red
        budget_color = '#94a3b8'  # Slate

        cursor.execute("SELECT DISTINCT strftime('%Y-%m', date) as m FROM transactions WHERE user_id=? ORDER BY m DESC", (user_id,))
        months = [row[0] for row in cursor.fetchall()]
        if not months:
            st.info("No data yet.")
            st.stop()
        selected_month = st.selectbox("Select Month", months)

        # DATA FETCH
        df = pd.read_sql_query("SELECT * FROM transactions WHERE user_id=? AND strftime('%Y-%m', date)=?", conn, params=(user_id, selected_month))
        
        def get_summary(uid, m):
            cursor.execute("SELECT type, SUM(amount) FROM transactions WHERE user_id=? AND strftime('%Y-%m', date)=? GROUP BY type", (uid, m))
            d = dict(cursor.fetchall())
            return d.get("Income", 0), d.get("Expense", 0), d.get("Investment", 0)

        inc, exp, inv = get_summary(user_id, selected_month)
        sav = inc - exp - inv

        # TREND DELTAS
        idx = months.index(selected_month)
        deltas = {"inc": None, "exp": None}
        if idx < len(months) - 1:
            p_inc, p_exp, _ = get_summary(user_id, months[idx+1])
            deltas['inc'] = inc - p_inc
            deltas['exp'] = exp - p_exp

        # TOP ROW KPIs
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Income", f"₹{inc:,.0f}", delta=f"₹{deltas['inc']:,.0f}" if deltas['inc'] is not None else None)
        c2.metric("Expenses", f"₹{exp:,.0f}", delta=f"₹{deltas['exp']:,.0f}" if deltas['exp'] is not None else None, delta_color="inverse")
        c3.metric("Investments", f"₹{inv:,.0f}")
        c4.metric("Savings", f"₹{sav:,.0f}")

        # BURN RATE SECTION
        st.divider()
        c5, c6, c7 = st.columns(3)
        
        today = datetime.now()
        day_count = today.day if selected_month == today.strftime('%Y-%m') else 30
        daily_burn = exp / day_count
        
        c5.metric("Daily Burn Rate", f"₹{daily_burn:,.0f}", help="Avg daily spend for the selected period.")
        c6.metric("Net Cashflow", f"₹{inc - exp:,.0f}")
        cursor.execute("SELECT SUM(opening_balance) FROM accounts WHERE user_id=? AND include_in_networth=1", (user_id,))
        assets = cursor.fetchone()[0] or 0
        c7.metric("Total Assets", f"₹{assets:,.0f}")

        st.divider()

        # CHARTS (EXACT NUMBERS - NO 1.2k ROUNDING)
        col_l, col_r = st.columns(2)
        with col_l:
            st.subheader("Composition")
            comp_df = pd.DataFrame({"Type": ["Income", "Expense", "Investment", "Savings"], "Amount": [inc, exp, inv, max(0, sav)]})
            st.plotly_chart(px.bar(comp_df, x="Type", y="Amount", color_discrete_sequence=[main_color], text_auto=',.0f').update_layout(template="plotly_dark", plot_bgcolor='rgba(0,0,0,0)'), use_container_width=True)
        
        with col_r:
            st.subheader("Category Breakdown")
            cat_df = df[df["type"].str.lower() == "expense"].groupby("category")["amount"].sum().reset_index()
            if not cat_df.empty:
                st.plotly_chart(px.bar(cat_df, x="category", y="amount", color_discrete_sequence=['#8b5cf6'], text_auto=',.0f').update_layout(template="plotly_dark", plot_bgcolor='rgba(0,0,0,0)'), use_container_width=True)

        st.divider()

        # BUDGET VS ACTUAL (UNIFIED SCALE)
        st.subheader("Budget vs Actual")
        b_df = pd.read_sql_query("""
            SELECT b.category, b.monthly_budget, IFNULL(SUM(t.amount), 0) AS spent
            FROM budgets b
            LEFT JOIN transactions t ON b.category = t.category AND strftime('%Y-%m', t.date) = ? AND b.user_id = t.user_id AND t.type = 'Expense'
            WHERE b.user_id = ? GROUP BY b.category""", conn, params=(selected_month, user_id))

        if not b_df.empty:
            b_df["usage"] = b_df["spent"] / b_df["monthly_budget"]
            
            for _, r in b_df[b_df["usage"] >= 0.9].iterrows():
                if r["usage"] >= 1.0: st.error(f"🚨 CRITICAL: Budget Blown for {r['category']}!")
                else: st.warning(f"⚠️ ALERT: {r['category']} usage at {r['usage']:.0%}")

            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=b_df["category"], 
                y=b_df["spent"], 
                name="Actual Spent", 
                marker_color=[warning_color if x >= 0.9 else main_color for x in b_df["usage"]],
                text=b_df["spent"],
                textposition='auto',
                texttemplate='₹%{text:,.0f}' 
            ))
            fig.add_trace(go.Scatter(
                x=b_df["category"], 
                y=b_df["monthly_budget"], 
                name="Budget Limit", 
                mode='lines+markers', 
                line=dict(color=budget_color, width=4, dash='dot')
            ))

            fig.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', yaxis_title="Amount (₹)", hovermode="x unified")
            st.plotly_chart(fig, use_container_width=True)
            
            b_df["remaining"] = b_df["monthly_budget"] - b_df["spent"]
            st.dataframe(b_df[["category", "monthly_budget", "spent", "remaining"]], use_container_width=True)

        # ================= NEW MATRIX BLOCK =================
        st.divider()
        st.subheader("Account-wise Category Contribution Matrix")

        matrix_df = pd.read_sql_query("""
            SELECT
                t.category,
                a.account_name,
                t.amount
            FROM transactions t
            JOIN accounts a
                ON t.account = a.id
            WHERE t.user_id = ?
              AND strftime('%Y-%m', t.date) = ?
              AND t.type = 'Expense'
        """, conn, params=(user_id, selected_month))

        if not matrix_df.empty:

            pivot_matrix = matrix_df.pivot_table(
                index="category",
                columns="account_name",
                values="amount",
                aggfunc="sum",
                fill_value=0
            )

            account_totals = pivot_matrix.sum(axis=0)
            grand_total = account_totals.sum()

            if grand_total > 0:
                contribution_row = (account_totals / grand_total * 100).round(2)
                pivot_matrix.loc["% Contribution"] = contribution_row

            st.dataframe(
                pivot_matrix.style.format(
                    lambda x: f"{x:.2f}%" if isinstance(x, float) and x <= 100 and "% Contribution" in pivot_matrix.index
                    else f"₹{x:,.0f}"
                ),
                use_container_width=True
            )

        else:
            st.info("No expense data available for this month.")
