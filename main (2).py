import sqlite3
from datetime import datetime

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Restaurant Management System", page_icon="🍽️", layout="wide")

# ---------------- Database ----------------
@st.cache_resource
def get_connection():
    conn = sqlite3.connect("restaurant.db", check_same_thread=False)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer TEXT,
            items TEXT,
            total REAL,
            date TEXT
        )
        """
    )
    conn.commit()
    return conn


conn = get_connection()

# ---------------- Menu ----------------
MENU = {
    "Burger": 450,
    "Zinger Burger": 550,
    "Pizza": 1200,
    "Chicken Biryani": 350,
    "Chicken Karahi": 1800,
    "French Fries": 250,
    "Cold Drink": 100,
    "Tea": 120,
}

# ---------------- Session state ----------------
if "cart" not in st.session_state:
    st.session_state.cart = []
if "receipt" not in st.session_state:
    st.session_state.receipt = None
if "message" not in st.session_state:
    st.session_state.message = None


def cart_total():
    return sum(item["total"] for item in st.session_state.cart)


# ---------------- Callbacks ----------------
def add_to_cart():
    food = st.session_state.food
    qty = int(st.session_state.qty)
    price = MENU[food]
    st.session_state.cart.append(
        {"food": food, "price": price, "quantity": qty, "total": price * qty}
    )
    st.session_state.receipt = None


def remove_item(index):
    if 0 <= index < len(st.session_state.cart):
        st.session_state.cart.pop(index)


def clear_order():
    st.session_state.cart = []


def place_order():
    customer = st.session_state.customer.strip()
    cart = st.session_state.cart

    if not customer:
        st.session_state.message = ("warning", "Please enter customer name")
        return
    if not cart:
        st.session_state.message = ("warning", "Cart is empty")
        return

    total = cart_total()
    items_text = "\n".join(
        f'{i["food"]} x {i["quantity"]} = Rs. {i["total"]}' for i in cart
    )
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cur = conn.execute(
        "INSERT INTO orders (customer, items, total, date) VALUES (?, ?, ?, ?)",
        (customer, items_text, total, date),
    )
    conn.commit()
    order_id = cur.lastrowid

    st.session_state.receipt = f"""       RESTAURANT RECEIPT
--------------------------------
Order Number: {order_id}
Customer: {customer}
Date: {date}
--------------------------------
{items_text}
--------------------------------
TOTAL: Rs. {total}
--------------------------------
     Thank You! Visit Again
"""
    st.session_state.cart = []
    st.session_state.customer = ""
    st.session_state.message = ("success", "Order placed successfully!")


# ---------------- UI ----------------
st.markdown(
    "<h1 style='text-align:center; background:#263238; color:white; padding:15px; "
    "border-radius:8px;'>RESTAURANT MANAGEMENT SYSTEM</h1>",
    unsafe_allow_html=True,
)

tab_order, tab_history = st.tabs(["🛒 New Order", "📜 Order History"])

with tab_order:
    st.text_input("Customer Name", key="customer")

    left, right = st.columns([1, 2], gap="large")

    with left:
        st.subheader("Food Menu")
        st.selectbox("Select Food", list(MENU.keys()), key="food")
        st.number_input("Quantity", min_value=1, max_value=50, value=1, step=1, key="qty")
        st.markdown(f"### Price: Rs. {MENU[st.session_state.food]}")
        st.button("Add to Cart", on_click=add_to_cart, type="primary", use_container_width=True)

    with right:
        st.subheader("Customer Order")
        cart = st.session_state.cart

        if cart:
            header = st.columns([3, 2, 2, 2, 1])
            for col, name in zip(header, ["Food", "Price", "Qty", "Total", ""]):
                col.markdown(f"**{name}**")

            for idx, item in enumerate(cart):
                row = st.columns([3, 2, 2, 2, 1])
                row[0].write(item["food"])
                row[1].write(item["price"])
                row[2].write(item["quantity"])
                row[3].write(item["total"])
                row[4].button("❌", key=f"rm_{idx}", on_click=remove_item, args=(idx,))
        else:
            st.info("Cart is empty. Add items from the menu.")

        st.markdown(f"## Total: Rs. {cart_total()}")

        b1, b2 = st.columns(2)
        b1.button("PLACE ORDER", on_click=place_order, type="primary", use_container_width=True)
        b2.button("CLEAR ORDER", on_click=clear_order, use_container_width=True)

    # Messages and receipt
    if st.session_state.message:
        kind, text = st.session_state.message
        getattr(st, kind)(text)
        st.session_state.message = None

    if st.session_state.receipt:
        st.subheader("Order Receipt")
        st.code(st.session_state.receipt, language=None)

with tab_history:
    st.subheader("Previous Orders")
    df = pd.read_sql_query(
        "SELECT id AS 'Order No', customer AS Customer, items AS Items, "
        "total AS Total, date AS Date FROM orders ORDER BY id DESC",
        conn,
    )
    if df.empty:
        st.info("No orders yet.")
    else:
        st.dataframe(df, use_container_width=True, hide_index=True)
