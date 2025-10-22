# thermal_printer.py - 80mm Thermal Printer using GDI
import win32print
import win32ui
import win32con
from datetime import datetime
from tkinter import messagebox

class ThermalPrinter:
    def __init__(self):
        self.paper_width_mm = 80  # 80mm thermal paper
        self.margin_mm = 3        # 3mm margin
        self.char_width = 32      # characters per line for 80mm
        
    def get_default_printer(self):
        """ดึงชื่อเครื่องพิมพ์ default"""
        try:
            return win32print.GetDefaultPrinter()
        except:
            return None
    
    def print_receipt(self, transaction_data, cart_items):
        """พิมพ์ใบเสร็จด้วย thermal printer"""
        try:
            printer_name = self.get_default_printer()
            if not printer_name:
                raise Exception("ไม่พบเครื่องพิมพ์ในระบบ")
            
            # เปิดการเชื่อมต่อเครื่องพิมพ์
            hprinter = win32print.OpenPrinter(printer_name)
            printer_info = win32print.GetPrinter(hprinter, 2)
            
            # สร้าง device context
            pdc = win32ui.CreateDC()
            pdc.CreatePrinterDC(printer_name)
            
            # เริ่มการพิมพ์
            pdc.StartDoc("Receipt - Uncle Shop")
            pdc.StartPage()
            
            # พิมพ์เนื้อหาใบเสร็จ
            self._print_receipt_content(pdc, transaction_data, cart_items)
            
            # จบการพิมพ์
            pdc.EndPage()
            pdc.EndDoc()
            pdc.DeleteDC()
            win32print.ClosePrinter(hprinter)
            
            return True
            
        except Exception as e:
            raise Exception(f"ไม่สามารถพิมพ์ได้: {str(e)}")
    
    def _print_receipt_content(self, pdc, transaction_data, cart_items):
        """พิมพ์เนื้อหาใบเสร็จ"""
        y_pos = 50  # ตำแหน่ง Y เริ่มต้น
        line_height = 60  # ความสูงของแต่ละบรรทัด (กลับเป็น 60)
        
        # ฟอนต์หัวข้อร้าน (ใหญ่) - ลดจาก 80 เป็น 56
        title_font = win32ui.CreateFont({
            "name": "Tahoma",
            "height": 56,
            "weight": 700,
        })
        
        # ฟอนต์ปกติ - ลดจาก 50 เป็น 35
        normal_font = win32ui.CreateFont({
            "name": "Tahoma", 
            "height": 35,
            "weight": 400,
        })
        
        # ฟอนต์เล็ก - ลดจาก 40 เป็น 28
        small_font = win32ui.CreateFont({
            "name": "Tahoma",
            "height": 28,
            "weight": 400,
        })
        
        # หัวข้อร้าน - ย้ายออกซ้ายหน่อย
        pdc.SelectObject(title_font)
        shop_name = "ร้านลุง - Uncle Shop"
        y_pos = self._print_left_center_text(pdc, shop_name, y_pos)  # ใช้ฟังก์ชันใหม่
        y_pos += line_height
        
        # ข้อมูลร้าน
        pdc.SelectObject(small_font)
        address = "123 ถนนตัวอย่าง กรุงเทพฯ 10000"
        y_pos = self._print_left_center_text(pdc, address, y_pos)
        y_pos += line_height // 2
        
        phone = "โทร: 02-123-4567"
        y_pos = self._print_left_center_text(pdc, phone, y_pos)
        y_pos += line_height
        
        # เส้นแบ่ง
        pdc.SelectObject(normal_font)
        separator = "=" * 20
        y_pos = self._print_center_text(pdc, separator, y_pos)
        y_pos += line_height // 2
        
        # ข้อมูลใบเสร็จ
        receipt_info = [
            f"เลขที่: {transaction_data['transaction_id']}",
            f"วันที่: {transaction_data['datetime']}",
            f"พนักงาน: Admin"
        ]
        
        for info in receipt_info:
            y_pos = self._print_left_text(pdc, info, y_pos)
            y_pos += line_height // 2
        
        # เส้นแบ่ง
        y_pos = self._print_center_text(pdc, separator, y_pos)
        y_pos += line_height // 2
        
        # หัวข้อตาราง
        header = f"{'รายการ':<20}{'จน.':<4}{'รวม':<8}"
        y_pos = self._print_left_text(pdc, header, y_pos)
        y_pos += line_height // 2
        
        # เส้นแบ่ง
        mini_sep = "-" * self.char_width
        y_pos = self._print_left_text(pdc, mini_sep, y_pos)
        y_pos += line_height // 2
        
        # รายการสินค้า
        for item in cart_items:
            barcode, title, price, quantity = item
            price = float(price)
            quantity = int(quantity)
            total = price * quantity
            
            # ตัดชื่อสินค้าให้พอดี
            display_title = title[:18] if len(title) > 18 else title
            
            # บรรทัดที่ 1: ชื่อสินค้า
            y_pos = self._print_left_text(pdc, display_title, y_pos)
            y_pos += line_height // 2
            
            # บรรทัดที่ 2: จำนวน x ราคา = รวม
            item_line = f"{quantity:>4} x {price:>6.2f} = {total:>8.2f}"
            y_pos = self._print_right_text(pdc, item_line, y_pos)
            y_pos += line_height // 2
        
        # เส้นแบ่ง
        y_pos = self._print_left_text(pdc, mini_sep, y_pos)
        y_pos += line_height // 2
        
        # สรุปยอดเงิน
        summary_lines = [
            f"{'ยอดรวม:':<20}{transaction_data['subtotal']:>10.2f}",
            f"{'VAT 7%:':<20}{transaction_data['vat']:>10.2f}",
            f"{'รวมทั้งหมด:':<20}{transaction_data['grand_total']:>10.2f}",
            f"{'รับเงิน:':<20}{transaction_data['received_amount']:>10.2f}",
            f"{'เงินทอน:':<20}{transaction_data['change_amount']:>10.2f}"
        ]
        
        for line in summary_lines:
            y_pos = self._print_left_text(pdc, line, y_pos)
            y_pos += line_height // 2
        
        # เส้นแบ่ง
        y_pos += line_height // 2
        y_pos = self._print_center_text(pdc, separator, y_pos)
        y_pos += line_height
        
        # ข้อความท้าย - เริ่มจากซ้ายสุด
        pdc.SelectObject(small_font)
        footer_lines = [
            "ขอบคุณที่ใช้บริการ",
            "Thank you for your business",
            f"พิมพ์: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        ]
        
        for line in footer_lines:
            y_pos = self._print_left_text(pdc, line, y_pos)  # เปลี่ยนจาก center เป็น left
            y_pos += line_height // 2
        
        # ให้กระดาษออกมาพอสมควร
        y_pos += line_height * 3
        pdc.TextOut(0, y_pos, " ")  # เว้นที่ว่างท้าย
    
    def _print_left_text(self, pdc, text, y_pos):
        """พิมพ์ข้อความชิดซ้าย"""
        pdc.TextOut(50, y_pos, text)
        return y_pos
    
    def _print_left_center_text(self, pdc, text, y_pos):
        """พิมพ์ข้อความออกซ้ายจากกึ่งกลางหน่อย (สำหรับ header)"""
        # คำนวณตำแหน่ง x ให้อยู่ออกซ้ายจากกึ่งกลาง
        x_left_center = 60  # ออกซ้ายจาก center หน่อย (เดิม 200)
        pdc.TextOut(x_left_center, y_pos, text)
        return y_pos
    
    def _print_center_text(self, pdc, text, y_pos):
        """พิมพ์ข้อความกึ่งกลาง"""
        # คำนวณตำแหน่ง x ให้อยู่กึ่งกลาง (ประมาณ)
        x_center = 50  # ปรับตามความกว้างกระดาษ
        pdc.TextOut(x_center, y_pos, text)
        return y_pos
    
    def _print_right_text(self, pdc, text, y_pos):
        """พิมพ์ข้อความชิดขวา"""
        # คำนวณตำแหน่ง x ให้ชิดขวา (ประมาณ)
        x_right = 100  # ปรับตามความกว้างกระดาษ
        pdc.TextOut(x_right, y_pos, text)
        return y_pos
    
    def test_printer(self):
        """ทดสอบเครื่องพิมพ์"""
        try:
            printer_name = self.get_default_printer()
            if not printer_name:
                return False, "ไม่พบเครื่องพิมพ์"
            
            # ทดสอบพิมพ์ข้อความง่ายๆ
            hprinter = win32print.OpenPrinter(printer_name)
            pdc = win32ui.CreateDC()
            pdc.CreatePrinterDC(printer_name)
            pdc.StartDoc("Test Print")
            pdc.StartPage()
            
            # ลดขนาดฟอนต์ทดสอบจาก 60 เป็น 42
            font = win32ui.CreateFont({
                "name": "Tahoma",
                "height": 42,
                "weight": 700,
            })
            pdc.SelectObject(font)
            
            pdc.TextOut(100, 100, "ทดสอบเครื่องพิมพ์")
            pdc.TextOut(100, 200, "Test Thermal Printer")
            pdc.TextOut(100, 300, f"Printer: {printer_name}")
            
            pdc.EndPage()
            pdc.EndDoc()
            pdc.DeleteDC()
            win32print.ClosePrinter(hprinter)
            
            return True, f"ทดสอบเรียบร้อย: {printer_name}"
            
        except Exception as e:
            return False, f"ทดสอบล้มเหลว: {str(e)}"

def test_thermal_printer():
    """ทดสอบ thermal printer"""
    try:
        printer = ThermalPrinter()
        
        # ทดสอบการเชื่อมต่อ
        success, message = printer.test_printer()
        print(f"การทดสอบ: {message}")
        
        if success:
            print("✅ Thermal printer พร้อมใช้งาน")
        else:
            print("❌ Thermal printer ไม่พร้อมใช้งาน")
            
        return success
        
    except Exception as e:
        print(f"❌ ข้อผิดพลาด: {e}")
        return False

if __name__ == "__main__":
    # ทดสอบระบบ
    print("🖨️ ทดสอบ Thermal Printer System")
    print("=" * 40)
    
    try:
        import win32print, win32ui, win32con
        print("✅ พบ pywin32 modules")
    except ImportError:
        print("❌ ไม่พบ pywin32 - ติดตั้งด้วย: pip install pywin32")
        exit(1)
    
    test_thermal_printer()