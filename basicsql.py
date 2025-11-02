import sqlite3
from datetime import datetime, timedelta

conn = sqlite3.connect('posdb.sqlite3')

c = conn.cursor()

# ตาราง product
c.execute("""CREATE TABLE IF NOT EXISTS product (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            barcode TEXT,
            title TEXT,
            price REAL,
            cost REAL,
            quantity INTEGER,
            unit TEXT,
            category TEXT,
            reorder_point INTEGER,
            supplier TEXT )""")

# ตาราง sales (แทน transaction เพราะเป็น reserved keyword)
c.execute("""CREATE TABLE IF NOT EXISTS sales (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_id TEXT,
            datetime TEXT,
            subtotal REAL,
            vat REAL,
            grand_total REAL,
            received_amount REAL,
            change_amount REAL,
            items TEXT )""")

# ==================== ตาราง CUSTOMERS ====================
c.execute('''CREATE TABLE IF NOT EXISTS customers (
    customer_id TEXT PRIMARY KEY,
    customer_name TEXT NOT NULL,
    phone TEXT,
    email TEXT,
    address TEXT,
    credit_limit REAL DEFAULT 0,
    credit_days INTEGER DEFAULT 0,
    total_debt REAL DEFAULT 0,
    created_date TEXT,
    notes TEXT
)''')

# ==================== ตาราง CREDIT_BILLS ====================
c.execute('''CREATE TABLE IF NOT EXISTS credit_bills (
    bill_id TEXT PRIMARY KEY,
    customer_id TEXT NOT NULL,
    transaction_id TEXT,
    bill_date TEXT,
    due_date TEXT,
    total_amount REAL,
    paid_amount REAL DEFAULT 0,
    remaining_amount REAL,
    status TEXT DEFAULT 'PENDING',
    payment_date TEXT,
    notes TEXT,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (transaction_id) REFERENCES sales(transaction_id)
)''')

conn.commit()
print("✅ Database tables created/verified")

# ==================== PRODUCT FUNCTIONS ====================

def insert_product(barcode, title, price, cost, quantity, unit, category, reorder_point, supplier):
    with conn:
        command = 'INSERT INTO product VALUES (?,?,?,?,?,?,?,?,?,?)'
        c.execute(command, (None, barcode, title, price, cost, quantity, unit, category, reorder_point, supplier))
        conn.commit()
        print('saved')

def update_product(barcode, title, price, cost, quantity, unit, category, reorder_point, supplier):
    """อัปเดตข้อมูลสินค้า"""
    with conn:
        command = 'UPDATE product SET title=?, price=?, cost=?, quantity=?, unit=?, category=?, reorder_point=?, supplier=? WHERE barcode=?'
        c.execute(command, (title, price, cost, quantity, unit, category, reorder_point, supplier, barcode))
        conn.commit()
        print(f'Product {barcode} updated')

def update_stock(barcode, quantity_sold):
    """อัปเดตจำนวนสต็อกหลังขาย"""
    with conn:
        command = 'UPDATE product SET quantity = quantity - ? WHERE barcode = ? AND quantity >= ?'
        c.execute(command, (quantity_sold, barcode, quantity_sold))
        if c.rowcount == 0:
            print(f'Warning: Insufficient stock for barcode {barcode}')
        else:
            conn.commit()
            print(f'Stock updated for {barcode}: -{quantity_sold}')

def get_product_by_barcode(barcode):
    """ดึงข้อมูลสินค้าตาม barcode"""
    with conn:
        command = 'SELECT * FROM product WHERE barcode=?'
        c.execute(command, (barcode,))
        data = c.fetchone()
        return data

def view_product(allfield=True):
    with conn:
        if allfield:
            command = 'SELECT * FROM product'
        else:
            command = 'SELECT barcode,title,price,cost,quantity,unit,category,reorder_point FROM product'
        c.execute(command)
        data = c.fetchall()
    return data

def delete_product(barcode):
    with conn:
        command = 'DELETE FROM product WHERE barcode=(?)'
        c.execute(command,([barcode]))
        conn.commit()

def search_barcode(barcode):
    with conn:
        command = 'SELECT barcode,title,price,cost,quantity,unit,category,reorder_point FROM product WHERE barcode=(?)'
        c.execute(command,([barcode]))
        result = c.fetchone()
        if result:
            data = list(result)
            return data
        return None

# ==================== SALES/TRANSACTION FUNCTIONS ====================

def get_sales_by_date_range(start_date, end_date):
    """ดึงข้อมูลการขายตามช่วงวันที่"""
    with conn:
        command = 'SELECT * FROM sales WHERE date(datetime) BETWEEN ? AND ? ORDER BY datetime DESC'
        c.execute(command, (start_date, end_date))
        data = c.fetchall()
        return data

def insert_transaction(transaction_id, subtotal, vat, grand_total, received_amount, change_amount, items):
    """บันทึกข้อมูลการขาย"""
    with conn:
        current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        command = 'INSERT INTO sales VALUES (?,?,?,?,?,?,?,?,?)'
        c.execute(command, (None, transaction_id, current_datetime, subtotal, vat, grand_total, received_amount, change_amount, items))
        conn.commit()
        print(f'Transaction {transaction_id} saved')

def view_transactions():
    """ดูข้อมูลการขายทั้งหมด"""
    with conn:
        command = 'SELECT * FROM sales ORDER BY datetime DESC'
        c.execute(command)
        data = c.fetchall()
        return data

def generate_transaction_id():
    """สร้าง transaction ID อัตโนมัติ"""
    with conn:
        command = 'SELECT COUNT(*) FROM sales'
        c.execute(command)
        count = c.fetchone()[0]
        return f"T{count + 1:06d}"  # T000001, T000002, etc.

# ==================== CUSTOMER FUNCTIONS ====================

def insert_customer(customer_id, name, phone='', email='', address='', 
                   credit_limit=0, credit_days=0, notes=''):
    """เพิ่มลูกค้าใหม่"""
    with conn:
        created_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        command = '''INSERT INTO customers VALUES (?, ?, ?, ?, ?, ?, ?, 0, ?, ?)'''
        c.execute(command, (customer_id, name, phone, email, address, credit_limit, 
                           credit_days, created_date, notes))
        conn.commit()
        print(f'Customer {customer_id} added')

def update_customer(customer_id, name, phone, email, address, 
                   credit_limit, credit_days, notes):
    """แก้ไขข้อมูลลูกค้า"""
    with conn:
        command = '''UPDATE customers SET 
                    customer_name=?, phone=?, email=?, address=?,
                    credit_limit=?, credit_days=?, notes=?
                    WHERE customer_id=?'''
        c.execute(command, (name, phone, email, address, credit_limit, credit_days, 
                           notes, customer_id))
        conn.commit()
        print(f'Customer {customer_id} updated')

def delete_customer(customer_id):
    """ลบลูกค้า"""
    with conn:
        command = 'DELETE FROM customers WHERE customer_id=?'
        c.execute(command, (customer_id,))
        conn.commit()
        print(f'Customer {customer_id} deleted')

def get_all_customers():
    """ดึงข้อมูลลูกค้าทั้งหมด"""
    with conn:
        command = 'SELECT * FROM customers ORDER BY customer_name'
        c.execute(command)
        data = c.fetchall()
        return data

def get_customer_by_id(customer_id):
    """ดึงข้อมูลลูกค้าจาก ID"""
    with conn:
        command = 'SELECT * FROM customers WHERE customer_id=?'
        c.execute(command, (customer_id,))
        data = c.fetchone()
        return data

def update_customer_debt(customer_id, amount):
    """อัปเดตยอดหนี้ลูกค้า"""
    with conn:
        command = 'UPDATE customers SET total_debt = total_debt + ? WHERE customer_id=?'
        c.execute(command, (amount, customer_id))
        conn.commit()
        print(f'Customer {customer_id} debt updated: +{amount}')

# ==================== CREDIT BILL FUNCTIONS ====================

def insert_credit_bill(bill_id, customer_id, transaction_id, credit_days, 
                      total_amount, notes=''):
    """สร้างบิลเครดิตใหม่"""
    with conn:
        bill_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        due_date = (datetime.now() + timedelta(days=credit_days)).strftime('%Y-%m-%d')
        
        command = '''INSERT INTO credit_bills 
                    (bill_id, customer_id, transaction_id, bill_date, due_date, 
                     total_amount, remaining_amount, status, notes) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, 'PENDING', ?)'''
        c.execute(command, (bill_id, customer_id, transaction_id, bill_date, due_date, 
                           total_amount, total_amount, notes))
        
        # อัปเดตยอดหนี้ลูกค้า
        command2 = 'UPDATE customers SET total_debt = total_debt + ? WHERE customer_id=?'
        c.execute(command2, (total_amount, customer_id))
        
        conn.commit()
        print(f'Credit bill {bill_id} created for customer {customer_id}')

def pay_credit_bill(bill_id, payment_amount):
    """ชำระบิลเครดิต"""
    with conn:
        # ดึงข้อมูลบิล
        command = 'SELECT customer_id, remaining_amount FROM credit_bills WHERE bill_id=?'
        c.execute(command, (bill_id,))
        result = c.fetchone()
        
        if not result:
            return False, "ไม่พบบิลนี้"
        
        customer_id, remaining = result
        
        if payment_amount > remaining:
            return False, "จำนวนเงินชำระมากกว่ายอดค้างชำระ"
        
        new_remaining = remaining - payment_amount
        new_status = 'PAID' if new_remaining == 0 else 'PARTIAL'
        payment_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # อัปเดตบิล
        command = '''UPDATE credit_bills SET 
                    paid_amount = paid_amount + ?,
                    remaining_amount = ?,
                    status = ?,
                    payment_date = ?
                    WHERE bill_id=?'''
        c.execute(command, (payment_amount, new_remaining, new_status, payment_date, bill_id))
        
        # อัปเดตยอดหนี้ลูกค้า
        command2 = 'UPDATE customers SET total_debt = total_debt - ? WHERE customer_id=?'
        c.execute(command2, (payment_amount, customer_id))
        
        conn.commit()
        print(f'Payment {payment_amount} received for bill {bill_id}')
        return True, "ชำระเงินสำเร็จ"

def get_all_credit_bills():
    """ดึงบิลเครดิตทั้งหมด"""
    with conn:
        command = '''SELECT cb.*, cu.customer_name 
                    FROM credit_bills cb
                    LEFT JOIN customers cu ON cb.customer_id = cu.customer_id
                    ORDER BY cb.bill_date DESC'''
        c.execute(command)
        data = c.fetchall()
        return data

def get_pending_credit_bills():
    """ดึงบิลเครดิตที่ค้างชำระ"""
    with conn:
        command = '''SELECT cb.*, cu.customer_name 
                    FROM credit_bills cb
                    LEFT JOIN customers cu ON cb.customer_id = cu.customer_id
                    WHERE cb.status IN ('PENDING', 'PARTIAL')
                    ORDER BY cb.due_date ASC'''
        c.execute(command)
        data = c.fetchall()
        return data

def get_overdue_credit_bills():
    """ดึงบิลเครดิตที่เกินกำหนด"""
    with conn:
        today = datetime.now().strftime('%Y-%m-%d')
        command = '''SELECT cb.*, cu.customer_name 
                    FROM credit_bills cb
                    LEFT JOIN customers cu ON cb.customer_id = cu.customer_id
                    WHERE cb.status IN ('PENDING', 'PARTIAL') 
                    AND cb.due_date < ?
                    ORDER BY cb.due_date ASC'''
        c.execute(command, (today,))
        data = c.fetchall()
        return data

def get_customer_credit_bills(customer_id):
    """ดึงบิลเครดิตของลูกค้า"""
    with conn:
        command = '''SELECT * FROM credit_bills 
                    WHERE customer_id=? 
                    ORDER BY bill_date DESC'''
        c.execute(command, (customer_id,))
        data = c.fetchall()
        return data

def get_credit_bill_by_id(bill_id):
    """ดึงข้อมูลบิลเครดิตจาก ID"""
    with conn:
        command = '''SELECT cb.*, cu.customer_name, cu.phone 
                    FROM credit_bills cb
                    LEFT JOIN customers cu ON cb.customer_id = cu.customer_id
                    WHERE cb.bill_id=?'''
        c.execute(command, (bill_id,))
        data = c.fetchone()
        return data

def get_credit_statistics():
    """ดึงสถิติระบบเครดิต"""
    with conn:
        stats = {}
        
        # จำนวนบิลค้างชำระ
        c.execute("SELECT COUNT(*) FROM credit_bills WHERE status IN ('PENDING', 'PARTIAL')")
        stats['pending_count'] = c.fetchone()[0]
        
        # จำนวนบิลเกินกำหนด
        today = datetime.now().strftime('%Y-%m-%d')
        c.execute("SELECT COUNT(*) FROM credit_bills WHERE status IN ('PENDING', 'PARTIAL') AND due_date < ?", (today,))
        stats['overdue_count'] = c.fetchone()[0]
        
        # ยอดหนี้รวมทั้งหมด
        c.execute("SELECT SUM(total_debt) FROM customers")
        result = c.fetchone()[0]
        stats['total_debt'] = result if result else 0
        
        # ยอดเงินที่ต้องรับในเดือนนี้
        first_day = datetime.now().replace(day=1).strftime('%Y-%m-%d')
        last_day = (datetime.now().replace(day=1) + timedelta(days=32)).replace(day=1).strftime('%Y-%m-%d')
        c.execute("SELECT SUM(remaining_amount) FROM credit_bills WHERE status IN ('PENDING', 'PARTIAL') AND due_date BETWEEN ? AND ?", 
                 (first_day, last_day))
        result = c.fetchone()[0]
        stats['due_this_month'] = result if result else 0
        
        return stats

# ==================== UTILITY FUNCTIONS ====================

def cleanup_old_data(days=365):
    """ลบข้อมูลเก่าที่เกินกำหนด (ระวัง!)"""
    with conn:
        cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        # ลบ transactions เก่า (ไม่รวมบิลเครดิตที่ยังไม่ชำระ)
        command = '''DELETE FROM sales 
                    WHERE date(datetime) < ? 
                    AND transaction_id NOT IN (
                        SELECT transaction_id FROM credit_bills 
                        WHERE status IN ('PENDING', 'PARTIAL')
                    )'''
        c.execute(command, (cutoff_date,))
        deleted_sales = c.rowcount
        
        conn.commit()
        print(f'Cleaned up {deleted_sales} old sales records')
        return deleted_sales

def backup_database(backup_path='backup_posdb.sqlite3'):
    """สำรองฐานข้อมูล"""
    import shutil
    try:
        shutil.copy2('posdb.sqlite3', backup_path)
        print(f'✅ Database backed up to {backup_path}')
        return True
    except Exception as e:
        print(f'❌ Backup failed: {e}')
        return False

def get_database_info():
    """แสดงข้อมูลสถิติฐานข้อมูล"""
    with conn:
        info = {}
        
        c.execute("SELECT COUNT(*) FROM product")
        info['total_products'] = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) FROM sales")
        info['total_sales'] = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) FROM customers")
        info['total_customers'] = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) FROM credit_bills")
        info['total_credit_bills'] = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) FROM credit_bills WHERE status IN ('PENDING', 'PARTIAL')")
        info['pending_bills'] = c.fetchone()[0]
        
        return info

# ==================== TESTING ====================

if __name__ == '__main__':
    print("=" * 60)
    print("POS Database System - Version 1.4 (Credit System)")
    print("=" * 60)
    
    # แสดงข้อมูลฐานข้อมูล
    db_info = get_database_info()
    print(f"\n📊 Database Statistics:")
    print(f"   • Products: {db_info['total_products']}")
    print(f"   • Sales: {db_info['total_sales']}")
    print(f"   • Customers: {db_info['total_customers']}")
    print(f"   • Credit Bills: {db_info['total_credit_bills']}")
    print(f"   • Pending Bills: {db_info['pending_bills']}")
    
    # แสดงสถิติเครดิต
    if db_info['total_customers'] > 0:
        credit_stats = get_credit_statistics()
        print(f"\n💳 Credit System Statistics:")
        print(f"   • Pending Bills: {credit_stats['pending_count']}")
        print(f"   • Overdue Bills: {credit_stats['overdue_count']}")
        print(f"   • Total Debt: {credit_stats['total_debt']:,.2f} บาท")
        print(f"   • Due This Month: {credit_stats['due_this_month']:,.2f} บาท")
    
    print("\n" + "=" * 60)
    print("✅ All systems ready!")
    print("=" * 60)