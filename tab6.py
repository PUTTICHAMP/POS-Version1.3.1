# tab6.py - Customer & Credit Management with Invoice Printing
from tkinter import *
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
from basicsql import *

# Import receipt printer
try:
    from receipt_printer import ReceiptPrinter
    RECEIPT_PRINTER_AVAILABLE = True
except ImportError:
    RECEIPT_PRINTER_AVAILABLE = False
    print("⚠️ Warning: receipt_printer.py not found. Invoice printing disabled.")

class CreditManagementTab(Frame):
    def __init__(self, parent):
        super().__init__(parent, bg='#f0f0f0')
        self.pack(fill=BOTH, expand=True)
        
        # สร้าง ReceiptPrinter instance
        if RECEIPT_PRINTER_AVAILABLE:
            self.receipt_printer = ReceiptPrinter()
        else:
            self.receipt_printer = None
        
        # สร้าง Canvas และ Scrollbar สำหรับทั้ง Tab
        self.canvas = Canvas(self, bg='#ffffff', highlightthickness=0)
        self.main_scrollbar = ttk.Scrollbar(self, orient=VERTICAL, command=self.canvas.yview)
        self.scrollable_frame = Frame(self.canvas, bg='#ffffff')
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.main_scrollbar.set)
        
        # Pack scrollbar และ canvas
        self.main_scrollbar.pack(side=RIGHT, fill=Y)
        self.canvas.pack(side=LEFT, fill=BOTH, expand=True)
        
        # Bind mouse wheel scrolling
        self.bind_mouse_wheel()
        
        self.create_widgets()
        
    def bind_mouse_wheel(self):
        """ผูก Mouse Wheel Event สำหรับ Scrolling"""
        def _on_mousewheel(event):
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        def _bind_to_mousewheel(event):
            self.canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        def _unbind_from_mousewheel(event):
            self.canvas.unbind_all("<MouseWheel>")
        
        # Bind เมื่อเมาส์เข้า-ออกจาก frame
        self.canvas.bind('<Enter>', _bind_to_mousewheel)
        self.canvas.bind('<Leave>', _unbind_from_mousewheel)
        
    def create_widgets(self):
        """สร้าง GUI หลัก"""
        # ใช้ scrollable_frame แทน self
        parent = self.scrollable_frame
        
        # Header
        header_frame = Frame(parent, bg='#ffffff')
        header_frame.pack(pady=5, fill=X, padx=10)

        title_label = Label(header_frame, text='💳 จัดการลูกค้าและบิลเครดิต', 
                           font=('Arial', 18, 'bold'), bg='#ffffff')
        title_label.pack(side=TOP)
        
        # Main Container - ปรับให้เต็มจอ
        main_container = ttk.Notebook(parent)
        main_container.pack(fill=BOTH, expand=True, padx=40, pady=5)
        
        # Tab 1: จัดการลูกค้า
        customer_frame = Frame(main_container, bg='#ffffff')
        main_container.add(customer_frame, text='  👥 จัดการลูกค้า  ')
        self.create_customer_section(customer_frame)
        
        # Tab 2: บิลเครดิต
        credit_frame = Frame(main_container, bg='#ffffff')
        main_container.add(credit_frame, text='  📋 บิลเครดิต  ')
        self.create_credit_bills_section(credit_frame)
        
        # Tab 3: สร้างใบวางบิลใหม่
        new_invoice_frame = Frame(main_container, bg='#ffffff')
        main_container.add(new_invoice_frame, text='  ➕ สร้างใบวางบิล  ')
        self.create_new_invoice_section(new_invoice_frame)
        
    def create_customer_section(self, parent):
        """สร้างส่วนจัดการลูกค้า"""
        # ส่วนค้นหาลูกค้า
        search_frame = Frame(parent, bg='#ffffff')
        search_frame.pack(fill=X, padx=5, pady=(5, 3))
        
        Label(search_frame, text="🔍 ค้นหาลูกค้า:", font=('Arial', 11, 'bold'), 
              bg='#ffffff').pack(side=LEFT, padx=(0, 10))
        
        self.customer_search_var = StringVar()
        self.customer_search_var.trace('w', lambda *args: self.search_customers())
        
        search_entry = ttk.Entry(search_frame, textvariable=self.customer_search_var, 
                                font=('Arial', 11), width=40)
        search_entry.pack(side=LEFT, padx=5)
        
        Label(search_frame, text="(ค้นหาจาก: รหัส, ชื่อ, เบอร์โทร)", 
              font=('Arial', 9), fg='gray', bg='#ffffff').pack(side=LEFT, padx=5)
        
        ttk.Button(search_frame, text="ล้างการค้นหา", 
                  command=lambda: self.customer_search_var.set('')).pack(side=LEFT, padx=5)
        
        ttk.Button(search_frame, text="🔄 รีเฟรช", 
                  command=self.refresh_customer_table).pack(side=RIGHT, padx=5)
        
        # ส่วนฟอร์มเพิ่ม/แก้ไขลูกค้า
        form_frame = LabelFrame(parent, text="ข้อมูลลูกค้า", 
                               font=('Arial', 12, 'bold'), 
                               bg='#ffffff', padx=10, pady=5)
        form_frame.pack(fill=X, padx=5, pady=5)
        
        # Variables
        self.customer_vars = {
            'id': StringVar(),
            'name': StringVar(),
            'phone': StringVar(),
            'email': StringVar(),
            'address': StringVar(),
            'credit_limit': StringVar(value='0'),
            'credit_days': StringVar(value='30'),
            'notes': StringVar()
        }
        
        # สร้างฟอร์ม
        fields = [
            ('รหัสลูกค้า:', 'id'),
            ('ชื่อลูกค้า:', 'name'),
            ('เบอร์โทร:', 'phone'),
            ('อีเมล:', 'email'),
            ('ที่อยู่:', 'address'),
            ('วงเงินเครดิต (บาท):', 'credit_limit'),
            ('ระยะเวลาชำระ (วัน):', 'credit_days'),
            ('หมายเหตุ:', 'notes')
        ]
        
        for i, (label, key) in enumerate(fields):
            Label(form_frame, text=label, font=('Arial', 10), 
                  bg="#f8f1f1").grid(row=i, column=0, sticky='e', padx=5, pady=5)
            
            entry = ttk.Entry(form_frame, textvariable=self.customer_vars[key], 
                font=('Arial', 10), width=40)
            entry.grid(row=i, column=1, sticky='ew', padx=5, pady=5)
        
        form_frame.columnconfigure(1, weight=1)
        
        # ปุ่มจัดการ
        btn_frame = Frame(form_frame, bg='#ffffff')
        btn_frame.grid(row=len(fields), column=0, columnspan=2, pady=7)
        
        ttk.Button(btn_frame, text='เพิ่มลูกค้า', 
                  command=self.add_customer).pack(side=LEFT, padx=3)
        ttk.Button(btn_frame, text='บันทึกการแก้ไข', 
                  command=self.update_customer).pack(side=LEFT, padx=3)
        ttk.Button(btn_frame, text='ลบลูกค้า', 
                  command=self.delete_customer).pack(side=LEFT, padx=3)
        ttk.Button(btn_frame, text='ล้างฟอร์ม', 
                  command=self.clear_customer_form).pack(side=LEFT, padx=3)
        
        # ตารางแสดงลูกค้า - เพิ่มความสูงและปรับให้เต็มจอ
        table_frame = LabelFrame(parent, text="รายชื่อลูกค้า", 
                                font=('Arial', 12, 'bold'), 
                                bg='#ffffff', padx=5, pady=5)
        table_frame.pack(fill=BOTH, expand=True, padx=5, pady=5)
        
        # สร้างตาราง - เพิ่ม height จาก 10 เป็น 20
        columns = ('id', 'name', 'phone', 'credit_limit', 'credit_days', 'total_debt')
        self.customer_table = ttk.Treeview(table_frame, columns=columns, 
                                          show='headings', height=20)
        
        headers = {
            'id': 'รหัสลูกค้า',
            'name': 'ชื่อลูกค้า',
            'phone': 'เบอร์โทร',
            'credit_limit': 'วงเงินเครดิต',
            'credit_days': 'ระยะเวลา (วัน)',
            'total_debt': 'ยอดหนี้คงค้าง'
        }
        
        widths = [100, 200, 120, 120, 100, 120]
        
        for col, width in zip(columns, widths):
            self.customer_table.heading(col, text=headers[col])
            self.customer_table.column(col, width=width, anchor='center')
        
        self.customer_table.column('name', anchor='w')
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient=VERTICAL, 
                                 command=self.customer_table.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.customer_table.configure(yscrollcommand=scrollbar.set)
        self.customer_table.pack(fill=BOTH, expand=True)
        
        # Bind double-click
        self.customer_table.bind('<Double-Button-1>', self.load_customer_to_form)
        
        # โหลดข้อมูล
        self.refresh_customer_table()
        
    def create_credit_bills_section(self, parent):
        """สร้างส่วนบิลเครดิต"""
        # สถิติด้านบน
        stats_frame = Frame(parent, bg='#ffffff')
        stats_frame.pack(fill=X, padx=5, pady=5)
        
        self.stats_labels = {}
        stats = [
            ('pending', 'บิลค้างชำระ', '#ff9800'),
            ('overdue', 'เกินกำหนด', '#f44336'),
            ('total_debt', 'ยอดหนี้รวม', '#2196F3')
        ]
        
        for key, text, color in stats:
            frame = Frame(stats_frame, bg=color, relief=RIDGE, bd=2)
            frame.pack(side=LEFT, fill=BOTH, expand=True, padx=5)
            
            Label(frame, text=text, font=('Arial', 11, 'bold'), 
                  bg=color, fg='white').pack(pady=5)
            
            label = Label(frame, text='0', font=('Arial', 16, 'bold'), 
                         bg=color, fg='white')
            label.pack(pady=5)
            self.stats_labels[key] = label
        
        # ส่วนค้นหาบิล
        search_frame = Frame(parent, bg='#ffffff')
        search_frame.pack(fill=X, padx=5, pady=3)
        
        Label(search_frame, text="🔍 ค้นหาบิล:", font=('Arial', 11, 'bold'), 
              bg='#ffffff').pack(side=LEFT, padx=(0, 10))
        
        self.bill_search_var = StringVar()
        self.bill_search_var.trace('w', lambda *args: self.search_credit_bills())
        
        bill_search_entry = ttk.Entry(search_frame, textvariable=self.bill_search_var, 
                                     font=('Arial', 11), width=30)
        bill_search_entry.pack(side=LEFT, padx=5)
        
        Label(search_frame, text="(ค้นหาจาก: เลขที่บิล, ชื่อลูกค้า)", 
              font=('Arial', 9), fg='gray', bg='#ffffff').pack(side=LEFT, padx=5)
        
        ttk.Button(search_frame, text="ล้างการค้นหา", 
                  command=lambda: self.bill_search_var.set('')).pack(side=LEFT, padx=5)
        
        # ตัวกรอง
        filter_frame = Frame(parent, bg='#ffffff')
        filter_frame.pack(fill=X, padx=5, pady=3)
        
        Label(filter_frame, text='แสดง:', font=('Arial', 10), 
              bg='#ffffff').pack(side=LEFT, padx=5)
        
        self.credit_filter = StringVar(value='ALL')
        ttk.Radiobutton(filter_frame, text='ทั้งหมด', variable=self.credit_filter, 
                       value='ALL', command=self.refresh_credit_table).pack(side=LEFT)
        ttk.Radiobutton(filter_frame, text='ค้างชำระ', variable=self.credit_filter, 
                       value='PENDING', command=self.refresh_credit_table).pack(side=LEFT)
        ttk.Radiobutton(filter_frame, text='เกินกำหนด', variable=self.credit_filter, 
                       value='OVERDUE', command=self.refresh_credit_table).pack(side=LEFT)
        
        ttk.Button(filter_frame, text='🔄 รีเฟรช', 
                  command=self.refresh_credit_table).pack(side=RIGHT, padx=5)
        
        # ตารางบิลเครดิต - ขยายให้เต็มจอ
        table_frame = Frame(parent, bg='#ffffff')
        table_frame.pack(fill=BOTH, expand=True, padx=5, pady=5)
        
        columns = ('bill_id', 'customer', 'bill_date', 'due_date', 
                  'total', 'paid', 'remaining', 'status')
        self.credit_table = ttk.Treeview(table_frame, columns=columns, 
                                        show='headings', height=15)
        
        headers = {
            'bill_id': 'เลขที่บิล',
            'customer': 'ลูกค้า',
            'bill_date': 'วันที่ออกบิล',
            'due_date': 'กำหนดชำระ',
            'total': 'ยอดรวม',
            'paid': 'ชำระแล้ว',
            'remaining': 'คงเหลือ',
            'status': 'สถานะ'
        }
        
        widths = [160, 140, 120, 120, 100, 100, 100, 100]
        
        for col, width in zip(columns, widths):
            self.credit_table.heading(col, text=headers[col])
            self.credit_table.column(col, width=width, anchor='center')
        
        self.credit_table.column('customer', anchor='w')
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient=VERTICAL, 
                                 command=self.credit_table.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.credit_table.configure(yscrollcommand=scrollbar.set)
        self.credit_table.pack(fill=BOTH, expand=True)
        
        # ปุ่มชำระเงิน
        btn_frame = Frame(parent, bg='#ffffff')
        btn_frame.pack(fill=X, padx=10, pady=10)
        
        ttk.Button(btn_frame, text='ชำระเงิน', 
                  command=self.pay_credit_bill).pack(side=LEFT, padx=5)
        ttk.Button(btn_frame, text='พิมพ์ใบวางบิล', 
                  command=self.print_credit_bill).pack(side=LEFT, padx=5)
        ttk.Button(btn_frame, text='ดูรายละเอียด', 
                  command=self.view_bill_details).pack(side=LEFT, padx=5)
        ttk.Button(btn_frame, text='ลบใบวางบิล', 
                  command=self.delete_credit_bill).pack(side=LEFT, padx=5)
        
        # Bind double-click
        self.credit_table.bind('<Double-Button-1>', 
                              lambda e: self.pay_credit_bill())
        
        # โหลดข้อมูล
        self.refresh_credit_table()
    
    def create_new_invoice_section(self, parent):
        """สร้างส่วนสร้างใบวางบิลใหม่"""
        # สร้าง Canvas และ Scrollbar (nested scrolling)
        canvas = Canvas(parent, bg='#ffffff')
        scrollbar = ttk.Scrollbar(parent, orient=VERTICAL, command=canvas.yview)
        scrollable_frame = Frame(canvas, bg='#ffffff')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack scrollbar และ canvas
        scrollbar.pack(side=RIGHT, fill=Y)
        canvas.pack(side=LEFT, fill=BOTH, expand=True)
        
        # Header
        Label(scrollable_frame, text="สร้างใบวางบิลใหม่", 
              font=('Arial', 16, 'bold'), bg='#ffffff').pack(pady=10)
        
        # คำเตือน
        if not RECEIPT_PRINTER_AVAILABLE:
            warning_frame = Frame(scrollable_frame, bg='#ffebee', relief=RIDGE, bd=2)
            warning_frame.pack(fill=X, padx=20, pady=10)
            Label(warning_frame, text="⚠️ ไม่พบ receipt_printer.py - ไม่สามารถพิมพ์ใบวางบิลได้", 
                  font=('Arial', 11), bg='#ffebee', fg='#c62828').pack(pady=10)
        
        # ฟอร์มข้อมูล
        form_frame = LabelFrame(scrollable_frame, text="ข้อมูลใบวางบิล", 
                               font=('Arial', 12, 'bold'), 
                               bg='#ffffff', padx=20, pady=10)
        form_frame.pack(fill=BOTH, expand=True, padx=20, pady=10)
        
        # Variables
        self.invoice_vars = {
            'customer_id': StringVar(),
            'transaction_id': StringVar(value=self.generate_invoice_id()),
            'due_days': StringVar(value='30'),
            'notes': StringVar()
        }
        
        # เลือกลูกค้า
        Label(form_frame, text="เลือกลูกค้า:", font=('Arial', 11), 
              bg='#ffffff').grid(row=0, column=0, sticky='e', padx=10, pady=10)
        
        customer_frame = Frame(form_frame, bg='#ffffff')
        customer_frame.grid(row=0, column=1, sticky='ew', padx=10, pady=10)
        
        self.customer_combo = ttk.Combobox(customer_frame, 
                                          textvariable=self.invoice_vars['customer_id'],
                                          font=('Arial', 10), width=40, state='readonly')
        self.customer_combo.pack(side=LEFT, padx=(0, 5))
        
        ttk.Button(customer_frame, text="รีเฟรช", 
                  command=self.refresh_customer_combo).pack(side=LEFT)
        
        # เลขที่ใบวางบิล
        Label(form_frame, text="เลขที่ใบวางบิล:", font=('Arial', 11), 
              bg='#ffffff').grid(row=1, column=0, sticky='e', padx=10, pady=10)
        
        transaction_frame = Frame(form_frame, bg='#ffffff')
        transaction_frame.grid(row=1, column=1, sticky='ew', padx=10, pady=10)
        
        ttk.Entry(transaction_frame, textvariable=self.invoice_vars['transaction_id'],
                 font=('Arial', 10), width=30).pack(side=LEFT, padx=(0, 5))
        
        ttk.Button(transaction_frame, text="สร้างใหม่", 
                  command=lambda: self.invoice_vars['transaction_id'].set(
                      self.generate_invoice_id())).pack(side=LEFT)
        
        # กำหนดชำระ
        Label(form_frame, text="ระยะเวลาชำระ (วัน):", font=('Arial', 11), 
              bg='#ffffff').grid(row=2, column=0, sticky='e', padx=10, pady=10)
        
        ttk.Entry(form_frame, textvariable=self.invoice_vars['due_days'],
                 font=('Arial', 10), width=40).grid(row=2, column=1, sticky='w', padx=10, pady=10)
        
        # หมายเหตุ
        Label(form_frame, text="หมายเหตุ:", font=('Arial', 11), 
              bg='#ffffff').grid(row=3, column=0, sticky='ne', padx=10, pady=10)
        
        self.notes_text = Text(form_frame, height=1, width=40, font=('Arial', 11))
        self.notes_text.grid(row=3, column=1, sticky='ew', padx=10, pady=10)
        
        # ตารางสินค้า
        Label(form_frame, text="รายการสินค้า:", font=('Arial', 11), 
              bg='#ffffff').grid(row=4, column=0, sticky='ne', padx=10, pady=10)
        
        item_frame = Frame(form_frame, bg='#ffffff')
        item_frame.grid(row=4, column=1, sticky='ew', padx=10, pady=10)
        
        # สร้างตารางสินค้า
        columns = ('barcode', 'title', 'price', 'quantity', 'total')
        self.invoice_items_table = ttk.Treeview(item_frame, columns=columns, 
                                               show='headings', height=5)
        
        headers = {
            'barcode': 'รหัส',
            'title': 'สินค้า',
            'price': 'ราคา',
            'quantity': 'จำนวน',
            'total': 'รวม'
        }
        
        widths = [80, 200, 80, 80, 100]
        
        for col, width in zip(columns, widths):
            self.invoice_items_table.heading(col, text=headers[col])
            self.invoice_items_table.column(col, width=width, anchor='center')
        
        self.invoice_items_table.column('title', anchor='w')
        
        item_scrollbar = ttk.Scrollbar(item_frame, orient=VERTICAL, 
                                 command=self.invoice_items_table.yview)
        item_scrollbar.pack(side=RIGHT, fill=Y)
        self.invoice_items_table.configure(yscrollcommand=item_scrollbar.set)
        self.invoice_items_table.pack(side=LEFT, fill=BOTH, expand=True)
        
        # ปุ่มจัดการสินค้า
        item_btn_frame = Frame(form_frame, bg='#ffffff')
        item_btn_frame.grid(row=5, column=1, sticky='w', padx=10, pady=5)
        
        ttk.Button(item_btn_frame, text="เพิ่มสินค้า", 
                  command=self.add_item_to_invoice).pack(side=LEFT, padx=3)
        ttk.Button(item_btn_frame, text="ลบสินค้า", 
                  command=self.remove_item_from_invoice).pack(side=LEFT, padx=3)
        ttk.Button(item_btn_frame, text="ล้างทั้งหมด", 
                  command=self.clear_invoice_items).pack(side=LEFT, padx=3)
        
        # สรุปยอด
        summary_frame = LabelFrame(form_frame, text="สรุปยอด", 
                                  font=('Arial', 11, 'bold'), 
                                  bg='#e3f2fd', padx=10, pady=10)
        summary_frame.grid(row=6, column=0, columnspan=2, sticky='ew', padx=10, pady=10)
        
        self.summary_labels = {
            'subtotal': Label(summary_frame, text="ยอดรวม: 0.00 บาท", 
                            font=('Arial', 12), bg='#e3f2fd'),
            'vat': Label(summary_frame, text="VAT 7%: 0.00 บาท", 
                        font=('Arial', 12), bg='#e3f2fd'),
            'grand_total': Label(summary_frame, text="รวมทั้งหมด: 0.00 บาท", 
                                font=('Arial', 14, 'bold'), bg='#e3f2fd', fg="#61768c")
        }
        
        for label in self.summary_labels.values():
            label.pack(anchor='e', pady=2)
        
        form_frame.columnconfigure(1, weight=1)
        
        # ปุ่มสร้างใบวางบิล
        btn_frame = Frame(scrollable_frame, bg='#ffffff')
        btn_frame.pack(fill=X, padx=20, pady=20)
        
        ttk.Button(btn_frame, text="สร้างและพิมพ์ใบวางบิล", 
                  command=self.create_and_print_invoice,
                  style='Accent.TButton').pack(side=LEFT, padx=5)
        
        ttk.Button(btn_frame, text="ล้างฟอร์ม", 
                  command=self.clear_invoice_form).pack(side=LEFT, padx=5)
        
        # โหลดรายการลูกค้า
        self.refresh_customer_combo()
        
    # ==================== Customer Functions ====================
    
    def add_customer(self):
        """เพิ่มลูกค้าใหม่"""
        try:
            customer_id = self.customer_vars['id'].get().strip()
            name = self.customer_vars['name'].get().strip()
            
            if not customer_id or not name:
                messagebox.showwarning("Warning", "กรุณากรอกรหัสและชื่อลูกค้า")
                return
            
            # ตรวจสอบรหัสซ้ำ
            existing = get_customer_by_id(customer_id)
            if existing:
                messagebox.showerror("Error", "รหัสลูกค้านี้มีอยู่แล้ว")
                return
            
            phone = self.customer_vars['phone'].get().strip()
            email = self.customer_vars['email'].get().strip()
            address = self.customer_vars['address'].get().strip()
            
            try:
                credit_limit = float(self.customer_vars['credit_limit'].get())
                credit_days = int(self.customer_vars['credit_days'].get())
            except ValueError:
                messagebox.showerror("Error", "วงเงินเครดิตและระยะเวลาต้องเป็นตัวเลข")
                return
            
            notes = self.customer_vars['notes'].get().strip()
            
            insert_customer(customer_id, name, phone, email, address, 
                          credit_limit, credit_days, notes)
            
            messagebox.showinfo("Success", "เพิ่มลูกค้าเรียบร้อย")
            self.clear_customer_form()
            self.refresh_customer_table()
            self.refresh_customer_combo()
            
        except Exception as e:
            messagebox.showerror("Error", f"เกิดข้อผิดพลาด: {str(e)}")
    
    def update_customer(self):
        """แก้ไขข้อมูลลูกค้า"""
        try:
            customer_id = self.customer_vars['id'].get().strip()
            
            if not customer_id:
                messagebox.showwarning("Warning", "กรุณาเลือกลูกค้าที่ต้องการแก้ไข")
                return
            
            existing = get_customer_by_id(customer_id)
            if not existing:
                messagebox.showerror("Error", "ไม่พบลูกค้านี้")
                return
            
            name = self.customer_vars['name'].get().strip()
            phone = self.customer_vars['phone'].get().strip()
            email = self.customer_vars['email'].get().strip()
            address = self.customer_vars['address'].get().strip()
            
            try:
                credit_limit = float(self.customer_vars['credit_limit'].get())
                credit_days = int(self.customer_vars['credit_days'].get())
            except ValueError:
                messagebox.showerror("Error", "วงเงินเครดิตและระยะเวลาต้องเป็นตัวเลข")
                return
            
            notes = self.customer_vars['notes'].get().strip()
            
            update_customer(customer_id, name, phone, email, address, 
                          credit_limit, credit_days, notes)
            
            messagebox.showinfo("Success", "แก้ไขข้อมูลเรียบร้อย")
            self.refresh_customer_table()
            self.refresh_customer_combo()
            
        except Exception as e:
            messagebox.showerror("Error", f"เกิดข้อผิดพลาด: {str(e)}")
    
    def delete_customer(self):
        """ลบลูกค้า"""
        try:
            customer_id = self.customer_vars['id'].get().strip()
            
            if not customer_id:
                messagebox.showwarning("Warning", "กรุณาเลือกลูกค้าที่ต้องการลบ")
                return
            
            # ตรวจสอบบิลค้างชำระ
            bills = get_customer_credit_bills(customer_id)
            pending = [b for b in bills if b[8] in ('PENDING', 'PARTIAL')]
            
            if pending:
                messagebox.showerror("Error", 
                    f"ไม่สามารถลบได้\nลูกค้ามีบิลค้างชำระ {len(pending)} บิล")
                return
            
            confirm = messagebox.askyesno("Confirm", 
                f"ต้องการลบลูกค้า {self.customer_vars['name'].get()} ใช่หรือไม่?")
            
            if confirm:
                delete_customer(customer_id)
                messagebox.showinfo("Success", "ลบลูกค้าเรียบร้อย")
                self.clear_customer_form()
                self.refresh_customer_table()
                self.refresh_customer_combo()
                
        except Exception as e:
            messagebox.showerror("Error", f"เกิดข้อผิดพลาด: {str(e)}")
    
    def load_customer_to_form(self, event=None):
        """โหลดข้อมูลลูกค้าสู่ฟอร์ม"""
        try:
            selected = self.customer_table.selection()
            if not selected:
                return
            
            item = self.customer_table.item(selected[0])
            customer_id = item['values'][0]
            
            customer = get_customer_by_id(customer_id)
            if customer:
                self.customer_vars['id'].set(customer[0])
                self.customer_vars['name'].set(customer[1])
                self.customer_vars['phone'].set(customer[2] or '')
                self.customer_vars['email'].set(customer[3] or '')
                self.customer_vars['address'].set(customer[4] or '')
                self.customer_vars['credit_limit'].set(customer[5])
                self.customer_vars['credit_days'].set(customer[6])
                self.customer_vars['notes'].set(customer[9] or '')
                
        except Exception as e:
            messagebox.showerror("Error", f"เกิดข้อผิดพลาด: {str(e)}")
    
    def clear_customer_form(self):
        """ล้างฟอร์มลูกค้า"""
        for var in self.customer_vars.values():
            var.set('')
        self.customer_vars['credit_limit'].set('0')
        self.customer_vars['credit_days'].set('30')
    
    def refresh_customer_table(self):
        """รีเฟรชตารางลูกค้า"""
        self.customer_table.delete(*self.customer_table.get_children())
        
        customers = get_all_customers()
        
        # ถ้ามีการค้นหา ให้กรองข้อมูล
        search_term = getattr(self, 'customer_search_var', StringVar()).get().lower()
        
        for customer in customers:
            # กรองตามคำค้นหา
            if search_term:
                customer_id = str(customer[0]).lower()
                name = str(customer[1]).lower()
                phone = str(customer[2] or '').lower()
                
                if not (search_term in customer_id or 
                       search_term in name or 
                       search_term in phone):
                    continue
            
            self.customer_table.insert('', 'end', values=(
                customer[0],  # ID
                customer[1],  # Name
                customer[2] or '-',  # Phone
                f"{customer[5]:,.2f}",  # Credit Limit
                customer[6],  # Credit Days
                f"{customer[7]:,.2f}"  # Total Debt
            ))
    
    def search_customers(self):
        """ค้นหาลูกค้าแบบ Real-time"""
        self.refresh_customer_table()
    
    # ==================== Credit Bill Functions ====================
    
    def pay_credit_bill(self):
        """ชำระบิลเครดิต"""
        try:
            selected = self.credit_table.selection()
            if not selected:
                messagebox.showwarning("Warning", "กรุณาเลือกบิลที่ต้องการชำระ")
                return
            
            item = self.credit_table.item(selected[0])
            bill_id = item['values'][0]
            remaining = float(item['values'][6].replace(',', ''))
            
            # สร้างหน้าต่างชำระเงิน
            pay_window = Toplevel(self)
            pay_window.title("ชำระบิลเครดิต")
            pay_window.geometry("400x300")
            pay_window.transient(self)
            pay_window.grab_set()
            
            Label(pay_window, text="ชำระบิลเครดิต", 
                  font=('Arial', 16, 'bold')).pack(pady=10)
            
            info_frame = Frame(pay_window)
            info_frame.pack(padx=20, pady=10, fill=X)
            
            Label(info_frame, text=f"เลขที่บิล: {bill_id}", 
                  font=('Arial', 11)).pack(anchor='w')
            Label(info_frame, text=f"ยอดค้างชำระ: {remaining:,.2f} บาท", 
                  font=('Arial', 11, 'bold'), fg='red').pack(anchor='w')
            
            Label(pay_window, text="จำนวนเงินที่ชำระ:", 
                  font=('Arial', 11)).pack(pady=(10, 0))
            
            payment_var = StringVar(value=str(remaining))
            payment_entry = ttk.Entry(pay_window, textvariable=payment_var, 
                                     font=('Arial', 14), width=20, justify='center')
            payment_entry.pack(pady=5)
            payment_entry.select_range(0, 'end')
            payment_entry.focus()
            
            def process_payment():
                try:
                    amount = float(payment_var.get())
                    if amount <= 0:
                        messagebox.showerror("Error", "จำนวนเงินต้องมากกว่า 0")
                        return
                    
                    success, message = pay_credit_bill(bill_id, amount)
                    
                    if success:
                        messagebox.showinfo("Success", message)
                        pay_window.destroy()
                        self.refresh_credit_table()
                        self.refresh_customer_table()
                    else:
                        messagebox.showerror("Error", message)
                        
                except ValueError:
                    messagebox.showerror("Error", "กรุณากรอกจำนวนเงินที่ถูกต้อง")
            
            btn_frame = Frame(pay_window)
            btn_frame.pack(pady=20)
            
            ttk.Button(btn_frame, text="💰 ชำระเงิน", 
                      command=process_payment).pack(side=LEFT, padx=5)
            ttk.Button(btn_frame, text="ยกเลิก", 
                      command=pay_window.destroy).pack(side=LEFT, padx=5)
            
            payment_entry.bind('<Return>', lambda e: process_payment())
            
        except Exception as e:
            messagebox.showerror("Error", f"เกิดข้อผิดพลาด: {str(e)}")
    
    def print_credit_bill(self):
        """พิมพ์ใบวางบิล"""
        try:
            if not RECEIPT_PRINTER_AVAILABLE or not self.receipt_printer:
                messagebox.showerror("Error", 
                    "ไม่พบ receipt_printer.py\nกรุณาตรวจสอบว่าไฟล์อยู่ในโฟลเดอร์เดียวกัน")
                return
            
            selected = self.credit_table.selection()
            if not selected:
                messagebox.showwarning("Warning", "กรุณาเลือกบิลที่ต้องการพิมพ์")
                return
            
            item = self.credit_table.item(selected[0])
            bill_id = item['values'][0]
            
            # ดึงข้อมูลบิลจากฐานข้อมูล
            bill = get_credit_bill_by_id(bill_id)
            
            if not bill:
                messagebox.showerror("Error", "ไม่พบข้อมูลบิล")
                return
            
            # แปลง transaction_id จากบิลเป็นข้อมูล sales
            transaction_id = bill[2]
            
            # ดึงข้อมูลสินค้าจาก sales
            with conn:
                c.execute('SELECT * FROM sales WHERE transaction_id=?', (transaction_id,))
                sale = c.fetchone()
            
            if not sale:
                messagebox.showerror("Error", "ไม่พบข้อมูลการขาย")
                return
            
            # แปลง items จาก string เป็น list
            import json
            cart_items = json.loads(sale[8])  # items column
            
            # เตรียมข้อมูลลูกค้า
            customer_info = {
                'name': bill[11] if len(bill) > 11 else 'N/A',  # customer_name
                'phone': bill[12] if len(bill) > 12 else 'N/A',  # phone
                'address': 'ที่อยู่ลูกค้า'  # ถ้ามีใน DB
            }
            
            # คำนวณวันครบกำหนด
            bill_date = datetime.strptime(bill[3][:10], '%Y-%m-%d')
            due_date = datetime.strptime(bill[4], '%Y-%m-%d')
            due_days = (due_date - bill_date).days
            
            # สร้างใบวางบิล
            try:
                filename = self.receipt_printer.create_invoice(
                    transaction_id=bill_id,
                    subtotal=bill[5],  # total_amount (ก่อน VAT)
                    vat=bill[5] * 0.07,  # คำนวณ VAT 7%
                    grand_total=bill[5] * 1.07,  # รวม VAT
                    cart_items=cart_items,
                    customer_info=customer_info,
                    due_days=due_days
                )
                
                messagebox.showinfo("Success", 
                    f"พิมพ์ใบวางบิล {bill_id} เรียบร้อย\nไฟล์: {filename}")
                
            except Exception as e:
                messagebox.showerror("Error", f"ไม่สามารถพิมพ์ได้: {str(e)}")
            
        except Exception as e:
            messagebox.showerror("Error", f"เกิดข้อผิดพลาด: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def view_bill_details(self):
        """ดูรายละเอียดบิล"""
        try:
            selected = self.credit_table.selection()
            if not selected:
                messagebox.showwarning("Warning", "กรุณาเลือกบิลที่ต้องการดู")
                return
            
            item = self.credit_table.item(selected[0])
            bill_id = item['values'][0]
            
            bill = get_credit_bill_by_id(bill_id)
            
            if not bill:
                messagebox.showerror("Error", "ไม่พบข้อมูลบิล")
                return
            
            # สร้างหน้าต่างแสดงรายละเอียด
            detail_window = Toplevel(self)
            detail_window.title(f"รายละเอียดบิล {bill_id}")
            detail_window.geometry("500x600")
            detail_window.transient(self)
            
            # Header
            Label(detail_window, text=f"รายละเอียดบิล {bill_id}", 
                  font=('Arial', 16, 'bold')).pack(pady=10)
            
            # ข้อมูลบิล
            info_frame = LabelFrame(detail_window, text="ข้อมูลบิล", 
                                   font=('Arial', 11, 'bold'), padx=20, pady=10)
            info_frame.pack(fill=X, padx=20, pady=10)
            
            details = [
                ("เลขที่บิล:", bill[0]),
                ("รหัสลูกค้า:", bill[1]),
                ("ชื่อลูกค้า:", bill[11] if len(bill) > 11 else 'N/A'),
                ("เบอร์โทร:", bill[12] if len(bill) > 12 else 'N/A'),
                ("วันที่ออกบิล:", bill[3][:10] if bill[3] else 'N/A'),
                ("กำหนดชำระ:", bill[4] if bill[4] else 'N/A'),
                ("ยอดรวม:", f"{bill[5]:,.2f} บาท"),
                ("ชำระแล้ว:", f"{bill[6]:,.2f} บาท"),
                ("คงเหลือ:", f"{bill[7]:,.2f} บาท"),
                ("สถานะ:", bill[8]),
                ("หมายเหตุ:", bill[10] if bill[10] else '-')
            ]
            
            for label, value in details:
                frame = Frame(info_frame)
                frame.pack(fill=X, pady=2)
                Label(frame, text=label, font=('Arial', 10), 
                      width=15, anchor='w').pack(side=LEFT)
                Label(frame, text=str(value), font=('Arial', 10, 'bold')).pack(side=LEFT)
            
            # ปุ่มปิด
            ttk.Button(detail_window, text="ปิด", 
                      command=detail_window.destroy).pack(pady=20)
            
        except Exception as e:
            messagebox.showerror("Error", f"เกิดข้อผิดพลาด: {str(e)}")
    
    def delete_credit_bill(self):
        """ลบใบวางบิล"""
        try:
            selected = self.credit_table.selection()
            if not selected:
                messagebox.showwarning("Warning", "กรุณาเลือกบิลที่ต้องการลบ")
                return
            
            item = self.credit_table.item(selected[0])
            bill_id = item['values'][0]
            customer_name = item['values'][1]
            total_amount = float(item['values'][4].replace(',', ''))
            paid_amount = float(item['values'][5].replace(',', ''))
            remaining = float(item['values'][6].replace(',', ''))
            status = item['values'][7]
            
            # ตรวจสอบสถานะ
            if status == 'ชำระแล้ว':
                confirm = messagebox.askyesno(
                    "Confirm Delete",
                    f"ต้องการลบบิล {bill_id} ใช่หรือไม่?\n\n"
                    f"ลูกค้า: {customer_name}\n"
                    f"ยอดเงิน: {total_amount:,.2f} บาท\n"
                    f"สถานะ: {status}\n\n"
                    f"⚠️ บิลนี้ชำระครบแล้ว คุณแน่ใจหรือไม่?"
                )
            elif paid_amount > 0:
                confirm = messagebox.askyesno(
                    "Confirm Delete",
                    f"⚠️ คำเตือน: บิลนี้มีการชำระเงินไปแล้ว!\n\n"
                    f"เลขที่บิล: {bill_id}\n"
                    f"ลูกค้า: {customer_name}\n"
                    f"ยอดรวม: {total_amount:,.2f} บาท\n"
                    f"ชำระแล้ว: {paid_amount:,.2f} บาท\n"
                    f"คงเหลือ: {remaining:,.2f} บาท\n\n"
                    f"การลบจะทำให้:\n"
                    f"• ยอดหนี้ลูกค้าลดลง {remaining:,.2f} บาท\n"
                    f"• ข้อมูลการชำระเงิน {paid_amount:,.2f} บาท จะหายไป\n\n"
                    f"ต้องการดำเนินการต่อหรือไม่?"
                )
            else:
                confirm = messagebox.askyesno(
                    "Confirm Delete",
                    f"ต้องการลบบิล {bill_id} ใช่หรือไม่?\n\n"
                    f"ลูกค้า: {customer_name}\n"
                    f"ยอดเงิน: {total_amount:,.2f} บาท\n"
                    f"สถานะ: {status}"
                )
            
            if not confirm:
                return
            
            # ดึงข้อมูลบิลเพื่อหา customer_id
            bill = get_credit_bill_by_id(bill_id)
            if not bill:
                messagebox.showerror("Error", "ไม่พบข้อมูลบิล")
                return
            
            customer_id = bill[1]
            
            # ลบบิลและอัพเดทยอดหนี้ลูกค้า
            with conn:
                # ลบบิลเครดิต
                c.execute('DELETE FROM credit_bills WHERE bill_id=?', (bill_id,))
                
                # อัพเดทยอดหนี้ลูกค้า (ลดยอดค้างชำระ)
                c.execute('UPDATE customers SET total_debt = total_debt - ? WHERE customer_id=?', 
                         (remaining, customer_id))
                
                conn.commit()
            
            messagebox.showinfo("Success", 
                f"ลบบิล {bill_id} เรียบร้อย\n"
                f"ยอดหนี้ลูกค้าลดลง {remaining:,.2f} บาท")
            
            # รีเฟรชข้อมูล
            self.refresh_credit_table()
            self.refresh_customer_table()
            
        except Exception as e:
            messagebox.showerror("Error", f"เกิดข้อผิดพลาด: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def refresh_credit_table(self):
        """รีเฟรชตารางบิลเครดิต"""
        self.credit_table.delete(*self.credit_table.get_children())
        
        filter_type = self.credit_filter.get()
        
        if filter_type == 'PENDING':
            bills = get_pending_credit_bills()
        elif filter_type == 'OVERDUE':
            bills = get_overdue_credit_bills()
        else:
            bills = get_all_credit_bills()
        
        # อัปเดตสถิติ
        pending_bills = get_pending_credit_bills()
        overdue_bills = get_overdue_credit_bills()
        
        total_debt = sum(b[7] for b in pending_bills)  # remaining_amount
        
        self.stats_labels['pending'].config(text=f"{len(pending_bills)} บิล")
        self.stats_labels['overdue'].config(text=f"{len(overdue_bills)} บิล")
        self.stats_labels['total_debt'].config(text=f"{total_debt:,.2f} ฿")
        
        # ถ้ามีการค้นหา ให้กรองข้อมูล
        search_term = getattr(self, 'bill_search_var', StringVar()).get().lower()
        
        # เพิ่มข้อมูลในตาราง
        for bill in bills:
            # กรองตามคำค้นหา
            if search_term:
                bill_id = str(bill[0]).lower()
                customer_name = str(bill[11] if len(bill) > 11 else '').lower()
                
                if not (search_term in bill_id or search_term in customer_name):
                    continue
            
            status_thai = {
                'PENDING': 'ค้างชำระ',
                'PARTIAL': 'ชำระบางส่วน',
                'PAID': 'ชำระแล้ว'
            }.get(bill[8], bill[8])
            
            self.credit_table.insert('', 'end', values=(
                bill[0],  # bill_id
                bill[11] if len(bill) > 11 else '-',  # customer_name
                bill[3][:10] if bill[3] else '-',  # bill_date
                bill[4] if bill[4] else '-',  # due_date
                f"{bill[5]:,.2f}",  # total_amount
                f"{bill[6]:,.2f}",  # paid_amount
                f"{bill[7]:,.2f}",  # remaining_amount
                status_thai
            ))
    
    def search_credit_bills(self):
        """ค้นหาบิลเครดิตแบบ Real-time"""
        self.refresh_credit_table()
    
    # ==================== Invoice Creation Functions ====================
    
    def generate_invoice_id(self):
        """สร้างเลขที่ใบวางบิลอัตโนมัติ"""
        try:
            with conn:
                c.execute("SELECT COUNT(*) FROM credit_bills")
                count = c.fetchone()[0]
                return f"INV{count + 1:06d}"
        except:
            return f"INV{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    def refresh_customer_combo(self):
        """รีเฟรช Combobox ลูกค้า"""
        customers = get_all_customers()
        customer_list = [f"{c[0]} - {c[1]}" for c in customers]
        self.customer_combo['values'] = customer_list
        if customer_list:
            self.customer_combo.current(0)
    
    def add_item_to_invoice(self):
        """เพิ่มสินค้าลงในใบวางบิล"""
        # สร้างหน้าต่างเลือกสินค้า
        item_window = Toplevel(self)
        item_window.title("เลือกสินค้า")
        item_window.geometry("600x400")
        item_window.transient(self)
        item_window.grab_set()
        
        Label(item_window, text="เลือกสินค้า", 
              font=('Arial', 14, 'bold')).pack(pady=10)
        
        # ค้นหาสินค้า
        search_frame = Frame(item_window)
        search_frame.pack(fill=X, padx=20, pady=5)
        
        Label(search_frame, text="ค้นหา:", font=('Arial', 10)).pack(side=LEFT)
        search_var = StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=search_var, width=30)
        search_entry.pack(side=LEFT, padx=5)
        
        # ตารางสินค้า
        table_frame = Frame(item_window)
        table_frame.pack(fill=BOTH, expand=True, padx=20, pady=10)
        
        columns = ('barcode', 'title', 'price', 'stock')
        product_table = ttk.Treeview(table_frame, columns=columns, 
                                    show='headings', height=10)
        
        headers = {'barcode': 'รหัส', 'title': 'สินค้า', 'price': 'ราคา', 'stock': 'คงเหลือ'}
        widths = [100, 250, 100, 100]
        
        for col, width in zip(columns, widths):
            product_table.heading(col, text=headers[col])
            product_table.column(col, width=width, anchor='center')
        
        product_table.column('title', anchor='w')
        
        scrollbar = ttk.Scrollbar(table_frame, orient=VERTICAL, 
                                 command=product_table.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        product_table.configure(yscrollcommand=scrollbar.set)
        product_table.pack(side=LEFT, fill=BOTH, expand=True)
        
        # โหลดสินค้า
        def load_products(search_term=''):
            product_table.delete(*product_table.get_children())
            products = view_product(allfield=False)
            
            for product in products:
                barcode, title, price, cost, quantity, unit, category, reorder = product
                if search_term.lower() in title.lower() or search_term in barcode:
                    product_table.insert('', 'end', values=(
                        barcode, title, f"{price:,.2f}", quantity
                    ))
        
        load_products()
        
        search_var.trace('w', lambda *args: load_products(search_var.get()))
        
        # เลือกสินค้า
        def select_product():
            selected = product_table.selection()
            if not selected:
                messagebox.showwarning("Warning", "กรุณาเลือกสินค้า")
                return
            
            item = product_table.item(selected[0])
            barcode = item['values'][0]
            title = item['values'][1]
            price = float(item['values'][2].replace(',', ''))
            stock = item['values'][3]
            
            # ถามจำนวน
            qty_window = Toplevel(item_window)
            qty_window.title("ระบุจำนวน")
            qty_window.geometry("300x150")
            qty_window.transient(item_window)
            qty_window.grab_set()
            
            Label(qty_window, text=f"สินค้า: {title}", 
                  font=('Arial', 10)).pack(pady=10)
            Label(qty_window, text=f"คงเหลือ: {stock} ชิ้น", 
                  font=('Arial', 9), fg='gray').pack()
            
            Label(qty_window, text="จำนวน:", font=('Arial', 10)).pack(pady=5)
            qty_var = StringVar(value='1')
            qty_entry = ttk.Entry(qty_window, textvariable=qty_var, 
                                 font=('Arial', 12), width=15, justify='center')
            qty_entry.pack(pady=5)
            qty_entry.select_range(0, 'end')
            qty_entry.focus()
            
            def add_to_table():
                try:
                    quantity = int(qty_var.get())
                    if quantity <= 0:
                        messagebox.showerror("Error", "จำนวนต้องมากกว่า 0")
                        return
                    
                    if quantity > stock:
                        messagebox.showerror("Error", f"สินค้าคงเหลือไม่พอ (มีเพียง {stock} ชิ้น)")
                        return
                    
                    total = price * quantity
                    
                    self.invoice_items_table.insert('', 'end', values=(
                        barcode, title, f"{price:,.2f}", quantity, f"{total:,.2f}"
                    ))
                    
                    self.update_invoice_summary()
                    qty_window.destroy()
                    item_window.destroy()
                    
                except ValueError:
                    messagebox.showerror("Error", "กรุณากรอกจำนวนที่ถูกต้อง")
            
            ttk.Button(qty_window, text="เพิ่ม", 
                      command=add_to_table).pack(pady=10)
            
            qty_entry.bind('<Return>', lambda e: add_to_table())
        
        ttk.Button(item_window, text="เลือก", 
                  command=select_product).pack(pady=10)
        
        product_table.bind('<Double-Button-1>', lambda e: select_product())
    
    def remove_item_from_invoice(self):
        """ลบสินค้าออกจากใบวางบิล"""
        selected = self.invoice_items_table.selection()
        if not selected:
            messagebox.showwarning("Warning", "กรุณาเลือกสินค้าที่ต้องการลบ")
            return
        
        self.invoice_items_table.delete(selected[0])
        self.update_invoice_summary()
    
    def clear_invoice_items(self):
        """ล้างสินค้าทั้งหมด"""
        self.invoice_items_table.delete(*self.invoice_items_table.get_children())
        self.update_invoice_summary()
    
    def update_invoice_summary(self):
        """อัพเดทสรุปยอด"""
        items = self.invoice_items_table.get_children()
        subtotal = sum(float(self.invoice_items_table.item(item)['values'][4].replace(',', '')) 
                      for item in items)
        
        vat = subtotal * 0.07
        grand_total = subtotal + vat
        
        self.summary_labels['subtotal'].config(text=f"ยอดรวม: {subtotal:,.2f} บาท")
        self.summary_labels['vat'].config(text=f"VAT 7%: {vat:,.2f} บาท")
        self.summary_labels['grand_total'].config(text=f"รวมทั้งหมด: {grand_total:,.2f} บาท")
    
    def create_and_print_invoice(self):
        """สร้างและพิมพ์ใบวางบิล"""
        try:
            if not RECEIPT_PRINTER_AVAILABLE or not self.receipt_printer:
                messagebox.showerror("Error", 
                    "ไม่พบ receipt_printer.py\nไม่สามารถพิมพ์ใบวางบิลได้")
                return
            
            # ตรวจสอบข้อมูล
            customer_text = self.invoice_vars['customer_id'].get()
            if not customer_text:
                messagebox.showwarning("Warning", "กรุณาเลือกลูกค้า")
                return
            
            customer_id = customer_text.split(' - ')[0]
            
            items = self.invoice_items_table.get_children()
            if not items:
                messagebox.showwarning("Warning", "กรุณาเพิ่มสินค้าอย่างน้อย 1 รายการ")
                return
            
            try:
                due_days = int(self.invoice_vars['due_days'].get())
            except ValueError:
                messagebox.showerror("Error", "ระยะเวลาชำระต้องเป็นตัวเลข")
                return
            
            # เตรียมข้อมูล
            transaction_id = self.invoice_vars['transaction_id'].get()
            notes = self.notes_text.get('1.0', 'end-1c').strip()
            
            # คำนวณยอด
            cart_items = []
            subtotal = 0
            
            for item in items:
                values = self.invoice_items_table.item(item)['values']
                barcode = values[0]
                title = values[1]
                price = float(values[2].replace(',', ''))
                quantity = int(values[3])
                
                cart_items.append([barcode, title, price, quantity])
                subtotal += price * quantity
            
            vat = subtotal * 0.07
            grand_total = subtotal + vat
            
            # ข้อมูลลูกค้า
            customer = get_customer_by_id(customer_id)
            if not customer:
                messagebox.showerror("Error", "ไม่พบข้อมูลลูกค้า")
                return
            
            customer_info = {
                'name': customer[1],
                'phone': customer[2] or '-',
                'address': customer[4] or '-'
            }
            
            # บันทึกลงฐานข้อมูล
            # 1. บันทึก sales
            import json
            items_json = json.dumps(cart_items, ensure_ascii=False)
            insert_transaction(transaction_id, subtotal, vat, grand_total, 0, 0, items_json)
            
            # 2. สร้างบิลเครดิต
            insert_credit_bill(transaction_id, customer_id, transaction_id, 
                             due_days, grand_total, notes)
            
            # 3. พิมพ์ใบวางบิล
            filename = self.receipt_printer.create_invoice(
                transaction_id=transaction_id,
                subtotal=subtotal,
                vat=vat,
                grand_total=grand_total,
                cart_items=cart_items,
                customer_info=customer_info,
                due_days=due_days
            )
            
            messagebox.showinfo("Success", 
                f"สร้างใบวางบิล {transaction_id} เรียบร้อย\nไฟล์: {filename}")
            
            # ล้างฟอร์ม
            self.clear_invoice_form()
            
            # รีเฟรช
            self.refresh_credit_table()
            self.refresh_customer_table()
            
        except Exception as e:
            messagebox.showerror("Error", f"เกิดข้อผิดพลาด: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def clear_invoice_form(self):
        """ล้างฟอร์มใบวางบิล"""
        self.invoice_vars['transaction_id'].set(self.generate_invoice_id())
        self.invoice_vars['due_days'].set('30')
        self.notes_text.delete('1.0', 'end')
        self.clear_invoice_items()
        self.refresh_customer_combo()
    
    def refresh_data(self):
        """รีเฟรชข้อมูลทั้งหมด"""
        self.refresh_customer_table()
        self.refresh_credit_table()
        self.refresh_customer_combo()