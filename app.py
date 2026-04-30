import streamlit as st
import psycopg2
from datetime import datetime
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from database import create_tables

# Initialize database tables
create_tables()

# Database connection
conn = psycopg2.connect(
    host=st.secrets["DB_HOST"],
    database=st.secrets["DB_NAME"],
    user=st.secrets["DB_USER"],
    password=st.secrets["DB_PASSWORD"],
    port=st.secrets["DB_PORT"],
    sslmode="require"
)

cursor = conn.cursor()

# ================= PAGE LAYOUT =================
st.set_page_config(layout="wide", page_title="Finance Analytics Pro")

# ================= USER FUNCTIONS =================

def create_user(username, password):
    try:
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (%s, %s)",
            (username, password)
        )
        conn.commit()
        cursor.execute(
            "SELECT id FROM users WHERE username=%s",
            (username,)
        )
        user_id = cursor.fetchone()[0]
        load_default_categories(user_id)
        return True
    except:
        return False

def login_user(username, password):
    cursor.execute(
        "SELECT id FROM users WHERE username=%s AND password=%s",
        (username, password)
    )
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
            WHERE user_id=%s AND category=%s AND subcategory=%s
        """, (user_id, category, subcategory))

        if not cursor.fetchone():
            cursor.execute("""
                INSERT INTO categories (user_id, category, subcategory, type)
                VALUES (%s, %s, %s, %s)
            """, (user_id, category, subcategory, type_))
    conn.commit()

def get_categories(user_id, type_):
    cursor.execute(
        "SELECT DISTINCT category FROM categories WHERE user_id=%s AND type=%s",
        (user_id, type_)
    )
    return [x[0] for x in cursor.fetchall()]

def get_subcategories(user_id, category):
    cursor.execute(
        "SELECT subcategory FROM categories WHERE user_id=%s AND category=%s",
        (user_id, category)
    )
    return [x[0] for x in cursor.fetchall()]

# ================= ACCOUNT FUNCTIONS =================
def get_accounts(user_id):
    cursor.execute(
        "SELECT id, account_name, opening_balance FROM accounts WHERE user_id=%s",
        (user_id,)
    )
    return cursor.fetchall()

def add_account(user_id, name, type_, balance, include_networth):
    cursor.execute("""
        INSERT INTO accounts
        (user_id, account_name, account_type, opening_balance, include_in_networth)
        VALUES (%s, %s, %s, %s, %s)
    """, (user_id, name, type_, balance, include_networth))
    conn.commit()

def update_balance(account_id, new_balance):
    cursor.execute(
        "UPDATE accounts SET opening_balance=%s WHERE id=%s",
        (new_balance, account_id)
    )
    conn.commit()

# ================= TRANSACTION ENGINE =================
def add_transaction(user_id, date, type_, category, subcategory, account_id, amount, notes):
    signed_amount = -amount if type_ in ["Expense", "Investment"] else amount
    cursor.execute("""
        INSERT INTO transactions
        (user_id,date,type,category,subcategory,account,amount,signed_amount,tag,notes,created_at)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """, (user_id,date,type_,category,subcategory,account_id,amount,signed_amount,"",notes,datetime.now()))

    cursor.execute(
        "SELECT opening_balance FROM accounts WHERE id=%s",
        (account_id,)
    )
    balance = cursor.fetchone()[0]
    update_balance(account_id, balance + signed_amount)
    conn.commit()

def delete_transaction(transaction_id):
    cursor.execute(
        "SELECT account, signed_amount FROM transactions WHERE id=%s",
        (transaction_id,)
    )
    account_id, signed_amount = cursor.fetchone()
    
    cursor.execute(
        "SELECT opening_balance FROM accounts WHERE id=%s",
        (account_id,)
    )
    balance = cursor.fetchone()[0]
    update_balance(account_id, balance - signed_amount)
    
    cursor.execute(
        "DELETE FROM transactions WHERE id=%s",
        (transaction_id,)
    )
    conn.commit()

def get_transactions(user_id):
    cursor.execute("""
        SELECT id, date, type, category, subcategory, account, amount, notes
        FROM transactions
        WHERE user_id=%s
        ORDER BY date DESC
    """, (user_id,))
    return cursor.fetchall()

# ================= BUDGET FUNCTIONS =================
def set_budget(user_id, category, amount):
    cursor.execute(
        "SELECT id FROM budgets WHERE user_id=%s AND category=%s",
        (user_id, category)
    )
    if cursor.fetchone():
        cursor.execute("""
            UPDATE budgets
            SET monthly_budget=%s
            WHERE user_id=%s AND category=%s
        """, (amount, user_id, category))
    else:
        cursor.execute("""
            INSERT INTO budgets (user_id, category, monthly_budget)
            VALUES (%s, %s, %s)
        """, (user_id, category, amount))
    conn.commit()

def get_budgets(user_id):
    cursor.execute(
        "SELECT category, monthly_budget FROM budgets WHERE user_id=%s",
        (user_id,)
    )
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
    
    # HORIZONTAL NAVIGATION BAR (MAIN BODY)
    menu = st.radio(
        "",
        ["Dashboard", "Transactions", "Accounts", "Categories", "Budgets"],
        horizontal=True
    )

    st.divider()

    # ================= TRANSACTIONS HUB =================
    if menu == "Transactions":
        tab1, tab2 = st.tabs(["Add Transaction", "View Transactions"])

        with tab1:
            st.subheader("Add Transaction")
            c1, c2 = st.columns(2)
            with c1:
                date = st.date_input("Date")
                type_ = st.selectbox("Type", ["Income", "Expense", "Investment", "Transfer"])
            with c2:
                if type_ == "Transfer":
                    category, subcategory = "Transfer", "Transfer Out"
                    st.info("Category set to Transfer for internal movement.")
                else:
                    category = st.selectbox("Category", get_categories(user_id, type_))
                    subcategory = st.selectbox("Subcategory", get_subcategories(user_id, category))

            acc_dict = {x[1]: x[0] for x in get_accounts(user_id)}
            
            if type_ == "Transfer":
                col_a, col_b = st.columns(2)
                from_account = col_a.selectbox("From Account", list(acc_dict.keys()), key="from_account")
                to_account = col_b.selectbox("To Account", [acc for acc in acc_dict.keys() if acc != from_account], key="to_account")
            else:
                account = st.selectbox("Account", list(acc_dict.keys()))

            amount = st.number_input("Amount", min_value=0.0)
            notes = st.text_input("Notes")

            if st.button("Save"):
                if type_ == "Transfer":
                    from_id, to_id = acc_dict[from_account], acc_dict[to_account]
                    # Deduct from source
                    add_transaction(user_id, date, "Expense", "Transfer", "Transfer Out", from_id, amount, f"Transfer to {to_account} | {notes}")
                    # Add to destination
                    add_transaction(user_id, date, "Income", "Transfer", "Transfer In", to_id, amount, f"Transfer from {from_account} | {notes}")
                    st.success("Transfer completed")
                else:
                    add_transaction(user_id, date, type_, category, subcategory, acc_dict[account], amount, notes)
                    st.success("Saved")

        with tab2:
            st.subheader("Transaction History")
            for txn in get_transactions(user_id):
                col1, col2 = st.columns([6,1])
                col1.write(f"{txn[1]} | {txn[2]} | {txn[3]} → {txn[4]} | ₹{txn[6]:,.0f} ({txn[7]})")
                if col2.button("Del", key=f"del_{txn[0]}"):
                    delete_transaction(txn[0])
                    st.rerun()

    # ================= ACCOUNTS HUB =================
    elif menu == "Accounts":
        tab1, tab2 = st.tabs(["Add Account", "View Accounts"])

        with tab1:
            st.subheader("Add Account")
            name = st.text_input("Name")
            type_acc = st.selectbox("Type", ["Savings Account", "Cash", "Credit Card", "Investment"])
            balance = st.number_input("Balance")
            include = st.checkbox("Net Worth?", value=True)
            if st.button("Save Account"):
                add_account(user_id, name, type_acc, balance, int(include))
                st.success("Added")

        with tab2:
            st.subheader("Account Balances")
            for acc in get_accounts(user_id):
                c1, c2 = st.columns([3,1])
                new_bal = c1.number_input(acc[1], value=float(acc[2]), key=f"bal_{acc[0]}")
                if c2.button("Update", key=f"btn_{acc[0]}"):
                    update_balance(acc[0], new_bal)
                    st.success("Updated")

    # ================= CATEGORIES HUB =================
    elif menu == "Categories":
        st.subheader("Add Custom Category")
        type_cat = st.selectbox("Type", ["Income", "Expense", "Investment", "Transfer"])
        existing_categories = get_categories(user_id, type_cat)
        category_name = st.text_input("New Category Name")
        if existing_categories:
            parent_category = st.selectbox("Or Select Existing Category", ["None"] + existing_categories)
        else:
            parent_category = "None"
        subcategory_name = st.text_input("Subcategory Name")
        if st.button("Save Category"):
            final_category = category_name if parent_category == "None" else parent_category
            cursor.execute("""
                SELECT 1 FROM categories
                WHERE user_id=%s AND category=%s AND subcategory=%s
            """, (user_id, final_category, subcategory_name))
            if cursor.fetchone():
                st.error("This category + subcategory already exists.")
            else:
                cursor.execute("""
                    INSERT INTO categories (user_id, category, subcategory, type)
                    VALUES (%s, %s, %s, %s)
                """, (user_id, final_category, subcategory_name, type_cat))
                conn.commit()
                st.success("Category added successfully.")

    # ================= BUDGETS HUB =================
    elif menu == "Budgets":
        tab1, tab2 = st.tabs(["Set Budget", "View Budgets"])

        with tab1:
            cat_b = st.selectbox("Category", get_categories(user_id, "Expense"))
            amt_b = st.number_input("Budget")
            if st.button("Save Budget"):
                set_budget(user_id, cat_b, amt_b)
                st.success("Saved")

        with tab2:
            st.subheader("Budget Overview")
            for b in get_budgets(user_id):
                st.write(f"{b[0]} → ₹{b[1]:,.0f}")

    # ================= DASHBOARD =================
    elif menu == "Dashboard":
        st.subheader("📊 Financial Dashboard")
        main_color = '#6366f1'
        warning_color = '#ef4444'
        budget_color = '#94a3b8'

        cursor.execute("SELECT DISTINCT TO_CHAR(date, 'YYYY-MM') as m FROM transactions WHERE user_id=%s ORDER BY m DESC", (user_id,))
        months = [row[0] for row in cursor.fetchall()]
        if not months:
            st.info("No data yet.")
            st.stop()
        selected_month = st.selectbox("Select Month", months)

        # FIXED SQL: Exclude 'Transfer' category from summary totals to prevent metric inflation
        def get_summary_clean(uid, m):
            cursor.execute("""
                SELECT type, SUM(amount) 
                FROM transactions 
                WHERE user_id=%s AND TO_CHAR(date, 'YYYY-MM')=%s AND category != 'Transfer'
                GROUP BY type
            """, (uid, m))
            d = dict(cursor.fetchall())
            return d.get("Income", 0), d.get("Expense", 0), d.get("Investment", 0)

        inc, exp, inv = get_summary_clean(user_id, selected_month)
        sav = inc - exp - inv

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Income (Net)", f"₹{inc:,.0f}")
        c2.metric("Expenses (Net)", f"₹{exp:,.0f}")
        c3.metric("Investments", f"₹{inv:,.0f}")
        c4.metric("Savings", f"₹{sav:,.0f}")

        # Dataframes excluding Transfers for visualization
        df_clean = pd.read_sql_query("""
            SELECT * FROM transactions 
            WHERE user_id=%s AND TO_CHAR(date, 'YYYY-MM')=%s AND category != 'Transfer'
        """, conn, params=(user_id, selected_month))
        
        st.divider()
        col_l, col_r = st.columns(2)
        with col_l:
            st.subheader("Composition (Excl. Transfers)")
            comp_df = pd.DataFrame({"Type": ["Income", "Expense", "Investment"], "Amount": [inc, exp, inv]})
            st.plotly_chart(px.bar(comp_df, x="Type", y="Amount", color_discrete_sequence=[main_color], text_auto=',.0f').update_layout(template="plotly_dark", plot_bgcolor='rgba(0,0,0,0)'), use_container_width=True)
        with col_r:
            st.subheader("Category Breakdown")
            cat_df = df_clean[df_clean["type"].str.lower() == "expense"].groupby("category")["amount"].sum().reset_index()
            if not cat_df.empty:
                st.plotly_chart(px.bar(cat_df, x="category", y="amount", color_discrete_sequence=['#8b5cf6'], text_auto=',.0f').update_layout(template="plotly_dark", plot_bgcolor='rgba(0,0,0,0)'), use_container_width=True)

        # ================= SUBCATEGORY ANALYSIS =================
        st.divider()
        st.subheader("Subcategory-wise Expense Analysis")
        sub_df = df_clean[df_clean["type"].str.lower() == "expense"]
        if not sub_df.empty:
            selected_category = st.selectbox("Select Category for Detailed Analysis", sorted(sub_df["category"].unique()))
            subcategory_df = sub_df[sub_df["category"] == selected_category]
            if not subcategory_df.empty:
                sub_summary = subcategory_df.groupby("subcategory")["amount"].sum().reset_index()
                st.plotly_chart(px.pie(sub_summary, names="subcategory", values="amount", title=f"Subcategory Breakdown for {selected_category}", hole=0.4).update_traces(textinfo="percent+label"), use_container_width=True)
            else:
                st.info("No subcategory data available.")
        else:
            st.info("No expense data available for this month.")

        # ================= BUDGET VS ACTUAL =================
        st.divider()
        st.subheader("Budget vs Actual")
        b_df = pd.read_sql_query("""
            SELECT b.category, b.monthly_budget, COALESCE(SUM(t.amount), 0) AS spent
            FROM budgets b
            LEFT JOIN transactions t ON b.category = t.category AND TO_CHAR(t.date, 'YYYY-MM') = %s AND b.user_id = t.user_id AND t.type = 'Expense'
            WHERE b.user_id = %s GROUP BY b.category, b.monthly_budget""", conn, params=(selected_month, user_id))

        if not b_df.empty:
            b_df["usage"] = b_df["spent"] / b_df["monthly_budget"]
            for _, r in b_df[b_df["usage"] >= 0.9].iterrows():
                if r["usage"] >= 1.0: st.error(f"🚨 CRITICAL: Budget Blown for {r['category']}!")
                else: st.warning(f"⚠️ ALERT: {r['category']} usage at {r['usage']:.0%}")
            fig = go.Figure()
            fig.add_trace(go.Bar(x=b_df["category"], y=b_df["spent"], name="Actual Spent", marker_color=[warning_color if x >= 0.9 else main_color for x in b_df["usage"]], text=b_df["spent"], textposition='auto', texttemplate='₹%{text:,.0f}'))
            fig.add_trace(go.Scatter(x=b_df["category"], y=b_df["monthly_budget"], name="Budget Limit", mode='lines+markers', line=dict(color=budget_color, width=4, dash='dot')))
            fig.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', yaxis_title="Amount (₹)", hovermode="x unified")
            st.plotly_chart(fig, use_container_width=True)
            b_df["remaining"] = b_df["monthly_budget"] - b_df["spent"]
            st.dataframe(b_df[["category", "monthly_budget", "spent", "remaining"]], use_container_width=True)

        # ================= ACCOUNT ALLOCATION MATRIX (FIXED) =================
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
            WHERE t.user_id = %s
              AND TO_CHAR(t.date, 'YYYY-MM') = %s
              AND t.type = 'Expense'
              AND t.category != 'Transfer'
        """, conn, params=(user_id, selected_month))

        if not matrix_df.empty:
            pivot_matrix = matrix_df.pivot_table(index="category", columns="account_name", values="amount", aggfunc="sum", fill_value=0)
            account_totals = pivot_matrix.sum(axis=0)
            grand_total = account_totals.sum()
            if grand_total > 0:
                contribution_row = (account_totals / grand_total * 100).round(2)
                pivot_matrix.loc["% Contribution"] = contribution_row

            # Convert entire dataframe safely to string display format
            display_df = pivot_matrix.astype(object)

            for col in display_df.columns:
                display_df[col] = display_df[col].apply(
                    lambda x: f"{x:.2f}%" if display_df.index[display_df[col] == x][0] == "% Contribution"
                    else f"₹{x:,.0f}"
                )

            # Fix contribution row formatting separately (cleaner + safer)
            if "% Contribution" in display_df.index:
                for col in display_df.columns:
                    display_df.loc["% Contribution", col] = f"{pivot_matrix.loc['% Contribution', col]:.2f}%"

            st.dataframe(display_df, use_container_width=True)
        else:
            st.info("No expense data available for this month.")
