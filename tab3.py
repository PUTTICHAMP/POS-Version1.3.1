from tkinter import *
from tkinter import ttk, messagebox
from basicsql import *

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
        Label(self, text='Dashboard - สรุปข้อมูลร้าน', font=('Arial', 18, 'bold')).pack(pady=10)
        # Frame หลัก
        main_frame = Frame(self)
        main_frame.pack(fill=BOTH, expand=True, padx=20, pady=10)
        
        # ส่วนสรุปข้อมูลสินค้า
        self.create_product_summary(main_frame)
        
        # ส่วนการแจ้งเตือน
        self.create_alert_section(main_frame)
        
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
        Label(info_frame, text="สินค้าใกล้หมด (≤ Reorder Point):", font=(None, 12)).grid(row=1, column=0, sticky='w', padx=10, pady=5)
        Label(info_frame, textvariable=self.v_low_stock, font=(None, 12, 'bold'), fg='orange').grid(row=1, column=1, sticky='w', padx=10, pady=5)
        
        Label(info_frame, text="สินค้าหมดสต็อก:", font=(None, 12)).grid(row=1, column=2, sticky='w', padx=10, pady=5)
        Label(info_frame, textvariable=self.v_out_of_stock, font=(None, 12, 'bold'), fg='red').grid(row=1, column=3, sticky='w', padx=10, pady=5)
        
        # แถวที่ 3
        Label(info_frame, text="มูลค่าสต็อกรวม:", font=(None, 12)).grid(row=2, column=0, sticky='w', padx=10, pady=5)
        Label(info_frame, textvariable=self.v_total_value, font=(None, 12, 'bold'), fg='purple').grid(row=2, column=1, sticky='w', padx=10, pady=5)
        
    def create_alert_section(self, parent):
        """สร้างส่วนการแจ้งเตือน"""
        alert_frame = LabelFrame(parent, text="การแจ้งเตือน", font=(None, 14))
        alert_frame.pack(fill=X, pady=10)
        
        # Listbox สำหรับแสดงการแจ้งเตือน
        self.alert_listbox = Listbox(alert_frame, height=4, font=(None, 11))
        self.alert_listbox.pack(fill=X, padx=10, pady=10)
        
    def create_stock_table(self, parent):
        """สร้างตารางแสดงสินค้าคงเหลือ"""
        table_frame = LabelFrame(parent, text="รายการสินค้าคงเหลือ", font=(None, 14))
        table_frame.pack(fill=BOTH, expand=True, pady=10)
        
        # สร้าง Treeview พร้อม scrollbar
        tree_frame = Frame(table_frame)
        tree_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        # Headers และ widths
        headers = ['บาร์โค้ด', 'ชื่อสินค้า', 'ราคาขาย', 'ราคาทุน', 'สต็อก', 'หน่วย', 'หมวดหมู่', 'Reorder Point', 'สถานะ', 'มูลค่า']
        widths = [90, 150, 70, 70, 50, 60, 80, 80, 70, 80]
        
        self.stock_table = ttk.Treeview(tree_frame, columns=headers, show='headings', height=12)
        
        # กำหนด heading และ column
        for header, width in zip(headers, widths):
            self.stock_table.heading(header, text=header)
            self.stock_table.column(header, width=width, anchor='center')
            
        # จัด alignment ให้เหมาะสม
        self.stock_table.column('ชื่อสินค้า', anchor='w')
        self.stock_table.column('ราคาขาย', anchor='e')
        self.stock_table.column('ราคาทุน', anchor='e')
        self.stock_table.column('สต็อก', anchor='e')
        self.stock_table.column('Reorder Point', anchor='e')
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
            products = view_product(allfield=True)  # ใช้ allfield=True เพื่อได้ข้อมูลครบ
            
            # คำนวณข้อมูลสรุป
            total_products = len(products)
            total_stock = 0
            low_stock_count = 0
            out_of_stock_count = 0
            total_value = 0
            alert_messages = []
            
            # เคลียร์ตาราง
            for item in self.stock_table.get_children():
                self.stock_table.delete(item)
                
            # วนลูปผ่านสินค้าแต่ละรายการ
            for product in products:
                if len(product) >= 9:  # ตรวจสอบว่ามีข้อมูลครบ (รวม reorder_point)
                    try:
                        id_val, barcode, title, price, cost, quantity, unit, category, reorder_point = product[:9]
                        
                        # แปลงข้อมูลให้เป็นชนิดที่ถูกต้อง
                        price = float(price)
                        cost = float(cost) 
                        quantity = int(quantity)
                        reorder_point = int(reorder_point) if reorder_point else 5
                        
                        # คำนวณสถิติ
                        total_stock += quantity
                        item_value = cost * quantity
                        total_value += item_value
                        
                        # กำหนดสถานะตาม reorder point
                        if quantity == 0:
                            status = "หมดสต็อก"
                            out_of_stock_count += 1
                            alert_messages.append(f"⚠️ {title} - หมดสต็อก!")
                        elif quantity <= reorder_point:
                            status = "ต้องสั่งซื้อ"
                            low_stock_count += 1
                            alert_messages.append(f"🔄 {title} - สต็อกเหลือ {quantity} {unit} (ต้องสั่งซื้อ)")
                        else:
                            status = "ปกติ"
                        
                        # เพิ่มข้อมูลลงตาราง
                        item_id = self.stock_table.insert('', 'end', values=[
                            barcode, title, f"{price:,.2f}", f"{cost:,.2f}", 
                            quantity, unit, category, reorder_point, status, f"{item_value:,.2f}"
                        ])
                        
                        # เปลี่ยนสีตามสถานะ
                        if quantity == 0:
                            self.stock_table.set(item_id, 'สต็อก', f"{quantity} ⚠️")
                        elif quantity <= reorder_point:
                            self.stock_table.set(item_id, 'สต็อก', f"{quantity} 🔄")
                            
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
            
            # อัปเดตการแจ้งเตือน
            self.alert_listbox.delete(0, END)
            if alert_messages:
                for msg in alert_messages[:10]:  # แสดงแค่ 10 รายการแรก
                    self.alert_listbox.insert(END, msg)
            else:
                self.alert_listbox.insert(END, "✅ ไม่มีการแจ้งเตือน - สต็อกสินค้าปกติ")
            
        except Exception as e:
            messagebox.showerror("Error", f"เกิดข้อผิดพลาดในการโหลดข้อมูล: {str(e)}")