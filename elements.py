from tkinter import *
from tkinter import ttk, messagebox
from basicsql import *
import json

class SalesTab(Frame):
    def __init__(self, parent, product_tab=None, dashboard_tab=None):
        super().__init__(parent)
        self.pack(fill=BOTH, expand=True)
        
        # Reference ไปยังแท็บอื่นๆ
        self.product_tab = product_tab
        self.dashboard_tab = dashboard_tab
        
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
        L1 = Label(self, text='เมนูสำหรับขายสินค้า', font=FONT1)
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
        """สร้างปุ่ม Checkout"""
        self.F4 = Frame(self.F2)
        self.F4.pack(pady=10, fill=X)
        
        self.btn_checkout = ttk.Button(self.F4, text="CHECKOUT", 
                                      command=self.open_checkout_window,
                                      style='Checkout.TButton')
        self.btn_checkout.pack(fill=X, ipady=10)
        
        # สร้าง style สำหรับปุ่ม checkout
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
                
                # แสดงข้อความสำเร็จ
                messagebox.showinfo("Success", f"บันทึกการขายเรียบร้อย\nTransaction ID: {transaction_id}\nเงินทอน: {change:,.2f} บาท")
                
                # เคลียร์ตะกร้า
                self.clear_cart()
                
                # รีเฟรชทุกแท็บ
                self.refresh_all_tabs()
                
                # ปิดหน้าต่าง
                checkout_window.destroy()
                
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
                
            print("All tabs refreshed after checkout")
            
        except Exception as e:
            print(f"Error refreshing tabs: {str(e)}")
            
    def set_references(self, product_tab=None, dashboard_tab=None):
        """ตั้งค่า reference ไปยังแท็บอื่นๆ (เรียกหลังสร้างแท็บทั้งหมดแล้ว)"""
        self.product_tab = product_tab
        self.dashboard_tab = dashboard_tab
            
    def refresh_product_buttons(self):
        """อัปเดตปุ่มสินค้าใหม่"""
        # ลบปุ่มเก่า
        for widget in self.F1.winfo_children():
            widget.destroy()
        # สร้างปุ่มใหม่
        self.create_product_buttons()


class ProductTab(Frame):
    def __init__(self, parent, sales_tab=None, dashboard_tab=None):
        super().__init__(parent)
        self.pack(fill=BOTH, expand=True)
        
        # Reference ไปยังแท็บอื่นๆ
        self.sales_tab = sales_tab
        self.dashboard_tab = dashboard_tab
        
        # ตัวแปร
        self.v_barcode2 = StringVar()
        self.v_title2 = StringVar()
        self.v_price2 = StringVar()
        self.v_cost2 = StringVar()
        self.v_quantity2 = StringVar()
        self.v_unit2 = StringVar()
        self.v_category2 = StringVar()
        self.v_unit2.set('ชิ้น')
        self.v_category2.set('fruit')
        
        # โหมดแก้ไข
        self.edit_mode = False
        self.current_barcode = None
        
        # สร้าง GUI
        self.create_widgets()
        
    def create_widgets(self):
        FONT1 = (None, 20)
        FONT2 = (None, 18)
        
        # Frame สำหรับเพิ่มสินค้า
        self.FT21 = Frame(self)
        self.FT21.place(x=600, y=50)
        
        self.L2 = Label(self.FT21, text='เพิ่มสินค้า', font=FONT1)
        self.L2.pack(pady=20)
        
        # Form เพิ่มสินค้า
        Label(self.FT21, text='barcode', font=FONT2).pack()
        self.ET21 = ttk.Entry(self.FT21, textvariable=self.v_barcode2, font=FONT2)
        self.ET21.pack()
        
        Label(self.FT21, text='ชื่อสินค้า', font=FONT2).pack()
        self.ET22 = ttk.Entry(self.FT21, textvariable=self.v_title2, font=FONT2)
        self.ET22.pack()
        
        Label(self.FT21, text='ราคาขาย', font=FONT2).pack()
        self.ET23 = ttk.Entry(self.FT21, textvariable=self.v_price2, font=FONT2)
        self.ET23.pack()
        
        Label(self.FT21, text='ราคาทุน', font=FONT2).pack()
        self.ET24 = ttk.Entry(self.FT21, textvariable=self.v_cost2, font=FONT2)
        self.ET24.pack()
        
        Label(self.FT21, text='จำนวนสต็อก', font=FONT2).pack()
        self.ET25 = ttk.Entry(self.FT21, textvariable=self.v_quantity2, font=FONT2)
        self.ET25.pack()
        
        Label(self.FT21, text='หน่วย', font=FONT2).pack()
        self.unit_frame = Frame(self.FT21)
        self.unit_frame.pack()
        
        # Dropdown สำหรับเลือกหน่วย
        units = ['ชิ้น', 'ลูก', 'กิโลกรัม', 'กรัม', 'แผง', 'ขวด', 'ถุง', 'กล่อง']
        self.ET26 = ttk.Combobox(self.unit_frame, textvariable=self.v_unit2, 
                                values=units, font=FONT2, width=18, state='readonly')
        self.ET26.pack()
        
        Label(self.FT21, text='ประเภท', font=FONT2).pack()
        self.ET27 = ttk.Entry(self.FT21, textvariable=self.v_category2, font=FONT2)
        self.ET27.pack()
        
        # ปุ่มจัดการ
        button_frame = Frame(self.FT21)
        button_frame.pack(pady=20)
        
        self.btn_save = ttk.Button(button_frame, text='บันทึก', command=self.savedata)
        self.btn_save.grid(row=0, column=0, padx=5, ipadx=20, ipady=10)
        
        self.btn_edit = ttk.Button(button_frame, text='แก้ไข', command=self.edit_product)
        self.btn_edit.grid(row=0, column=1, padx=5, ipadx=20, ipady=10)
        
        self.btn_delete = ttk.Button(button_frame, text='ลบ', command=self.delete_product)
        self.btn_delete.grid(row=0, column=2, padx=5, ipadx=20, ipady=10)
        
        self.btn_cancel = ttk.Button(button_frame, text='ยกเลิก', command=self.cancel_edit)
        self.btn_cancel.grid(row=0, column=3, padx=5, ipadx=20, ipady=10)
        
        # Frame สำหรับตารางสินค้า
        self.FT22 = Frame(self)
        self.FT22.place(x=20, y=50)
        
        # ตารางแสดงสินค้า
        self.create_product_table()
        self.update_table_product()
        
        # Focus ที่ช่องบาร์โค้ด
        self.ET21.focus()
        
    def create_product_table(self):
        """สร้างตารางแสดงข้อมูลสินค้า"""
        product_header = ['barcode', 'title', 'price', 'cost', 'quantity', 'unit', 'category']
        product_width = [100, 150, 80, 80, 70, 80, 100]
        
        self.table_product = ttk.Treeview(self.FT22, columns=product_header, 
                                         show='headings', height=10)
        self.table_product.pack()
        
        for hd, w in zip(product_header, product_width):
            self.table_product.heading(hd, text=hd)
            self.table_product.column(hd, width=w, anchor='center')
            
        self.table_product.column('title', anchor='w')
        self.table_product.column('price', anchor='e')
        self.table_product.column('cost', anchor='e')
        self.table_product.column('quantity', anchor='e')
        
        # Event การคลิกแถว
        self.table_product.bind('<ButtonRelease-1>', self.on_row_select)
        
    def update_table_product(self):
        """อัปเดตข้อมูลในตารางสินค้า"""
        self.table_product.delete(*self.table_product.get_children())
        data = view_product(allfield=False)
        for d in data:
            self.table_product.insert('', 'end', values=d)
            
    def savedata(self):
        """บันทึกข้อมูลสินค้าใหม่หรืออัปเดต"""
        barcode = self.v_barcode2.get()
        title = self.v_title2.get()
        price = self.v_price2.get()
        cost = self.v_cost2.get()
        quantity = self.v_quantity2.get()
        unit = self.v_unit2.get()
        category = self.v_category2.get()
        
        if not all([barcode, title, price, cost, quantity, unit, category]):
            messagebox.showerror("Error", "กรุณากรอกข้อมูลให้ครบทุกช่อง")
            return
            
        try:
            price = float(price)
            cost = float(cost)
            quantity = int(quantity)
            
            if self.edit_mode:
                # อัปเดตข้อมูล
                update_product(barcode, title, price, cost, quantity, unit, category)
                messagebox.showinfo("Success", "อัปเดตข้อมูลสินค้าเรียบร้อยแล้ว")
                self.cancel_edit()
            else:
                # เพิ่มข้อมูลใหม่
                insert_product(barcode, title, price, cost, quantity, unit, category)
                messagebox.showinfo("Success", "บันทึกข้อมูลสินค้าเรียบร้อยแล้ว")
            
            # เคลียร์ข้อมูลในฟอร์ม
            self.clear_form()
            
            # อัปเดตตาราง
            self.update_table_product()
            
            # อัปเดตปุ่มสินค้าในแท็บขาย (ถ้ามี)
            if self.sales_tab:
                self.sales_tab.refresh_product_buttons()
                
            # อัปเดต Dashboard (ถ้ามี)
            if self.dashboard_tab:
                self.dashboard_tab.refresh_data()
                
            # กลับไป focus ที่ช่องบาร์โค้ด
            self.ET21.focus()
            
        except ValueError:
            messagebox.showerror("Error", "กรุณากรอกราคา/ทุน/จำนวนเป็นตัวเลข")
        except Exception as e:
            messagebox.showerror("Error", f"เกิดข้อผิดพลาด: {str(e)}")
            
    def clear_form(self):
        """เคลียร์ข้อมูลในฟอร์ม"""
        self.v_barcode2.set('')
        self.v_title2.set('')
        self.v_price2.set('')
        self.v_cost2.set('')
        self.v_quantity2.set('')
        self.v_unit2.set('ชิ้น')
        self.v_category2.set('fruit')
        
    def on_row_select(self, event):
        """เมื่อคลิกเลือกแถวในตาราง"""
        selection = self.table_product.selection()
        if selection:
            item = self.table_product.item(selection[0])
            values = item['values']
            
            # โหลดข้อมูลลงฟอร์ม
            self.v_barcode2.set(values[0])
            self.v_title2.set(values[1])
            self.v_price2.set(values[2])
            self.v_cost2.set(values[3])
            self.v_quantity2.set(values[4])
            self.v_unit2.set(values[5])
            self.v_category2.set(values[6])
            
    def edit_product(self):
        """เข้าสู่โหมดแก้ไขสินค้า"""
        if not self.v_barcode2.get():
            messagebox.showwarning("Warning", "กรุณาเลือกสินค้าที่ต้องการแก้ไขจากตาราง")
            return
            
        self.edit_mode = True
        self.current_barcode = self.v_barcode2.get()
        self.L2.config(text='แก้ไขสินค้า')
        self.ET21.config(state='disabled')  # ไม่ให้แก้ไขบาร์โค้ด
        
    def delete_product(self):
        """ลบสินค้า"""
        if not self.v_barcode2.get():
            messagebox.showwarning("Warning", "กรุณาเลือกสินค้าที่ต้องการลบจากตาราง")
            return
            
        result = messagebox.askyesno("Confirm", f"คุณต้องการลบสินค้า {self.v_title2.get()} หรือไม่?")
        if result:
            try:
                delete_product(self.v_barcode2.get())
                messagebox.showinfo("Success", "ลบสินค้าเรียบร้อยแล้ว")
                self.clear_form()
                self.update_table_product()
                
                # อัปเดตปุ่มสินค้าในแท็บขาย
                if self.sales_tab:
                    self.sales_tab.refresh_product_buttons()
                    
                # อัปเดต Dashboard
                if self.dashboard_tab:
                    self.dashboard_tab.refresh_data()
                    
            except Exception as e:
                messagebox.showerror("Error", f"เกิดข้อผิดพลาด: {str(e)}")
                
    def cancel_edit(self):
        """ยกเลิกการแก้ไข"""
        self.edit_mode = False
        self.current_barcode = None
        self.L2.config(text='เพิ่มสินค้า')
        self.ET21.config(state='normal')
        self.clear_form()
        self.ET21.focus()
                
    def set_references(self, sales_tab=None, dashboard_tab=None):
        """ตั้งค่า reference ไปยังแท็บอื่นๆ (เรียกหลังสร้างแท็บทั้งหมดแล้ว)"""
        self.sales_tab = sales_tab
        self.dashboard_tab = dashboard_tab


class DashboardTab(Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.pack(fill=BOTH, expand=True)
        
        # สร้าง GUI
        self.create_widgets()
        
    def create_widgets(self):
        FONT1 = (None, 20)
        FONT2 = (None, 14)
        
        # หัวข้อ
        Label(self, text='Dashboard - สรุปข้อมูลร้าน', font=FONT1).pack(pady=10)
        
        # Frame หลัก
        main_frame = Frame(self)
        main_frame.pack(fill=BOTH, expand=True, padx=20, pady=10)
        
        # ส่วนสรุปข้อมูลสินค้า
        self.create_product_summary(main_frame)
        
        # ส่วนตารางสินค้าคงเหลือ
        self.create_stock_table(main_frame)
        
        # ปุ่มรีเฟรช
        refresh_btn = ttk.Button(main_frame, text="รีเฟรชข้อมูล", command=self.refresh_data)
        refresh_btn.pack(pady=10)
        
        # โหลดข้อมูลครั้งแรก
        self.refresh_data()
        
    def create_product_summary(self, parent):
        """สร้างส่วนสรุปข้อมูลสินค้า"""
        summary_frame = LabelFrame(parent, text="สรุปข้อมูลสินค้า", font=(None, 14))
        summary_frame.pack(fill=X, pady=10)
        
        # ตัวแปรสำหรับแสดงข้อมูลสรุป
        self.v_total_products = StringVar()
        self.v_total_stock = StringVar()
        self.v_low_stock = StringVar()
        self.v_out_of_stock = StringVar()
        self.v_total_value = StringVar()
        
        # Grid layout สำหรับข้อมูลสรุป
        info_frame = Frame(summary_frame)
        info_frame.pack(padx=20, pady=15)
        
        # แถวที่ 1
        Label(info_frame, text="จำนวนสินค้าทั้งหมด:", font=(None, 12)).grid(row=0, column=0, sticky='w', padx=10, pady=5)
        Label(info_frame, textvariable=self.v_total_products, font=(None, 12, 'bold'), fg='blue').grid(row=0, column=1, sticky='w', padx=10, pady=5)
        
        Label(info_frame, text="สต็อกรวม:", font=(None, 12)).grid(row=0, column=2, sticky='w', padx=10, pady=5)
        Label(info_frame, textvariable=self.v_total_stock, font=(None, 12, 'bold'), fg='green').grid(row=0, column=3, sticky='w', padx=10, pady=5)
        
        # แถวที่ 2
        Label(info_frame, text="สินค้าใกล้หมด (≤5):", font=(None, 12)).grid(row=1, column=0, sticky='w', padx=10, pady=5)
        Label(info_frame, textvariable=self.v_low_stock, font=(None, 12, 'bold'), fg='orange').grid(row=1, column=1, sticky='w', padx=10, pady=5)
        
        Label(info_frame, text="สินค้าหมดสต็อก:", font=(None, 12)).grid(row=1, column=2, sticky='w', padx=10, pady=5)
        Label(info_frame, textvariable=self.v_out_of_stock, font=(None, 12, 'bold'), fg='red').grid(row=1, column=3, sticky='w', padx=10, pady=5)
        
        # แถวที่ 3
        Label(info_frame, text="มูลค่าสต็อกรวม:", font=(None, 12)).grid(row=2, column=0, sticky='w', padx=10, pady=5)
        Label(info_frame, textvariable=self.v_total_value, font=(None, 12, 'bold'), fg='purple').grid(row=2, column=1, sticky='w', padx=10, pady=5)
        
    def create_stock_table(self, parent):
        """สร้างตารางแสดงสินค้าคงเหลือ"""
        table_frame = LabelFrame(parent, text="รายการสินค้าคงเหลือ", font=(None, 14))
        table_frame.pack(fill=BOTH, expand=True, pady=10)
        
        # สร้าง Treeview พร้อม scrollbar
        tree_frame = Frame(table_frame)
        tree_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        # Headers และ widths
        headers = ['บาร์โค้ด', 'ชื่อสินค้า', 'ราคาขาย', 'ราคาทุน', 'สต็อก', 'หน่วย', 'หมวดหมู่', 'สถานะ', 'มูลค่า']
        widths = [100, 180, 80, 80, 60, 80, 100, 80, 100]
        
        self.stock_table = ttk.Treeview(tree_frame, columns=headers, show='headings', height=15)
        
        # กำหนด heading และ column
        for header, width in zip(headers, widths):
            self.stock_table.heading(header, text=header)
            self.stock_table.column(header, width=width, anchor='center')
            
        # จัด alignment ให้เหมาะสม
        self.stock_table.column('ชื่อสินค้า', anchor='w')
        self.stock_table.column('ราคาขาย', anchor='e')
        self.stock_table.column('ราคาทุน', anchor='e')
        self.stock_table.column('สต็อก', anchor='e')
        self.stock_table.column('มูลค่า', anchor='e')
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient=VERTICAL, command=self.stock_table.yview)
        self.stock_table.configure(yscrollcommand=scrollbar.set)
        
        # Pack table และ scrollbar
        self.stock_table.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)
        
    def refresh_data(self):
        """รีเฟรชข้อมูลทั้งหมด"""
        try:
            # ดึงข้อมูลสินค้าทั้งหมด
            products = view_product(allfield=False)
            
            # คำนวณข้อมูลสรุป
            total_products = len(products)
            total_stock = 0
            low_stock_count = 0
            out_of_stock_count = 0
            total_value = 0
            
            # เคลียร์ตาราง
            for item in self.stock_table.get_children():
                self.stock_table.delete(item)
                
            # วนลูปผ่านสินค้าแต่ละรายการ
            for product in products:
                if len(product) >= 7:  # ตรวจสอบว่ามีข้อมูลครบ (รวมหน่วย)
                    try:
                        barcode, title, price, cost, quantity, unit, category = product
                        
                        # แปลงข้อมูลให้เป็นชนิดที่ถูกต้อง
                        price = float(price)
                        cost = float(cost) 
                        quantity = int(quantity)
                        
                        # คำนวณสถิติ
                        total_stock += quantity
                        item_value = cost * quantity
                        total_value += item_value
                        
                        # กำหนดสถานะ
                        if quantity == 0:
                            status = "หมดสต็อก"
                            out_of_stock_count += 1
                        elif quantity <= 5:
                            status = "ใกล้หมด"
                            low_stock_count += 1
                        else:
                            status = "ปกติ"
                        
                        # เพิ่มข้อมูลลงตาราง
                        item_id = self.stock_table.insert('', 'end', values=[
                            barcode, title, f"{price:,.2f}", f"{cost:,.2f}", 
                            quantity, unit, category, status, f"{item_value:,.2f}"
                        ])
                        
                        # เปลี่ยนสีตามสถานะ
                        if quantity == 0:
                            self.stock_table.set(item_id, 'สต็อก', f"{quantity} ⚠️")
                        elif quantity <= 5:
                            self.stock_table.set(item_id, 'สต็อก', f"{quantity} ⚠️")
                            
                    except (ValueError, IndexError) as e:
                        # หากมีปัญหาในการแปลงข้อมูล ให้ข้ามรายการนี้
                        print(f"Error processing product {product}: {e}")
                        continue
            
            # อัปเดตข้อมูลสรุป
            self.v_total_products.set(f"{total_products} รายการ")
            self.v_total_stock.set(f"{total_stock:,} ชิ้น")
            self.v_low_stock.set(f"{low_stock_count} รายการ")
            self.v_out_of_stock.set(f"{out_of_stock_count} รายการ")
            self.v_total_value.set(f"{total_value:,.2f} บาท")
            
        except Exception as e:
            messagebox.showerror("Error", f"เกิดข้อผิดพลาดในการโหลดข้อมูล: {str(e)}")