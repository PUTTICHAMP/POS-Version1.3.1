# receipt_printer.py - Fixed Thai Font Version
from reportlab.lib.pagesizes import A4, letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm, cm
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime
import os
import json
from tkinter import messagebox

class ReceiptPrinter:
    def __init__(self):
        self.thai_font_available = False
        self.thai_font_name = 'THFont'
        self.setup_fonts()
        
    def setup_fonts(self):
        """ตั้งค่าฟอนต์ภาษาไทยตามตัวอย่าง"""
        try:
            # รายการฟอนต์ที่จะลอง
            font_paths = [
                "THSarabunNew.ttf",  # Local file (แนะนำ)
                "C:/Windows/Fonts/THSarabunNew.ttf",  # Windows
                "C:/Windows/Fonts/tahoma.ttf",        # Windows Tahoma
                "/usr/share/fonts/truetype/thai/THSarabunNew.ttf",  # Linux
                "/System/Library/Fonts/Tahoma.ttf",   # macOS
            ]
            
            for font_path in font_paths:
                if os.path.exists(font_path):
                    try:
                        # ลงทะเบียนฟอนต์แบบเดียวกับตัวอย่าง
                        pdfmetrics.registerFont(TTFont(self.thai_font_name, font_path))
                        self.thai_font_available = True
                        print(f"✅ Thai font loaded successfully: {font_path}")
                        return
                    except Exception as e:
                        print(f"❌ Could not register font {font_path}: {e}")
                        continue
                        
        except Exception as e:
            print(f"Font setup error: {e}")
        
        if not self.thai_font_available:
            print("⚠️ No Thai font found - receipt will be in English")
            
    def create_receipt(self, transaction_data, cart_items, output_filename=None):
        """สร้างใบเสร็จ PDF ด้วยฟอนต์ไทยที่ถูกต้อง"""
        try:
            # กำหนดชื่อไฟล์
            if not output_filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_filename = f"receipt_{transaction_data['transaction_id']}_{timestamp}.pdf"
            
            # สร้างเอกสาร PDF
            doc = SimpleDocTemplate(
                output_filename,
                pagesize=A4,
                rightMargin=25*mm,
                leftMargin=25*mm,
                topMargin=25*mm,
                bottomMargin=25*mm
            )
            
            # ลงทะเบียนฟอนต์อีกครั้ง (สำคัญ!)
            if self.thai_font_available:
                font_paths = ["THSarabunNew.ttf", "C:/Windows/Fonts/THSarabunNew.ttf"]
                for font_path in font_paths:
                    if os.path.exists(font_path):
                        pdfmetrics.registerFont(TTFont(self.thai_font_name, font_path))
                        break
            
            # เตรียม elements
            elements = []
            styles = getSampleStyleSheet()
            
            # สร้าง custom styles สำหรับภาษาไทย
            if self.thai_font_available:
                title_style = ParagraphStyle(
                    'ThaiTitle',
                    parent=styles['Title'],
                    fontName=self.thai_font_name,
                    fontSize=20,
                    spaceAfter=20,
                    alignment=TA_CENTER,
                    textColor=colors.darkblue
                )
                
                header_style = ParagraphStyle(
                    'ThaiHeader',
                    parent=styles['Normal'],
                    fontName=self.thai_font_name,
                    fontSize=12,
                    spaceAfter=10,
                    alignment=TA_CENTER
                )
                
                normal_style = ParagraphStyle(
                    'ThaiNormal',
                    parent=styles['Normal'],
                    fontName=self.thai_font_name,
                    fontSize=11,
                    spaceAfter=6
                )
                
                footer_style = ParagraphStyle(
                    'ThaiFooter',
                    parent=styles['Normal'],
                    fontName=self.thai_font_name,
                    fontSize=10,
                    alignment=TA_CENTER,
                    textColor=colors.grey
                )
            else:
                # ใช้ฟอนต์ default
                title_style = ParagraphStyle('EngTitle', parent=styles['Title'], fontSize=18, spaceAfter=20, alignment=TA_CENTER, textColor=colors.darkblue)
                header_style = ParagraphStyle('EngHeader', parent=styles['Normal'], fontSize=12, spaceAfter=10, alignment=TA_CENTER)
                normal_style = ParagraphStyle('EngNormal', parent=styles['Normal'], fontSize=11, spaceAfter=6)
                footer_style = ParagraphStyle('EngFooter', parent=styles['Normal'], fontSize=10, alignment=TA_CENTER, textColor=colors.grey)
            
            # หัวข้อร้าน
            if self.thai_font_available:
                elements.append(Paragraph(f"<font name='{self.thai_font_name}'><b>ร้าน..... - POS Shop</b></font>", title_style))
                elements.append(Paragraph(f"<font name='{self.thai_font_name}'>29/25 หมู่2 ตำบลสะเดียง เพชรบูรณ? 67000</font>", header_style))
                elements.append(Paragraph(f"<font name='{self.thai_font_name}'>โทร: 090-951-3031 | อีเมล: Phattananbaosin@shop.com</font>", header_style))
            else:
                elements.append(Paragraph("<b>Uncle Shop</b>", title_style))
                elements.append(Paragraph("29/25 M2 , Sadaing District, Phatcahbun 67000", header_style))
                elements.append(Paragraph("Tel: 090-951-3031 | Email: Phattananbaosin@gmail.com", header_style))
            
            elements.append(Spacer(1, 20))
            
            # ข้อมูลใบเสร็จ
            if self.thai_font_available:
                elements.append(Paragraph(f"<font name='{self.thai_font_name}'><b>เลขที่ใบเสร็จ:</b> {transaction_data['transaction_id']}</font>", normal_style))
                elements.append(Paragraph(f"<font name='{self.thai_font_name}'><b>วันที่:</b> {transaction_data['datetime']}</font>", normal_style))
                elements.append(Paragraph(f"<font name='{self.thai_font_name}'><b>พนักงานขาย:</b> Admin</font>", normal_style))
            else:
                elements.append(Paragraph(f"<b>Receipt No:</b> {transaction_data['transaction_id']}", normal_style))
                elements.append(Paragraph(f"<b>Date:</b> {transaction_data['datetime']}", normal_style))
                elements.append(Paragraph(f"<b>Cashier:</b> Admin", normal_style))
            
            elements.append(Spacer(1, 20))
            
            # ตารางรายการสินค้า
            if self.thai_font_available:
                # สร้าง style สำหรับ header ที่ชิดขวา
                header_right_style = ParagraphStyle(
                    'ThaiHeaderRight',
                    parent=normal_style,
                    fontName=self.thai_font_name,
                    fontSize=11,
                    alignment=TA_RIGHT
                )
                
                table_headers = [
                    Paragraph(f"<font name='{self.thai_font_name}'><b>รายการ</b></font>", normal_style),
                    Paragraph(f"<font name='{self.thai_font_name}'><b>จำนวน</b></font>", header_right_style),
                    Paragraph(f"<font name='{self.thai_font_name}'><b>ราคา/หน่วย</b></font>", header_right_style),
                    Paragraph(f"<font name='{self.thai_font_name}'><b>รวม</b></font>", header_right_style)
                ]
            else:
                # สร้าง style สำหรับ header ที่ชิดขวา
                header_right_style = ParagraphStyle(
                    'EngHeaderRight',
                    parent=normal_style,
                    fontSize=11,
                    alignment=TA_RIGHT
                )
                
                table_headers = [
                    Paragraph("<b>Items</b>", normal_style),
                    Paragraph("<b>Qty</b>", header_right_style),
                    Paragraph("<b>Price/Unit</b>", header_right_style),
                    Paragraph("<b>Total</b>", header_right_style)
                ]
            
            table_data = [table_headers]
            
            # เพิ่มข้อมูลสินค้า
            for item in cart_items:
                barcode, title, price, quantity = item
                price = float(price)
                quantity = int(quantity)
                total = price * quantity
                
                if self.thai_font_available:
                    # สร้าง style สำหรับตัวเลขชิดขวา
                    number_right_style = ParagraphStyle(
                        'ThaiNumberRight',
                        parent=normal_style,
                        fontName=self.thai_font_name,
                        fontSize=11,
                        alignment=TA_RIGHT
                    )
                    
                    row = [
                        Paragraph(f"<font name='{self.thai_font_name}'>{title}</font>", normal_style),
                        Paragraph(f"<font name='{self.thai_font_name}'>{quantity}</font>", number_right_style),
                        Paragraph(f"<font name='{self.thai_font_name}'>{price:,.2f}</font>", number_right_style),
                        Paragraph(f"<font name='{self.thai_font_name}'>{total:,.2f}</font>", number_right_style)
                    ]
                else:
                    # สร้าง style สำหรับตัวเลขชิดขวา
                    number_right_style = ParagraphStyle(
                        'EngNumberRight',
                        parent=normal_style,
                        fontSize=11,
                        alignment=TA_RIGHT
                    )
                    
                    # แปลงข้อความไทยเป็นอังกฤษ
                    clean_title = self.clean_thai_text(title)
                    row = [
                        Paragraph(clean_title, normal_style),
                        Paragraph(str(quantity), number_right_style),
                        Paragraph(f"{price:,.2f}", number_right_style),
                        Paragraph(f"{total:,.2f}", number_right_style)
                    ]
                
                table_data.append(row)
            
            # สร้างตาราง
            table = Table(table_data, colWidths=[8*cm, 2*cm, 3*cm, 3*cm])
            table.setStyle(TableStyle([
                # Header
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                
                # Data rows
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            
            elements.append(table)
            elements.append(Spacer(1, 20))
            
            # สรุปยอดเงิน
            if self.thai_font_available:
                summary_data = [
                    [Paragraph(f"<font name='{self.thai_font_name}'>ยอดรวม (Subtotal)</font>", normal_style), 
                     Paragraph(f"<font name='{self.thai_font_name}'>{transaction_data['subtotal']:,.2f} บาท</font>", normal_style)],
                    [Paragraph(f"<font name='{self.thai_font_name}'>ภาษีมูลค่าเพิ่ม 7%</font>", normal_style), 
                     Paragraph(f"<font name='{self.thai_font_name}'>{transaction_data['vat']:,.2f} บาท</font>", normal_style)],
                    ['', ''],  # เส้นแบ่ง
                    [Paragraph(f"<font name='{self.thai_font_name}'><b>รวมทั้งหมด (Grand Total)</b></font>", normal_style), 
                     Paragraph(f"<font name='{self.thai_font_name}'><b>{transaction_data['grand_total']:,.2f} บาท</b></font>", normal_style)],
                    [Paragraph(f"<font name='{self.thai_font_name}'>เงินที่รับ</font>", normal_style), 
                     Paragraph(f"<font name='{self.thai_font_name}'>{transaction_data['received_amount']:,.2f} บาท</font>", normal_style)],
                    [Paragraph(f"<font name='{self.thai_font_name}'>เงินทอน</font>", normal_style), 
                     Paragraph(f"<font name='{self.thai_font_name}'>{transaction_data['change_amount']:,.2f} บาท</font>", normal_style)]
                ]
            else:
                summary_data = [
                    [Paragraph("Subtotal", normal_style), Paragraph(f"{transaction_data['subtotal']:,.2f} THB", normal_style)],
                    [Paragraph("VAT 7%", normal_style), Paragraph(f"{transaction_data['vat']:,.2f} THB", normal_style)],
                    ['', ''],
                    [Paragraph("<b>Grand Total</b>", normal_style), Paragraph(f"<b>{transaction_data['grand_total']:,.2f} THB</b>", normal_style)],
                    [Paragraph("Received", normal_style), Paragraph(f"{transaction_data['received_amount']:,.2f} THB", normal_style)],
                    [Paragraph("Change", normal_style), Paragraph(f"{transaction_data['change_amount']:,.2f} THB", normal_style)]
                ]
            
            summary_table = Table(summary_data, colWidths=[10*cm, 6*cm])
            summary_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (0, -1), 'RIGHT'),   # คอลัมน์ซ้าย (ป้ายกำกับ) ชิดขวา
                ('ALIGN', (1, 0), (1, -1), 'RIGHT'),   # คอลัมน์ขวา (ตัวเลข) ชิดขวา
                ('FONTSIZE', (0, 0), (-1, -1), 11),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('BACKGROUND', (0, 3), (-1, 3), colors.lightgrey),  # Grand total row
                ('LINEBELOW', (0, 2), (-1, 2), 1, colors.black),   # เส้นแบ่ง
            ]))
            
            elements.append(summary_table)
            elements.append(Spacer(1, 30))
            
            # ข้อความท้ายใบเสร็จ
            if self.thai_font_available:
                elements.append(Paragraph(f"<font name='{self.thai_font_name}'>ขอบคุณที่ใช้บริการ</font>", footer_style))
                elements.append(Paragraph(f"<font name='{self.thai_font_name}'>Thank you for your business</font>", footer_style))
                elements.append(Spacer(1, 10))
                elements.append(Paragraph(f"<font name='{self.thai_font_name}'>พิมพ์เมื่อ: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</font>", footer_style))
            else:
                elements.append(Paragraph("Thank you for your business", footer_style))
                elements.append(Paragraph("Have a nice day!", footer_style))
                elements.append(Spacer(1, 10))
                elements.append(Paragraph(f"Printed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", footer_style))
            
            # สร้าง PDF
            doc.build(elements)
            
            return output_filename
            
        except Exception as e:
            raise Exception(f"Error creating receipt: {str(e)}")
    
    def clean_thai_text(self, text):
        """แปลงข้อความไทยเป็นอังกฤษ"""
        import re
        
        thai_to_eng = {
            'แอปเปิ้ล': 'Apple', 'กล้วย': 'Banana', 'ส้ม': 'Orange',
            'มะม่วง': 'Mango', 'สับปะรด': 'Pineapple', 'มะละกอ': 'Papaya',
            'ชิ้น': 'pcs', 'ลูก': 'pieces', 'กิโลกรัม': 'kg', 'กรัม': 'g',
            'แผง': 'pack', 'ขวด': 'bottle', 'ถุง': 'bag', 'กล่อง': 'box',
            'นม': 'Milk', 'ขนมปัง': 'Bread', 'น้ำ': 'Water', 'ข้าว': 'Rice'
        }
        
        # แทนที่คำที่รู้จัก
        for thai, eng in thai_to_eng.items():
            text = text.replace(thai, eng)
        
        # ลบตัวอักษรไทยที่เหลือ
        text = re.sub(r'[ก-๙]', '', text)
        text = ' '.join(text.split())  # ทำความสะอาดช่องว่าง
        
        return text.strip() if text.strip() else "Product"
    
    def print_receipt_from_transaction(self, transaction_id, subtotal, vat, grand_total, 
                                     received_amount, change_amount, cart_items):
        """สร้างใบเสร็จจากข้อมูลการขาย"""
        try:
            transaction_data = {
                'transaction_id': transaction_id,
                'datetime': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'subtotal': subtotal,
                'vat': vat,
                'grand_total': grand_total,
                'received_amount': received_amount,
                'change_amount': change_amount
            }
            
            filename = self.create_receipt(transaction_data, cart_items)
            
            # เปิดไฟล์ PDF
            try:
                os.startfile(filename)  # Windows
            except AttributeError:
                try:
                    os.system(f"open '{filename}'")  # macOS
                except:
                    os.system(f"xdg-open '{filename}'")  # Linux
            
            return filename
            
        except Exception as e:
            raise Exception(f"Error printing receipt: {str(e)}")

# ตัวอย่างการใช้งาน
def test_receipt_printer():
    """ทดสอบการสร้างใบเสร็จ"""
    printer = ReceiptPrinter()
    
    # ข้อมูลทดสอบ
    test_cart = [
        ['001', 'Apple - แอปเปิ้ล', 25.00, 3],
        ['002', 'Banana - กล้วย', 15.50, 5],
        ['003', 'Orange - ส้ม', 30.00, 2],
        ['004', 'Milk - นม', 45.00, 1],
        ['005', 'Bread - ขนมปัง', 35.00, 2]
    ]
    
    subtotal = 292.50
    vat = 20.48
    grand_total = 312.98
    received = 350.00
    change = 37.02
    
    try:
        filename = printer.print_receipt_from_transaction(
            transaction_id="T000001",
            subtotal=subtotal,
            vat=vat,
            grand_total=grand_total,
            received_amount=received,
            change_amount=change,
            cart_items=test_cart
        )
        print(f"✅ Receipt created successfully: {filename}")
        print(f"🔤 Thai font available: {printer.thai_font_available}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n🔧 Solutions:")
        print("1. Download THSarabunNew.ttf and place in program folder")
        print("2. Install: pip install reportlab")
        print("3. Check font paths in code")

if __name__ == "__main__":
    test_receipt_printer()