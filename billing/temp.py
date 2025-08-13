import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime
import sqlite3
import os
from ttkwidgets.autocomplete import AutocompleteCombobox
import tempfile
from tkinter import font as tkfont

class BillingSystem:
    def __init__(self, root):
        self.root = root
        self.root.geometry('1200x700')
        self.root.title('Retail Billing System')
        self.root.configure(bg='#f0f0f0')
        
        # Setup database
        self.setup_database()
        
        # Variables
        self.customer_name = tk.StringVar()
        self.customer_contact = tk.StringVar()
        self.search_product = tk.StringVar()
        self.product_name = tk.StringVar()
        self.product_price = tk.DoubleVar()
        self.product_quantity = tk.IntVar()
        self.product_quantity.set(1)
        self.subtotal = tk.DoubleVar()
        self.tax = tk.DoubleVar()
        self.total = tk.DoubleVar()
        self.paid_amount = tk.DoubleVar()
        self.balance = tk.DoubleVar()
        
        # Cart data
        self.cart = []
        
        # Sample products (in real application, these would come from a database)
        self.add_sample_products()
        
        # Load product names for autocomplete
        self.product_list = self.get_all_products()
        
        # Create UI
        self.create_widgets()
        
        # Bindings
        self.product_search_entry.bind('<KeyRelease>', self.update_product_list)
        self.root.bind('<Return>', lambda event: self.add_to_cart())
    
    def setup_database(self):
        # Create a connection to the database (or create it if it doesn't exist)
        self.conn = sqlite3.connect('billing_system.db')
        self.cursor = self.conn.cursor()
        
        # Create products table if it doesn't exist
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY,
                name TEXT UNIQUE,
                price REAL
            )
        ''')
        
        # Create orders table if it doesn't exist
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY,
                customer_name TEXT,
                customer_contact TEXT,
                date TEXT,
                total_amount REAL
            )
        ''')
        
        # Create order_items table if it doesn't exist
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS order_items (
                id INTEGER PRIMARY KEY,
                order_id INTEGER,
                product_name TEXT,
                price REAL,
                quantity INTEGER,
                total REAL,
                FOREIGN KEY (order_id) REFERENCES orders (id)
            )
        ''')
        
        self.conn.commit()
    
    def add_sample_products(self):
        sample_products = [
            ('Pen', 10.0),
            ('Pencil', 5.0),
            ('Notebook', 25.0),
            ('Eraser', 3.0),
            ('Ruler', 15.0),
            ('Sharpener', 8.0),
            ('Stapler', 45.0),
            ('Paper Clips', 12.0),
            ('Highlighter', 18.0),
            ('Calculator', 120.0),
            ('Scissors', 35.0),
            ('Glue Stick', 22.0),
            ('Paper Ream', 150.0),
            ('Marker', 30.0),
            ('Sticky Notes', 40.0)
        ]
        
        # Add sample products to the database if they don't exist
        for name, price in sample_products:
            try:
                self.cursor.execute(
                    "INSERT INTO products (name, price) VALUES (?, ?)",
                    (name, price)
                )
            except sqlite3.IntegrityError:
                # Product already exists, skip
                pass
        
        self.conn.commit()
    
    def get_all_products(self):
        self.cursor.execute("SELECT name FROM products")
        products = [row[0] for row in self.cursor.fetchall()]
        return products
    
    def get_product_price(self, product_name):
        self.cursor.execute("SELECT price FROM products WHERE name = ?", (product_name,))
        result = self.cursor.fetchone()
        if result:
            return result[0]
        return 0.0
    
    def create_widgets(self):
        # Title
        title_font = tkfont.Font(family="Helvetica", size=18, weight="bold")
        title = tk.Label(self.root, text="Retail Billing System", font=title_font, bg='#f0f0f0', fg='#333333')
        title.pack(pady=10)
        
        # Main frame
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Left frame - Customer Info & Product Selection
        left_frame = tk.LabelFrame(main_frame, text="Customer & Product", font=("Helvetica", 12), bg='#f0f0f0', fg='#333333')
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Customer Information Section
        customer_frame = tk.Frame(left_frame, bg='#f0f0f0')
        customer_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(customer_frame, text="Customer Name:", bg='#f0f0f0', fg='#333333').grid(row=0, column=0, sticky=tk.W, pady=5)
        tk.Entry(customer_frame, textvariable=self.customer_name, width=30).grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(customer_frame, text="Customer Contact:", bg='#f0f0f0', fg='#333333').grid(row=1, column=0, sticky=tk.W, pady=5)
        tk.Entry(customer_frame, textvariable=self.customer_contact, width=30).grid(row=1, column=1, padx=5, pady=5)
        
        # Product Selection Section
        product_frame = tk.LabelFrame(left_frame, text="Product Selection", font=("Helvetica", 11), bg='#f0f0f0', fg='#333333')
        product_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tk.Label(product_frame, text="Search Product:", bg='#f0f0f0', fg='#333333').grid(row=0, column=0, sticky=tk.W, pady=5)
        
        self.product_search_entry = AutocompleteCombobox(
            product_frame, 
            textvariable=self.search_product,
            completevalues=self.product_list,
            width=28
        )
        self.product_search_entry.grid(row=0, column=1, padx=5, pady=5)
        self.product_search_entry.focus()
        
        tk.Label(product_frame, text="Quantity:", bg='#f0f0f0', fg='#333333').grid(row=1, column=0, sticky=tk.W, pady=5)
        quantity_entry = tk.Entry(product_frame, textvariable=self.product_quantity, width=10)
        quantity_entry.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        add_btn = tk.Button(product_frame, text="Add to Cart", command=self.add_to_cart, bg='#4CAF50', fg='white', padx=10)
        add_btn.grid(row=2, column=0, columnspan=2, pady=10)
        
        # Right frame - Bill and Cart
        right_frame = tk.Frame(main_frame, bg='#f0f0f0')
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Cart Section
        cart_frame = tk.LabelFrame(right_frame, text="Shopping Cart", font=("Helvetica", 12), bg='#f0f0f0', fg='#333333')
        cart_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Scrollable Treeview for cart items
        self.cart_treeview_frame = tk.Frame(cart_frame)
        self.cart_treeview_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Scrollbar for Treeview
        tree_scroll = tk.Scrollbar(self.cart_treeview_frame)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Treeview configuration
        self.cart_treeview = ttk.Treeview(
            self.cart_treeview_frame,
            columns=("Product", "Price", "Quantity", "Total"),
            show="headings",
            yscrollcommand=tree_scroll.set
        )
        self.cart_treeview.pack(fill=tk.BOTH, expand=True)
        tree_scroll.config(command=self.cart_treeview.yview)
        
        # Configure treeview columns
        self.cart_treeview.heading("Product", text="Product")
        self.cart_treeview.heading("Price", text="Price")
        self.cart_treeview.heading("Quantity", text="Quantity")
        self.cart_treeview.heading("Total", text="Total")
        
        self.cart_treeview.column("Product", width=150)
        self.cart_treeview.column("Price", width=70, anchor=tk.E)
        self.cart_treeview.column("Quantity", width=70, anchor=tk.CENTER)
        self.cart_treeview.column("Total", width=100, anchor=tk.E)
        
        # Button to remove selected item
        remove_btn = tk.Button(cart_frame, text="Remove Item", command=self.remove_item, bg='#f44336', fg='white', padx=10)
        remove_btn.pack(pady=5)
        
        # Billing section
        bill_frame = tk.LabelFrame(right_frame, text="Billing Summary", font=("Helvetica", 12), bg='#f0f0f0', fg='#333333')
        bill_frame.pack(fill=tk.BOTH, padx=10, pady=10)
        
        # Summary Frame
        summary_frame = tk.Frame(bill_frame, bg='#f0f0f0')
        summary_frame.pack(fill=tk.X, pady=5)
        
        # Summary Labels and Values
        tk.Label(summary_frame, text="Subtotal:", font=("Helvetica", 10, "bold"), bg='#f0f0f0', fg='#333333').grid(row=0, column=0, sticky=tk.W, padx=10, pady=3)
        tk.Label(summary_frame, textvariable=tk.StringVar(value="₹ 0.00"), font=("Helvetica", 10), bg='#f0f0f0', fg='#333333').grid(row=0, column=1, sticky=tk.E, padx=10, pady=3)
        self.subtotal_label = tk.Label(summary_frame, textvariable=self.format_currency(self.subtotal), font=("Helvetica", 10), bg='#f0f0f0', fg='#333333')
        self.subtotal_label.grid(row=0, column=1, sticky=tk.E, padx=10, pady=3)
        
        tk.Label(summary_frame, text="Tax (5%):", font=("Helvetica", 10, "bold"), bg='#f0f0f0', fg='#333333').grid(row=1, column=0, sticky=tk.W, padx=10, pady=3)
        self.tax_label = tk.Label(summary_frame, textvariable=self.format_currency(self.tax), font=("Helvetica", 10), bg='#f0f0f0', fg='#333333')
        self.tax_label.grid(row=1, column=1, sticky=tk.E, padx=10, pady=3)
        
        separator = ttk.Separator(summary_frame, orient='horizontal')
        separator.grid(row=2, column=0, columnspan=2, sticky=tk.EW, padx=10, pady=5)
        
        tk.Label(summary_frame, text="Total:", font=("Helvetica", 12, "bold"), bg='#f0f0f0', fg='#333333').grid(row=3, column=0, sticky=tk.W, padx=10, pady=3)
        self.total_label = tk.Label(summary_frame, textvariable=self.format_currency(self.total), font=("Helvetica", 12, "bold"), bg='#f0f0f0', fg='#333333')
        self.total_label.grid(row=3, column=1, sticky=tk.E, padx=10, pady=3)
        
        # Payment frame
        payment_frame = tk.Frame(bill_frame, bg='#f0f0f0')
        payment_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(payment_frame, text="Paid Amount:", font=("Helvetica", 10, "bold"), bg='#f0f0f0', fg='#333333').grid(row=0, column=0, sticky=tk.W, padx=10, pady=3)
        tk.Entry(payment_frame, textvariable=self.paid_amount, width=15).grid(row=0, column=1, sticky=tk.E, padx=10, pady=3)
        
        calculate_btn = tk.Button(payment_frame, text="Calculate", command=self.calculate_balance, bg='#2196F3', fg='white', padx=5)
        calculate_btn.grid(row=0, column=2, padx=5, pady=3)
        
        tk.Label(payment_frame, text="Balance:", font=("Helvetica", 10, "bold"), bg='#f0f0f0', fg='#333333').grid(row=1, column=0, sticky=tk.W, padx=10, pady=3)
        self.balance_label = tk.Label(payment_frame, textvariable=self.format_currency(self.balance), font=("Helvetica", 10), bg='#f0f0f0', fg='#333333')
        self.balance_label.grid(row=1, column=1, sticky=tk.E, padx=10, pady=3)
        
        # Action Buttons
        button_frame = tk.Frame(bill_frame, bg='#f0f0f0')
        button_frame.pack(fill=tk.X, pady=10)
        
        # Action buttons
        clear_btn = tk.Button(button_frame, text="Clear", command=self.clear_all, bg='#FF9800', fg='white', width=10)
        clear_btn.pack(side=tk.LEFT, padx=10)
        
        save_btn = tk.Button(button_frame, text="Save Order", command=self.save_order, bg='#4CAF50', fg='white', width=12)
        save_btn.pack(side=tk.LEFT, padx=10)
        
        print_btn = tk.Button(button_frame, text="Print Bill", command=self.print_bill, bg='#2196F3', fg='white', width=10)
        print_btn.pack(side=tk.LEFT, padx=10)
    
    def format_currency(self, var):
        formatted = tk.StringVar()
        
        def update_format(*args):
            formatted.set(f"₹ {var.get():.2f}")
        
        var.trace_add('write', update_format)
        update_format()  # Initial format
        return formatted
    
    def update_product_list(self, event=None):
        search_term = self.search_product.get().lower()
        if search_term:
            filtered_products = [p for p in self.product_list if search_term in p.lower()]
            self.product_search_entry.configure(completevalues=filtered_products)
        else:
            self.product_search_entry.configure(completevalues=self.product_list)
    
    def add_to_cart(self):
        product_name = self.search_product.get()
        if not product_name:
            messagebox.showwarning("Warning", "Please select a product")
            return
        
        quantity = self.product_quantity.get()
        if quantity <= 0:
            messagebox.showwarning("Warning", "Quantity must be greater than zero")
            return
        
        # Get price from database
        price = self.get_product_price(product_name)
        if price == 0:
            messagebox.showerror("Error", f"Product '{product_name}' not found or has no price")
            return
            
        total_price = price * quantity
        
        # Check if product already in cart, update quantity if it is
        for i, item in enumerate(self.cart):
            if item['product'] == product_name:
                # Update existing product
                self.cart[i]['quantity'] += quantity
                self.cart[i]['total'] = self.cart[i]['price'] * self.cart[i]['quantity']
                self.update_cart_display()
                self.update_totals()
                self.clear_product_selection()
                return
        
        # Add as new item if not already in cart
        item = {
            'product': product_name,
            'price': price,
            'quantity': quantity,
            'total': total_price
        }
        self.cart.append(item)
        
        self.update_cart_display()
        self.update_totals()
        self.clear_product_selection()
    
    def update_cart_display(self):
        # Clear the treeview
        for item in self.cart_treeview.get_children():
            self.cart_treeview.delete(item)
        
        # Add items from cart to treeview
        for item in self.cart:
            self.cart_treeview.insert(
                "", 
                "end", 
                values=(
                    item['product'], 
                    f"{item['price']:.2f}", 
                    item['quantity'], 
                    f"{item['total']:.2f}"
                )
            )
    
    def remove_item(self):
        selected_item = self.cart_treeview.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select an item to remove")
            return
        
        selected_index = self.cart_treeview.index(selected_item[0])
        if 0 <= selected_index < len(self.cart):
            self.cart.pop(selected_index)
            self.update_cart_display()
            self.update_totals()
    
    def update_totals(self):
        subtotal = sum(item['total'] for item in self.cart)
        tax_rate = 0.05  # 5% tax
        tax_amount = subtotal * tax_rate
        total = subtotal + tax_amount
        
        self.subtotal.set(subtotal)
        self.tax.set(tax_amount)
        self.total.set(total)
    
    def calculate_balance(self):
        paid = self.paid_amount.get()
        total = self.total.get()
        balance = paid - total
        self.balance.set(balance)
    
    def clear_product_selection(self):
        self.search_product.set("")
        self.product_quantity.set(1)
        self.product_search_entry.focus()
    
    def clear_all(self):
        self.customer_name.set("")
        self.customer_contact.set("")
        self.search_product.set("")
        self.product_quantity.set(1)
        self.subtotal.set(0)
        self.tax.set(0)
        self.total.set(0)
        self.paid_amount.set(0)
        self.balance.set(0)
        self.cart = []
        self.update_cart_display()
    
    def save_order(self):
        if not self.cart:
            messagebox.showwarning("Warning", "Cart is empty")
            return
        
        try:
            # Save order details
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.cursor.execute(
                """INSERT INTO orders 
                   (customer_name, customer_contact, date, total_amount) 
                   VALUES (?, ?, ?, ?)""",
                (self.customer_name.get(), self.customer_contact.get(), now, self.total.get())
            )
            
            # Get the order ID
            order_id = self.cursor.lastrowid
            
            # Save order items
            for item in self.cart:
                self.cursor.execute(
                    """INSERT INTO order_items 
                       (order_id, product_name, price, quantity, total) 
                       VALUES (?, ?, ?, ?, ?)""",
                    (order_id, item['product'], item['price'], item['quantity'], item['total'])
                )
            
            self.conn.commit()
            messagebox.showinfo("Success", f"Order #{order_id} saved successfully")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save order: {str(e)}")
    
    def print_bill(self):
        if not self.cart:
            messagebox.showwarning("Warning", "Cart is empty")
            return
        
        # Generate bill content
        bill_text = self.generate_bill()
        
        # Create a temporary file to store the bill
        with tempfile.NamedTemporaryFile(delete=False, suffix='.txt', mode='w') as f:
            f.write(bill_text)
            bill_file = f.name
        
        # Open the file for viewing (simulating print)
        # On Windows
        try:
            os.startfile(bill_file)
            return
        except:
            pass
        
        # On Mac/Linux
        try:
            os.system(f"open {bill_file}")
            return
        except:
            pass
        
        # If all else fails, display in a new window
        self.display_bill(bill_text)
    
    def generate_bill(self):
        # Create a formatted bill
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        bill = []
        
        bill.append("="*50)
        bill.append(f"{'RETAIL BILLING SYSTEM':^50}")
        bill.append("="*50)
        bill.append(f"Date: {now}")
        bill.append(f"Invoice #: {int(datetime.now().timestamp())}")
        bill.append("-"*50)
        
        if self.customer_name.get():
            bill.append(f"Customer: {self.customer_name.get()}")
        if self.customer_contact.get():
            bill.append(f"Contact: {self.customer_contact.get()}")
        
        bill.append("-"*50)
        bill.append(f"{'Product':<20}{'Price':>10}{'Qty':>8}{'Total':>12}")
        bill.append("-"*50)
        
        for item in self.cart:
            bill.append(
                f"{item['product']:<20}{item['price']:>10.2f}{item['quantity']:>8}{item['total']:>12.2f}"
            )
        
        bill.append("-"*50)
        bill.append(f"{'Subtotal':<38}{self.subtotal.get():>12.2f}")
        bill.append(f"{'Tax (5%)':<38}{self.tax.get():>12.2f}")
        bill.append("="*50)
        bill.append(f"{'TOTAL':<38}{self.total.get():>12.2f}")
        bill.append("-"*50)
        
        if self.paid_amount.get() > 0:
            bill.append(f"{'Paid Amount':<38}{self.paid_amount.get():>12.2f}")
            bill.append(f"{'Balance':<38}{self.balance.get():>12.2f}")
        
        bill.append("-"*50)
        bill.append(f"{'Thank you for your business!':^50}")
        bill.append("="*50)
        
        return "\n".join(bill)
    
    def display_bill(self, bill_text):
        bill_window = tk.Toplevel(self.root)
        bill_window.title("Bill Preview")
        bill_window.geometry("500x600")
        
        bill_frame = tk.Frame(bill_window)
        bill_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Scrollable text area for bill
        scrollbar = tk.Scrollbar(bill_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        bill_text_widget = tk.Text(bill_frame, font=("Courier", 10), yscrollcommand=scrollbar.set)
        bill_text_widget.pack(fill=tk.BOTH, expand=True)
        
        scrollbar.config(command=bill_text_widget.yview)
        
        bill_text_widget.insert(tk.END, bill_text)
        bill_text_widget.config(state=tk.DISABLED)
        
        # Print button
        print_button = tk.Button(
            bill_window, 
            text="Print",
            command=lambda: self.system_print(bill_text_widget),
            bg='#2196F3',
            fg='white'
        )
        print_button.pack(pady=10)
    
    def system_print(self, text_widget):
        # This would normally connect to the system's print dialog
        # For this example, we'll just show a message
        messagebox.showinfo("Print", "Sending to printer...")

# Main function to run the application
def main():
    root = tk.Tk()
    app = BillingSystem(root)
    root.mainloop()

if __name__ == "__main__":
    main()