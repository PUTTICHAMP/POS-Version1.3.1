from tkinter import *
from tkinter import ttk, messagebox
from basicsql import *
import json
from datetime import datetime, timedelta

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
    def __init__(self, parent, product_tab=None, dashboard_tab=None, profit_tab=None, credit_tab=None):
        super().__init__(parent, bg='#ffffff')
        self.pack(fill=BOTH, expand=True)
        
        # Reference ไปยังแท็บอื่นๆ
        self.product_tab = product_tab
        self.dashboard_tab = dashboard_tab
        self.profit_tab = profit_tab
        self.credit_tab = credit_tab
        
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

        header_frame = Frame(self)
        header_frame.pack(pady=10, fill=X, padx=20)

        title_label = Label(header_frame, text='🛒 ระบบขายสินค้า', font=('Arial', 18, 'bold'))
        title_label.pack(side=TOP)

        main_container = Frame(self, bg="#ffffff")
        main_container.pack(fill=BOTH, expand=True, padx=20, pady=20)
        
        # ⭐ สร้าง Frame พร้อม Canvas และ Scrollbar สำหรับปุ่มสินค้า
        product_container = Frame(self, bg='#ffffff', relief=RIDGE, bd=2)
        product_container.place(x=65, y=60, width=618, height=588)
        
        # สร้าง Canvas
        self.product_canvas = Canvas(product_container, bg="#ffffff", highlightthickness=0)
        
        # สร้าง Scrollbar แนวตั้ง
        v_scrollbar = ttk.Scrollbar(product_container, orient=VERTICAL, 
                                    command=self.product_canvas.yview)
        v_scrollbar.pack(side=RIGHT, fill=Y)
        
        # สร้าง Scrollbar แนวนอน
        h_scrollbar = ttk.Scrollbar(product_container, orient=HORIZONTAL,
                                    command=self.product_canvas.xview)
        h_scrollbar.pack(side=BOTTOM, fill=X)
        
        self.product_canvas.pack(side=LEFT, fill=BOTH, expand=True)
        
        # Configure canvas scrollbar
        self.product_canvas.configure(yscrollcommand=v_scrollbar.set,
                                     xscrollcommand=h_scrollbar.set)
        
        # สร้าง Frame ภายใน Canvas สำหรับใส่ปุ่ม
        self.F1 = Frame(self.product_canvas, bg='#ffffff')
        self.canvas_window = self.product_canvas.create_window((0, 0), 
                                                               window=self.F1, 
                                                               anchor='nw')
        
        # Bind event เพื่ออัปเดต scroll region
        self.F1.bind('<Configure>', self.on_frame_configure)
        
        # เพิ่ม Mouse wheel scrolling
        self.product_canvas.bind_all("<MouseWheel>", self.on_mousewheel)
        
        # สร้างปุ่มสินค้าจากฐานข้อมูล
        self.create_product_buttons()
        
        # Frame สำหรับตารางขาย
        self.F2 = Frame(self)
        self.F2.place(x=750, y=50)
        
        # ช่องค้นหารหัสสินค้า พร้อมป้ายกำกับ
        search_label_frame = Frame(self.F2)
        search_label_frame.pack(pady=(15, 5))
        
        Label(search_label_frame, text="🔍 ค้นหารหัสสินค้า:", 
              font=(None, 10, 'bold')).pack()
        
        self.search = ttk.Entry(self.F2, textvariable=self.v_search, font=(None, 25), width=12)
        self.search.pack(pady=(0, 9))
        self.search.bind('<Return>', self.search_product)
        self.search.focus()
        
        # Label แสดง Barcode ที่สแกนล่าสุด
        self.last_barcode_frame = Frame(self.F2, bg='#ffffff', relief=RIDGE, bd=2)
        self.last_barcode_frame.pack(fill=X, pady=(0, 8))
        
        self.v_last_barcode = StringVar()
        self.v_last_barcode.set("พร้อมสแกนสินค้า...")
        
        Label(self.last_barcode_frame, textvariable=self.v_last_barcode, 
              font=(None, 10), bg='#ffffff', fg='#2e7d32').pack(pady=3)
        
        # ตารางขาย
        self.create_sales_table()
        
        # ปุ่มล้างตะกร้าและลบสินค้าที่เลือก
        self.create_clear_button()
    
        # สรุปยอดขาย
        self.create_summary_section()
        
        # ปุ่ม Checkout
        self.create_checkout_button()
    
    def on_frame_configure(self, event=None):
        """อัปเดต scroll region เมื่อ frame มีการเปลี่ยนแปลง"""
        self.product_canvas.configure(scrollregion=self.product_canvas.bbox("all"))
    
    def on_mousewheel(self, event):
        """เลื่อน canvas ด้วย mouse wheel"""
        x, y = self.winfo_pointerxy()
        widget = self.winfo_containing(x, y)
        
        if widget == self.product_canvas or self.is_child_of(widget, self.product_canvas):
            self.product_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def is_child_of(self, widget, parent):
        """ตรวจสอบว่า widget เป็น child ของ parent หรือไม่"""
        if widget is None:
            return False
        if widget == parent:
            return True
        return self.is_child_of(widget.master, parent)
        
    def create_product_buttons(self):
        """สร้างปุ่มสินค้าจากฐานข้อมูล"""
        col = 0
        row = 0
        
        for i, db in enumerate(view_product(allfield=False), start=1):
            try:
                if len(db) >= 5 and int(db[4]) <= 0:
                    continue
                    
                barcode_text = f"[{db[0]}]" if len(db) > 0 else ""
                stock_text = f"({db[4]} {db[5] if len(db) >= 6 else 'ชิ้น'})" if len(db) >= 6 else ""
                display_text = f"{db[1]}\n{barcode_text}\n{stock_text}"
                
                B = ttk.Button(self.F1, text=display_text, 
                              command=lambda pd=db: self.button_insert(pd[0], pd[1], pd[2], 1))
                B.grid(row=row, column=col, ipadx=10, ipady=20, padx=5, pady=5, sticky='ew')
                col = col + 1
                if i % 4 == 0:
                    col = 0
                    row = row + 1
            except (ValueError, IndexError):
                B = ttk.Button(self.F1, text=db[1] if len(db) > 1 else "Unknown", 
                              command=lambda pd=db: self.button_insert(pd[0], pd[1], pd[2], 1))
                B.grid(row=row, column=col, ipadx=10, ipady=20, padx=5, pady=5, sticky='ew')
                col = col + 1
                if i % 4 == 0:
                    col = 0
                    row = row + 1
        
        for i in range(4):
            self.F1.grid_columnconfigure(i, weight=1, minsize=150)
        
        self.F1.update_idletasks()
        self.product_canvas.configure(scrollregion=self.product_canvas.bbox("all"))
                
    def create_sales_table(self):
        """สร้างตารางแสดงรายการขาย"""
        style = ttk.Style()
        style.configure('Treeview.Heading', font=(None, 12, 'bold'))
        style.configure('Treeview', font=(None, 10))
        
        sales_header = ['barcode', 'title', 'price', 'quantity', 'total']
        sales_width = [120, 180, 80, 80, 90]
        
        table_frame = Frame(self.F2)
        table_frame.pack(fill=BOTH, expand=True)
        
        self.table_sales = ttk.Treeview(table_frame, columns=sales_header, 
                                       show='headings', height=8)
        self.table_sales.pack(side=LEFT, fill=BOTH, expand=True)
        
        header_names = {
            'barcode': 'รหัสสินค้า',
            'title': 'ชื่อสินค้า',
            'price': 'ราคา (฿)',
            'quantity': 'จำนวน',
            'total': 'รวม (฿)'
        }
        
        for hd, w in zip(sales_header, sales_width):
            self.table_sales.heading(hd, text=header_names.get(hd, hd))
            self.table_sales.column(hd, width=w, anchor='center')
            
        self.table_sales.column('title', anchor='w')
        self.table_sales.column('barcode', anchor='center')
        self.table_sales.column('price', anchor='e')
        self.table_sales.column('quantity', anchor='e')
        self.table_sales.column('total', anchor='e')
        
        scrollbar = ttk.Scrollbar(table_frame, orient=VERTICAL, command=self.table_sales.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.table_sales.configure(yscrollcommand=scrollbar.set)
        
        self.table_sales.tag_configure('oddrow', background='#ffffff')
        self.table_sales.tag_configure('evenrow', background='#ffffff')
    
    def create_clear_button(self):
        """สร้างปุ่มล้างตะกร้า"""
        clear_frame = Frame(self.F2, bg='#ffffff')
        clear_frame.pack(pady=5, fill=X)
        
        self.btn_delete_item = Button(
            clear_frame,
            text='❌ ลบสินค้าที่เลือก',
            command=self.delete_selected_item,
            bg='#ff9800',
            fg='white',
            font=('Arial', 10, 'bold'),
            cursor='hand2',
            relief=FLAT,
            pady=3
        )
        self.btn_delete_item.pack(side=LEFT, fill=X, expand=True, padx=(0, 5))
        
        self.btn_delete_item.bind('<Enter>', lambda e: e.widget.config(bg='#f57c00'))
        self.btn_delete_item.bind('<Leave>', lambda e: e.widget.config(bg='#ff9800'))
        
        self.btn_clear_cart = Button(
            clear_frame,
            text='🗑️ล้างตะกร้า',
            command=self.clear_cart_confirm,
            bg='#f44336',
            fg='white',
            font=('Arial', 10, 'bold'),
            cursor='hand2',
            relief=FLAT,
            pady=3
        )
        self.btn_clear_cart.pack(side=RIGHT, fill=X, expand=True, padx=(5, 0))
        
        self.btn_clear_cart.bind('<Enter>', lambda e: e.widget.config(bg='#d32f2f'))
        self.btn_clear_cart.bind('<Leave>', lambda e: e.widget.config(bg='#f44336'))
    
    def delete_selected_item(self):
        """ลบสินค้าที่เลือก"""
        try:
            selected = self.table_sales.selection()
            
            if not selected:
                messagebox.showwarning("ไม่ได้เลือกสินค้า", "กรุณาเลือกสินค้าที่ต้องการลบในตาราง")
                return
            
            selected_item = self.table_sales.item(selected[0])
            values = selected_item['values']
            barcode = str(values[0])
            product_name = values[1]
            
            confirm = messagebox.askyesno("⚠️ ยืนยันการลบสินค้า",
                f"คุณต้องการลบสินค้านี้ออกจากตะกร้าใช่หรือไม่?\n\n📦 สินค้า: {product_name}")
            
            if confirm:
                if barcode in self.cart:
                    del self.cart[barcode]
                    self.table_sales.delete(selected[0])
                    self.update_table_with_totals()
                    
                    self.v_last_barcode.set(f"🗑️ ลบสินค้าแล้ว: {product_name}")
                    self.last_barcode_frame.config(bg='#fff9c4')
                    self.after(2000, lambda: self.reset_barcode_label())
                    self.search.focus()
                    
        except Exception as e:
            messagebox.showerror("เกิดข้อผิดพลาด", f"ไม่สามารถลบสินค้าได้\n\n{str(e)}")
    
    def clear_cart_confirm(self):
        """ล้างตะกร้าสินค้า"""
        try:
            if not self.cart:
                messagebox.showinfo("ตะกร้าว่าง", "ไม่มีสินค้าในตะกร้า")
                return
            
            total_items = len(self.cart)
            
            confirm = messagebox.askyesno("⚠️ ยืนยันการล้างตะกร้า",
                f"คุณต้องการลบสินค้าทั้งหมดออกจากตะกร้าใช่หรือไม่?\n\n📦 จำนวนรายการ: {total_items} รายการ")
            
            if confirm:
                self.clear_cart()
                self.v_last_barcode.set(f"✅ ล้างตะกร้าเรียบร้อยแล้ว!")
                self.after(3000, lambda: self.reset_barcode_label())
                
        except Exception as e:
            messagebox.showerror("เกิดข้อผิดพลาด", f"ไม่สามารถล้างตะกร้าได้\n\n{str(e)}")
        
    def create_summary_section(self):
        """สร้างส่วนสรุปยอดขาย"""
        self.F3 = Frame(self.F2)
        self.F3.pack(pady=10, fill=X)
        
        self.v_subtotal = StringVar()
        self.v_vat = StringVar()
        self.v_grand_total = StringVar()
        
        Label(self.F3, text="ยอดรวม:", font=(None, 12)).grid(row=0, column=0, sticky='e', padx=5)
        Label(self.F3, textvariable=self.v_subtotal, font=(None, 12, 'bold'), width=15, anchor='e').grid(row=0, column=1, sticky='e', padx=5)
        
        Label(self.F3, text="VAT 7%:", font=(None, 12)).grid(row=1, column=0, sticky='e', padx=5)
        Label(self.F3, textvariable=self.v_vat, font=(None, 12, 'bold'), width=15, anchor='e').grid(row=1, column=1, sticky='e', padx=5)
        
        ttk.Separator(self.F3, orient='horizontal').grid(row=2, column=0, columnspan=2, sticky='ew', pady=3)
        
        Label(self.F3, text="รวมทั้งหมด:", font=(None, 14, 'bold')).grid(row=3, column=0, sticky='e', padx=5)
        Label(self.F3, textvariable=self.v_grand_total, font=(None, 14, 'bold'), fg='red', width=15, anchor='e').grid(row=3, column=1, sticky='e', padx=5)
        
        self.update_summary()
        
    def create_checkout_button(self):
        """สร้างปุ่ม Checkout"""
        self.F4 = Frame(self.F2)
        self.F4.pack(pady=5, fill=X)
        
        self.btn_checkout = ttk.Button(self.F4, text="💳 CHECKOUT", 
                                      command=self.open_checkout_window,
                                      style='Checkout.TButton')
        self.btn_checkout.pack(fill=X, ipady=10)
        
        test_frame = Frame(self.F4)
        test_frame.pack(fill=X, pady=(10, 0))
        
        if RECEIPT_AVAILABLE:
            self.btn_test_pdf = ttk.Button(test_frame, text="📄 ทดสอบ PDF", 
                                          command=self.test_pdf_receipt)
            self.btn_test_pdf.pack(side=LEFT, padx=2, fill=X, expand=True)
        
        if THERMAL_AVAILABLE:
            self.btn_test_thermal = ttk.Button(test_frame, text="🖨️ ทดสอบ Thermal", 
                                              command=self.test_thermal_printer)
            self.btn_test_thermal.pack(side=RIGHT, padx=2, fill=X, expand=True)
        
        style = ttk.Style()
        style.configure('Checkout.TButton', font=(None, 10, 'bold'))
        
    def calculate_totals(self):
        """คำนวณยอดรวม"""
        subtotal = 0
        for item in self.cart.values():
            price = float(item[2])
            quantity = int(item[3])
            subtotal += price * quantity
            
        vat = subtotal * 0.07
        grand_total = subtotal + vat
        
        return subtotal, vat, grand_total
        
    def update_summary(self):
        """อัปเดตการแสดงยอดรวม"""
        subtotal, vat, grand_total = self.calculate_totals()
        
        self.v_subtotal.set(f"{subtotal:,.2f} บาท")
        self.v_vat.set(f"{vat:,.2f} บาท")
        self.v_grand_total.set(f"{grand_total:,.2f} บาท")
        
    def update_table_with_totals(self):
        """อัปเดตตาราง"""
        self.table_sales.delete(*self.table_sales.get_children())
        
        for idx, item in enumerate(self.cart.values()):
            barcode = item[0]
            title = item[1]
            price = float(item[2])
            quantity = int(item[3])
            total = price * quantity
            
            tag = 'evenrow' if idx % 2 == 0 else 'oddrow'
            self.table_sales.insert('', 'end', 
                                   values=[barcode, title, f"{price:,.2f}", quantity, f"{total:,.2f}"],
                                   tags=(tag,))
            
        self.update_summary()
        
    def button_insert(self, b, t, p, q=1):
        """เพิ่มสินค้าลงตะกร้า"""
        product_data = get_product_by_barcode(b)
        if product_data and len(product_data) >= 7:
            try:
                available_stock = int(product_data[5])
                current_qty = self.cart[b][3] if b in self.cart else 0
                
                if current_qty >= available_stock:
                    messagebox.showwarning("Warning", f"สินค้า {t} มีสต็อกเหลือ {available_stock} ชิ้น")
                    return
            except (ValueError, IndexError):
                pass
        
        if b not in self.cart:
            self.cart[b] = [b, t, p, q]
        else:
            self.cart[b][3] = self.cart[b][3] + 1
        
        self.v_last_barcode.set(f"✅ เพิ่มแล้ว: {t}")
        self.last_barcode_frame.config(bg='#c8e6c9')
        
        self.after(2000, lambda: self.reset_barcode_label())
            
        self.update_table_with_totals()
    
    def reset_barcode_label(self):
        """รีเซ็ต label barcode"""
        self.last_barcode_frame.config(bg='#e8f5e9')
        self.v_last_barcode.set("พร้อมสแกนสินค้า...")
            
    def search_product(self, event=None):
        """ค้นหาสินค้า"""
        barcode = self.v_search.get()
        try:
            data = search_barcode(barcode)
            if data:
                if len(data) >= 5:
                    try:
                        available_stock = int(data[4])
                        current_qty = self.cart[data[0]][3] if data[0] in self.cart else 0
                        
                        if current_qty >= available_stock:
                            messagebox.showwarning("Warning", f"สินค้า {data[1]} มีสต็อกเหลือ {available_stock} ชิ้น")
                            self.v_search.set('')
                            self.search.focus()
                            return
                    except (ValueError, IndexError):
                        pass
                
                if data[0] not in self.cart:
                    self.cart[data[0]] = [data[0], data[1], data[2], 1]
                else:
                    self.cart[data[0]][3] = self.cart[data[0]][3] + 1
                
                self.v_last_barcode.set(f"✅ เพิ่มแล้ว: {data[1]}")
                self.last_barcode_frame.config(bg='#c8e6c9')
                self.after(2000, lambda: self.reset_barcode_label())
                    
                self.update_table_with_totals()
                    
                self.v_search.set('')
                self.search.focus()
            else:
                self.v_last_barcode.set(f"❌ ไม่พบสินค้า")
                self.last_barcode_frame.config(bg='#ffcdd2')
                self.after(2000, lambda: self.reset_barcode_label())
                
                messagebox.showerror("Error", "ไม่พบสินค้าที่มีรหัสสินค้านี้")
                self.v_search.set('')
                self.search.focus()
        except Exception as e:
            messagebox.showerror("Error", f"เกิดข้อผิดพลาด: {str(e)}")
            self.v_search.set('')
            self.search.focus()
            
    def open_checkout_window(self):
        """เปิดหน้าต่าง Checkout พร้อมตัวเลือกวางบิล"""
        if not self.cart:
            messagebox.showwarning("Warning", "ไม่มีสินค้าในตะกร้า")
            return
            
        subtotal, vat, grand_total = self.calculate_totals()
        
        checkout_window = Toplevel(self)
        checkout_window.title("ระบบชำระเงิน - Checkout")
        checkout_window.geometry("700x780")
        checkout_window.transient(self.master)
        checkout_window.grab_set()
        
        checkout_window.update_idletasks()
        x = (checkout_window.winfo_screenwidth() // 2) - (50)
        y = (checkout_window.winfo_screenheight() // 2) - (435)
        checkout_window.geometry(f"700x780+{x}+{y}")
        
        # Header
        Label(checkout_window, text="ระบบชำระเงิน", font=(None, 19, 'bold')).pack(pady=5)
        
        # เลือกประเภทการชำระ
        payment_type_frame = LabelFrame(checkout_window, text="ประเภทการชำระเงิน", font=(None, 14))
        payment_type_frame.pack(padx=20, pady=10, fill=X)
        
        payment_type = StringVar(value='CASH')
        
        def toggle_payment_sections():
            """สลับการแสดงส่วนชำระเงิน/วางบิล"""
            if payment_type.get() == 'CASH':
                cash_frame.pack(padx=20, pady=10, fill=X, before=buttons_frame_bottom)
                credit_frame.pack_forget()
                change_frame.pack(padx=20, pady=10, fill=X, before=buttons_frame_bottom)
            else:
                cash_frame.pack_forget()
                change_frame.pack_forget()
                credit_frame.pack(padx=20, pady=10, fill=X, before=buttons_frame_bottom)
                load_customers_to_combobox()
        
        ttk.Radiobutton(payment_type_frame, text="💵 ชำระเงินสด", 
                       variable=payment_type, value='CASH',
                       command=toggle_payment_sections).pack(side=LEFT, padx=20, pady=10)
        ttk.Radiobutton(payment_type_frame, text="💳 วางบิล (เครดิต)", 
                       variable=payment_type, value='CREDIT',
                       command=toggle_payment_sections).pack(side=LEFT, padx=20, pady=10)
        
        # สรุปยอดขาย
        summary_frame = LabelFrame(checkout_window, text="สรุปยอดขาย", font=(None, 14))
        summary_frame.pack(padx=20, pady=10, fill=X)
        
        Label(summary_frame, text=f"ยอดรวม: {subtotal:,.2f} บาท", font=(None, 12)).pack(anchor='w', padx=10, pady=2)
        Label(summary_frame, text=f"VAT 7%: {vat:,.2f} บาท", font=(None, 12)).pack(anchor='w', padx=10, pady=2)
        Label(summary_frame, text=f"รวมทั้งหมด: {grand_total:,.2f} บาท", font=(None, 16, 'bold'), fg='red').pack(anchor='w', padx=10, pady=5)
        
        # ส่วนชำระเงินสด
        cash_frame = LabelFrame(checkout_window, text="รับเงิน", font=(None, 14))
        
        received_var = StringVar(value="0")
        
        Label(cash_frame, text="เงินที่รับ:", font=(None, 12)).pack(anchor='w', padx=10)
        received_label = Label(cash_frame, textvariable=received_var, font=(None, 20, 'bold'), fg='purple')
        received_label.pack(anchor='w', padx=10, pady=5)
        
        bills_frame = Frame(cash_frame)
        bills_frame.pack(padx=10, pady=10, fill=X)
        
        bills = [20, 50, 100, 500, 1000]
        
        def add_bill(amount):
            current = float(received_var.get().replace(',', ''))
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
            
        ttk.Button(buttons_frame, text="เคลียร์", command=clear_received).grid(row=0, column=len(bills), padx=10)
        
        manual_frame = Frame(cash_frame)
        manual_frame.pack(padx=10, pady=5, fill=X)
        
        Label(manual_frame, text="หรือกรอกจำนวนเงิน:", font=(None, 12)).pack(anchor='w')
        manual_entry = ttk.Entry(manual_frame, font=(None, 14), width=15)
        manual_entry.pack(anchor='w', pady=2)
        
        def add_manual():
            try:
                amount = float(manual_entry.get().replace(',', ''))
                current = float(received_var.get().replace(',', ''))
                new_amount = current + amount
                received_var.set(f"{new_amount:,.0f}")
                manual_entry.delete(0, END)
                update_change()
            except ValueError:
                messagebox.showerror("Error", "กรุณากรอกตัวเลขที่ถูกต้อง")
                
        ttk.Button(manual_frame, text="เพิ่ม", command=add_manual).pack(anchor='w', pady=2)
        
        # ส่วนเงินทอน
        change_frame = LabelFrame(checkout_window, text="เงินทอน", font=(None, 12))
        
        change_var = StringVar(value="0.00")
        
        Label(change_frame, text="เงินทอน:", font=(None, 12)).pack(anchor='w', padx=10)
        change_label = Label(change_frame, textvariable=change_var, font=(None, 20, 'bold'), fg='green')
        change_label.pack(anchor='w', padx=10, pady=4)
        
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
        
        # ส่วนวางบิล (เครดิต)
        credit_frame = LabelFrame(checkout_window, text="ข้อมูลลูกค้า (วางบิล)", font=(None, 14))
        
        Label(credit_frame, text="เลือกลูกค้า:", font=(None, 12)).pack(anchor='w', padx=10, pady=5)
        
        customer_var = StringVar()
        customer_combo = ttk.Combobox(credit_frame, textvariable=customer_var, 
                                     font=(None, 12), width=40, state='readonly')
        customer_combo.pack(padx=10, pady=5, fill=X)
        
        customer_info_frame = Frame(credit_frame, bg='#f0f0f0', relief=RIDGE, bd=2)
        customer_info_frame.pack(padx=10, pady=5, fill=X)
        
        customer_info_labels = {
            'credit_limit': StringVar(value='วงเงิน: -'),
            'credit_days': StringVar(value='ระยะเวลา: -'),
            'total_debt': StringVar(value='ยอดหนี้: -'),
            'available': StringVar(value='คงเหลือ: -')
        }
        
        for key, var in customer_info_labels.items():
            Label(customer_info_frame, textvariable=var, font=(None, 10), 
                  bg='#f0f0f0').pack(anchor='w', padx=5, pady=2)
        
        def load_customers_to_combobox():
            """โหลดรายชื่อลูกค้า"""
            try:
                customers = get_all_customers()
                customer_list = [f"{c[0]} - {c[1]}" for c in customers]
                customer_combo['values'] = customer_list
                
                if customer_list:
                    customer_combo.current(0)
                    update_customer_info()
                else:
                    messagebox.showwarning("Warning", 
                        "ไม่มีข้อมูลลูกค้า\nกรุณาเพิ่มลูกค้าก่อนใช้งานระบบเครดิต")
            except Exception as e:
                print(f"Error loading customers: {e}")
                messagebox.showerror("Error", f"ไม่สามารถโหลดข้อมูลลูกค้าได้\n{str(e)}")
        
        def update_customer_info(event=None):
            """อัปเดตข้อมูลลูกค้า"""
            try:
                selected = customer_var.get()
                if not selected:
                    return
                
                customer_id = selected.split(' - ')[0]
                customer = get_customer_by_id(customer_id)
                
                if customer:
                    credit_limit = customer[5]
                    credit_days = customer[6]
                    total_debt = customer[7]
                    available = credit_limit - total_debt
                    
                    customer_info_labels['credit_limit'].set(f"วงเงินเครดิต: {credit_limit:,.2f} บาท")
                    customer_info_labels['credit_days'].set(f"ระยะเวลาชำระ: {credit_days} วัน")
                    customer_info_labels['total_debt'].set(f"ยอดหนี้คงค้าง: {total_debt:,.2f} บาท")
                    customer_info_labels['available'].set(f"วงเงินคงเหลือ: {available:,.2f} บาท")
                    
                    if available < grand_total:
                        messagebox.showwarning("Warning", 
                            f"⚠️ วงเงินคงเหลือไม่เพียงพอ!\n\n"
                            f"ต้องการ: {grand_total:,.2f} บาท\n"
                            f"คงเหลือ: {available:,.2f} บาท")
                        
            except Exception as e:
                print(f"Error updating customer info: {e}")
        
        customer_combo.bind('<<ComboboxSelected>>', update_customer_info)
        
        # ปุ่มบันทึก
        buttons_frame_bottom = Frame(checkout_window)
        buttons_frame_bottom.pack(padx=20, pady=20, fill=X)
        
        def save_transaction():
            try:
                transaction_id = generate_transaction_id()
                items_data = json.dumps(list(self.cart.values()))
                
                if payment_type.get() == 'CASH':
                    # ชำระเงินสด
                    received = float(received_var.get().replace(',', ''))
                    change = received - grand_total
                    
                    if received < grand_total:
                        messagebox.showerror("Error", "เงินที่รับไม่เพียงพอ")
                        return
                    
                    insert_transaction(transaction_id, subtotal, vat, grand_total, 
                                     received, change, items_data)
                    
                    for item in self.cart.values():
                        barcode = item[0]
                        quantity = item[3]
                        update_stock(barcode, quantity)
                    
                    checkout_window.destroy()
                    self.show_print_options(transaction_id, subtotal, vat, grand_total, received, change)
                    
                else:
                    # วางบิล (เครดิต)
                    selected = customer_var.get()
                    if not selected:
                        messagebox.showerror("Error", "กรุณาเลือกลูกค้า")
                        return
                    
                    customer_id = selected.split(' - ')[0]
                    customer = get_customer_by_id(customer_id)
                    
                    if not customer:
                        messagebox.showerror("Error", "ไม่พบข้อมูลลูกค้า")
                        return
                    
                    # ตรวจสอบวงเงิน
                    credit_limit = customer[5]
                    total_debt = customer[7]
                    available = credit_limit - total_debt
                    
                    if available < grand_total:
                        confirm = messagebox.askyesno("Warning", 
                            f"⚠️ วงเงินคงเหลือไม่เพียงพอ!\n\n"
                            f"ต้องการ: {grand_total:,.2f} บาท\n"
                            f"คงเหลือ: {available:,.2f} บาท\n\n"
                            f"ต้องการดำเนินการต่อหรือไม่?")
                        if not confirm:
                            return
                    
                    # บันทึกธุรกรรม
                    insert_transaction(transaction_id, subtotal, vat, grand_total, 0, 0, items_data)
                    
                    # สร้างบิลเครดิต
                    bill_id = f"BILL{datetime.now().strftime('%Y%m%d%H%M%S')}"
                    credit_days = customer[6]
                    
                    insert_credit_bill(bill_id, customer_id, transaction_id, credit_days, grand_total)
                    
                    # อัปเดตสต็อก
                    for item in self.cart.values():
                        barcode = item[0]
                        quantity = item[3]
                        update_stock(barcode, quantity)
                    
                    checkout_window.destroy()
                    
                    due_date = (datetime.now() + timedelta(days=credit_days)).strftime('%d/%m/%Y')
                    
                    messagebox.showinfo("Success", 
                        f"✅ บันทึกการขายแบบวางบิลเรียบร้อย!\n\n"
                        f"เลขที่บิล: {bill_id}\n"
                        f"ลูกค้า: {customer[1]}\n"
                        f"ยอดเงิน: {grand_total:,.2f} บาท\n"
                        f"กำหนดชำระภายใน: {credit_days} วัน\n"
                        f"วันที่ครบกำหนด: {due_date}")
                    
                    # พิมพ์ใบวางบิล
                    self.print_credit_bill(bill_id, customer, transaction_id, 
                                         subtotal, vat, grand_total, credit_days)
                
                self.clear_cart()
                self.refresh_all_tabs()
                
            except Exception as e:
                messagebox.showerror("Error", f"เกิดข้อผิดพลาด: {str(e)}")
                import traceback
                traceback.print_exc()
        
        def cancel_checkout():
            checkout_window.destroy()
        
        ttk.Button(buttons_frame_bottom, text="💾 บันทึกการขาย", 
                  command=save_transaction, 
                  style='Success.TButton').pack(side=LEFT, padx=7, fill=X, expand=True, ipady=7)
        ttk.Button(buttons_frame_bottom, text="ยกเลิก", 
                  command=cancel_checkout,
                  style='Cancel.TButton').pack(side=RIGHT, padx=7, fill=X, expand=True, ipady=7)
        
        style = ttk.Style()
        style.configure('Success.TButton', font=(None, 10,'bold'))
        style.configure('Cancel.TButton', font=(None, 10,'bold'))
        
        # แสดงส่วนชำระเงินสดเริ่มต้น
        toggle_payment_sections()
        update_change()

    def print_credit_bill(self, bill_id, customer, transaction_id, 
                         subtotal, vat, grand_total, credit_days):
        """พิมพ์ใบวางบิล"""
        try:
            if not RECEIPT_AVAILABLE:
                print("Receipt printer not available")
                return
            
            printer = ReceiptPrinter()
            
            due_date = (datetime.now() + timedelta(days=credit_days)).strftime('%Y-%m-%d')
            
            transaction_data = {
                'transaction_id': bill_id,
                'datetime': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'subtotal': subtotal,
                'vat': vat,
                'grand_total': grand_total,
                'received_amount': 0,
                'change_amount': 0,
                'payment_type': 'CREDIT',
                'customer_name': customer[1],
                'customer_phone': customer[2] or '-',
                'credit_days': credit_days,
                'due_date': due_date
            }
            
            filename = printer.create_receipt(transaction_data, list(self.cart.values()), 
                                             f"credit_bill_{bill_id}.pdf")
            
            print(f"Credit bill created: {filename}")
            
        except Exception as e:
            print(f"Error printing credit bill: {e}")
            import traceback
            traceback.print_exc()

    def show_print_options(self, transaction_id, subtotal, vat, grand_total, received_amount, change_amount):
        """แสดงหน้าต่างตัวเลือกการพิมพ์"""
        print_window = Toplevel(self)
        print_window.title("ตัวเลือกการพิมพ์ใบเสร็จ")
        print_window.geometry("500x400")
        print_window.transient(self.master)
        print_window.grab_set()
        
        print_window.update_idletasks()
        x = (print_window.winfo_screenwidth() // 2) - (250)
        y = (print_window.winfo_screenheight() // 2) - (200)
        print_window.geometry(f"500x400+{x}+{y}")
        
        Label(print_window, text="บันทึกการขายเรียบร้อยแล้ว! 🎉", 
              font=('Arial', 16, 'bold'), fg='green').pack(pady=20)
        
        info_frame = Frame(print_window, bg='#f0f0f0', relief=RIDGE, bd=2)
        info_frame.pack(fill=X, padx=20, pady=10)
        
        Label(info_frame, text=f"เลขที่ใบเสร็จ: {transaction_id}", 
              font=('Arial', 12, 'bold'), bg='#f0f0f0').pack(pady=5)
        Label(info_frame, text=f"ยอดรวม: {grand_total:,.2f} บาท", 
              font=('Arial', 11), bg='#f0f0f0').pack(pady=2)
        Label(info_frame, text=f"เงินทอน: {change_amount:,.2f} บาท", 
              font=('Arial', 11), bg='#f0f0f0').pack(pady=2)
        
        Label(print_window, text="เลือกประเภทใบเสร็จ:", 
              font=('Arial', 14, 'bold')).pack(pady=(20, 10))
        
        button_frame = Frame(print_window)
        button_frame.pack(pady=20, fill=X, padx=20)
        
        transaction_data = {
            'transaction_id': transaction_id,
            'subtotal': subtotal,
            'vat': vat,
            'grand_total': grand_total,
            'received_amount': received_amount,
            'change_amount': change_amount
        }
        
        cart_items = list(self.cart.values())
        
        if RECEIPT_AVAILABLE:
            pdf_btn = Button(button_frame, 
                            text="📄 Export PDF\n(ใบเสร็จขนาด A4)",
                            command=lambda: self.export_pdf_receipt(transaction_data, cart_items, print_window),
                            bg='#4CAF50', fg='white', font=('Arial', 11, 'bold'),
                            height=3, width=20)
            pdf_btn.pack(side=LEFT, padx=10, pady=5, fill=X, expand=True)
        
        if THERMAL_AVAILABLE:
            thermal_btn = Button(button_frame,
                               text="🖨️ Print Receipt\n(Thermal Printer 80mm)",
                               command=lambda: self.print_thermal_receipt(transaction_data, cart_items, print_window),
                               bg='#2196F3', fg='white', font=('Arial', 11, 'bold'),
                               height=3, width=20)
            thermal_btn.pack(side=RIGHT, padx=10, pady=5, fill=X, expand=True)
        
        skip_btn = Button(print_window,
                         text="ข้าม (ไม่พิมพ์ใบเสร็จ)",
                         command=print_window.destroy,
                         font=('Arial', 10),
                         height=2)
        skip_btn.pack(pady=10, padx=20, fill=X)

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
                               f"Export PDF เรียบร้อย!\nไฟล์: {filename}\nไฟล์จะเปิดอัตโนมัติ")
            parent_window.destroy()
            
        except Exception as e:
            messagebox.showerror("ข้อผิดพลาด", f"ไม่สามารถ Export PDF ได้:\n{str(e)}")

    def print_thermal_receipt(self, transaction_data, cart_items, parent_window):
        """พิมพ์ใบเสร็จด้วย Thermal Printer"""
        try:
            printer = ThermalPrinter()
            transaction_data['datetime'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            success = printer.print_receipt(transaction_data, cart_items)
            
            if success:
                messagebox.showinfo("สำเร็จ", 
                                   f"พิมพ์ใบเสร็จเรียบร้อย!\nเลขที่: {transaction_data['transaction_id']}")
                parent_window.destroy()
            
        except Exception as e:
            messagebox.showerror("ข้อผิดพลาด", 
                               f"ไม่สามารถพิมพ์ได้:\n{str(e)}\n\nกรุณาตรวจสอบ:\n• เครื่องพิมพ์เชื่อมต่อแล้ว\n• ติดตั้ง pywin32\n• เปิดเครื่องพิมพ์")

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
        self.reset_barcode_label()
        self.search.focus()
        
    def refresh_all_tabs(self):
        """รีเฟรชข้อมูลทุกแท็บหลังการขาย"""
        try:
            self.refresh_product_buttons()
            
            if self.product_tab:
                self.product_tab.update_table_product()
                
            if self.dashboard_tab:
                self.dashboard_tab.refresh_data()
                
            if self.profit_tab:
                self.profit_tab.refresh_data()
            
            if self.credit_tab:
                self.credit_tab.refresh_data()
                
            print("All tabs refreshed after checkout")
            
        except Exception as e:
            print(f"Error refreshing tabs: {str(e)}")
            
    def set_references(self, product_tab=None, dashboard_tab=None, profit_tab=None, credit_tab=None):
        """ตั้งค่า reference ไปยังแท็บอื่นๆ"""
        self.product_tab = product_tab
        self.dashboard_tab = dashboard_tab
        self.profit_tab = profit_tab
        self.credit_tab = credit_tab
            
    def refresh_product_buttons(self):
        """อัปเดตปุ่มสินค้าใหม่"""
        for widget in self.F1.winfo_children():
            widget.destroy()
        self.create_product_buttons()