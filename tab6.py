# tab6.py - Customer & Credit Management
from tkinter import *
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
from basicsql import *

class CreditManagementTab(Frame):
    def __init__(self, parent):
        super().__init__(parent, bg='#ffffff')
        self.pack(fill=BOTH, expand=True)
        
        self.create_widgets()
        
    def create_widgets(self):
        """สร้าง GUI หลัก"""
        # Header
        header_frame = Frame(self)
        header_frame.pack(pady=2, fill=X, padx=20)

        title_label = Label(header_frame, text='💳 จัดการลูกค้าและบิลเครดิต', font=('Arial', 18, 'bold'))
        title_label.pack(side=TOP)
        
        # Label(header_frame, text='💳 จัดการลูกค้าและบิลเครดิต', 
        #       font=('Arial', 18, 'bold')).pack()
        
        # Main Container
        main_container = ttk.Notebook(self)
        main_container.pack(fill=BOTH, expand=True, padx=20, pady=10)
        
        # Tab 1: จัดการลูกค้า
        customer_frame = Frame(main_container, bg='#ffffff')
        main_container.add(customer_frame, text='  👥 จัดการลูกค้า  ')
        self.create_customer_section(customer_frame)
        
        # Tab 2: บิลเครดิต
        credit_frame = Frame(main_container, bg='#ffffff')
        main_container.add(credit_frame, text='  📋 บิลเครดิต  ')
        self.create_credit_bills_section(credit_frame)
        
    def create_customer_section(self, parent):
        """สร้างส่วนจัดการลูกค้า"""
        # ส่วนฟอร์มเพิ่ม/แก้ไขลูกค้า
        form_frame = LabelFrame(parent, text="ข้อมูลลูกค้า", 
                               font=('Arial', 12, 'bold'), 
                               bg='#ffffff', padx=10, pady=10)
        form_frame.pack(fill=X, padx=10, pady=10)
        
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
                  bg='#ffffff').grid(row=i, column=0, sticky='e', padx=5, pady=5)
            
            # if key == 'address' or key == 'notes':
            #     entry = Text(form_frame, height=3, width=40, font=('Arial', 10))
            #     entry.grid(row=i, column=1, sticky='ew', padx=5, pady=5)
            #     setattr(self, f'customer_{key}_text', entry)
            # else:
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
        
        # ตารางแสดงลูกค้า
        table_frame = LabelFrame(parent, text="รายชื่อลูกค้า", 
                                font=('Arial', 12, 'bold'), 
                                bg='#ffffff', padx=10, pady=10)
        table_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        # สร้างตาราง
        columns = ('id', 'name', 'phone', 'credit_limit', 'credit_days', 'total_debt')
        self.customer_table = ttk.Treeview(table_frame, columns=columns, 
                                          show='headings', height=10)
        
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
        stats_frame.pack(fill=X, padx=10, pady=10)
        
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
        
        # ตัวกรอง
        filter_frame = Frame(parent, bg='#ffffff')
        filter_frame.pack(fill=X, padx=10, pady=5)
        
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
        
        # ตารางบิลเครดิต
        table_frame = Frame(parent, bg='#ffffff')
        table_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        columns = ('bill_id', 'customer', 'bill_date', 'due_date', 
                  'total', 'paid', 'remaining', 'status')
        self.credit_table = ttk.Treeview(table_frame, columns=columns, 
                                        show='headings', height=9)
        
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
        
        widths = [120, 150, 120, 120, 100, 100, 100, 100]
        
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
        
        ttk.Button(btn_frame, text='💰 ชำระเงิน', 
                  command=self.pay_credit_bill).pack(side=LEFT, padx=5)
        ttk.Button(btn_frame, text='📄 พิมพ์ใบวางบิล', 
                  command=self.print_credit_bill).pack(side=LEFT, padx=5)
        
        # Bind double-click
        self.credit_table.bind('<Double-Button-1>', 
                              lambda e: self.pay_credit_bill())
        
        # โหลดข้อมูล
        self.refresh_credit_table()
        
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
        for customer in customers:
            self.customer_table.insert('', 'end', values=(
                customer[0],  # ID
                customer[1],  # Name
                customer[2] or '-',  # Phone
                f"{customer[5]:,.2f}",  # Credit Limit
                customer[6],  # Credit Days
                f"{customer[7]:,.2f}"  # Total Debt
            ))
    
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
            selected = self.credit_table.selection()
            if not selected:
                messagebox.showwarning("Warning", "กรุณาเลือกบิลที่ต้องการพิมพ์")
                return
            
            item = self.credit_table.item(selected[0])
            bill_id = item['values'][0]
            
            # TODO: เชื่อมต่อกับ receipt_printer.py เพื่อพิมพ์ใบวางบิล
            messagebox.showinfo("Info", f"กำลังพิมพ์บิล {bill_id}\n(ฟีเจอร์นี้อยู่ระหว่างพัฒนา)")
            
        except Exception as e:
            messagebox.showerror("Error", f"เกิดข้อผิดพลาด: {str(e)}")
    
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
        
        # เพิ่มข้อมูลในตาราง
        for bill in bills:
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
    
    def refresh_data(self):
        """รีเฟรชข้อมูลทั้งหมด"""
        self.refresh_customer_table()
        self.refresh_credit_table()