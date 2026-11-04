import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime

# Database connection
conn = sqlite3.connect("restaurant.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer TEXT,
    items TEXT,
    total REAL,
    date TEXT
)
""")
conn.commit()

# Restaurant menu
menu = {
    "Burger": 450,
    "Zinger Burger": 550,
    "Pizza": 1200,
    "Chicken Biryani": 350,
    "Chicken Karahi": 1800,
    "French Fries": 250,
    "Cold Drink": 100,
    "Tea": 120
}

cart = []

# Main window
root = tk.Tk()
root.title("Restaurant Management System")
root.geometry("850x650")
root.configure(bg="#f0f0f0")

# Heading
tk.Label(
    root,
    text="RESTAURANT MANAGEMENT SYSTEM",
    font=("Arial", 22, "bold"),
    bg="#263238",
    fg="white",
    pady=15
).pack(fill="x")

# Customer section
customer_frame = tk.Frame(root, bg="#f0f0f0")
customer_frame.pack(pady=15)

tk.Label(
    customer_frame,
    text="Customer Name:",
    font=("Arial", 12, "bold"),
    bg="#f0f0f0"
).grid(row=0, column=0, padx=5)

customer_entry = tk.Entry(customer_frame, font=("Arial", 12), width=25)
customer_entry.grid(row=0, column=1, padx=5)

# Main content
main_frame = tk.Frame(root, bg="#f0f0f0")
main_frame.pack(fill="both", expand=True, padx=20)

# Menu section
menu_frame = tk.LabelFrame(
    main_frame,
    text="Food Menu",
    font=("Arial", 14, "bold"),
    padx=15,
    pady=15
)
menu_frame.pack(side="left", fill="y", padx=10)

tk.Label(menu_frame, text="Select Food", font=("Arial", 11)).pack()

food_var = tk.StringVar()
food_combo = ttk.Combobox(
    menu_frame,
    textvariable=food_var,
    values=list(menu.keys()),
    state="readonly",
    width=22
)
food_combo.pack(pady=8)
food_combo.current(0)

tk.Label(menu_frame, text="Quantity", font=("Arial", 11)).pack()

quantity_var = tk.IntVar(value=1)
quantity_spin = tk.Spinbox(
    menu_frame,
    from_=1,
    to=50,
    textvariable=quantity_var,
    width=10
)
quantity_spin.pack(pady=8)

price_label = tk.Label(
    menu_frame,
    text="Price: Rs. 450",
    font=("Arial", 12, "bold")
)
price_label.pack(pady=10)


def update_price(event=None):
    food = food_var.get()
    if food:
        price_label.config(text=f"Price: Rs. {menu[food]}")


food_combo.bind("<<ComboboxSelected>>", update_price)

# Cart section
cart_frame = tk.LabelFrame(
    main_frame,
    text="Customer Order",
    font=("Arial", 14, "bold"),
    padx=10,
    pady=10
)
cart_frame.pack(side="right", fill="both", expand=True, padx=10)

columns = ("Food", "Price", "Quantity", "Total")

tree = ttk.Treeview(
    cart_frame,
    columns=columns,
    show="headings",
    height=12
)

for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=100)

tree.pack(fill="both", expand=True)

total_label = tk.Label(
    cart_frame,
    text="Total: Rs. 0",
    font=("Arial", 16, "bold"),
    fg="green"
)
total_label.pack(pady=12)


def update_total():
    total = sum(item["total"] for item in cart)
    total_label.config(text=f"Total: Rs. {total}")


def add_to_cart():
    food = food_var.get()

    if not food:
        messagebox.showwarning("Warning", "Please select food")
        return

    try:
        quantity = int(quantity_var.get())
        if quantity < 1:
            raise ValueError
    except (ValueError, tk.TclError):
        messagebox.showerror("Error", "Enter a valid quantity")
        return

    price = menu[food]
    amount = price * quantity

    cart.append({
        "food": food,
        "price": price,
        "quantity": quantity,
        "total": amount
    })

    tree.insert(
        "",
        "end",
        values=(food, price, quantity, amount)
    )

    update_total()


def remove_item():
    selected = tree.selection()

    if not selected:
        messagebox.showwarning("Warning", "Select an item first")
        return

    index = tree.index(selected[0])
    tree.delete(selected[0])
    cart.pop(index)

    update_total()


def clear_order():
    cart.clear()

    for item in tree.get_children():
        tree.delete(item)

    update_total()


def place_order():
    customer = customer_entry.get().strip()

    if not customer:
        messagebox.showwarning("Warning", "Enter customer name")
        return

    if not cart:
        messagebox.showwarning("Warning", "Cart is empty")
        return

    total = sum(item["total"] for item in cart)

    items_text = "\n".join(
        f'{item["food"]} x {item["quantity"]} = Rs. {item["total"]}'
        for item in cart
    )

    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute(
        "INSERT INTO orders (customer, items, total, date) VALUES (?, ?, ?, ?)",
        (customer, items_text, total, date)
    )

    conn.commit()
    order_id = cursor.lastrowid

    receipt = f"""
       RESTAURANT RECEIPT
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

    messagebox.showinfo("Order Receipt", receipt)

    clear_order()
    customer_entry.delete(0, tk.END)


# Buttons
button_frame = tk.Frame(root, bg="#f0f0f0")
button_frame.pack(pady=15)

tk.Button(
    menu_frame,
    text="Add to Cart",
    command=add_to_cart,
    bg="#2e7d32",
    fg="white",
    font=("Arial", 11, "bold"),
    width=18
).pack(pady=10)

tk.Button(
    cart_frame,
    text="Remove Selected Item",
    command=remove_item,
    bg="#e65100",
    fg="white",
    font=("Arial", 10, "bold")
).pack(pady=5)

tk.Button(
    button_frame,
    text="PLACE ORDER",
    command=place_order,
    bg="#1565c0",
    fg="white",
    font=("Arial", 13, "bold"),
    width=18
).pack(side="left", padx=10)

tk.Button(
    button_frame,
    text="CLEAR ORDER",
    command=clear_order,
    bg="#c62828",
    fg="white",
    font=("Arial", 13, "bold"),
    width=18
).pack(side="left", padx=10)


def close_app():
    conn.close()
    root.destroy()


root.protocol("WM_DELETE_WINDOW", close_app)
root.mainloop()
