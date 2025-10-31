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
        
        # เก็บข้อมูลสำหรับ Export
        self.current_data = []
        
        # สร้าง GUI
        self.create_widgets()
        
    def create_widgets(self):
        FONT1 = (None, 20)
        FONT2 = (None, 14)
        
        # Frame สำหรับหัวข้อและปุ่ม Export
        header_frame = Frame(self)
        header_frame.pack(fill=X, pady=10, padx=20)
        
        # หัวข้อ
        Label(header_frame, text='Profit Analysis - วิเคราะห์กำไร', font=('Arial', 18, 'bold')).pack(side=LEFT)
        
        # ปุ่ม Export
        ttk.Button(header_frame, text='📊 Export CSV', command=self.export_to_csv).pack(side=RIGHT, padx=5)
        ttk.Button(header_frame, text='📈 Export สรุป', command=self.export_summary_csv).pack(side=RIGHT, padx=5)
        
        # Frame หลัก
        main_frame = Frame(self)
        main_frame.pack(fill=BOTH, expand=True, padx=20, pady=10)
        
        # ส่วนควบคุมการกรอง
        self.create_filter_section(main_frame)
        
        # ส่วนสรุปกำไร
        self.create_profit_summary(main_frame)
        
        # ส่วนตารางรายละเอียด
        self.create_profit_table(main_frame)
        
        # โหลดข้อมูลครั้งแรก
        self.refresh_data()
        
    def create_filter_section(self, parent):
        """สร้างส่วนควบคุมการกรองข้อมูล"""
        filter_frame = LabelFrame(parent, text="กรองข้อมูล", font=(None, 14))
        filter_frame.pack(fill=X, pady=10)
        
        # Frame สำหรับควบคุม
        control_frame = Frame(filter_frame)
        control_frame.pack(padx=20, pady=15)
        
        # วันที่เริ่มต้น
        Label(control_frame, text="วันที่เริ่มต้น:", font=(None, 12)).grid(row=0, column=0, sticky='w', padx=5)
        self.start_date = DateEntry(control_frame, width=12, background='darkblue',
                                   foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        self.start_date.grid(row=0, column=1, padx=5)
        
        # วันที่สิ้นสุด
        Label(control_frame, text="วันที่สิ้นสุด:", font=(None, 12)).grid(row=0, column=2, sticky='w', padx=5)
        self.end_date = DateEntry(control_frame, width=12, background='darkblue',
                                 foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        self.end_date.grid(row=0, column=3, padx=5)
        
        # ปุ่มควบคุม
        ttk.Button(control_frame, text="วันนี้", command=self.set_today).grid(row=1, column=0, padx=5, pady=10)
        ttk.Button(control_frame, text="สัปดาห์นี้", command=self.set_this_week).grid(row=1, column=1, padx=5, pady=10)
        ttk.Button(control_frame, text="เดือนนี้", command=self.set_this_month).grid(row=1, column=2, padx=5, pady=10)
        ttk.Button(control_frame, text="ค้นหา", command=self.refresh_data).grid(row=1, column=3, padx=5, pady=10)
        
        # ตั้งค่าเริ่มต้นเป็นวันนี้
        self.set_today()
        
    def create_profit_summary(self, parent):
        """สร้างส่วนสรุปกำไร"""
        summary_frame = LabelFrame(parent, text="สรุปกำไร", font=(None, 14))
        summary_frame.pack(fill=X, pady=10)
        
        # ตัวแปรสำหรับแสดงข้อมูลสรุป
        self.v_total_sales = StringVar()
        self.v_total_cost = StringVar()
        self.v_total_profit = StringVar()
        self.v_profit_margin = StringVar()
        
        # Grid layout สำหรับข้อมูลสรุป
        info_frame = Frame(summary_frame)
        info_frame.pack(padx=20, pady=15)
        
        # แถวที่ 1
        Label(info_frame, text="ยอดขายรวม:", font=(None, 14, 'bold')).grid(row=0, column=0, sticky='w', padx=10, pady=5)
        Label(info_frame, textvariable=self.v_total_sales, font=(None, 14, 'bold'), fg='blue').grid(row=0, column=1, sticky='w', padx=10, pady=5)
        
        Label(info_frame, text="ต้นทุนรวม:", font=(None, 14, 'bold')).grid(row=0, column=2, sticky='w', padx=10, pady=5)
        Label(info_frame, textvariable=self.v_total_cost, font=(None, 14, 'bold'), fg='red').grid(row=0, column=3, sticky='w', padx=10, pady=5)
        
        # แถวที่ 2
        Label(info_frame, text="กำไรสุทธิ:", font=(None, 16, 'bold')).grid(row=1, column=0, sticky='w', padx=10, pady=10)
        Label(info_frame, textvariable=self.v_total_profit, font=(None, 16, 'bold'), fg='green').grid(row=1, column=1, sticky='w', padx=10, pady=10)
        
        Label(info_frame, text="อัตรากำไร:", font=(None, 14, 'bold')).grid(row=1, column=2, sticky='w', padx=10, pady=10)
        Label(info_frame, textvariable=self.v_profit_margin, font=(None, 14, 'bold'), fg='purple').grid(row=1, column=3, sticky='w', padx=10, pady=10)
        
    def create_profit_table(self, parent):
        """สร้างตารางแสดงรายละเอียดกำไร"""
        table_frame = LabelFrame(parent, text="รายละเอียดการขาย", font=(None, 14))
        table_frame.pack(fill=BOTH, expand=True, pady=10)
        
        # สร้าง Treeview พร้อม scrollbar
        tree_frame = Frame(table_frame)
        tree_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        # Headers และ widths
        headers = ['วันที่', 'Transaction ID', 'สินค้า', 'จำนวน', 'ราคาขาย', 'ต้นทุน', 'รายได้', 'ต้นทุนรวม', 'กำไร', 'อัตรากำไร%']
        widths = [80, 100, 150, 60, 80, 80, 80, 80, 80, 80]
        
        self.profit_table = ttk.Treeview(tree_frame, columns=headers, show='headings', height=15)
        
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
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient=VERTICAL, command=self.profit_table.yview)
        self.profit_table.configure(yscrollcommand=scrollbar.set)
        
        # Pack table และ scrollbar
        self.profit_table.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)
        
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
            
            # เคลียร์ตารางและข้อมูล
            for item in self.profit_table.get_children():
                self.profit_table.delete(item)
            
            self.current_data = []  # เคลียร์ข้อมูลเก่า
                
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
                        
                        # เก็บข้อมูลสำหรับ Export
                        self.current_data.append({
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
                        })
                        
                        # เพิ่มลงตาราง
                        self.profit_table.insert('', 'end', values=[
                            trans_date_short, trans_id, title, quantity,
                            f"{price:,.2f}", f"{cost:,.2f}", f"{revenue:,.2f}",
                            f"{total_item_cost:,.2f}", f"{profit:,.2f}", f"{profit_margin:.1f}%"
                        ])
                        
                except (ValueError, KeyError, json.JSONDecodeError) as e:
                    print(f"Error processing transaction: {e}")
                    continue
            
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
                if self.current_data:
                    writer.writerow(['สถิติเพิ่มเติม'])
                    writer.writerow(['จำนวนรายการขายทั้งหมด', len(self.current_data)])
                    writer.writerow(['รายได้เฉลี่ยต่อรายการ', f"{self.summary_data['total_sales'] / len(self.current_data):,.2f}"])
                    writer.writerow(['กำไรเฉลี่ยต่อรายการ', f"{self.summary_data['total_profit'] / len(self.current_data):,.2f}"])
            
            messagebox.showinfo("Success", f"Export รายงานสรุปสำเร็จ!\n\nบันทึกที่: {file_path}")
            
        except Exception as e:
            messagebox.showerror("Error", f"เกิดข้อผิดพลาดในการ Export: {str(e)}")