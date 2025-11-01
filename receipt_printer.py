# receipt_printer.py - Modern Design Version with Shop Settings Integration
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, cm
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.graphics.shapes import Drawing, Rect, Line
from reportlab.graphics import renderPDF
from datetime import datetime
import os
import json

class ReceiptPrinter:
    def __init__(self):
        self.thai_font_available = False
        self.thai_font_name = 'THFont'
        self.shop_settings = self.load_shop_settings()  # โหลดข้อมูลร้าน
        self.setup_fonts()
        
    def load_shop_settings(self):
        """โหลดข้อมูลร้านค้าจากไฟล์"""
        settings_file = "shop_settings.json"
        default_settings = {
            'shop_name': 'ร้านค้าสำหรับ..POS..',
            'address': '29/25 หมู่2 ตำบลสะเดียง เพชรบูรณ์ 67000',
            'phone': '090-951-3031',
            'email': 'Phattananbaosin@shop.com'
        }
        
        try:
            if os.path.exists(settings_file):
                with open(settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    print(f"✅ โหลดข้อมูลร้านค้าจาก {settings_file}")
                    return settings
            else:
                print(f"⚠️ ไม่พบไฟล์ {settings_file} - ใช้ข้อมูลเริ่มต้น")
                return default_settings
        except Exception as e:
            print(f"❌ Error loading shop settings: {e}")
            return default_settings
    
    def setup_fonts(self):
        """ตั้งค่าฟอนต์ภาษาไทย"""
        try:
            font_paths = [
                "THSarabunNew.ttf",
                "C:/Windows/Fonts/THSarabunNew.ttf",
                "C:/Windows/Fonts/tahoma.ttf",
                "/usr/share/fonts/truetype/thai/THSarabunNew.ttf",
                "/System/Library/Fonts/Tahoma.ttf",
            ]
            
            for font_path in font_paths:
                if os.path.exists(font_path):
                    try:
                        pdfmetrics.registerFont(TTFont(self.thai_font_name, font_path))
                        self.thai_font_available = True
                        print(f"✅ Thai font loaded: {font_path}")
                        return
                    except Exception as e:
                        continue
                        
        except Exception as e:
            print(f"Font setup error: {e}")
        
        if not self.thai_font_available:
            print("⚠️ No Thai font found - using default")
    
    def create_header_decoration(self, width):
        """สร้างเส้นตกแต่งส่วนหัว"""
        d = Drawing(width, 3*mm)
        d.add(Rect(0, 0, width, 3*mm, fillColor=colors.HexColor('#2563eb'), strokeColor=None))
        return d
    
    def create_divider(self, width, color='#e5e7eb'):
        """สร้างเส้นแบ่ง"""
        d = Drawing(width, 1*mm)
        d.add(Line(0, 0.5*mm, width, 0.5*mm, strokeColor=colors.HexColor(color), strokeWidth=1))
        return d
            
    def create_receipt(self, transaction_data, cart_items, output_filename=None):
        """สร้างใบเสร็จ PDF สไตล์โมเดิร์น พร้อมข้อมูลร้านค้า"""
        try:
            # รีโหลดข้อมูลร้านค้าทุกครั้งที่พิมพ์ใบเสร็จ
            self.shop_settings = self.load_shop_settings()
            
            if not output_filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_filename = f"receipt_{transaction_data['transaction_id']}_{timestamp}.pdf"
            
            # สร้างเอกสาร PDF
            doc = SimpleDocTemplate(
                output_filename,
                pagesize=A4,
                rightMargin=20*mm,
                leftMargin=20*mm,
                topMargin=15*mm,
                bottomMargin=15*mm
            )
            
            # ลงทะเบียนฟอนต์อีกครั้ง
            if self.thai_font_available:
                font_paths = ["THSarabunNew.ttf", "C:/Windows/Fonts/THSarabunNew.ttf"]
                for font_path in font_paths:
                    if os.path.exists(font_path):
                        pdfmetrics.registerFont(TTFont(self.thai_font_name, font_path))
                        break
            
            elements = []
            styles = getSampleStyleSheet()
            
            # 🎨 สร้าง Modern Styles
            if self.thai_font_available:
                title_style = ParagraphStyle(
                    'ModernTitle',
                    parent=styles['Title'],
                    fontName=self.thai_font_name,
                    fontSize=28,
                    textColor=colors.HexColor('#0f172a'),
                    spaceAfter=10,
                    alignment=TA_CENTER,
                    leading=34
                )
                
                subtitle_style = ParagraphStyle(
                    'ModernSubtitle',
                    parent=styles['Normal'],
                    fontName=self.thai_font_name,
                    fontSize=14,
                    textColor=colors.HexColor('#475569'),
                    spaceAfter=8,
                    alignment=TA_CENTER,
                    leading=18
                )
                
                info_label_style = ParagraphStyle(
                    'ModernInfoLabel',
                    parent=styles['Normal'],
                    fontName=self.thai_font_name,
                    fontSize=14,
                    textColor=colors.HexColor('#334155'),
                    spaceAfter=5,
                    leading=18
                )
                
                info_value_style = ParagraphStyle(
                    'ModernInfoValue',
                    parent=styles['Normal'],
                    fontName=self.thai_font_name,
                    fontSize=14,
                    textColor=colors.HexColor('#0f172a'),
                    spaceAfter=5,
                    leading=18
                )
                
                table_header_style = ParagraphStyle(
                    'ModernTableHeader',
                    parent=styles['Normal'],
                    fontName=self.thai_font_name,
                    fontSize=14,
                    textColor=colors.white,
                    alignment=TA_LEFT,
                    leading=18
                )
                
                footer_style = ParagraphStyle(
                    'ModernFooter',
                    parent=styles['Normal'],
                    fontName=self.thai_font_name,
                    fontSize=13,
                    alignment=TA_CENTER,
                    textColor=colors.HexColor('#64748b'),
                    leading=17
                )
            else:
                title_style = ParagraphStyle('EngTitle', parent=styles['Title'], fontSize=28, spaceAfter=10, alignment=TA_CENTER, textColor=colors.HexColor('#0f172a'))
                subtitle_style = ParagraphStyle('EngSubtitle', parent=styles['Normal'], fontSize=14, spaceAfter=8, alignment=TA_CENTER, textColor=colors.HexColor('#475569'))
                info_label_style = ParagraphStyle('EngInfoLabel', parent=styles['Normal'], fontSize=14, spaceAfter=5, textColor=colors.HexColor('#334155'))
                info_value_style = ParagraphStyle('EngInfoValue', parent=styles['Normal'], fontSize=14, spaceAfter=5, textColor=colors.HexColor('#0f172a'))
                table_header_style = ParagraphStyle('EngTableHeader', parent=styles['Normal'], fontSize=14, textColor=colors.white, alignment=TA_LEFT)
                footer_style = ParagraphStyle('EngFooter', parent=styles['Normal'], fontSize=13, alignment=TA_CENTER, textColor=colors.HexColor('#64748b'))
            
            # 📌 Header Section - ใช้ข้อมูลจาก shop_settings
            elements.append(Spacer(1, 5))
            
            # ชื่อร้าน
            if self.thai_font_available:
                elements.append(Paragraph(
                    f"<font name='{self.thai_font_name}'><b>{self.shop_settings['shop_name']}</b></font>", 
                    title_style
                ))
                elements.append(Paragraph(
                    f"<font name='{self.thai_font_name}'>{self.shop_settings['address']}</font>", 
                    subtitle_style
                ))
                elements.append(Paragraph(
                    f"<font name='{self.thai_font_name}'>โทร: {self.shop_settings['phone']} | อีเมล: {self.shop_settings['email']}</font>", 
                    subtitle_style
                ))
            else:
                elements.append(Paragraph(
                    f"<b>{self.clean_thai_text(self.shop_settings['shop_name'])}</b>", 
                    title_style
                ))
                elements.append(Paragraph(
                    self.clean_thai_text(self.shop_settings['address']), 
                    subtitle_style
                ))
                elements.append(Paragraph(
                    f"Tel: {self.shop_settings['phone']} | Email: {self.shop_settings['email']}", 
                    subtitle_style
                ))
            
            elements.append(Spacer(1, 15))
            elements.append(self.create_divider(17*cm))
            elements.append(Spacer(1, 15))
            
            # 📋 ข้อมูลใบเสร็จ
            if self.thai_font_available:
                info_data = [
                    [
                        Paragraph(f"<font name='{self.thai_font_name}'>เลขที่ใบเสร็จ:</font>", info_label_style),
                        Paragraph(f"<font name='{self.thai_font_name}'><b>{transaction_data['transaction_id']}</b></font>", info_value_style),
                        Paragraph(f"<font name='{self.thai_font_name}'>วันที่:</font>", info_label_style),
                        Paragraph(f"<font name='{self.thai_font_name}'><b>{transaction_data['datetime']}</b></font>", info_value_style)
                    ],
                    [
                        Paragraph(f"<font name='{self.thai_font_name}'>พนักงานขาย:</font>", info_label_style),
                        Paragraph(f"<font name='{self.thai_font_name}'><b>Admin</b></font>", info_value_style),
                        '',
                        ''
                    ]
                ]
            else:
                info_data = [
                    [
                        Paragraph("Receipt No:", info_label_style),
                        Paragraph(f"<b>{transaction_data['transaction_id']}</b>", info_value_style),
                        Paragraph("Date:", info_label_style),
                        Paragraph(f"<b>{transaction_data['datetime']}</b>", info_value_style)
                    ],
                    [
                        Paragraph("Cashier:", info_label_style),
                        Paragraph("<b>Admin</b>", info_value_style),
                        '',
                        ''
                    ]
                ]
            
            info_table = Table(info_data, colWidths=[3.5*cm, 4*cm, 2.5*cm, 7*cm])
            info_table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ]))
            elements.append(info_table)
            
            elements.append(Spacer(1, 15))
            
            # 🛒 ตารางสินค้า
            if self.thai_font_available:
                header_right = ParagraphStyle('ThaiHR', parent=table_header_style, alignment=TA_RIGHT, fontName=self.thai_font_name)
                table_headers = [
                    Paragraph(f"<font name='{self.thai_font_name}'><b>รายการสินค้า</b></font>", table_header_style),
                    Paragraph(f"<font name='{self.thai_font_name}'><b>จำนวน</b></font>", header_right),
                    Paragraph(f"<font name='{self.thai_font_name}'><b>ราคา/หน่วย</b></font>", header_right),
                    Paragraph(f"<font name='{self.thai_font_name}'><b>รวม</b></font>", header_right)
                ]
            else:
                header_right = ParagraphStyle('EngHR', parent=table_header_style, alignment=TA_RIGHT)
                table_headers = [
                    Paragraph("<b>Items</b>", table_header_style),
                    Paragraph("<b>Qty</b>", header_right),
                    Paragraph("<b>Price</b>", header_right),
                    Paragraph("<b>Total</b>", header_right)
                ]
            
            table_data = [table_headers]
            
            # เพิ่มสินค้า
            for item in cart_items:
                barcode, title, price, quantity = item
                price = float(price)
                quantity = int(quantity)
                total = price * quantity
                
                if self.thai_font_available:
                    item_style = ParagraphStyle('ThaiItem', parent=info_value_style, fontSize=13, fontName=self.thai_font_name)
                    num_right = ParagraphStyle('ThaiNumR', parent=info_value_style, alignment=TA_RIGHT, fontSize=13, fontName=self.thai_font_name)
                    
                    row = [
                        Paragraph(f"<font name='{self.thai_font_name}'><b>{title}</b></font>", item_style),
                        Paragraph(f"<font name='{self.thai_font_name}'><b>{quantity}</b></font>", num_right),
                        Paragraph(f"<font name='{self.thai_font_name}'><b>{price:,.2f}</b></font>", num_right),
                        Paragraph(f"<font name='{self.thai_font_name}'><b>{total:,.2f}</b></font>", num_right)
                    ]
                else:
                    item_style = ParagraphStyle('EngItem', parent=info_value_style, fontSize=13)
                    num_right = ParagraphStyle('EngNumR', parent=info_value_style, alignment=TA_RIGHT, fontSize=13)
                    
                    clean_title = self.clean_thai_text(title)
                    row = [
                        Paragraph(f"<b>{clean_title}</b>", item_style),
                        Paragraph(f"<b>{quantity}</b>", num_right),
                        Paragraph(f"<b>{price:,.2f}</b>", num_right),
                        Paragraph(f"<b>{total:,.2f}</b>", num_right)
                    ]
                
                table_data.append(row)
            
            # สร้างตาราง
            table = Table(table_data, colWidths=[7.5*cm, 2.5*cm, 3.5*cm, 3.5*cm])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0d9488')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTSIZE', (0, 0), (-1, 0), 14),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('TOPPADDING', (0, 0), (-1, 0), 12),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f1f5f9')]),
                ('LINEBELOW', (0, 0), (-1, 0), 2.5, colors.HexColor('#0d9488')),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('LEFTPADDING', (0, 0), (-1, -1), 10),
                ('RIGHTPADDING', (0, 0), (-1, -1), 10),
                ('TOPPADDING', (0, 1), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 10),
            ]))
            
            elements.append(table)
            elements.append(Spacer(1, 20))
            
            # 💰 สรุปยอดเงิน
            if self.thai_font_available:
                summary_label = ParagraphStyle('ThaiSumLabel', parent=info_label_style, fontSize=15, alignment=TA_RIGHT, fontName=self.thai_font_name)
                summary_value = ParagraphStyle('ThaiSumValue', parent=info_value_style, fontSize=15, alignment=TA_RIGHT, fontName=self.thai_font_name)
                summary_total = ParagraphStyle('ThaiTotal', parent=info_value_style, fontSize=20, alignment=TA_RIGHT, textColor=colors.HexColor('#0d9488'), fontName=self.thai_font_name)
                
                summary_data = [
                    [Paragraph(f"<font name='{self.thai_font_name}'><b>ยอดรวม</b></font>", summary_label), 
                     Paragraph(f"<font name='{self.thai_font_name}'><b>{transaction_data['subtotal']:,.2f} ฿</b></font>", summary_value)],
                    [Paragraph(f"<font name='{self.thai_font_name}'><b>ภาษีมูลค่าเพิ่ม 7%</b></font>", summary_label), 
                     Paragraph(f"<font name='{self.thai_font_name}'><b>{transaction_data['vat']:,.2f} ฿</b></font>", summary_value)],
                    ['', ''],
                    [Paragraph(f"<font name='{self.thai_font_name}'><b>รวมทั้งหมด</b></font>", summary_total), 
                     Paragraph(f"<font name='{self.thai_font_name}'><b>{transaction_data['grand_total']:,.2f} ฿</b></font>", summary_total)],
                    ['', ''],
                    [Paragraph(f"<font name='{self.thai_font_name}'><b>เงินที่รับ</b></font>", summary_label), 
                     Paragraph(f"<font name='{self.thai_font_name}'><b>{transaction_data['received_amount']:,.2f} ฿</b></font>", summary_value)],
                    [Paragraph(f"<font name='{self.thai_font_name}'><b>เงินทอน</b></font>", summary_label), 
                     Paragraph(f"<font name='{self.thai_font_name}'><b>{transaction_data['change_amount']:,.2f} ฿</b></font>", summary_value)]
                ]
            else:
                summary_label = ParagraphStyle('EngSumLabel', parent=info_label_style, fontSize=15, alignment=TA_RIGHT)
                summary_value = ParagraphStyle('EngSumValue', parent=info_value_style, fontSize=15, alignment=TA_RIGHT)
                summary_total = ParagraphStyle('EngTotal', parent=info_value_style, fontSize=20, alignment=TA_RIGHT, textColor=colors.HexColor('#0d9488'))
                
                summary_data = [
                    [Paragraph("<b>Subtotal</b>", summary_label), Paragraph(f"<b>{transaction_data['subtotal']:,.2f} ฿</b>", summary_value)],
                    [Paragraph("<b>VAT 7%</b>", summary_label), Paragraph(f"<b>{transaction_data['vat']:,.2f} ฿</b>", summary_value)],
                    ['', ''],
                    [Paragraph("<b>Grand Total</b>", summary_total), Paragraph(f"<b>{transaction_data['grand_total']:,.2f} ฿</b>", summary_total)],
                    ['', ''],
                    [Paragraph("<b>Received</b>", summary_label), Paragraph(f"<b>{transaction_data['received_amount']:,.2f} ฿</b>", summary_value)],
                    [Paragraph("<b>Change</b>", summary_label), Paragraph(f"<b>{transaction_data['change_amount']:,.2f} ฿</b>", summary_value)]
                ]
            
            summary_table = Table(summary_data, colWidths=[11*cm, 6*cm])
            summary_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
                ('LINEABOVE', (0, 2), (-1, 2), 1.5, colors.HexColor('#e5e7eb')),
                ('LINEABOVE', (0, 4), (-1, 4), 1.5, colors.HexColor('#e5e7eb')),
                ('BACKGROUND', (0, 3), (-1, 3), colors.HexColor('#eff6ff')),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 3), (-1, 3), 10),
                ('BOTTOMPADDING', (0, 3), (-1, 3), 10),
            ]))
            
            elements.append(summary_table)
            elements.append(Spacer(1, 25))
            
            # 📝 Footer
            elements.append(self.create_divider(17*cm))
            elements.append(Spacer(1, 15))
            
            if self.thai_font_available:
                elements.append(Paragraph(
                    f"<font name='{self.thai_font_name}'><b>ขอบคุณที่ใช้บริการ | Thank you | พิมพ์เมื่อ: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</b></font>", 
                    footer_style
                ))
            else:
                elements.append(Paragraph("<b>Thank you for your business</b>", footer_style))
                elements.append(Spacer(1, 8))
                elements.append(Paragraph(f"Printed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", footer_style))
            
            # สร้าง PDF
            doc.build(elements)
            
            print(f"✅ ใบเสร็จถูกสร้างด้วยข้อมูล: {self.shop_settings['shop_name']}")
            
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
            'นม': 'Milk', 'ขนมปัง': 'Bread', 'น้ำ': 'Water', 'ข้าว': 'Rice',
            'ร้าน': 'Shop', 'ค้า': '', 'สำหรับ': 'for', 'ตำบล': '', 
            'หมู่': 'Moo', 'โทร': 'Tel', 'อีเมล': 'Email'
        }
        
        for thai, eng in thai_to_eng.items():
            text = text.replace(thai, eng)
        
        text = re.sub(r'[ก-๙]', '', text)
        text = ' '.join(text.split())
        
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
                os.startfile(filename)
            except AttributeError:
                try:
                    os.system(f"open '{filename}'")
                except:
                    os.system(f"xdg-open '{filename}'")
            
            return filename
            
        except Exception as e:
            raise Exception(f"Error printing receipt: {str(e)}")

# ตัวอย่างการใช้งาน
def test_receipt_printer():
    """ทดสอบการสร้างใบเสร็จแบบโมเดิร์น"""
    printer = ReceiptPrinter()
    
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
        print(f"✅ Modern receipt created: {filename}")
        print(f"🎨 Thai font available: {printer.thai_font_available}")
        print(f"🏪 Shop name: {printer.shop_settings['shop_name']}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_receipt_printer()