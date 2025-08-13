import tkinter as tk
from tkinter import messagebox, filedialog
import pandas as pd
from tkinter import ttk
from datetime import datetime

# Load product data from Excel
df = pd.read_excel("products.xlsx")

# Create main window
root = tk.Tk()
root.title("Advanced Billing Software")
root.geometry("1400x1000")
root.config(padx=50, pady=50)

# Define variables
cart = []  # List to store multiple products
total_var = tk.StringVar(value="0.00")
balance_var = tk.StringVar(value="0.00")
bill_text = tk.StringVar()
product_var = tk.StringVar()
price_var = tk.StringVar()
quantity_var = tk.IntVar(value=1)
discount_var = tk.DoubleVar(value=0)
paid_amount_var = tk.DoubleVar(value=0)

# Function to auto-fill price based on product name
def update_price(*args):
    product = product_var.get().strip().lower()
    match = df[df['Product'].str.lower() == product]
    if not match.empty:
        price_var.set(str(match.iloc[0]['Price']))
    else:
        price_var.set("")

# Function to add product to cart
def add_to_cart():
    try:
        product = product_var.get().strip()
        price = float(price_var.get())
        qty = quantity_var.get()
        if not product or qty <= 0:
            messagebox.showerror("Input Error", "Please select a valid product and quantity.", parent=root)
            return
        cart.append({"Product": product, "Price": price, "Quantity": qty})
        update_cart_display()
        clear_inputs()
    except ValueError:
        messagebox.showerror("Input Error", "Please enter valid price and quantity.", parent=root)

# Function to clear input fields
def clear_inputs():
    product_var.set("")
    price_var.set("")
    quantity_var.set(1)
    product_dropdown.set("Type or Select Product")

# Function to update cart display
def update_cart_display():
    cart_text = "\n".join([f"{item['Product']} - Qty: {item['Quantity']} - ₹{item['Price']*item['Quantity']:.2f}" for item in cart])
    cart_display.config(state="normal")
    cart_display.delete(1.0, tk.END)
    cart_display.insert(tk.END, cart_text or "No items in cart")
    cart_display.config(state="disabled")

# Function to calculate totals
def calculate_total():
    try:
        discount = discount_var.get()
        paid = paid_amount_var.get()
        if discount < 0 or paid < 0:
            messagebox.showerror("Input Error", "Discount and paid amount cannot be negative.", parent=root)
            return

        subtotal = sum(item["Price"] * item["Quantity"] for item in cart)
        discounted_total = subtotal - (subtotal * discount / 100)
        balance = paid - discounted_total

        total_var.set(f"{discounted_total:.2f}")
        balance_var.set(f"{balance:.2f}")

        # Generate bill with date and time
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        bill = (
            f"{'='*40}\n"
            f"{'BILL RECEIPT':^40}\n"
            f"{'='*40}\n"
            f"Date & Time: {current_time}\n"
            f"{'-'*40}\n"
        )
        for item in cart:
            bill += (
                f"Product    : {item['Product']}\n"
                f"Quantity   : {item['Quantity']}\n"
                f"Price/unit : ₹{item['Price']:.2f}\n"
                f"Subtotal   : ₹{item['Price'] * item['Quantity']:.2f}\n"
                f"{'-'*40}\n"
            )
        bill += (
            f"Discount   : {discount:.2f}%\n"
            f"Total      : ₹{discounted_total:.2f}\n"
            f"Paid Amount: ₹{paid:.2f}\n"
            f"Balance    : ₹{balance:.2f}\n"
            f"{'='*40}\n"
            f"Thank you for your purchase!\n"
        )
        bill_text.set(bill)
    except Exception as e:
        messagebox.showerror("Calculation Error", str(e), parent=root)

# Function to print (save as .txt file)
def print_bill():
    if not cart:
        messagebox.showerror("Error", "Cart is empty. Add products to generate a bill.", parent=root)
        return
    file = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
    if file:
        with open(file, "w") as f:
            f.write(bill_text.get())
        messagebox.showinfo("Success", "Bill saved successfully!", parent=root)

# Function to reset all fields
def reset_all():
    cart.clear()
    update_cart_display()
    clear_inputs()
    discount_var.set(0)
    paid_amount_var.set(0)
    total_var.set("0.00")
    balance_var.set("0.00")
    bill_text.set("")

# Configure larger dialog boxes
root.option_add("*Dialog.msg.font", "Helvetica 12")
root.option_add("*Dialog.msg.width", 40)

# UI Layout
main_frame = ttk.Frame(root)
main_frame.pack(fill="both", expand=True)

# Left frame for inputs
input_frame = ttk.LabelFrame(main_frame, text="Product Details", padding=10)
input_frame.grid(row=0, column=0, padx=10, pady=10, sticky="n")

ttk.Label(input_frame, text="Product Name").pack()
product_entry = ttk.Entry(input_frame, textvariable=product_var)
product_entry.pack(pady=5)
product_var.trace_add("write", update_price)
product_list = df['Product'].tolist()

product_dropdown = ttk.Combobox(input_frame, textvariable=product_var)
product_dropdown['values'] = product_list
product_dropdown.set("Type or Select Product")
product_dropdown.pack(pady=5)

def on_keyrelease(event):
    value = product_dropdown.get().lower()
    filtered = [item for item in product_list if value in item.lower()]
    product_dropdown['values'] = filtered

product_dropdown.bind("<KeyRelease>", on_keyrelease)
product_dropdown.bind("6912ComboboxSelected>>", update_price)

ttk.Label(input_frame, text="Price (₹)").pack()
ttk.Entry(input_frame, textvariable=price_var, state="readonly").pack(pady=5)

ttk.Label(input_frame, text="Quantity").pack()
ttk.Entry(input_frame, textvariable=quantity_var).pack(pady=5)

ttk.Button(input_frame, text="Add to Cart", command=add_to_cart).pack(pady=10)

# Right frame for cart and totals
cart_frame = ttk.LabelFrame(main_frame, text="Cart & Billing", padding=10)
cart_frame.grid(row=0, column=1, padx=10, pady=10, sticky="n")

cart_display = tk.Text(cart_frame, height=10, width=40, state="disabled")
cart_display.pack(pady=5)

ttk.Label(cart_frame, text="Discount (%)").pack()
ttk.Entry(cart_frame, textvariable=discount_var).pack(pady=5)

ttk.Label(cart_frame, text="Paid Amount (₹)").pack()
ttk.Entry(cart_frame, textvariable=paid_amount_var).pack(pady=5)

ttk.Button(cart_frame, text="Calculate Total", command=calculate_total).pack(pady=5)

ttk.Label(cart_frame, text="Total Amount (₹)").pack()
ttk.Entry(cart_frame, textvariable=total_var, state="readonly").pack(pady=5)

ttk.Label(cart_frame, text="Balance (₹)").pack()
ttk.Entry(cart_frame, textvariable=balance_var, state="readonly").pack(pady=5)

ttk.Label(cart_frame, text="Bill Summary").pack(pady=10)
tk.Message(cart_frame, textvariable=bill_text, width=500, bg="#f0f0f0").pack(pady=5)

# Button frame
button_frame = ttk.Frame(main_frame)
button_frame.grid(row=1, column=0, columnspan=2, pady=20)

ttk.Button(button_frame, text="Print Bill", command=print_bill).pack(side="left", padx=10)
ttk.Button(button_frame, text="Reset", command=reset_all).pack(side="left", padx=10)

root.mainloop()