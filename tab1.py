from tkinter import *
from tkinter import ttk, messagebox
from basicsql import *
import json
from datetime import datetime

# Import สำหรับ receipt printing
try:
    from receipt_printer import ReceiptPrinter
    RECEIPT_AVAILABLE = True
    print("✅ Receipt printer module loaded")
except ImportError as e:
    RECEIPT_AVAILABLE = False
    print(f"❌ Receipt printer not available: {e}")

# Import สำหรับ thermal printing  
try:
    from thermal_printer import ThermalPrinter
    THERMAL_AVAILABLE = True
    print("✅ Thermal printer module loaded")
except ImportError as e:
    THERMAL_AVAILABLE = False
    print(f"❌ Thermal printer not available: {e}")

class SalesTab(Frame):
    def __init__(self, parent, product_tab=None, dashboard_tab=None, profit_tab=None):
        super().__init__(parent)
        self.pack(fill=BOTH, expand=True)
        
        # Reference ไปยังแท็บอื่นๆ
        self.product_tab = product_tab
        self.dashboard_tab = dashboard_tab
        self.profit_tab = profit_tab
        
        # ตัวแปร
        self.v_title = StringVar()
        self.v_price = StringVar()
        self.v_quantity = StringVar()
        self.v_result = StringVar()
        self.v_search = StringVar()
        
        # ตะกร้าสินค้า
        self.cart = {}
        
        # สร้าง GUI
        self.create_widgets()
        
    def create_widgets(self):
        FONT1 = (None, 20)
        FONT2 = (None, 18)
        
        # หัวข้อ
        L1 = Label(self, text='เมนูสำหรับขาย', font=FONT1)
        L1.pack()
        
        # Frame สำหรับปุ่มสินค้า
        self.F1 = Frame(self)
        self.F1.place(x=20, y=50)
        
        # สร้างปุ่มสินค้าจากฐานข้อมูล
        self.create_product_buttons()
        
        # Frame สำหรับตารางขาย
        self.F2 = Frame(self)
        self.F2.place(x=350, y=50)
        
        # ช่องค้นหาบาร์โค้ด
        self.search = ttk.Entry(self.F2, textvariable=self.v_search, font=(None, 25), width=12)
        self.search.pack(pady=20)
        self.search.bind('<Return>', self.search_product)
        self.search.focus()
        
        # ตารางขาย
        self.create_sales_table()
        
        # สรุปยอดขาย
        self.create_summary_section()
        
        # ปุ่ม Checkout
        self.create_checkout_button()
        
    def create_product_buttons(self):
        """สร้างปุ่มสินค้าจากฐานข้อมูล"""
        col = 0
        row = 0
        
        for i, db in enumerate(view_product(allfield=False), start=1):
            # ตรวจสอบสต็อก
            try:
                if len(db) >= 5 and int(db[4]) <= 0:  # แปลง quantity เป็น int
                    continue  # ข้ามสินค้าที่หมดสต็อก
                    
                # แสดงชื่อสินค้า + สต็อก + หน่วย
                display_text = f"{db[1]}\n({db[4]} {db[5] if len(db) >= 6 else 'ชิ้น'})" if len(db) >= 6 else db[1]
                
                B = ttk.Button(self.F1, text=display_text, 
                              command=lambda pd=db: self.button_insert(pd[0], pd[1], pd[2], 1))
                B.grid(row=row, column=col, ipadx=10, ipady=20, padx=5, pady=5)
                col = col + 1
                if i % 3 == 0:
                    col = 0
                    row = row + 1
            except (ValueError, IndexError):
                # หากมีปัญหาในการแปลงข้อมูล ให้แสดงปุ่มแบบปกติ
                B = ttk.Button(self.F1, text=db[1] if len(db) > 1 else "Unknown", 
                              command=lambda pd=db: self.button_insert(pd[0], pd[1], pd[2], 1))
                B.grid(row=row, column=col, ipadx=10, ipady=20, padx=5, pady=5)
                col = col + 1
                if i % 3 == 0:
                    col = 0
                    row = row + 1
                
    def create_sales_table(self):
        """สร้างตารางแสดงรายการขาย"""
        # Style
        style = ttk.Style()
        style.configure('Treeview.Heading', font=(None, 12))
        
        sales_header = ['barcode', 'title', 'price', 'quantity', 'total']
        sales_width = [120, 180, 70, 70, 80]
        
        self.table_sales = ttk.Treeview(self.F2, columns=sales_header, 
                                       show='headings', height=8)
        self.table_sales.pack()
        
        for hd, w in zip(sales_header, sales_width):
            self.table_sales.heading(hd, text=hd)
            self.table_sales.column(hd, width=w, anchor='center')
            
        self.table_sales.column('title', anchor='w')
        self.table_sales.column('price', anchor='e')
        self.table_sales.column('quantity', anchor='e')
        self.table_sales.column('total', anchor='e')
        
    def create_summary_section(self):
        """สร้างส่วนสรุปยอดขาย"""
        # Frame สำหรับสรุปยอด
        self.F3 = Frame(self.F2)
        self.F3.pack(pady=10, fill=X)
        
        # ตัวแปรสำหรับแสดงยอด
        self.v_subtotal = StringVar()
        self.v_vat = StringVar()
        self.v_grand_total = StringVar()
        
        # Labels สำหรับแสดงยอด
        Label(self.F3, text="ยอดรวม (Subtotal):", font=(None, 12)).grid(row=0, column=0, sticky='e', padx=5)
        Label(self.F3, textvariable=self.v_subtotal, font=(None, 12, 'bold'), width=15, anchor='e').grid(row=0, column=1, sticky='e', padx=5)
        
        Label(self.F3, text="VAT 7%:", font=(None, 12)).grid(row=1, column=0, sticky='e', padx=5)
        Label(self.F3, textvariable=self.v_vat, font=(None, 12, 'bold'), width=15, anchor='e').grid(row=1, column=1, sticky='e', padx=5)
        
        # เส้นแบ่ง
        ttk.Separator(self.F3, orient='horizontal').grid(row=2, column=0, columnspan=2, sticky='ew', pady=5)
        
        Label(self.F3, text="รวมทั้งหมด (Grand Total):", font=(None, 14, 'bold')).grid(row=3, column=0, sticky='e', padx=5)
        Label(self.F3, textvariable=self.v_grand_total, font=(None, 14, 'bold'), fg='red', width=15, anchor='e').grid(row=3, column=1, sticky='e', padx=5)
        
        # เริ่มต้นด้วยยอด 0
        self.update_summary()
        
    def create_checkout_button(self):
        """สร้างปุ่ม Checkout และปุ่มทดสอบ"""
        self.F4 = Frame(self.F2)
        self.F4.pack(pady=10, fill=X)
        
        # ปุ่ม Checkout หลัก
        self.btn_checkout = ttk.Button(self.F4, text="💳 CHECKOUT", 
                                      command=self.open_checkout_window,
                                      style='Checkout.TButton')
        self.btn_checkout.pack(fill=X, ipady=10)
        
        # ปุ่มทดสอบต่างๆ
        test_frame = Frame(self.F4)
        test_frame.pack(fill=X, pady=(10, 0))
        
        # ปุ่มทดสอบ PDF
        if RECEIPT_AVAILABLE:
            self.btn_test_pdf = ttk.Button(test_frame, text="📄 ทดสอบ PDF", 
                                          command=self.test_pdf_receipt)
            self.btn_test_pdf.pack(side=LEFT, padx=2, fill=X, expand=True)
        
        # ปุ่มทดสอบ Thermal
        if THERMAL_AVAILABLE:
            self.btn_test_thermal = ttk.Button(test_frame, text="🖨️ ทดสอบ Thermal", 
                                              command=self.test_thermal_printer)
            self.btn_test_thermal.pack(side=RIGHT, padx=2, fill=X, expand=True)
        
        # สร้าง styles
        style = ttk.Style()
        style.configure('Checkout.TButton', font=(None, 16, 'bold'))
        
    def calculate_totals(self):
        """คำนวณยอดรวมทั้งหมด"""
        subtotal = 0
        for item in self.cart.values():
            price = float(item[2])
            quantity = int(item[3])
            subtotal += price * quantity
            
        vat = subtotal * 0.07  # VAT 7%
        grand_total = subtotal + vat
        
        return subtotal, vat, grand_total
        
    def update_summary(self):
        """อัปเดตการแสดงยอดรวม"""
        subtotal, vat, grand_total = self.calculate_totals()
        
        self.v_subtotal.set(f"{subtotal:,.2f} บาท")
        self.v_vat.set(f"{vat:,.2f} บาท")
        self.v_grand_total.set(f"{grand_total:,.2f} บาท")
        
    def update_table_with_totals(self):
        """อัปเดตตารางพร้อมคำนวณยอดรวมแต่ละรายการ"""
        self.table_sales.delete(*self.table_sales.get_children())
        
        for item in self.cart.values():
            barcode = item[0]
            title = item[1]
            price = float(item[2])
            quantity = int(item[3])
            total = price * quantity
            
            # เพิ่มข้อมูลพร้อมยอดรวม
            self.table_sales.insert('', 'end', values=[barcode, title, f"{price:,.2f}", quantity, f"{total:,.2f}"])
            
        # อัปเดตสรุปยอด
        self.update_summary()
        
    def button_insert(self, b, t, p, q=1):
        """เพิ่มสินค้าลงตะกร้า"""
        # ตรวจสอบสต็อก
        product_data = get_product_by_barcode(b)
        if product_data and len(product_data) >= 7:
            try:
                available_stock = int(product_data[5])  # แปลง quantity เป็น int
                current_qty = self.cart[b][3] if b in self.cart else 0
                
                if current_qty >= available_stock:
                    messagebox.showwarning("Warning", f"สินค้า {t} มีสต็อกเหลือ {available_stock} ชิ้น")
                    return
            except (ValueError, IndexError):
                # หากแปลงไม่ได้หรือ index ผิด ให้ดำเนินการต่อ
                pass
        
        if b not in self.cart:
            self.cart[b] = [b, t, p, q]
        else:
            self.cart[b][3] = self.cart[b][3] + 1
            
        # อัปเดตตารางพร้อมยอดรวม
        self.update_table_with_totals()
            
    def search_product(self, event=None):
        """ค้นหาสินค้าด้วยบาร์โค้ด"""
        barcode = self.v_search.get()
        try:
            data = search_barcode(barcode)
            if data:
                # ตรวจสอบสต็อก
                if len(data) >= 5:
                    try:
                        available_stock = int(data[4])  # แปลง quantity เป็น int
                        current_qty = self.cart[data[0]][3] if data[0] in self.cart else 0
                        
                        if current_qty >= available_stock:
                            messagebox.showwarning("Warning", f"สินค้า {data[1]} มีสต็อกเหลือ {available_stock} ชิ้น")
                            self.v_search.set('')
                            self.search.focus()
                            return
                    except (ValueError, IndexError):
                        # หากแปลงไม่ได้ ให้ดำเนินการต่อ
                        pass
                
                if data[0] not in self.cart:
                    self.cart[data[0]] = [data[0], data[1], data[2], 1]
                else:
                    self.cart[data[0]][3] = self.cart[data[0]][3] + 1
                    
                # อัปเดตตารางพร้อมยอดรวม
                self.update_table_with_totals()
                    
                self.v_search.set('')  # clear data
                self.search.focus()  # กลับไปที่ช่องค้นหา
            else:
                messagebox.showerror("Error", "ไม่พบสินค้าที่มีบาร์โค้ดนี้")
                self.v_search.set('')
                self.search.focus()
        except Exception as e:
            messagebox.showerror("Error", f"เกิดข้อผิดพลาด: {str(e)}")
            self.v_search.set('')
            self.search.focus()
            
    def open_checkout_window(self):
        """เปิดหน้าต่าง Checkout"""
        if not self.cart:
            messagebox.showwarning("Warning", "ไม่มีสินค้าในตะกร้า")
            return
            
        subtotal, vat, grand_total = self.calculate_totals()
        
        # สร้างหน้าต่าง Checkout
        checkout_window = Toplevel(self)
        checkout_window.title("ระบบชำระเงิน - Checkout")
        checkout_window.geometry("600x700")
        checkout_window.transient(self.master)
        checkout_window.grab_set()
        
        # ตำแหน่งกลางหน้าจอ
        checkout_window.update_idletasks()
        x = (checkout_window.winfo_screenwidth() // 2) - (600 // 2)
        y = (checkout_window.winfo_screenheight() // 2) - (700 // 2)
        checkout_window.geometry(f"600x700+{x}+{y}")
        
        # หัวข้อ
        Label(checkout_window, text="ระบบชำระเงิน", font=(None, 20, 'bold')).pack(pady=10)
        
        # แสดงสรุปยอด
        summary_frame = LabelFrame(checkout_window, text="สรุปยอดขาย", font=(None, 14))
        summary_frame.pack(padx=20, pady=10, fill=X)
        
        Label(summary_frame, text=f"ยอดรวม: {subtotal:,.2f} บาท", font=(None, 12)).pack(anchor='w', padx=10, pady=2)
        Label(summary_frame, text=f"VAT 7%: {vat:,.2f} บาท", font=(None, 12)).pack(anchor='w', padx=10, pady=2)
        Label(summary_frame, text=f"รวมทั้งหมด: {grand_total:,.2f} บาท", font=(None, 16, 'bold'), fg='red').pack(anchor='w', padx=10, pady=5)
        
        # ส่วนรับเงิน
        payment_frame = LabelFrame(checkout_window, text="รับเงิน", font=(None, 14))
        payment_frame.pack(padx=20, pady=10, fill=X)
        
        # ตัวแปรเก็บยอดเงินที่รับ
        received_var = StringVar()
        received_var.set("0")
        
        # แสดงยอดเงินที่รับ
        Label(payment_frame, text="เงินที่รับ:", font=(None, 12)).pack(anchor='w', padx=10)
        received_label = Label(payment_frame, textvariable=received_var, font=(None, 20, 'bold'), fg='blue')
        received_label.pack(anchor='w', padx=10, pady=5)
        
        # ปุ่มธนบัตร
        bills_frame = Frame(payment_frame)
        bills_frame.pack(padx=10, pady=10, fill=X)
        
        bills = [20, 50, 100, 500, 1000]
        
        def add_bill(amount):
            current = float(received_var.get().replace(',', ''))  # ลบจุลภาคก่อนแปลง
            new_amount = current + amount
            received_var.set(f"{new_amount:,.0f}")
            update_change()
        
        def clear_received():
            received_var.set("0")
            update_change()
            
        Label(bills_frame, text="เลือกธนบัตร:", font=(None, 12)).pack(anchor='w')
        
        buttons_frame = Frame(bills_frame)
        buttons_frame.pack(fill=X, pady=5)
        
        for i, bill in enumerate(bills):
            btn = ttk.Button(buttons_frame, text=f"{bill:,}", width=8,
                           command=lambda b=bill: add_bill(b))
            btn.grid(row=0, column=i, padx=2, pady=2)
            
        # ปุ่มเคลียร์
        ttk.Button(buttons_frame, text="เคลียร์", command=clear_received).grid(row=0, column=len(bills), padx=10)
        
        # ช่องกรอกเงินเอง
        manual_frame = Frame(payment_frame)
        manual_frame.pack(padx=10, pady=5, fill=X)
        
        Label(manual_frame, text="หรือกรอกจำนวนเงิน:", font=(None, 12)).pack(anchor='w')
        manual_entry = ttk.Entry(manual_frame, font=(None, 14), width=15)
        manual_entry.pack(anchor='w', pady=2)
        
        def add_manual():
            try:
                amount = float(manual_entry.get().replace(',', ''))  # รองรับการกรอกจุลภาค
                current = float(received_var.get().replace(',', ''))
                new_amount = current + amount
                received_var.set(f"{new_amount:,.0f}")
                manual_entry.delete(0, END)
                update_change()
            except ValueError:
                messagebox.showerror("Error", "กรุณากรอกตัวเลขที่ถูกต้อง")
                
        ttk.Button(manual_frame, text="เพิ่ม", command=add_manual).pack(anchor='w', pady=2)
        
        # ส่วนเงินทอน
        change_frame = LabelFrame(checkout_window, text="เงินทอน", font=(None, 14))
        change_frame.pack(padx=20, pady=10, fill=X)
        
        change_var = StringVar()
        change_var.set("0.00")
        
        Label(change_frame, text="เงินทอน:", font=(None, 12)).pack(anchor='w', padx=10)
        change_label = Label(change_frame, textvariable=change_var, font=(None, 24, 'bold'), fg='green')
        change_label.pack(anchor='w', padx=10, pady=5)
        
        def update_change():
            try:
                received = float(received_var.get().replace(',', ''))
                change = received - grand_total
                if change >= 0:
                    change_var.set(f"{change:,.2f} บาท")
                    change_label.config(fg='green')
                else:
                    change_var.set(f"{abs(change):,.2f} บาท (ขาด)")
                    change_label.config(fg='red')
            except:
                change_var.set("0.00 บาท")
        
        # ปุ่มบันทึก
        buttons_frame_bottom = Frame(checkout_window)
        buttons_frame_bottom.pack(padx=20, pady=20, fill=X)
        
        def save_transaction():
            try:
                received = float(received_var.get().replace(',', ''))
                change = received - grand_total
                
                if received < grand_total:
                    messagebox.showerror("Error", "เงินที่รับไม่เพียงพอ")
                    return
                
                # สร้าง transaction ID
                transaction_id = generate_transaction_id()
                
                # แปลงข้อมูลตะกร้าเป็น JSON
                items_data = json.dumps(list(self.cart.values()))
                
                # บันทึกลงฐานข้อมูล
                insert_transaction(transaction_id, subtotal, vat, grand_total, received, change, items_data)
                
                # อัปเดตสต็อก
                for item in self.cart.values():
                    barcode = item[0]
                    quantity = item[3]
                    update_stock(barcode, quantity)
                
                # ปิดหน้าต่าง checkout ก่อน
                checkout_window.destroy()
                
                # แสดงหน้าต่างตัวเลือกการพิมพ์
                self.show_print_options(transaction_id, subtotal, vat, grand_total, received, change)
                
                # เคลียร์ตะกร้า
                self.clear_cart()
                
                # รีเฟรชทุกแท็บ
                self.refresh_all_tabs()
                
            except Exception as e:
                messagebox.showerror("Error", f"เกิดข้อผิดพลาด: {str(e)}")
        
        def cancel_checkout():
            checkout_window.destroy()
        
        ttk.Button(buttons_frame_bottom, text="บันทึกการขาย", command=save_transaction, 
                  style='Success.TButton').pack(side=LEFT, padx=5, fill=X, expand=True, ipady=10)
        ttk.Button(buttons_frame_bottom, text="ยกเลิก", command=cancel_checkout,
                  style='Cancel.TButton').pack(side=RIGHT, padx=5, fill=X, expand=True, ipady=10)
        
        # สร้าง styles
        style = ttk.Style()
        style.configure('Success.TButton', font=(None, 14, 'bold'))
        style.configure('Cancel.TButton', font=(None, 14))
        
        # เริ่มต้นการคำนวณเงินทอน
        update_change()

    def show_print_options(self, transaction_id, subtotal, vat, grand_total, received_amount, change_amount):
        """แสดงหน้าต่างตัวเลือกการพิมพ์"""
        print_window = Toplevel(self)
        print_window.title("ตัวเลือกการพิมพ์ใบเสร็จ")
        print_window.geometry("500x400")
        print_window.transient(self.master)
        print_window.grab_set()
        
        # ตำแหน่งกลางหน้าจอ
        print_window.update_idletasks()
        x = (print_window.winfo_screenwidth() // 2) - (250)
        y = (print_window.winfo_screenheight() // 2) - (200)
        print_window.geometry(f"500x400+{x}+{y}")
        
        # หัวข้อ
        Label(print_window, text="บันทึกการขายเรียบร้อยแล้ว! 🎉", 
              font=('Arial', 16, 'bold'), fg='green').pack(pady=20)
        
        # ข้อมูลการขาย
        info_frame = Frame(print_window, bg='#f0f0f0', relief=RIDGE, bd=2)
        info_frame.pack(fill=X, padx=20, pady=10)
        
        Label(info_frame, text=f"เลขที่ใบเสร็จ: {transaction_id}", 
              font=('Arial', 12, 'bold'), bg='#f0f0f0').pack(pady=5)
        Label(info_frame, text=f"ยอดรวม: {grand_total:,.2f} บาท", 
              font=('Arial', 11), bg='#f0f0f0').pack(pady=2)
        Label(info_frame, text=f"เงินทอน: {change_amount:,.2f} บาท", 
              font=('Arial', 11), bg='#f0f0f0').pack(pady=2)
        
        # ตัวเลือกการพิมพ์
        Label(print_window, text="เลือกประเภทใบเสร็จ:", 
              font=('Arial', 14, 'bold')).pack(pady=(20, 10))
        
        # ปุ่มต่างๆ
        button_frame = Frame(print_window)
        button_frame.pack(pady=20, fill=X, padx=20)
        
        # ข้อมูลสำหรับ callback
        transaction_data = {
            'transaction_id': transaction_id,
            'subtotal': subtotal,
            'vat': vat,
            'grand_total': grand_total,
            'received_amount': received_amount,
            'change_amount': change_amount
        }
        
        cart_items = list(self.cart.values())
        
        # ปุ่ม Export PDF
        if RECEIPT_AVAILABLE:
            pdf_btn = Button(button_frame, 
                            text="📄 Export PDF\n(ใบเสร็จขนาด A4)",
                            command=lambda: self.export_pdf_receipt(transaction_data, cart_items, print_window),
                            bg='#4CAF50', fg='white', font=('Arial', 11, 'bold'),
                            height=3, width=20)
            pdf_btn.pack(side=LEFT, padx=10, pady=5, fill=X, expand=True)
        else:
            Label(button_frame, text="PDF ไม่พร้อมใช้\n(ติดตั้ง reportlab)", 
                  fg='red', font=('Arial', 9)).pack(side=LEFT, padx=10)
        
        # ปุ่ม Thermal Print
        if THERMAL_AVAILABLE:
            thermal_btn = Button(button_frame,
                               text="🖨️ Print Receipt\n(Thermal Printer 80mm)",
                               command=lambda: self.print_thermal_receipt(transaction_data, cart_items, print_window),
                               bg='#2196F3', fg='white', font=('Arial', 11, 'bold'),
                               height=3, width=20)
            thermal_btn.pack(side=RIGHT, padx=10, pady=5, fill=X, expand=True)
        else:
            Label(button_frame, text="Thermal Printer ไม่พร้อมใช้\n(ติดตั้ง pywin32)", 
                  fg='red', font=('Arial', 9)).pack(side=RIGHT, padx=10)
        
        # ตัวเลือกเพิ่มเติม
        options_frame = Frame(print_window)
        options_frame.pack(pady=20, fill=X, padx=20)
        
        # ปุ่มพิมพ์ทั้งคู่
        if RECEIPT_AVAILABLE and THERMAL_AVAILABLE:
            both_btn = Button(options_frame,
                             text="📄🖨️ Export PDF และ Print Receipt",
                             command=lambda: self.export_and_print_both(transaction_data, cart_items, print_window),
                             bg='#FF9800', fg='white', font=('Arial', 11, 'bold'),
                             height=2)
            both_btn.pack(fill=X, pady=5)
        
        # ปุ่มข้าม
        skip_btn = Button(options_frame,
                         text="ข้าม (ไม่พิมพ์ใบเสร็จ)",
                         command=print_window.destroy,
                         font=('Arial', 10),
                         height=2)
        skip_btn.pack(fill=X, pady=5)
        
        # ปุ่มทดสอบเครื่องพิมพ์
        if THERMAL_AVAILABLE:
            test_frame = Frame(print_window)
            test_frame.pack(pady=10)
            
            test_btn = Button(test_frame,
                             text="🔧 ทดสอบ Thermal Printer",
                             command=self.test_thermal_printer,
                             font=('Arial', 9))
            test_btn.pack()

    def export_pdf_receipt(self, transaction_data, cart_items, parent_window):
        """Export ใบเสร็จเป็น PDF"""
        try:
            printer = ReceiptPrinter()
            filename = printer.print_receipt_from_transaction(
                transaction_id=transaction_data['transaction_id'],
                subtotal=transaction_data['subtotal'],
                vat=transaction_data['vat'],
                grand_total=transaction_data['grand_total'],
                received_amount=transaction_data['received_amount'],
                change_amount=transaction_data['change_amount'],
                cart_items=cart_items
            )
            
            messagebox.showinfo("สำเร็จ", 
                               f"Export PDF เรียบร้อย!\n"
                               f"ไฟล์: {filename}\n"
                               f"ไฟล์จะเปิดอัตโนมัติ")
            parent_window.destroy()
            
        except Exception as e:
            messagebox.showerror("ข้อผิดพลาด", 
                               f"ไม่สามารถ Export PDF ได้:\n{str(e)}")

    def print_thermal_receipt(self, transaction_data, cart_items, parent_window):
        """พิมพ์ใบเสร็จด้วย Thermal Printer"""
        try:
            printer = ThermalPrinter()
            
            # เตรียมข้อมูลสำหรับ thermal printer
            transaction_data['datetime'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            success = printer.print_receipt(transaction_data, cart_items)
            
            if success:
                messagebox.showinfo("สำเร็จ", 
                                   f"พิมพ์ใบเสร็จเรียบร้อย!\n"
                                   f"เลขที่: {transaction_data['transaction_id']}")
                parent_window.destroy()
            
        except Exception as e:
            messagebox.showerror("ข้อผิดพลาด", 
                               f"ไม่สามารถพิมพ์ได้:\n{str(e)}\n\n"
                               f"กรุณาตรวจสอบ:\n"
                               f"• เครื่องพิมพ์เชื่อมต่อแล้ว\n"
                               f"• ติดตั้ง pywin32\n"
                               f"• เปิดเครื่องพิมพ์")

    def export_and_print_both(self, transaction_data, cart_items, parent_window):
        """Export PDF และ Print Thermal พร้อมกัน"""
        try:
            # Export PDF ก่อน
            pdf_printer = ReceiptPrinter()
            pdf_filename = pdf_printer.print_receipt_from_transaction(
                transaction_id=transaction_data['transaction_id'],
                subtotal=transaction_data['subtotal'],
                vat=transaction_data['vat'],
                grand_total=transaction_data['grand_total'],
                received_amount=transaction_data['received_amount'],
                change_amount=transaction_data['change_amount'],
                cart_items=cart_items
            )
            
            # Print Thermal
            thermal_printer = ThermalPrinter()
            transaction_data['datetime'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            thermal_printer.print_receipt(transaction_data, cart_items)
            
            messagebox.showinfo("สำเร็จ", 
                               f"Export PDF และพิมพ์ใบเสร็จเรียบร้อย!\n"
                               f"PDF: {pdf_filename}\n"
                               f"เลขที่: {transaction_data['transaction_id']}")
            parent_window.destroy()
            
        except Exception as e:
            messagebox.showerror("ข้อผิดพลาด", 
                               f"เกิดข้อผิดพลาด:\n{str(e)}")

    def test_thermal_printer(self):
        """ทดสอบ Thermal Printer"""
        try:
            printer = ThermalPrinter()
            success, message = printer.test_printer()
            
            if success:
                messagebox.showinfo("ทดสอบสำเร็จ", f"✅ {message}")
            else:
                messagebox.showerror("ทดสอบล้มเหลว", f"❌ {message}")
                
        except Exception as e:
            messagebox.showerror("ข้อผิดพลาด", f"ไม่สามารถทดสอบได้:\n{str(e)}")

    def test_pdf_receipt(self):
        """ทดสอบ PDF Receipt"""
        if not self.cart:
            messagebox.showwarning("Warning", "ไม่มีสินค้าในตะกร้า\nกรุณาเพิ่มสินค้าเพื่อทดสอบ")
            return
        
        try:
            subtotal, vat, grand_total = self.calculate_totals()
            
            printer = ReceiptPrinter()
            filename = printer.print_receipt_from_transaction(
                transaction_id="TEST_PDF",
                subtotal=subtotal,
                vat=vat,
                grand_total=grand_total,
                received_amount=grand_total + 100,
                change_amount=100,
                cart_items=list(self.cart.values())
            )
            
            messagebox.showinfo("ทดสอบ PDF สำเร็จ", f"✅ สร้าง PDF ทดสอบเรียบร้อย!\nไฟล์: {filename}")
            
        except Exception as e:
            messagebox.showerror("ทดสอบ PDF ล้มเหลว", f"❌ เกิดข้อผิดพลาด:\n{str(e)}")
        
    def clear_cart(self):
        """เคลียร์ตะกร้าสินค้า"""
        self.cart.clear()
        self.update_table_with_totals()
        self.search.focus()
        
    def refresh_all_tabs(self):
        """รีเฟรชข้อมูลทุกแท็บหลังการขาย"""
        try:
            # รีเฟรชปุ่มสินค้าในแท็บขาย
            self.refresh_product_buttons()
            
            # รีเฟรชตารางสินค้าในแท็บ Product
            if self.product_tab:
                self.product_tab.update_table_product()
                
            # รีเฟรช Dashboard
            if self.dashboard_tab:
                self.dashboard_tab.refresh_data()
                
            # รีเฟรช Profit Tab
            if self.profit_tab:
                self.profit_tab.refresh_data()
                
            print("All tabs refreshed after checkout")
            
        except Exception as e:
            print(f"Error refreshing tabs: {str(e)}")
            
    def set_references(self, product_tab=None, dashboard_tab=None, profit_tab=None):
        """ตั้งค่า reference ไปยังแท็บอื่นๆ (เรียกหลังสร้างแท็บทั้งหมดแล้ว)"""
        self.product_tab = product_tab
        self.dashboard_tab = dashboard_tab
        self.profit_tab = profit_tab
            
    def refresh_product_buttons(self):
        """อัปเดตปุ่มสินค้าใหม่"""
        # ลบปุ่มเก่า
        for widget in self.F1.winfo_children():
            widget.destroy()
        # สร้างปุ่มใหม่
        self.create_product_buttons()