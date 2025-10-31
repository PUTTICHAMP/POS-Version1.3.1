from tkinter import *
from tkinter import ttk, messagebox, filedialog
from basicsql import *
import csv

class ProductTab(Frame):
    def __init__(self, parent, sales_tab=None, dashboard_tab=None, profit_tab=None):
        super().__init__(parent)
        self.pack(fill=BOTH, expand=True)
        
        # Reference ไปยังแท็บอื่นๆ
        self.sales_tab = sales_tab
        self.dashboard_tab = dashboard_tab
        self.profit_tab = profit_tab
        
        # ตัวแปร
        self.v_barcode2 = StringVar()
        self.v_title2 = StringVar()
        self.v_price2 = StringVar()
        self.v_cost2 = StringVar()
        self.v_quantity2 = StringVar()
        self.v_unit2 = StringVar()
        self.v_category2 = StringVar()
        self.v_reorder_point2 = StringVar()
        
        # ค่าเริ่มต้น
        self.v_unit2.set('ชิ้น')
        self.v_category2.set('')
        self.v_reorder_point2.set('1')
        
        # โหมดแก้ไข
        self.edit_mode = False
        self.current_barcode = None
        
        # สร้าง GUI
        self.create_widgets()
        
    def create_widgets(self):
        # หัวข้อและปุ่ม Import
        header_frame = Frame(self)
        header_frame.pack(pady=10, fill=X, padx=20)
        
        title_label = Label(header_frame, text='จัดการข้อมูลสินค้า', font=('Arial', 18, 'bold'))
        title_label.pack(side=LEFT)
        
        # ปุ่ม Import CSV
        btn_import = ttk.Button(header_frame, text='📂 นำเข้า CSV', command=self.import_csv)
        btn_import.pack(side=RIGHT, padx=5)
        
        # ปุ่ม Download Template
        btn_template = ttk.Button(header_frame, text='📄 ดาวน์โหลด Template', command=self.download_template)
        btn_template.pack(side=RIGHT, padx=5)
        
        # สร้าง main container
        main_container = Frame(self)
        main_container.pack(fill=BOTH, expand=True, padx=20, pady=10)
        
        # ส่วนซ้าย - ตารางสินค้า (65% ของพื้นที่)
        left_frame = Frame(main_container, bg='white', relief=RIDGE, bd=1)
        left_frame.pack(side=LEFT, fill=BOTH, expand=True, padx=(0, 10))
        
        # ส่วนขวา - ฟอร์มเพิ่มสินค้า (35% ของพื้นที่)
        right_frame = Frame(main_container, bg='#f0f0f0', relief=RIDGE, bd=1, width=350)
        right_frame.pack(side=RIGHT, fill=Y, padx=(10, 0))
        right_frame.pack_propagate(False)  # ป้องกันการปรับขนาดอัตโนมัติ
        
        # สร้างตารางสินค้าในส่วนซ้าย
        self.create_product_table(left_frame)
        
        # สร้างฟอร์มในส่วนขวา
        self.create_product_form(right_frame)
        
    def create_product_table(self, parent):
        """สร้างตารางแสดงข้อมูลสินค้า"""
        # หัวข้อตาราง
        table_title = Label(parent, text='รายการสินค้าทั้งหมด', font=('Arial', 14, 'bold'), bg='white')
        table_title.pack(pady=10)
        
        # Frame สำหรับตารางและ scrollbar
        table_frame = Frame(parent, bg='white')
        table_frame.pack(fill=BOTH, expand=True, padx=10, pady=(0, 10))
        
        # สร้าง Treeview
        product_header = ['Barcode', 'ชื่อสินค้า', 'ราคาขาย', 'ราคาทุน', 'สต็อก', 'หน่วย', 'ประเภท', 'Reorder']
        product_width = [90, 150, 80, 80, 60, 70, 90, 70]
        
        self.table_product = ttk.Treeview(table_frame, columns=product_header, 
                                         show='headings', height=18)
        
        for hd, w in zip(product_header, product_width):
            self.table_product.heading(hd, text=hd)
            self.table_product.column(hd, width=w, anchor='center')
            
        self.table_product.column('ชื่อสินค้า', anchor='w')
        self.table_product.column('ราคาขาย', anchor='e')
        self.table_product.column('ราคาทุน', anchor='e')
        self.table_product.column('สต็อก', anchor='e')
        self.table_product.column('Reorder', anchor='e')
        
        # Scrollbar สำหรับตาราง
        table_scrollbar = ttk.Scrollbar(table_frame, orient=VERTICAL, command=self.table_product.yview)
        self.table_product.configure(yscrollcommand=table_scrollbar.set)
        
        # Pack ตารางและ scrollbar
        self.table_product.pack(side=LEFT, fill=BOTH, expand=True)
        table_scrollbar.pack(side=RIGHT, fill=Y)
        
        # Event การคลิกแถว
        self.table_product.bind('<ButtonRelease-1>', self.on_row_select)
        
        # โหลดข้อมูลตาราง
        self.update_table_product()
        
    def create_product_form(self, parent):
        """สร้างฟอร์มเพิ่ม/แก้ไขสินค้า"""
        # หัวข้อฟอร์ม
        self.L2 = Label(parent, text='เพิ่มสินค้าใหม่', font=('Arial', 14, 'bold'), bg='#f0f0f0')
        self.L2.pack(pady=15)
        
        # Frame สำหรับฟอร์ม
        form_frame = Frame(parent, bg='#f0f0f0')
        form_frame.pack(fill=BOTH, expand=True, padx=15)
        
        # สร้างฟิลด์แบบ 2 คอลัมน์
        fields = [
            ('Barcode:', self.v_barcode2),
            ('ชื่อสินค้า:', self.v_title2),
            ('ราคาขาย (บาท):', self.v_price2),
            ('ราคาทุน (บาท):', self.v_cost2),
            ('จำนวนสต็อก:', self.v_quantity2),
            ('จุดสั่งซื้อใหม่:', self.v_reorder_point2),
            ('ประเภท:', self.v_category2),
        ]
        
        self.entries = {}
        row = 0
        
        for label_text, var in fields:
            # Label (คอลัมน์ซ้าย)
            label = Label(form_frame, text=label_text, font=('Arial', 10), bg='#f0f0f0', anchor='w')
            label.grid(row=row, column=0, sticky='w', pady=3, padx=(0, 5))
            
            # Entry (คอลัมน์ขวา)
            entry = ttk.Entry(form_frame, textvariable=var, font=('Arial', 10), width=18)
            entry.grid(row=row, column=1, sticky='ew', pady=3)
            self.entries[label_text] = entry
            row += 1
        
        # หน่วย (Dropdown) - แถวพิเศษ
        Label(form_frame, text='หน่วย:', font=('Arial', 10), bg='#f0f0f0', anchor='w').grid(row=row, column=0, sticky='w', pady=3, padx=(0, 5))
        units = ['ชิ้น', 'ลูก', 'กิโลกรัม', 'กรัม', 'แผง', 'ขวด', 'ถุง', 'กล่อง']
        self.unit_combo = ttk.Combobox(form_frame, textvariable=self.v_unit2, 
                                      values=units, font=('Arial', 10), width=16, state='readonly')
        self.unit_combo.grid(row=row, column=1, sticky='ew', pady=3)
        row += 1
        
        # ข้อมูลผู้ขาย (Textarea) - ใช้ 2 คอลัมน์
        Label(form_frame, text='ข้อมูลผู้ขาย/ซัพพลายเออร์:', font=('Arial', 10), bg='#f0f0f0').grid(row=row, column=0, columnspan=2, sticky='w', pady=(10, 3))
        row += 1
        self.supplier_text = Text(form_frame, height=4, width=25, font=('Arial', 9))
        self.supplier_text.grid(row=row, column=0, columnspan=2, sticky='ew', pady=(0, 10))
        row += 1
        
        # กำหนดให้คอลัมน์ขวาขยายได้
        form_frame.grid_columnconfigure(1, weight=1)
        
        # ปุ่มจัดการ
        self.create_buttons(form_frame, row)
        
        # Focus ที่ช่องบาร์โค้ด
        self.entries['Barcode:'].focus()
        
    def create_buttons(self, parent, start_row):
        """สร้างปุ่มจัดการ"""
        # Frame สำหรับปุ่ม
        button_frame = Frame(parent, bg='#f0f0f0')
        button_frame.grid(row=start_row, column=0, columnspan=2, sticky='ew', pady=20)
        
        # Label แสดงสถานะ
        self.status_label = Label(button_frame, text="", font=('Arial', 9), bg='#f0f0f0', fg='red')
        self.status_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))
        
        # ปุ่มแถวที่ 1
        self.btn_save = ttk.Button(button_frame, text='💾 บันทึก', command=self.savedata)
        self.btn_save.grid(row=1, column=0, padx=2, pady=5, sticky='ew', ipady=5)
        
        self.btn_edit = ttk.Button(button_frame, text='✏️ แก้ไข', command=self.edit_product)
        self.btn_edit.grid(row=1, column=1, padx=2, pady=5, sticky='ew', ipady=5)
        
        # ปุ่มแถวที่ 2
        self.btn_delete = ttk.Button(button_frame, text='🗑️ ลบ', command=self.delete_product)
        self.btn_delete.grid(row=2, column=0, padx=2, pady=5, sticky='ew', ipady=5)
        
        self.btn_cancel = ttk.Button(button_frame, text='↶ ยกเลิก', command=self.cancel_edit)
        self.btn_cancel.grid(row=2, column=1, padx=2, pady=5, sticky='ew', ipady=5)
        
        # กำหนดให้ปุ่มขยายเต็มความกว้าง
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)
        
    def import_csv(self):
        """นำเข้าข้อมูลจากไฟล์ CSV"""
        file_path = filedialog.askopenfilename(
            title="เลือกไฟล์ CSV",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if not file_path:
            return
        
        try:
            success_count = 0
            error_count = 0
            error_details = []
            
            with open(file_path, 'r', encoding='utf-8-sig') as file:
                csv_reader = csv.DictReader(file)
                
                # ตรวจสอบ header ที่จำเป็น
                required_fields = ['barcode', 'title', 'price', 'cost', 'quantity', 'unit', 'category', 'reorder_point']
                headers = [h.lower().strip() for h in csv_reader.fieldnames]
                
                missing_fields = [f for f in required_fields if f not in headers]
                if missing_fields:
                    messagebox.showerror("Error", f"ไฟล์ CSV ขาดคอลัมน์: {', '.join(missing_fields)}")
                    return
                
                # อ่านข้อมูลและเพิ่มลงฐานข้อมูล
                for row_num, row in enumerate(csv_reader, start=2):
                    try:
                        # ทำความสะอาดข้อมูล
                        barcode = row.get('barcode', '').strip()
                        title = row.get('title', '').strip()
                        price = float(row.get('price', '0').strip())
                        cost = float(row.get('cost', '0').strip())
                        quantity = int(row.get('quantity', '0').strip())
                        unit = row.get('unit', 'ชิ้น').strip()
                        category = row.get('category', '').strip()
                        reorder_point = int(row.get('reorder_point', '1').strip())
                        supplier = row.get('supplier', '').strip()
                        
                        # ตรวจสอบข้อมูลที่จำเป็น
                        if not all([barcode, title, price, cost, quantity, unit, category]):
                            error_details.append(f"แถว {row_num}: ข้อมูลไม่ครบถ้วน")
                            error_count += 1
                            continue
                        
                        # เพิ่มข้อมูลลงฐานข้อมูล
                        insert_product(barcode, title, price, cost, quantity, unit, category, reorder_point, supplier)
                        success_count += 1
                        
                    except ValueError as e:
                        error_details.append(f"แถว {row_num}: ข้อมูลตัวเลขไม่ถูกต้อง ({str(e)})")
                        error_count += 1
                    except Exception as e:
                        error_details.append(f"แถว {row_num}: {str(e)}")
                        error_count += 1
            
            # แสดงผลลัพธ์
            result_message = f"นำเข้าข้อมูลสำเร็จ: {success_count} รายการ"
            if error_count > 0:
                result_message += f"\nมีข้อผิดพลาด: {error_count} รายการ"
                if len(error_details) <= 10:
                    result_message += "\n\n" + "\n".join(error_details)
                else:
                    result_message += "\n\n" + "\n".join(error_details[:10]) + f"\n... และอีก {len(error_details)-10} ข้อผิดพลาด"
            
            messagebox.showinfo("Import CSV", result_message)
            
            # อัปเดตตารางและแท็บอื่นๆ
            self.update_table_product()
            self.refresh_other_tabs()
            
        except Exception as e:
            messagebox.showerror("Error", f"เกิดข้อผิดพลาดในการอ่านไฟล์: {str(e)}")
    
    def download_template(self):
        """ดาวน์โหลดไฟล์ Template CSV"""
        file_path = filedialog.asksaveasfilename(
            title="บันทึก Template CSV",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile="product_template.csv"
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'w', newline='', encoding='utf-8-sig') as file:
                writer = csv.writer(file)
                
                # เขียน header
                headers = ['barcode', 'title', 'price', 'cost', 'quantity', 'unit', 'category', 'reorder_point', 'supplier']
                writer.writerow(headers)
                
                # เขียนตัวอย่างข้อมูล
                writer.writerow(['0001', 'สินค้าตัวอย่าง 1', '100', '80', '50', 'ชิ้น', 'อาหาร', '10', 'บริษัท ABC'])
                writer.writerow(['0002', 'สินค้าตัวอย่าง 2', '200', '150', '30', 'กล่อง', 'เครื่องดื่ม', '5', 'บริษัท XYZ'])
                writer.writerow(['0003', 'สินค้าตัวอย่าง 3', '50', '35', '100', 'ถุง', 'ของใช้', '20', ''])
            
            messagebox.showinfo("Success", f"บันทึก Template สำเร็จที่:\n{file_path}")
            
        except Exception as e:
            messagebox.showerror("Error", f"เกิดข้อผิดพลาดในการบันทึกไฟล์: {str(e)}")
    
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
        reorder_point = self.v_reorder_point2.get()
        supplier = self.supplier_text.get("1.0", END).strip()
        
        if not all([barcode, title, price, cost, quantity, unit, category, reorder_point]):
            messagebox.showerror("Error", "กรุณากรอกข้อมูลให้ครบทุกช่อง")
            return
            
        try:
            price = float(price)
            cost = float(cost)
            quantity = int(quantity)
            reorder_point = int(reorder_point)
            
            if self.edit_mode:
                # อัปเดตข้อมูล
                update_product(barcode, title, price, cost, quantity, unit, category, reorder_point, supplier)
                messagebox.showinfo("Success", "อัปเดตข้อมูลสินค้าเรียบร้อยแล้ว")
                self.cancel_edit()
            else:
                # เพิ่มข้อมูลใหม่
                insert_product(barcode, title, price, cost, quantity, unit, category, reorder_point, supplier)
                messagebox.showinfo("Success", "บันทึกข้อมูลสินค้าเรียบร้อยแล้ว")
                
                # เคลียร์ข้อมูลในฟอร์มหลังเพิ่มใหม่
                self.clear_form()
                self.status_label.config(text='✅ บันทึกสำเร็จ - พร้อมเพิ่มสินค้าใหม่', fg='green')
            
            # อัปเดตตาราง
            self.update_table_product()
            
            # อัปเดตแท็บอื่นๆ
            self.refresh_other_tabs()
                
            # กลับไป focus ที่ช่องบาร์โค้ด และรีเซ็ตสถานะ
            self.entries['Barcode:'].focus()
            self.L2.config(text='เพิ่มสินค้าใหม่')
            self.btn_save.config(state='normal')  # Enable ปุ่มบันทึกหลังบันทึกสำเร็จ
            
        except ValueError:
            messagebox.showerror("Error", "กรุณากรอกราคา/ทุน/จำนวน/จุดสั่งซื้อเป็นตัวเลข")
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
        self.v_category2.set('')
        self.v_reorder_point2.set('5')
        self.supplier_text.delete("1.0", END)
        
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
            
            if len(values) >= 8:
                self.v_reorder_point2.set(values[7])
            
            # โหลดข้อมูล supplier
            try:
                product_data = get_product_by_barcode(values[0])
                if product_data and len(product_data) >= 10:
                    self.supplier_text.delete("1.0", END)
                    self.supplier_text.insert("1.0", product_data[9])
            except:
                pass  # ไม่แสดง error หากไม่สามารถโหลดข้อมูล supplier ได้
            
    def edit_product(self):
        """เข้าสู่โหมดแก้ไขสินค้า"""
        if not self.v_barcode2.get():
            messagebox.showwarning("Warning", "กรุณาเลือกสินค้าที่ต้องการแก้ไขจากตาราง")
            return
            
        self.edit_mode = True
        self.current_barcode = self.v_barcode2.get()
        self.L2.config(text='แก้ไขข้อมูลสินค้า')
        self.entries['Barcode:'].config(state='disabled')  # ไม่ให้แก้ไขบาร์โค้ด
        
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
                
                # รีเซ็ตสถานะหลังลบ
                self.L2.config(text='เพิ่มสินค้าใหม่')
                self.btn_save.config(state='normal')  # Enable ปุ่มบันทึกหลังลบ
                self.status_label.config(text='✅ ลบสำเร็จ - พร้อมเพิ่มสินค้าใหม่', fg='green')
                self.entries['Barcode:'].focus()
                
                # อัปเดตแท็บอื่นๆ
                self.refresh_other_tabs()
                    
            except Exception as e:
                messagebox.showerror("Error", f"เกิดข้อผิดพลาด: {str(e)}")
                
    def cancel_edit(self):
        """ยกเลิกการแก้ไข"""
        self.edit_mode = False
        self.current_barcode = None
        self.L2.config(text='เพิ่มสินค้าใหม่')
        self.entries['Barcode:'].config(state='normal')
        self.clear_form()
        self.entries['Barcode:'].focus()
        
    def refresh_other_tabs(self):
        """รีเฟรชแท็บอื่นๆ"""
        try:
            if self.sales_tab:
                self.sales_tab.refresh_product_buttons()
            if self.dashboard_tab:
                self.dashboard_tab.refresh_data()
            if self.profit_tab:
                self.profit_tab.refresh_data()
        except Exception as e:
            print(f"Error refreshing other tabs: {e}")
                
    def set_references(self, sales_tab=None, dashboard_tab=None, profit_tab=None):
        """ตั้งค่า reference ไปยังแท็บอื่นๆ (เรียกหลังสร้างแท็บทั้งหมดแล้ว)"""
        self.sales_tab = sales_tab
        self.dashboard_tab = dashboard_tab
        self.profit_tab = profit_tab