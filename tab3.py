from tkinter import *
from tkinter import ttk, messagebox
from basicsql import *

class DashboardTab(Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.pack(fill=BOTH, expand=True)
        
        # เก็บข้อมูลสำหรับการค้นหา
        self.all_products = []
        self.filtered_products = []
        
        # สร้าง Canvas และ Scrollbar สำหรับหน้าทั้งหมด
        self.canvas = Canvas(self, highlightthickness=0)
        self.main_scrollbar = ttk.Scrollbar(self, orient=VERTICAL, command=self.canvas.yview)
        self.scrollable_frame = Frame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.main_scrollbar.set)
        
        # ผูก event สำหรับการปรับขนาด
        self.canvas.bind('<Configure>', self._on_canvas_configure)
        
        # Pack canvas และ scrollbar
        self.canvas.pack(side=LEFT, fill=BOTH, expand=True)
        self.main_scrollbar.pack(side=RIGHT, fill=Y)
        
        # ผูก mousewheel กับ canvas และ children
        self._bind_mousewheel(self.scrollable_frame)
        
        # สร้าง GUI
        self.create_widgets()
    
    def _on_canvas_configure(self, event):
        """ปรับความกว้างของ scrollable_frame ให้เต็ม canvas"""
        canvas_width = event.width
        self.canvas.itemconfig(self.canvas_window, width=canvas_width)
    
    def _bind_mousewheel(self, widget):
        """ผูก mousewheel กับ widget และ children ทั้งหมด"""
        widget.bind("<Enter>", lambda e: self._bound_to_mousewheel(widget))
        widget.bind("<Leave>", lambda e: self._unbound_from_mousewheel(widget))
        
        for child in widget.winfo_children():
            self._bind_mousewheel(child)
    
    def _bound_to_mousewheel(self, widget):
        """เปิดใช้งาน mousewheel"""
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
    
    def _unbound_from_mousewheel(self, widget):
        """ปิดใช้งาน mousewheel"""
        self.canvas.unbind_all("<MouseWheel>")
    
    def _on_mousewheel(self, event):
        """จัดการ mousewheel scrolling"""
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def create_widgets(self):
        FONT1 = (None, 20)
        FONT2 = (None, 14)
        
        # ใช้ scrollable_frame แทน self
        parent = self.scrollable_frame
        
        # หัวข้อ
        Label(parent, text='📊 Dashboard - สรุปข้อมูลร้าน', font=('Arial', 18, 'bold')).pack(pady=10)
        
        # Frame หลัก (ไม่ใช้ padx เพื่อให้เต็มหน้าจอ)
        main_frame = Frame(parent)
        main_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        # ส่วนสรุปข้อมูลสินค้า
        self.create_product_summary(main_frame)
        
        # ส่วนการแจ้งเตือน
        self.create_alert_section(main_frame)
        
        # ส่วนค้นหาสินค้า (เพิ่มใหม่)
        self.create_search_section(main_frame)
        
        # ส่วนตารางสินค้าคงเหลือ
        self.create_stock_table(main_frame)
        
        # ปุ่มรีเฟรช
        refresh_btn = ttk.Button(main_frame, text="🔄 รีเฟรชข้อมูล", command=self.refresh_data)
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
        
        # Frame สำหรับ Listbox และ Scrollbar
        listbox_frame = Frame(alert_frame)
        listbox_frame.pack(fill=X, padx=10, pady=10)
        
        # Listbox สำหรับแสดงการแจ้งเตือน
        self.alert_listbox = Listbox(listbox_frame, height=4, font=(None, 11))
        alert_scrollbar = ttk.Scrollbar(listbox_frame, orient=VERTICAL, command=self.alert_listbox.yview)
        self.alert_listbox.configure(yscrollcommand=alert_scrollbar.set)
        
        self.alert_listbox.pack(side=LEFT, fill=BOTH, expand=True)
        alert_scrollbar.pack(side=RIGHT, fill=Y)
    
    def create_search_section(self, parent):
        """สร้างส่วนค้นหาสินค้า"""
        search_frame = LabelFrame(parent, text="🔍 ค้นหาสินค้า", font=(None, 14))
        search_frame.pack(fill=X, pady=10)
        
        # Frame สำหรับควบคุมการค้นหา
        control_frame = Frame(search_frame)
        control_frame.pack(padx=20, pady=15)
        
        # แถวที่ 1: ช่องค้นหา
        Label(control_frame, text="รหัส/ชื่อสินค้า:", font=(None, 12)).grid(row=0, column=0, sticky='w', padx=5)
        
        self.search_var = StringVar()
        self.search_var.trace('w', self.on_search_change)  # Real-time search
        
        search_entry = ttk.Entry(control_frame, textvariable=self.search_var, width=40, font=(None, 12))
        search_entry.grid(row=0, column=1, padx=5)
        
        # ปุ่มเคลียร์
        ttk.Button(control_frame, text="🗑️ ล้างการค้นหา", command=self.clear_search).grid(row=0, column=2, padx=5)
        
        # แถวที่ 2: ตัวกรองสถานะ
        Label(control_frame, text="กรองตามสถานะ:", font=(None, 12)).grid(row=1, column=0, sticky='w', padx=5, pady=(10, 0))
        
        # Frame สำหรับปุ่มกรอง
        filter_btn_frame = Frame(control_frame)
        filter_btn_frame.grid(row=1, column=1, columnspan=2, sticky='w', padx=5, pady=(10, 0))
        
        self.filter_status = StringVar(value="ทั้งหมด")
        
        ttk.Radiobutton(filter_btn_frame, text="ทั้งหมด", variable=self.filter_status, 
                       value="ทั้งหมด", command=self.apply_filters).pack(side=LEFT, padx=5)
        ttk.Radiobutton(filter_btn_frame, text="ปกติ", variable=self.filter_status, 
                       value="ปกติ", command=self.apply_filters).pack(side=LEFT, padx=5)
        ttk.Radiobutton(filter_btn_frame, text="ต้องสั่งซื้อ", variable=self.filter_status, 
                       value="ต้องสั่งซื้อ", command=self.apply_filters).pack(side=LEFT, padx=5)
        ttk.Radiobutton(filter_btn_frame, text="หมดสต็อก", variable=self.filter_status, 
                       value="หมดสต็อก", command=self.apply_filters).pack(side=LEFT, padx=5)
        
        # แสดงจำนวนผลลัพธ์
        self.search_result_label = Label(control_frame, text="", font=(None, 10), fg='blue')
        self.search_result_label.grid(row=2, column=0, columnspan=3, pady=5)
        
    def create_stock_table(self, parent):
        """สร้างตารางแสดงสินค้าคงเหลือ"""
        table_frame = LabelFrame(parent, text="รายการสินค้าคงเหลือ", font=(None, 14))
        table_frame.pack(fill=BOTH, expand=True, pady=10)
        
        # สร้าง Frame สำหรับ Treeview และ Scrollbars
        tree_frame = Frame(table_frame)
        tree_frame.pack(fill=BOTH, expand=True, padx=5, pady=5)
        
        # Headers และ widths
        headers = ['รหัสสินค้า', 'ชื่อสินค้า', 'ราคาขาย', 'ราคาทุน', 'สต็อก', 'หน่วย', 'หมวดหมู่', 'Reorder Point', 'สถานะ', 'มูลค่า']
        widths = [100, 200, 80, 80, 60, 70, 100, 100, 80, 100]
        
        # เพิ่ม height ของตาราง
        self.stock_table = ttk.Treeview(tree_frame, columns=headers, show='headings', height=25)
        
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
        
        # Scrollbars
        y_scrollbar = ttk.Scrollbar(tree_frame, orient=VERTICAL, command=self.stock_table.yview)
        x_scrollbar = ttk.Scrollbar(tree_frame, orient=HORIZONTAL, command=self.stock_table.xview)
        
        self.stock_table.configure(
            yscrollcommand=y_scrollbar.set,
            xscrollcommand=x_scrollbar.set
        )
        
        # Grid layout
        self.stock_table.grid(row=0, column=0, sticky='nsew')
        y_scrollbar.grid(row=0, column=1, sticky='ns')
        x_scrollbar.grid(row=1, column=0, sticky='ew')
        
        # Configure grid weights
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        # ผูก mousewheel กับตาราง
        self._bind_mousewheel(tree_frame)
    
    def on_search_change(self, *args):
        """Real-time search เมื่อมีการพิมพ์ในช่องค้นหา"""
        self.apply_filters()
    
    def apply_filters(self):
        """ใช้ตัวกรองทั้งการค้นหาและสถานะ"""
        search_text = self.search_var.get().strip().lower()
        status_filter = self.filter_status.get()
        
        # เริ่มจากข้อมูลทั้งหมด
        filtered = self.all_products.copy()
        
        # กรองตามคำค้นหา
        if search_text:
            filtered = [
                product for product in filtered
                if search_text in str(product.get('barcode', '')).lower() 
                or search_text in str(product.get('title', '')).lower()
            ]
        
        # กรองตามสถานะ
        if status_filter != "ทั้งหมด":
            filtered = [
                product for product in filtered
                if product.get('status') == status_filter
            ]
        
        # แสดงผลลัพธ์
        self.display_products(filtered)
        
        # อัพเดทข้อความแสดงจำนวนผลลัพธ์
        if search_text or status_filter != "ทั้งหมด":
            if filtered:
                filter_info = []
                if search_text:
                    filter_info.append(f"คำค้นหา '{self.search_var.get()}'")
                if status_filter != "ทั้งหมด":
                    filter_info.append(f"สถานะ '{status_filter}'")
                
                self.search_result_label.config(
                    text=f"พบ {len(filtered)} รายการจากทั้งหมด {len(self.all_products)} รายการ ({', '.join(filter_info)})",
                    fg='green'
                )
            else:
                self.search_result_label.config(
                    text=f"ไม่พบสินค้าที่ตรงกับเงื่อนไขที่เลือก",
                    fg='red'
                )
        else:
            self.search_result_label.config(text="")
    
    def clear_search(self):
        """ล้างการค้นหาและแสดงข้อมูลทั้งหมด"""
        self.search_var.set("")
        self.filter_status.set("ทั้งหมด")
        self.display_products(self.all_products)
        self.search_result_label.config(text="")
    
    def display_products(self, products):
        """แสดงข้อมูลสินค้าในตารางและอัพเดทสรุป"""
        # เคลียร์ตาราง
        for item in self.stock_table.get_children():
            self.stock_table.delete(item)
        
        # คำนวณข้อมูลสรุปจากข้อมูลที่กรอง
        total_products = len(products)
        total_stock = 0
        low_stock_count = 0
        out_of_stock_count = 0
        total_value = 0
        
        # แสดงข้อมูลในตาราง
        for product in products:
            barcode = product['barcode']
            title = product['title']
            price = product['price']
            cost = product['cost']
            quantity = product['quantity']
            unit = product['unit']
            category = product['category']
            reorder_point = product['reorder_point']
            status = product['status']
            item_value = product['item_value']
            
            # คำนวณสถิติ
            total_stock += quantity
            total_value += item_value
            
            if quantity == 0:
                out_of_stock_count += 1
            elif quantity <= reorder_point:
                low_stock_count += 1
            
            # เพิ่มข้อมูลลงตาราง
            stock_display = f"{quantity} ⚠️" if quantity == 0 else (f"{quantity} 🔄" if quantity <= reorder_point else str(quantity))
            
            item_id = self.stock_table.insert('', 'end', values=[
                barcode, title, f"{price:,.2f}", f"{cost:,.2f}", 
                stock_display, unit, category, reorder_point, status, f"{item_value:,.2f}"
            ])
        
        # อัปเดตข้อมูลสรุป
        self.v_total_products.set(f"{total_products} รายการ")
        self.v_total_stock.set(f"{total_stock:,} ชิ้น")
        self.v_low_stock.set(f"{low_stock_count} รายการ")
        self.v_out_of_stock.set(f"{out_of_stock_count} รายการ")
        self.v_total_value.set(f"{total_value:,.2f} บาท")
        
    def refresh_data(self):
        """รีเฟรชข้อมูลทั้งหมด"""
        try:
            # ดึงข้อมูลสินค้าทั้งหมด
            products = view_product(allfield=True)
            
            # เคลียร์ข้อมูลเก่า
            self.all_products = []
            alert_messages = []
            
            # วนลูปผ่านสินค้าแต่ละรายการ
            for product in products:
                if len(product) >= 9:
                    try:
                        id_val, barcode, title, price, cost, quantity, unit, category, reorder_point = product[:9]
                        
                        # แปลงข้อมูลให้เป็นชนิดที่ถูกต้อง
                        price = float(price)
                        cost = float(cost) 
                        quantity = int(quantity)
                        reorder_point = int(reorder_point) if reorder_point else 5
                        
                        # คำนวณมูลค่า
                        item_value = cost * quantity
                        
                        # กำหนดสถานะ
                        if quantity == 0:
                            status = "หมดสต็อก"
                            alert_messages.append(f"⚠️ {title} - หมดสต็อก!")
                        elif quantity <= reorder_point:
                            status = "ต้องสั่งซื้อ"
                            alert_messages.append(f"🔄 {title} - สต็อกเหลือ {quantity} {unit} (ต้องสั่งซื้อ)")
                        else:
                            status = "ปกติ"
                        
                        # เก็บข้อมูลในรูปแบบ dictionary
                        product_dict = {
                            'id': id_val,
                            'barcode': barcode,
                            'title': title,
                            'price': price,
                            'cost': cost,
                            'quantity': quantity,
                            'unit': unit,
                            'category': category,
                            'reorder_point': reorder_point,
                            'status': status,
                            'item_value': item_value
                        }
                        
                        self.all_products.append(product_dict)
                        
                    except (ValueError, IndexError) as e:
                        print(f"Error processing product {product}: {e}")
                        continue
            
            # แสดงข้อมูลทั้งหมด
            self.display_products(self.all_products)
            
            # อัปเดตการแจ้งเตือน
            self.alert_listbox.delete(0, END)
            if alert_messages:
                for msg in alert_messages[:10]:  # แสดงแค่ 10 รายการแรก
                    self.alert_listbox.insert(END, msg)
                if len(alert_messages) > 10:
                    self.alert_listbox.insert(END, f"... และอีก {len(alert_messages) - 10} รายการ")
            else:
                self.alert_listbox.insert(END, "✅ ไม่มีการแจ้งเตือน - สต็อกสินค้าปกติ")
            
            # ล้างการค้นหาและตัวกรอง
            self.search_var.set("")
            self.filter_status.set("ทั้งหมด")
            self.search_result_label.config(text="")
            
        except Exception as e:
            messagebox.showerror("Error", f"เกิดข้อผิดพลาดในการโหลดข้อมูล: {str(e)}")