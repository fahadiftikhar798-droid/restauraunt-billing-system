# ==========================================================
# RESTAURANT BILLING SYSTEM - REAL LIFE PROJECT
# Developed by: Fahad Iftikhar | BS Software Engineering
# Features: Menu, Tables, GST, Discount, Receipt, Sales Report
# ==========================================================

import sqlite3
from datetime import datetime
import json
import os

DB = "restaurant.db"

# 1. DATABASE SETUP
def setup_db():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS menu (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT, category TEXT, price REAL)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        table_no INTEGER, items TEXT, total REAL, payment TEXT, time TEXT)""")
    
    cur.execute("SELECT COUNT(*) FROM menu")
    if cur.fetchone()[0] == 0:
        menu = [
            ("Chicken Biryani", "Main Course", 450),
            ("Beef Biryani", "Main Course", 500),
            ("Chicken Karahi Full", "Main Course", 1200),
            ("Mutton Karahi", "Main Course", 1800),
            ("Naan Roghni", "Bread", 40),
            ("Naan", "Bread", 30),
            ("Chicken Tikka", "BBQ", 350),
            ("Seekh Kabab", "BBQ", 300),
            ("Raita", "Side", 80),
            ("Cold Drink", "Drink", 180),
            ("Kheer", "Dessert", 150),
        ]
        cur.executemany("INSERT INTO menu (name,category,price) VALUES (?,?,?)", menu)
    conn.commit()
    conn.close()

# 2. CORE BILLING CLASS
class BillingSystem:
    def __init__(self):
        self.GST = 0.16  # 16% Pakistan
        self.order = []

    def show_menu(self):
        conn = sqlite3.connect(DB)
        rows = conn.execute("SELECT id,name,category,price FROM menu").fetchall()
        print("\n" + "="*55)
        print(f"{'ID':<3} {'ITEM NAME':<22} {'CATEGORY':<12} {'PRICE'}")
        print("="*55)
        for r in rows:
            print(f"{r[0]:<3} {r[1]:<22} {r[2]:<12} Rs.{r[3]}")
        print("="*55)
        conn.close()
        return {r[0]: (r[1], r[3]) for r in rows}

    def take_order(self):
        menu = self.show_menu()
        self.order = []
        while True:
            try:
                item_id = input("\nEnter Item ID (0 to finish): ")
                if item_id == '0': break
                item_id = int(item_id)
                if item_id not in menu: 
                    print("Invalid ID!")
                    continue
                qty = int(input(f"Qty for {menu[item_id][0]}: "))
                name, price = menu[item_id]
                self.order.append({"name":name, "qty":qty, "price":price, "amount":price*qty})
                print(f"Added: {qty} x {name} = Rs.{price*qty}")
            except:
                print("Enter valid number")
        return self.order

    def calculate(self, discount=0):
        subtotal = sum(i['amount'] for i in self.order)
        disc_amt = subtotal * (discount/100)
        tax = (subtotal - disc_amt) * self.GST
        total = subtotal - disc_amt + tax
        return subtotal, disc_amt, tax, total

    def print_bill(self, table_no, payment="Cash", discount=0):
        subtotal, disc_amt, tax, total = self.calculate(discount)
        time = datetime.now().strftime("%d-%m-%Y %I:%M %p")
        bill_no = datetime.now().strftime("%Y%m%d%H%M%S")

        print("\n" + "="*55)
        print("      AL-FAHAD RESTAURANT - ISLAMABAD")
        print("      Phone: 0300-XXXXXXX | GST No: 12345")
        print("="*55)
        print(f"Bill No: {bill_no} | Table: {table_no}")
        print(f"Date: {time} | Cashier: Fahad")
        print("-"*55)
        print(f"{'Item':<20} {'Qty':<4} {'Rate':<6} {'Amount'}")
        print("-"*55)
        for it in self.order:
            print(f"{it['name'][:20]:<20} {it['qty']:<4} {it['price']:<6} {it['amount']}")
        print("-"*55)
        print(f"{'Subtotal':<35} Rs.{subtotal:.2f}")
        if discount>0:
            print(f"{'Discount '+str(discount)+'%':<35} -Rs.{disc_amt:.2f}")
        print(f"{'GST 16%':<35} Rs.{tax:.2f}")
        print("="*55)
        print(f"{'GRAND TOTAL':<35} Rs.{total:.2f}")
        print("="*55)
        print(f"Payment: {payment} | Thank you! Visit Again")
        print("="*55)

        # Save to DB
        conn = sqlite3.connect(DB)
        conn.execute("INSERT INTO orders (table_no,items,total,payment,time) VALUES (?,?,?,?,?)",
                     (table_no, json.dumps(self.order), total, payment, time))
        conn.commit()
        conn.close()
        return total

    def sales_report(self):
        conn = sqlite3.connect(DB)
        rows = conn.execute("SELECT * FROM orders").fetchall()
        total = sum(r[3] for r in rows)
        print(f"\n--- DAILY SALES REPORT ---")
        print(f"Total Orders: {len(rows)}")
        print(f"Total Sales: Rs.{total:.2f}")
        for r in rows[-10:]:  # Last 10
            print(f"Table {r[1]} - Rs.{r[3]} - {r[4]} - {r[5]}")
        conn.close()

# 3. MAIN PROGRAM
def main():
    setup_db()
    app = BillingSystem()
    
    while True:
        print("\n====== AL-FAHAD RESTAURANT POS ======")
        print("1. New Order")
        print("2. Show Menu")
        print("3. Sales Report")
        print("4. Exit")
        ch = input("Select (1-4): ")

        if ch == '1':
            try:
                table = int(input("Table No (1-20): "))
                if not app.take_order():
                    print("No items!")
                    continue
                disc = float(input("Discount % (0 for none): ") or 0)
                pay = input("Payment (Cash/Card/JazzCash) [Cash]: ") or "Cash"
                app.print_bill(table, pay, disc)
            except Exception as e:
                print("Error:", e)

        elif ch == '2':
            app.show_menu()
        elif ch == '3':
            app.sales_report()
        elif ch == '4':
            print("Allah Hafiz!")
            break

if __name__ == "__main__":
    main()