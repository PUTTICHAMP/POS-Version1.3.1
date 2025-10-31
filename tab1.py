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
        super().__init__(parent, bg='#ffffff')
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

        header_frame = Frame(self, bg= '#f0f0f0', height=40)
        header_frame.pack(fill=X)
        header_frame.pack_propagate(False)
        # title_label = Label(self, text='จัดการข้อมูลสินค้า', font=('Arial', 18, 'bold'))
        Label(header_frame, text='🛒 ระบบขายสินค้า', 
              font=('Arial', 18, 'bold',), 
              fg='white', bg='#1e40af').pack(pady=5)

        main_container = Frame(self, bg='#ffffff')
        main_container.pack(fill=BOTH, expand=True, padx=20, pady=20)
        
        # Frame สำหรับปุ่มสินค้า
        self.F1 = Frame(self, bg='#ffffff', height=80)
        self.F1.place(x=70, y=60)
        
        # สร้างปุ่มสินค้าจากฐานข้อมูล
        self.create_product_buttons()
        
        # Frame สำหรับตารางขาย
        self.F2 = Frame(self)
        self.F2.place(x=750, y=50)
        
        # ช่องค้นหาบาร์โค้ด พร้อมป้ายกำกับ
        search_label_frame = Frame(self.F2)
        search_label_frame.pack(pady=(15, 5))
        
        Label(search_label_frame, text="🔍 สแกนบาร์โค้ดหรือค้นหา:", 
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
        
        # ⭐ ปุ่มล้างตะกร้าและลบสินค้าที่เลือก
        self.create_clear_button()
    
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
                if len(db) >= 5 and int(db[4]) <= 0:
                    continue
                    
                # แสดงชื่อสินค้า + บาร์โค้ด + สต็อก
                barcode_text = f"[{db[0]}]" if len(db) > 0 else ""
                stock_text = f"({db[4]} {db[5] if len(db) >= 6 else 'ชิ้น'})" if len(db) >= 6 else ""
                display_text = f"{db[1]}\n{barcode_text}\n{stock_text}"
                
                B = ttk.Button(self.F1, text=display_text, 
                              command=lambda pd=db: self.button_insert(pd[0], pd[1], pd[2], 1))
                B.grid(row=row, column=col, ipadx=10, ipady=20, padx=5, pady=5)
                col = col + 1
                if i % 4 == 0:
                    col = 0
                    row = row + 1
            except (ValueError, IndexError):
                B = ttk.Button(self.F1, text=db[1] if len(db) > 1 else "Unknown", 
                              command=lambda pd=db: self.button_insert(pd[0], pd[1], pd[2], 1))
                B.grid(row=row, column=col, ipadx=10, ipady=20, padx=5, pady=5)
                col = col + 1
                if i % 3 == 0:
                    col = 0
                    row = row + 1
                
    def create_sales_table(self):
        """สร้างตารางแสดงรายการขาย พร้อมคอลัมน์ Barcode"""
        # Style
        style = ttk.Style()
        style.configure('Treeview.Heading', font=(None, 12, 'bold'))
        style.configure('Treeview', font=(None, 10))
        
        # เพิ่มคอลัมน์ barcode
        sales_header = ['barcode', 'title', 'price', 'quantity', 'total']
        sales_width = [120, 180, 80, 80, 90]
        
        # สร้าง Frame container สำหรับตารางและ scrollbar
        table_frame = Frame(self.F2)
        table_frame.pack(fill=BOTH, expand=True)
        
        self.table_sales = ttk.Treeview(table_frame, columns=sales_header, 
                                       show='headings', height=8)
        self.table_sales.pack(side=LEFT, fill=BOTH, expand=True)
        
        # แก้ไขชื่อ heading ให้อ่านง่ายขึ้น
        header_names = {
            'barcode': 'บาร์โค้ด',
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
        
        # เพิ่ม scrollbar (ถ้าต้องการ)
        scrollbar = ttk.Scrollbar(table_frame, orient=VERTICAL, command=self.table_sales.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.table_sales.configure(yscrollcommand=scrollbar.set)
        
        # เพิ่ม tag สำหรับ alternating row colors
        self.table_sales.tag_configure('oddrow', background='#ffffff')
        self.table_sales.tag_configure('evenrow', background='#ffffff')
    
    def create_clear_button(self):
        """สร้างปุ่มล้างตะกร้าและปุ่มลบสินค้าที่เลือก"""
        clear_frame = Frame(self.F2, bg='#ffffff')
        clear_frame.pack(pady=5, fill=X)
        
        # ปุ่มลบสินค้าที่เลือก
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
        
        # Hover effect
        self.btn_delete_item.bind('<Enter>', lambda e: e.widget.config(bg='#f57c00'))
        self.btn_delete_item.bind('<Leave>', lambda e: e.widget.config(bg='#ff9800'))
        
        # ปุ่มล้างตะกร้า
        self.btn_clear_cart = Button(
            clear_frame,
            text='🗑️ ล้างตะกร้า',
            command=self.clear_cart_confirm,
            bg='#f44336',
            fg='white',
            font=('Arial', 10, 'bold'),
            cursor='hand2',
            relief=FLAT,
            pady=3
        )
        self.btn_clear_cart.pack(side=RIGHT, fill=X, expand=True, padx=(5, 0))
        
        # Hover effect
        self.btn_clear_cart.bind('<Enter>', lambda e: e.widget.config(bg='#d32f2f'))
        self.btn_clear_cart.bind('<Leave>', lambda e: e.widget.config(bg='#f44336'))
    
    def delete_selected_item(self):
        """ลบสินค้าที่เลือกในตาราง"""
        try:
            # ตรวจสอบว่ามีการเลือกสินค้าหรือไม่
            selected = self.table_sales.selection()
            
            if not selected:
                messagebox.showwarning(
                    "ไม่ได้เลือกสินค้า",
                    "กรุณาเลือกสินค้าที่ต้องการลบในตาราง"
                )
                return
            
            # ดึงข้อมูลสินค้าที่เลือก
            selected_item = self.table_sales.item(selected[0])
            values = selected_item['values']
            barcode = str(values[0])  # แปลง barcode เป็น string เพื่อให้ตรงกับ key ใน cart
            product_name = values[1]
            quantity = values[3]
            total = values[4]
            
            # Debug: แสดงข้อมูลที่กำลังจะลบ
            print(f"Attempting to delete - Barcode: {barcode}, Type: {type(barcode)}")
            print(f"Cart keys: {list(self.cart.keys())}")
            
            # ยืนยันการลบ
            confirm = messagebox.askyesno(
                "⚠️ ยืนยันการลบสินค้า",
                f"คุณต้องการลบสินค้านี้ออกจากตะกร้าใช่หรือไม่?\n\n"
                f"📦 สินค้า: {product_name}\n"
                f"🔢 Barcode: {barcode}\n"
                f"📊 จำนวน: {quantity} ชิ้น\n"
                f"💰 มูลค่า: {total} บาท",
                icon='warning'
            )
            
            if confirm:
                # ลบสินค้าออกจาก cart
                if barcode in self.cart:
                    del self.cart[barcode]
                    print(f"✅ Successfully deleted item with barcode: {barcode}")
                    
                    # ลบรายการออกจากตาราง
                    self.table_sales.delete(selected[0])
                    
                    # อัปเดตตารางและสรุปยอดใหม่
                    self.update_table_with_totals()
                    
                    # แสดงข้อความสำเร็จ
                    self.v_last_barcode.set(f"🗑️ ลบสินค้าแล้ว: {product_name}")
                    self.last_barcode_frame.config(bg='#fff9c4')
                    self.after(2000, lambda: self.reset_barcode_label())
                    
                    # Focus กลับไปที่ search box
                    self.search.focus()
                    
                    print(f"Cart after deletion: {list(self.cart.keys())}")
                else:
                    print(f"❌ Barcode {barcode} not found in cart")
                    messagebox.showerror(
                        "เกิดข้อผิดพลาด",
                        f"ไม่พบสินค้านี้ในตะกร้า\nBarcode: {barcode}"
                    )
                    
        except Exception as e:
            print(f"Error in delete_selected_item: {str(e)}")
            messagebox.showerror(
                "เกิดข้อผิดพลาด",
                f"ไม่สามารถลบสินค้าได้\n\nรายละเอียด: {str(e)}"
            )
    
    def clear_cart_confirm(self):
        """ล้างตะกร้าสินค้าทั้งหมด (พร้อมยืนยัน)"""
        try:
            # ตรวจสอบว่ามีสินค้าในตะกร้าหรือไม่
            if not self.cart or len(self.cart) == 0:
                messagebox.showinfo(
                    "ตะกร้าว่าง",
                    "ไม่มีสินค้าในตะกร้า"
                )
                return
            
            # นับจำนวนสินค้า
            total_items = len(self.cart)
            total_quantity = sum(item[3] for item in self.cart.values())
            subtotal, vat, grand_total = self.calculate_totals()
            
            # ยืนยันการล้างตะกร้า
            confirm = messagebox.askyesno(
                "⚠️ ยืนยันการล้างตะกร้า",
                f"คุณต้องการลบสินค้าทั้งหมดออกจากตะกร้าใช่หรือไม่?\n\n"
                f"📦 จำนวนรายการ: {total_items} รายการ\n"
                f"📊 จำนวนสินค้า: {total_quantity} ชิ้น\n"
                f"💰 มูลค่ารวม: {grand_total:,.2f} บาท\n\n"
                f"⚠️ การดำเนินการนี้ไม่สามารถย้อนกลับได้!",
                icon='warning'
            )
            
            if confirm:
                # เคลียร์ตะกร้า
                self.clear_cart()
                
                # แสดงข้อความสำเร็จ
                self.v_last_barcode.set(f"✅ ล้างตะกร้าเรียบร้อยแล้ว! ({total_items} รายการ)")
                self.last_barcode_frame.config(bg='#ffffff')
                self.after(3000, lambda: self.reset_barcode_label())
                
                print(f"Cart cleared: {total_items} items, {total_quantity} pieces")
                
        except Exception as e:
            messagebox.showerror(
                "เกิดข้อผิดพลาด",
                f"ไม่สามารถล้างตะกร้าได้\n\nรายละเอียด: {str(e)}"
            )
        
    def create_summary_section(self):
        """สร้างส่วนสรุปยอดขาย"""
        self.F3 = Frame(self.F2)
        self.F3.pack(pady=10, fill=X)
        
        self.v_subtotal = StringVar()
        self.v_vat = StringVar()
        self.v_grand_total = StringVar()
        
        Label(self.F3, text="ยอดรวม (Subtotal):", font=(None, 12)).grid(row=0, column=0, sticky='e', padx=5)
        Label(self.F3, textvariable=self.v_subtotal, font=(None, 12, 'bold'), width=15, anchor='e').grid(row=0, column=1, sticky='e', padx=5)
        
        Label(self.F3, text="VAT 7%:", font=(None, 12)).grid(row=1, column=0, sticky='e', padx=5)
        Label(self.F3, textvariable=self.v_vat, font=(None, 12, 'bold'), width=15, anchor='e').grid(row=1, column=1, sticky='e', padx=5)
        
        ttk.Separator(self.F3, orient='horizontal').grid(row=2, column=0, columnspan=2, sticky='ew', pady=5)
        
        Label(self.F3, text="รวมทั้งหมด (Grand Total):", font=(None, 14, 'bold')).grid(row=3, column=0, sticky='e', padx=5)
        Label(self.F3, textvariable=self.v_grand_total, font=(None, 14, 'bold'), fg='red', width=15, anchor='e').grid(row=3, column=1, sticky='e', padx=5)
        
        self.update_summary()
        
    def create_checkout_button(self):
        """สร้างปุ่ม Checkout และปุ่มทดสอบ"""
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
        """คำนวณยอดรวมทั้งหมด"""
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
        """อัปเดตตารางพร้อมคำนวณยอดรวมแต่ละรายการ และแสดง Barcode"""
        self.table_sales.delete(*self.table_sales.get_children())
        
        for idx, item in enumerate(self.cart.values()):
            barcode = item[0]
            title = item[1]
            price = float(item[2])
            quantity = int(item[3])
            total = price * quantity
            
            # เพิ่มข้อมูลพร้อม Barcode และใช้ alternating colors
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
        
        # อัปเดต label แสดง barcode ล่าสุด
        self.v_last_barcode.set(f"✅ เพิ่มแล้ว: {t} | Barcode: {b}")
        self.last_barcode_frame.config(bg='#c8e6c9')
        
        # เปลี่ยนสีกลับหลัง 2 วินาที
        self.after(2000, lambda: self.reset_barcode_label())
            
        self.update_table_with_totals()
    
    def reset_barcode_label(self):
        """รีเซ็ต label barcode กลับเป็นสีปกติ"""
        self.last_barcode_frame.config(bg='#e8f5e9')
        self.v_last_barcode.set("พร้อมสแกนสินค้า...")
            
    def search_product(self, event=None):
        """ค้นหาสินค้าด้วยบาร์โค้ด"""
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
                
                # อัปเดต label แสดง barcode
                self.v_last_barcode.set(f"✅ เพิ่มแล้ว: {data[1]} | Barcode: {barcode}")
                self.last_barcode_frame.config(bg='#c8e6c9')
                self.after(2000, lambda: self.reset_barcode_label())
                    
                self.update_table_with_totals()
                    
                self.v_search.set('')
                self.search.focus()
            else:
                self.v_last_barcode.set(f"❌ ไม่พบสินค้า Barcode: {barcode}")
                self.last_barcode_frame.config(bg='#ffcdd2')
                self.after(2000, lambda: self.reset_barcode_label())
                
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
        
        checkout_window = Toplevel(self)
        checkout_window.title("ระบบชำระเงิน - Checkout")
        checkout_window.geometry("600x800")
        checkout_window.transient(self.master)
        checkout_window.grab_set()
        
        checkout_window.update_idletasks()
        x = (checkout_window.winfo_screenwidth() // 2) - (100 // 2)
        y = (checkout_window.winfo_screenheight() // 2) - (700 // 2)
        checkout_window.geometry(f"700x750+{x}+{y}")
        
        Label(checkout_window, text="ระบบชำระเงิน", font=(None, 20, 'bold')).pack(pady=10)
        
        summary_frame = LabelFrame(checkout_window, text="สรุปยอดขาย", font=(None, 14))
        summary_frame.pack(padx=20, pady=10, fill=X)
        
        Label(summary_frame, text=f"ยอดรวม: {subtotal:,.2f} บาท", font=(None, 12)).pack(anchor='w', padx=10, pady=2)
        Label(summary_frame, text=f"VAT 7%: {vat:,.2f} บาท", font=(None, 12)).pack(anchor='w', padx=10, pady=2)
        Label(summary_frame, text=f"รวมทั้งหมด: {grand_total:,.2f} บาท", font=(None, 16, 'bold'), fg='red').pack(anchor='w', padx=10, pady=5)
        
        payment_frame = LabelFrame(checkout_window, text="รับเงิน", font=(None, 14))
        payment_frame.pack(padx=20, pady=10, fill=X)
        
        received_var = StringVar()
        received_var.set("0")
        
        Label(payment_frame, text="เงินที่รับ:", font=(None, 12)).pack(anchor='w', padx=10)
        received_label = Label(payment_frame, textvariable=received_var, font=(None, 20, 'bold'), fg='blue')
        received_label.pack(anchor='w', padx=10, pady=5)
        
        bills_frame = Frame(payment_frame)
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
        
        manual_frame = Frame(payment_frame)
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
        
        buttons_frame_bottom = Frame(checkout_window)
        buttons_frame_bottom.pack(padx=20, pady=20, fill=X)
        
        def save_transaction():
            try:
                received = float(received_var.get().replace(',', ''))
                change = received - grand_total
                
                if received < grand_total:
                    messagebox.showerror("Error", "เงินที่รับไม่เพียงพอ")
                    return
                
                transaction_id = generate_transaction_id()
                items_data = json.dumps(list(self.cart.values()))
                
                insert_transaction(transaction_id, subtotal, vat, grand_total, received, change, items_data)
                
                for item in self.cart.values():
                    barcode = item[0]
                    quantity = item[3]
                    update_stock(barcode, quantity)
                
                checkout_window.destroy()
                
                self.show_print_options(transaction_id, subtotal, vat, grand_total, received, change)
                
                self.clear_cart()
                self.refresh_all_tabs()
                
            except Exception as e:
                messagebox.showerror("Error", f"เกิดข้อผิดพลาด: {str(e)}")
        
        def cancel_checkout():
            checkout_window.destroy()
        
        ttk.Button(buttons_frame_bottom, text="บันทึกการขาย", command=save_transaction, 
                  style='Success.TButton').pack(side=LEFT, padx=5, fill=X, expand=True, ipady=10)
        ttk.Button(buttons_frame_bottom, text="ยกเลิก", command=cancel_checkout,
                  style='Cancel.TButton').pack(side=RIGHT, padx=5, fill=X, expand=True, ipady=10)
        
        style = ttk.Style()
        style.configure('Success.TButton', font=(None, 14,'bold'))
        style.configure('Cancel.TButton', font=(None, 14,'bold'))
        
        update_change()

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
        else:
            Label(button_frame, text="PDF ไม่พร้อมใช้\n(ติดตั้ง reportlab)", 
                  fg='red', font=('Arial', 9)).pack(side=LEFT, padx=10)
        
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
        
        options_frame = Frame(print_window)
        options_frame.pack(pady=20, fill=X, padx=20)
        
        if RECEIPT_AVAILABLE and THERMAL_AVAILABLE:
            both_btn = Button(options_frame,
                             text="📄🖨️ Export PDF และ Print Receipt",
                             command=lambda: self.export_and_print_both(transaction_data, cart_items, print_window),
                             bg='#FF9800', fg='white', font=('Arial', 11, 'bold'),
                             height=2)
            both_btn.pack(fill=X, pady=5)
        
        skip_btn = Button(options_frame,
                         text="ข้าม (ไม่พิมพ์ใบเสร็จ)",
                         command=print_window.destroy,
                         font=('Arial', 10),
                         height=2)
        skip_btn.pack(fill=X, pady=5)
        
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
                
            print("All tabs refreshed after checkout")
            
        except Exception as e:
            print(f"Error refreshing tabs: {str(e)}")
            
    def set_references(self, product_tab=None, dashboard_tab=None, profit_tab=None):
        """ตั้งค่า reference ไปยังแท็บอื่นๆ"""
        self.product_tab = product_tab
        self.dashboard_tab = dashboard_tab
        self.profit_tab = profit_tab
            
    def refresh_product_buttons(self):
        """อัปเดตปุ่มสินค้าใหม่"""
        for widget in self.F1.winfo_children():
            widget.destroy()
        self.create_product_buttons()