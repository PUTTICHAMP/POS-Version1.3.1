import sqlite3
from datetime import datetime

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
        print(data)

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
        data = list(c.fetchone())
        return data

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

if __name__ == '__main__':
    # insert_product('1002','Durian',200,'fruit')
    # delete_product('1002')
    # search_barcode('1003')
    view_product()