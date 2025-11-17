from tkinter import *
from tkinter import ttk, messagebox, filedialog
from basicsql import *
import json
import csv
from datetime import datetime, timedelta
from tkcalendar import DateEntry

class ProfitTab(Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.pack(fill=BOTH, expand=True)
        
        # เก็บข้อมูลสำหรับ Export และ Search
        self.current_data = []
        self.all_data = []  # เก็บข้อมูลทั้งหมดสำหรับการค้นหา
        
        # สร้าง Canvas และ Scrollbar สำหรับทั้งหน้า
        self.create_scrollable_frame()
        
        # สร้าง GUI
        self.create_widgets()
        
    def create_scrollable_frame(self):
        """สร้าง Canvas พร้อม Scrollbar สำหรับทั้งหน้า"""
        # Canvas หลัก
        self.canvas = Canvas(self, bg="#f0f0f0")
        self.canvas.pack(side=LEFT, fill=BOTH, expand=True)
        
        # Scrollbar แนวตั้ง
        self.v_scrollbar = ttk.Scrollbar(self, orient=VERTICAL, command=self.canvas.yview)
        self.v_scrollbar.pack(side=RIGHT, fill=Y)
        
        # กำหนด scrollbar ให้ canvas
        self.canvas.configure(yscrollcommand=self.v_scrollbar.set)
        
        # Frame ภายใน Canvas
        self.scrollable_frame = Frame(self.canvas, bg="#f0f0f0")
        self.canvas_frame = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor='nw')
        
        # อัพเดท scroll region เมื่อมีการเปลี่ยนแปลง
        self.scrollable_frame.bind('<Configure>', self.on_frame_configure)
        self.canvas.bind('<Configure>', self.on_canvas_configure)
        
        # Bind mouse wheel สำหรับการเลื่อน
        self.bind_mousewheel()
        
    def on_frame_configure(self, event=None):
        """อัพเดท scroll region เมื่อ frame มีการเปลี่ยนแปลง"""
        self.canvas.configure(scrollregion=self.canvas.bbox('all'))
        
    def on_canvas_configure(self, event):
        """ปรับขนาด frame ให้เต็มความกว้างของ canvas"""
        canvas_width = event.width
        self.canvas.itemconfig(self.canvas_frame, width=canvas_width)
        
    def bind_mousewheel(self):
        """Bind mouse wheel event สำหรับการเลื่อนด้วยลูกกลิ้งเมาส์"""
        def _on_mousewheel(event):
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            
        def _bind_to_mousewheel(event):
            self.canvas.bind_all("<MouseWheel>", _on_mousewheel)
            
        def _unbind_from_mousewheel(event):
            self.canvas.unbind_all("<MouseWheel>")
            
        self.canvas.bind('<Enter>', _bind_to_mousewheel)
        self.canvas.bind('<Leave>', _unbind_from_mousewheel)
        
    def create_widgets(self):
        FONT1 = (None, 20)
        FONT2 = (None, 14)
        
        # Frame สำหรับหัวข้อและปุ่ม Export
        header_frame = Frame(self.scrollable_frame, bg="#f0f0f0")
        header_frame.pack(fill=X, pady=10, padx=20)
        
        # หัวข้อ
        Label(header_frame, text='📈 Profit Analysis - วิเคราะห์กำไร', 
              font=('Arial', 18, 'bold'), bg="#f0f0f0").pack(side=TOP)
        
        # ปุ่ม Export
        ttk.Button(header_frame, text='📊 Export CSV', 
                   command=self.export_to_csv).pack(side=RIGHT, padx=5)
        ttk.Button(header_frame, text='📈 Export สรุป', 
                   command=self.export_summary_csv).pack(side=RIGHT, padx=5)
        
        # Frame หลัก
        main_frame = Frame(self.scrollable_frame, bg="#f0f0f0")
        main_frame.pack(fill=BOTH, expand=True, padx=20, pady=10)
        
        # ส่วนควบคุมการกรอง
        self.create_filter_section(main_frame)
        
        # ส่วนค้นหา (ใหม่)
        self.create_search_section(main_frame)
        
        # ส่วนสรุปกำไร
        self.create_profit_summary(main_frame)
        
        # ส่วนตารางรายละเอียด
        self.create_profit_table(main_frame)
        
        # โหลดข้อมูลครั้งแรก
        self.refresh_data()
        
    def create_filter_section(self, parent):
        """สร้างส่วนควบคุมการกรองข้อมูล"""
        filter_frame = LabelFrame(parent, text="กรองข้อมูลตามช่วงวันที่", 
                                 font=(None, 14), bg="#f0f0f0")
        filter_frame.pack(fill=X, pady=10)
        
        # Frame สำหรับควบคุม
        control_frame = Frame(filter_frame, bg="#f0f0f0")
        control_frame.pack(padx=20, pady=15)
        
        # วันที่เริ่มต้น
        Label(control_frame, text="วันที่เริ่มต้น:", font=(None, 12), 
              bg='white').grid(row=0, column=0, sticky='w', padx=5)
        self.start_date = DateEntry(control_frame, width=12, background='darkblue',
                                   foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        self.start_date.grid(row=0, column=1, padx=5)
        
        # วันที่สิ้นสุด
        Label(control_frame, text="วันที่สิ้นสุด:", font=(None, 12), 
              bg='white').grid(row=0, column=2, sticky='w', padx=5)
        self.end_date = DateEntry(control_frame, width=12, background='darkblue',
                                 foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        self.end_date.grid(row=0, column=3, padx=5)
        
        # ปุ่มควบคุม
        ttk.Button(control_frame, text="วันนี้", 
                   command=self.set_today).grid(row=1, column=0, padx=5, pady=10)
        ttk.Button(control_frame, text="สัปดาห์นี้", 
                   command=self.set_this_week).grid(row=1, column=1, padx=5, pady=10)
        ttk.Button(control_frame, text="เดือนนี้", 
                   command=self.set_this_month).grid(row=1, column=2, padx=5, pady=10)
        ttk.Button(control_frame, text="🔍 ค้นหา", 
                   command=self.refresh_data).grid(row=1, column=3, padx=5, pady=10)
        
        # ตั้งค่าเริ่มต้นเป็นวันนี้
        self.set_today()
        
    def create_search_section(self, parent):
        """สร้างส่วนค้นหาแบบ Real-time"""
        search_frame = LabelFrame(parent, text="🔍 ค้นหารายละเอียดการขาย", 
                                 font=(None, 14), bg='white')
        search_frame.pack(fill=X, pady=10)
        
        # Frame สำหรับควบคุมการค้นหา
        control_frame = Frame(search_frame, bg='white')
        control_frame.pack(padx=20, pady=15, fill=X)
        
        # Label คำแนะนำ
        Label(control_frame, text="ค้นหา:", font=(None, 12, 'bold'), 
              bg='white').grid(row=0, column=0, sticky='w', padx=5)
        
        # Entry สำหรับค้นหา
        self.search_var = StringVar()
        self.search_var.trace('w', self.on_search_change)  # Real-time search
        
        search_entry = ttk.Entry(control_frame, textvariable=self.search_var, 
                                width=40, font=(None, 11))
        search_entry.grid(row=0, column=1, padx=5, sticky='ew')
        
        # ปุ่มล้างการค้นหา
        ttk.Button(control_frame, text="❌ ล้าง", 
                   command=self.clear_search).grid(row=0, column=2, padx=5)
        
        # Label แสดงผลการค้นหา
        self.search_result_label = Label(control_frame, text="", 
                                        font=(None, 10), fg='blue', bg='white')
        self.search_result_label.grid(row=1, column=0, columnspan=3, sticky='w', pady=5)
        
        # ข้อความช่วยเหลือ
        help_text = "💡 คำแนะนำ: สามารถค้นหาด้วย วันที่ (YYYY-MM-DD), Transaction ID, หรือชื่อสินค้า"
        Label(control_frame, text=help_text, font=(None, 9), 
              fg='gray', bg='white').grid(row=2, column=0, columnspan=3, sticky='w')
        
        # ทำให้ search entry ขยายตามขนาดหน้าต่าง
        control_frame.columnconfigure(1, weight=1)
        
    def create_profit_summary(self, parent):
        """สร้างส่วนสรุปกำไร"""
        summary_frame = LabelFrame(parent, text="สรุปกำไร", font=(None, 14), bg='white')
        summary_frame.pack(fill=X, pady=10)
        
        # ตัวแปรสำหรับแสดงข้อมูลสรุป
        self.v_total_sales = StringVar()
        self.v_total_cost = StringVar()
        self.v_total_profit = StringVar()
        self.v_profit_margin = StringVar()
        
        # Grid layout สำหรับข้อมูลสรุป
        info_frame = Frame(summary_frame, bg='white')
        info_frame.pack(padx=20, pady=15)
        
        # แถวที่ 1
        Label(info_frame, text="ยอดขายรวม:", font=(None, 14, 'bold'), 
              bg='white').grid(row=0, column=0, sticky='w', padx=10, pady=5)
        Label(info_frame, textvariable=self.v_total_sales, font=(None, 14, 'bold'), 
              fg='blue', bg='white').grid(row=0, column=1, sticky='w', padx=10, pady=5)
        
        Label(info_frame, text="ต้นทุนรวม:", font=(None, 14, 'bold'), 
              bg='white').grid(row=0, column=2, sticky='w', padx=10, pady=5)
        Label(info_frame, textvariable=self.v_total_cost, font=(None, 14, 'bold'), 
              fg='red', bg='white').grid(row=0, column=3, sticky='w', padx=10, pady=5)
        
        # แถวที่ 2
        Label(info_frame, text="กำไรสุทธิ:", font=(None, 16, 'bold'), 
              bg='white').grid(row=1, column=0, sticky='w', padx=10, pady=10)
        Label(info_frame, textvariable=self.v_total_profit, font=(None, 16, 'bold'), 
              fg='green', bg='white').grid(row=1, column=1, sticky='w', padx=10, pady=10)
        
        Label(info_frame, text="อัตรากำไร:", font=(None, 14, 'bold'), 
              bg='white').grid(row=1, column=2, sticky='w', padx=10, pady=10)
        Label(info_frame, textvariable=self.v_profit_margin, font=(None, 14, 'bold'), 
              fg='purple', bg='white').grid(row=1, column=3, sticky='w', padx=10, pady=10)
        
    def create_profit_table(self, parent):
        """สร้างตารางแสดงรายละเอียดกำไร"""
        table_frame = LabelFrame(parent, text="รายละเอียดการขาย", 
                                font=(None, 14), bg='white')
        table_frame.pack(fill=BOTH, expand=True, pady=10)
        
        # สร้าง Treeview พร้อม scrollbar
        tree_frame = Frame(table_frame, bg='white')
        tree_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        # Headers และ widths
        headers = ['วันที่', 'Transaction ID', 'สินค้า', 'จำนวน', 'ราคาขาย', 
                  'ต้นทุน', 'รายได้', 'ต้นทุนรวม', 'กำไร', 'อัตรากำไร%']
        widths = [100, 120, 200, 80, 100, 100, 100, 100, 100, 100]
        
        self.profit_table = ttk.Treeview(tree_frame, columns=headers, 
                                        show='headings', height=20)
        
        # กำหนด heading และ column
        for header, width in zip(headers, widths):
            self.profit_table.heading(header, text=header)
            self.profit_table.column(header, width=width, anchor='center')
            
        # จัด alignment ให้เหมาะสม
        self.profit_table.column('สินค้า', anchor='w')
        self.profit_table.column('จำนวน', anchor='e')
        self.profit_table.column('ราคาขาย', anchor='e')
        self.profit_table.column('ต้นทุน', anchor='e')
        self.profit_table.column('รายได้', anchor='e')
        self.profit_table.column('ต้นทุนรวม', anchor='e')
        self.profit_table.column('กำไร', anchor='e')
        self.profit_table.column('อัตรากำไร%', anchor='e')
        
        # Scrollbar แนวตั้ง
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=VERTICAL, 
                                    command=self.profit_table.yview)
        self.profit_table.configure(yscrollcommand=v_scrollbar.set)
        
        # Scrollbar แนวนอน
        h_scrollbar = ttk.Scrollbar(tree_frame, orient=HORIZONTAL, 
                                    command=self.profit_table.xview)
        self.profit_table.configure(xscrollcommand=h_scrollbar.set)
        
        # Pack table และ scrollbar
        self.profit_table.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        # ทำให้ table ขยายเต็มพื้นที่
        tree_frame.rowconfigure(0, weight=1)
        tree_frame.columnconfigure(0, weight=1)
        
        # Bind mouse wheel สำหรับ table
        def _on_table_mousewheel(event):
            self.profit_table.yview_scroll(int(-1*(event.delta/120)), "units")
            
        self.profit_table.bind('<MouseWheel>', _on_table_mousewheel)
        
    def on_search_change(self, *args):
        """เรียกใช้เมื่อมีการเปลี่ยนแปลงในช่องค้นหา (Real-time)"""
        search_text = self.search_var.get().strip().lower()
        
        if not search_text:
            # ถ้าไม่มีข้อความค้นหา แสดงข้อมูลทั้งหมด
            self.display_data(self.all_data)
            self.search_result_label.config(text="")
            return
        
        # ค้นหาข้อมูลที่ตรงกับเงื่อนไข
        filtered_data = []
        for data in self.all_data:
            if (search_text in data['date'].lower() or
                search_text in str(data['transaction_id']).lower() or
                search_text in data['product'].lower() or
                search_text in data['barcode'].lower()):
                filtered_data.append(data)
        
        # แสดงผลข้อมูลที่กรอง
        self.display_data(filtered_data)
        
        # แสดงผลการค้นหา
        if filtered_data:
            self.search_result_label.config(
                text=f"✅ พบ {len(filtered_data)} รายการจาก {len(self.all_data)} รายการทั้งหมด",
                fg='green'
            )
        else:
            self.search_result_label.config(
                text=f"❌ ไม่พบข้อมูลที่ค้นหา '{self.search_var.get()}'",
                fg='red'
            )
    
    def clear_search(self):
        """ล้างการค้นหาและแสดงข้อมูลทั้งหมด"""
        self.search_var.set("")
        self.display_data(self.all_data)
        self.search_result_label.config(text="")
        
    def display_data(self, data_list):
        """แสดงข้อมูลในตาราง"""
        # เคลียร์ตาราง
        for item in self.profit_table.get_children():
            self.profit_table.delete(item)
        
        # เพิ่มข้อมูลใหม่
        for data in data_list:
            self.profit_table.insert('', 'end', values=[
                data['date'], 
                data['transaction_id'], 
                data['product'], 
                data['quantity'],
                f"{data['price']:,.2f}", 
                f"{data['cost']:,.2f}", 
                f"{data['revenue']:,.2f}",
                f"{data['total_cost']:,.2f}", 
                f"{data['profit']:,.2f}", 
                f"{data['profit_margin']:.1f}%"
            ])
        
        # อัพเดทข้อมูลสำหรับ Export
        self.current_data = data_list
        
    def set_today(self):
        """ตั้งค่าวันที่เป็นวันนี้"""
        today = datetime.now().date()
        self.start_date.set_date(today)
        self.end_date.set_date(today)
        
    def set_this_week(self):
        """ตั้งค่าวันที่เป็นสัปดาห์นี้"""
        today = datetime.now().date()
        start_week = today - timedelta(days=today.weekday())
        end_week = start_week + timedelta(days=6)
        self.start_date.set_date(start_week)
        self.end_date.set_date(end_week)
        
    def set_this_month(self):
        """ตั้งค่าวันที่เป็นเดือนนี้"""
        today = datetime.now().date()
        start_month = today.replace(day=1)
        next_month = start_month.replace(month=start_month.month + 1) if start_month.month < 12 else start_month.replace(year=start_month.year + 1, month=1)
        end_month = next_month - timedelta(days=1)
        self.start_date.set_date(start_month)
        self.end_date.set_date(end_month)
        
    def refresh_data(self):
        """รีเฟรชข้อมูลกำไร"""
        try:
            # ดึงข้อมูลการขายในช่วงวันที่ที่เลือก
            start_date_str = self.start_date.get_date().strftime('%Y-%m-%d')
            end_date_str = self.end_date.get_date().strftime('%Y-%m-%d')
            
            transactions = get_sales_by_date_range(start_date_str, end_date_str)
            
            # คำนวณข้อมูลสรุป
            total_sales = 0
            total_cost = 0
            total_profit = 0
            
            # เคลียร์ข้อมูลเก่า
            self.all_data = []
            self.current_data = []
            
            # ล้างการค้นหา
            self.search_var.set("")
            self.search_result_label.config(text="")
                
            # วิเคราะห์แต่ละ transaction
            for transaction in transactions:
                try:
                    trans_id, trans_date, subtotal, vat, grand_total, received, change, items_json = transaction[1:9]
                    
                    # แปลง JSON เป็นข้อมูลสินค้า
                    items = json.loads(items_json)
                    trans_date_short = trans_date.split(' ')[0]  # เอาแค่วันที่
                    
                    for item in items:
                        barcode, title, price, quantity = item
                        price = float(price)
                        quantity = int(quantity)
                        
                        # ดึงข้อมูลต้นทุนจากฐานข้อมูล
                        product_data = get_product_by_barcode(barcode)
                        if product_data and len(product_data) >= 5:
                            cost = float(product_data[4])  # cost field
                        else:
                            cost = 0  # หากไม่พบข้อมูลต้นทุน
                        
                        # คำนวณ
                        revenue = price * quantity
                        total_item_cost = cost * quantity
                        profit = revenue - total_item_cost
                        profit_margin = (profit / revenue * 100) if revenue > 0 else 0
                        
                        # รวมยอด
                        total_sales += revenue
                        total_cost += total_item_cost
                        total_profit += profit
                        
                        # เก็บข้อมูลทั้งหมด
                        data_item = {
                            'date': trans_date_short,
                            'transaction_id': trans_id,
                            'barcode': barcode,
                            'product': title,
                            'quantity': quantity,
                            'price': price,
                            'cost': cost,
                            'revenue': revenue,
                            'total_cost': total_item_cost,
                            'profit': profit,
                            'profit_margin': profit_margin
                        }
                        
                        self.all_data.append(data_item)
                        
                except (ValueError, KeyError, json.JSONDecodeError) as e:
                    print(f"Error processing transaction: {e}")
                    continue
            
            # แสดงข้อมูลทั้งหมด
            self.display_data(self.all_data)
            
            # คำนวณอัตรากำไรรวม
            overall_margin = (total_profit / total_sales * 100) if total_sales > 0 else 0
            
            # เก็บข้อมูลสรุปสำหรับ Export
            self.summary_data = {
                'total_sales': total_sales,
                'total_cost': total_cost,
                'total_profit': total_profit,
                'profit_margin': overall_margin
            }
            
            # อัปเดตข้อมูลสรุป
            self.v_total_sales.set(f"{total_sales:,.2f} บาท")
            self.v_total_cost.set(f"{total_cost:,.2f} บาท")
            self.v_total_profit.set(f"{total_profit:,.2f} บาท")
            self.v_profit_margin.set(f"{overall_margin:.1f}%")
            
            # Scroll กลับไปที่ด้านบน
            self.canvas.yview_moveto(0)
            
        except Exception as e:
            messagebox.showerror("Error", f"เกิดข้อผิดพลาดในการโหลดข้อมูล: {str(e)}")
    
    def export_to_csv(self):
        """Export รายงานรายละเอียดเป็น CSV"""
        if not self.current_data:
            messagebox.showwarning("Warning", "ไม่มีข้อมูลสำหรับ Export")
            return
        
        # เลือกที่บันทึกไฟล์
        start_date = self.start_date.get_date().strftime('%Y%m%d')
        end_date = self.end_date.get_date().strftime('%Y%m%d')
        default_filename = f"profit_report_{start_date}_to_{end_date}.csv"
        
        file_path = filedialog.asksaveasfilename(
            title="บันทึกรายงาน CSV",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile=default_filename
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'w', newline='', encoding='utf-8-sig') as file:
                writer = csv.writer(file)
                
                # หัวข้อรายงาน
                writer.writerow(['รายงานการวิเคราะห์กำไร (Profit Analysis Report)'])
                writer.writerow([f'ช่วงวันที่: {self.start_date.get_date().strftime("%d/%m/%Y")} - {self.end_date.get_date().strftime("%d/%m/%Y")}'])
                writer.writerow([f'วันที่ออกรายงาน: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}'])
                writer.writerow([])  # บรรทัดว่าง
                
                # ข้อมูลสรุป
                writer.writerow(['สรุปภาพรวม'])
                writer.writerow(['รายการ', 'จำนวนเงิน (บาท)'])
                writer.writerow(['ยอดขายรวม', f"{self.summary_data['total_sales']:,.2f}"])
                writer.writerow(['ต้นทุนรวม', f"{self.summary_data['total_cost']:,.2f}"])
                writer.writerow(['กำไรสุทธิ', f"{self.summary_data['total_profit']:,.2f}"])
                writer.writerow(['อัตรากำไร (%)', f"{self.summary_data['profit_margin']:.2f}"])
                writer.writerow([])  # บรรทัดว่าง
                
                # รายละเอียดการขาย
                writer.writerow(['รายละเอียดการขายแต่ละรายการ'])
                writer.writerow(['วันที่', 'Transaction ID', 'Barcode', 'ชื่อสินค้า', 'จำนวน', 
                               'ราคาขาย', 'ต้นทุน', 'รายได้', 'ต้นทุนรวม', 'กำไร', 'อัตรากำไร(%)'])
                
                for data in self.current_data:
                    writer.writerow([
                        data['date'],
                        data['transaction_id'],
                        data['barcode'],
                        data['product'],
                        data['quantity'],
                        f"{data['price']:.2f}",
                        f"{data['cost']:.2f}",
                        f"{data['revenue']:.2f}",
                        f"{data['total_cost']:.2f}",
                        f"{data['profit']:.2f}",
                        f"{data['profit_margin']:.2f}"
                    ])
            
            messagebox.showinfo("Success", f"Export รายงานสำเร็จ!\n\nบันทึกที่: {file_path}\nจำนวน: {len(self.current_data)} รายการ")
            
        except Exception as e:
            messagebox.showerror("Error", f"เกิดข้อผิดพลาดในการ Export: {str(e)}")
    
    def export_summary_csv(self):
        """Export เฉพาะข้อมูลสรุปเป็น CSV"""
        if not hasattr(self, 'summary_data'):
            messagebox.showwarning("Warning", "ไม่มีข้อมูลสำหรับ Export")
            return
        
        # เลือกที่บันทึกไฟล์
        start_date = self.start_date.get_date().strftime('%Y%m%d')
        end_date = self.end_date.get_date().strftime('%Y%m%d')
        default_filename = f"profit_summary_{start_date}_to_{end_date}.csv"
        
        file_path = filedialog.asksaveasfilename(
            title="บันทึกรายงานสรุป CSV",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile=default_filename
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'w', newline='', encoding='utf-8-sig') as file:
                writer = csv.writer(file)
                
                # หัวข้อรายงาน
                writer.writerow(['รายงานสรุปกำไร (Profit Summary Report)'])
                writer.writerow([f'ช่วงวันที่: {self.start_date.get_date().strftime("%d/%m/%Y")} - {self.end_date.get_date().strftime("%d/%m/%Y")}'])
                writer.writerow([f'วันที่ออกรายงาน: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}'])
                writer.writerow([])  # บรรทัดว่าง
                
                # ข้อมูลสรุป
                writer.writerow(['รายการ', 'จำนวนเงิน (บาท)', 'หมายเหตุ'])
                writer.writerow(['ยอดขายรวม', f"{self.summary_data['total_sales']:,.2f}", 'รายได้ทั้งหมดจากการขายสินค้า'])
                writer.writerow(['ต้นทุนรวม', f"{self.summary_data['total_cost']:,.2f}", 'ต้นทุนสินค้าที่ขายทั้งหมด'])
                writer.writerow(['กำไรสุทธิ', f"{self.summary_data['total_profit']:,.2f}", 'ยอดขาย - ต้นทุน'])
                writer.writerow(['อัตรากำไร', f"{self.summary_data['profit_margin']:.2f}%", '(กำไร/ยอดขาย) x 100'])
                writer.writerow([])  # บรรทัดว่าง
                
                # สถิติเพิ่มเติม
                if self.all_data:
                    writer.writerow(['สถิติเพิ่มเติม'])
                    writer.writerow(['จำนวนรายการขายทั้งหมด', len(self.all_data)])
                    writer.writerow(['รายได้เฉลี่ยต่อรายการ', f"{self.summary_data['total_sales'] / len(self.all_data):,.2f}"])
                    writer.writerow(['กำไรเฉลี่ยต่อรายการ', f"{self.summary_data['total_profit'] / len(self.all_data):,.2f}"])
            
            messagebox.showinfo("Success", f"Export รายงานสรุปสำเร็จ!\n\nบันทึกที่: {file_path}")
            
        except Exception as e:
            messagebox.showerror("Error", f"เกิดข้อผิดพลาดในการ Export: {str(e)}")