# receipt_printer.py - Modern Design Version with Invoice/Credit System
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
from datetime import datetime, timedelta
import os
import json

class ReceiptPrinter:
    def __init__(self):
        self.thai_font_available = False
        self.thai_font_name = 'THFont'
        self.shop_settings = self.load_shop_settings()
        self.invoices_file = "invoices_data.json"
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
    
    def load_invoices_data(self):
        """โหลดข้อมูลใบวางบิลทั้งหมด"""
        try:
            if os.path.exists(self.invoices_file):
                with open(self.invoices_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            print(f"❌ Error loading invoices: {e}")
            return {}
    
    def save_invoice_data(self, invoice_id, invoice_data):
        """บันทึกข้อมูลใบวางบิล"""
        try:
            invoices = self.load_invoices_data()
            invoices[invoice_id] = invoice_data
            
            with open(self.invoices_file, 'w', encoding='utf-8') as f:
                json.dump(invoices, f, ensure_ascii=False, indent=2)
            
            print(f"✅ บันทึกใบวางบิล {invoice_id} สำเร็จ")
            return True
        except Exception as e:
            print(f"❌ Error saving invoice: {e}")
            return False
    
    def update_invoice_payment(self, invoice_id, payment_amount, payment_date=None):
        """อัพเดทการชำระเงินของใบวางบิล"""
        try:
            invoices = self.load_invoices_data()
            
            if invoice_id not in invoices:
                print(f"❌ ไม่พบใบวางบิล {invoice_id}")
                return False
            
            invoice = invoices[invoice_id]
            
            # อัพเดทยอดชำระ
            invoice['paid_amount'] = invoice.get('paid_amount', 0) + payment_amount
            invoice['remaining_amount'] = invoice['grand_total'] - invoice['paid_amount']
            
            # อัพเดทสถานะ
            if invoice['remaining_amount'] <= 0:
                invoice['status'] = 'paid'
                invoice['paid_date'] = payment_date or datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            elif invoice['paid_amount'] > 0:
                invoice['status'] = 'partial'
            
            # บันทึกประวัติการชำระเงิน
            if 'payment_history' not in invoice:
                invoice['payment_history'] = []
            
            invoice['payment_history'].append({
                'date': payment_date or datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'amount': payment_amount,
                'remaining': invoice['remaining_amount']
            })
            
            invoices[invoice_id] = invoice
            
            with open(self.invoices_file, 'w', encoding='utf-8') as f:
                json.dump(invoices, f, ensure_ascii=False, indent=2)
            
            print(f"✅ อัพเดทการชำระเงิน {invoice_id} สำเร็จ")
            return True
            
        except Exception as e:
            print(f"❌ Error updating payment: {e}")
            return False
    
    def get_invoice_info(self, invoice_id):
        """ดึงข้อมูลใบวางบิล"""
        invoices = self.load_invoices_data()
        return invoices.get(invoice_id, None)
    
    def get_unpaid_invoices(self):
        """ดึงรายการใบวางบิลที่ยังไม่ได้ชำระหรือชำระไม่ครบ"""
        invoices = self.load_invoices_data()
        unpaid = {}
        
        for inv_id, inv_data in invoices.items():
            if inv_data.get('status') in ['unpaid', 'partial']:
                unpaid[inv_id] = inv_data
        
        return unpaid
    
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
            
    def create_receipt(self, transaction_data, cart_items, output_filename=None, is_invoice=False, customer_info=None):
        """สร้างใบเสร็จ/ใบวางบิล PDF สไตล์โมเดิร์น"""
        try:
            self.shop_settings = self.load_shop_settings()
            
            if not output_filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                prefix = "invoice" if is_invoice else "receipt"
                output_filename = f"{prefix}_{transaction_data['transaction_id']}_{timestamp}.pdf"
            
            doc = SimpleDocTemplate(
                output_filename,
                pagesize=A4,
                rightMargin=20*mm,
                leftMargin=20*mm,
                topMargin=15*mm,
                bottomMargin=15*mm
            )
            
            if self.thai_font_available:
                font_paths = ["THSarabunNew.ttf", "C:/Windows/Fonts/THSarabunNew.ttf"]
                for font_path in font_paths:
                    if os.path.exists(font_path):
                        pdfmetrics.registerFont(TTFont(self.thai_font_name, font_path))
                        break
            
            elements = []
            styles = getSampleStyleSheet()
            
            # สร้าง Styles
            if self.thai_font_available:
                title_style = ParagraphStyle(
                    'ModernTitle', parent=styles['Title'], fontName=self.thai_font_name,
                    fontSize=28, textColor=colors.HexColor('#0f172a'), spaceAfter=10,
                    alignment=TA_CENTER, leading=34
                )
                subtitle_style = ParagraphStyle(
                    'ModernSubtitle', parent=styles['Normal'], fontName=self.thai_font_name,
                    fontSize=14, textColor=colors.HexColor('#475569'), spaceAfter=8,
                    alignment=TA_CENTER, leading=18
                )
                info_label_style = ParagraphStyle(
                    'ModernInfoLabel', parent=styles['Normal'], fontName=self.thai_font_name,
                    fontSize=14, textColor=colors.HexColor('#334155'), spaceAfter=5, leading=18
                )
                info_value_style = ParagraphStyle(
                    'ModernInfoValue', parent=styles['Normal'], fontName=self.thai_font_name,
                    fontSize=14, textColor=colors.HexColor('#0f172a'), spaceAfter=5, leading=18
                )
                table_header_style = ParagraphStyle(
                    'ModernTableHeader', parent=styles['Normal'], fontName=self.thai_font_name,
                    fontSize=14, textColor=colors.white, alignment=TA_LEFT, leading=18
                )
                footer_style = ParagraphStyle(
                    'ModernFooter', parent=styles['Normal'], fontName=self.thai_font_name,
                    fontSize=13, alignment=TA_CENTER, textColor=colors.HexColor('#64748b'), leading=17
                )
            else:
                title_style = ParagraphStyle('EngTitle', parent=styles['Title'], fontSize=28, spaceAfter=10, alignment=TA_CENTER, textColor=colors.HexColor('#0f172a'))
                subtitle_style = ParagraphStyle('EngSubtitle', parent=styles['Normal'], fontSize=14, spaceAfter=8, alignment=TA_CENTER, textColor=colors.HexColor('#475569'))
                info_label_style = ParagraphStyle('EngInfoLabel', parent=styles['Normal'], fontSize=14, spaceAfter=5, textColor=colors.HexColor('#334155'))
                info_value_style = ParagraphStyle('EngInfoValue', parent=styles['Normal'], fontSize=14, spaceAfter=5, textColor=colors.HexColor('#0f172a'))
                table_header_style = ParagraphStyle('EngTableHeader', parent=styles['Normal'], fontSize=14, textColor=colors.white, alignment=TA_LEFT)
                footer_style = ParagraphStyle('EngFooter', parent=styles['Normal'], fontSize=13, alignment=TA_CENTER, textColor=colors.HexColor('#64748b'))
            
            # Header Section
            elements.append(Spacer(1, 5))
            
            # แสดงประเภทเอกสาร
            if is_invoice:
                doc_type_style = ParagraphStyle(
                    'InvoiceType', parent=title_style, fontSize=22,
                    textColor=colors.HexColor('#dc2626'), alignment=TA_CENTER
                )
                
                if self.thai_font_available:
                    elements.append(Paragraph(
                        f"<font name='{self.thai_font_name}'><b>ใบวางบิล / INVOICE</b></font>", 
                        doc_type_style
                    ))
                else:
                    elements.append(Paragraph("<b>🧾 INVOICE</b>", doc_type_style))
                
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
            
            # ข้อมูลลูกค้า (สำหรับใบวางบิล)
            if is_invoice and customer_info:
                if self.thai_font_available:
                    customer_style = ParagraphStyle('ThaiCustomer', parent=info_label_style, fontSize=13, fontName=self.thai_font_name)
                    
                    elements.append(Paragraph(f"<font name='{self.thai_font_name}'><b>ข้อมูลลูกค้า:</b></font>", info_label_style))
                    elements.append(Spacer(1, 8))
                    
                    customer_data = [
                        [Paragraph(f"<font name='{self.thai_font_name}'>ชื่อ:</font>", customer_style),
                         Paragraph(f"<font name='{self.thai_font_name}'><b>{customer_info.get('name', 'N/A')}</b></font>", info_value_style)],
                        [Paragraph(f"<font name='{self.thai_font_name}'>โทรศัพท์:</font>", customer_style),
                         Paragraph(f"<font name='{self.thai_font_name}'><b>{customer_info.get('phone', 'N/A')}</b></font>", info_value_style)],
                        [Paragraph(f"<font name='{self.thai_font_name}'>ที่อยู่:</font>", customer_style),
                         Paragraph(f"<font name='{self.thai_font_name}'><b>{customer_info.get('address', 'N/A')}</b></font>", info_value_style)],
                    ]
                else:
                    customer_style = ParagraphStyle('EngCustomer', parent=info_label_style, fontSize=13)
                    
                    elements.append(Paragraph("<b>Customer Information:</b>", info_label_style))
                    elements.append(Spacer(1, 8))
                    
                    customer_data = [
                        [Paragraph("Name:", customer_style),
                         Paragraph(f"<b>{customer_info.get('name', 'N/A')}</b>", info_value_style)],
                        [Paragraph("Phone:", customer_style),
                         Paragraph(f"<b>{customer_info.get('phone', 'N/A')}</b>", info_value_style)],
                        [Paragraph("Address:", customer_style),
                         Paragraph(f"<b>{customer_info.get('address', 'N/A')}</b>", info_value_style)],
                    ]
                
                customer_table = Table(customer_data, colWidths=[3*cm, 14*cm])
                customer_table.setStyle(TableStyle([
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 0),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                    ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
                    ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#e2e8f0')),
                    ('TOPPADDING', (0, 0), (-1, -1), 8),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ]))
                elements.append(customer_table)
                elements.append(Spacer(1, 15))
            
            # ข้อมูลใบเสร็จ/ใบวางบิล
            if self.thai_font_available:
                doc_label = "เลขที่ใบวางบิล:" if is_invoice else "เลขที่ใบเสร็จ:"
                
                info_data = [
                    [
                        Paragraph(f"<font name='{self.thai_font_name}'>{doc_label}</font>", info_label_style),
                        Paragraph(f"<font name='{self.thai_font_name}'><b>{transaction_data['transaction_id']}</b></font>", info_value_style),
                        Paragraph(f"<font name='{self.thai_font_name}'>วันที่:</font>", info_label_style),
                        Paragraph(f"<font name='{self.thai_font_name}'><b>{transaction_data['datetime']}</b></font>", info_value_style)
                    ],
                    [
                        Paragraph(f"<font name='{self.thai_font_name}'>พนักงานขาย:</font>", info_label_style),
                        Paragraph(f"<font name='{self.thai_font_name}'><b>Admin</b></font>", info_value_style),
                        Paragraph(f"<font name='{self.thai_font_name}'>กำหนดชำระ:</font>" if is_invoice else '', info_label_style),
                        Paragraph(f"<font name='{self.thai_font_name}'><b>{transaction_data.get('due_date', 'N/A')}</b></font>" if is_invoice else '', info_value_style)
                    ]
                ]
            else:
                doc_label = "Invoice No:" if is_invoice else "Receipt No:"
                
                info_data = [
                    [
                        Paragraph(doc_label, info_label_style),
                        Paragraph(f"<b>{transaction_data['transaction_id']}</b>", info_value_style),
                        Paragraph("Date:", info_label_style),
                        Paragraph(f"<b>{transaction_data['datetime']}</b>", info_value_style)
                    ],
                    [
                        Paragraph("Cashier:", info_label_style),
                        Paragraph("<b>Admin</b>", info_value_style),
                        Paragraph("Due Date:" if is_invoice else '', info_label_style),
                        Paragraph(f"<b>{transaction_data.get('due_date', 'N/A')}</b>" if is_invoice else '', info_value_style)
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
            
            # ตารางสินค้า
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
            
            # สรุปยอดเงิน
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
                ]
                
                if not is_invoice:
                    summary_data.extend([
                        ['', ''],
                        [Paragraph(f"<font name='{self.thai_font_name}'><b>เงินที่รับ</b></font>", summary_label), 
                         Paragraph(f"<font name='{self.thai_font_name}'><b>{transaction_data['received_amount']:,.2f} ฿</b></font>", summary_value)],
                        [Paragraph(f"<font name='{self.thai_font_name}'><b>เงินทอน</b></font>", summary_label), 
                         Paragraph(f"<font name='{self.thai_font_name}'><b>{transaction_data['change_amount']:,.2f} ฿</b></font>", summary_value)]
                    ])
                else:
                    paid_amount = transaction_data.get('paid_amount', 0)
                    remaining = transaction_data['grand_total'] - paid_amount
                    
                    summary_data.extend([
                        ['', ''],
                        [Paragraph(f"<font name='{self.thai_font_name}'><b>ชำระแล้ว</b></font>", summary_label), 
                         Paragraph(f"<font name='{self.thai_font_name}'><b>{paid_amount:,.2f} ฿</b></font>", summary_value)],
                        [Paragraph(f"<font name='{self.thai_font_name}'><b>คงเหลือ</b></font>", summary_label), 
                         Paragraph(f"<font name='{self.thai_font_name}'><b>{remaining:,.2f} ฿</b></font>", ParagraphStyle('ThaiRemain', parent=summary_value, textColor=colors.HexColor('#dc2626')))]
                    ])
                    
            else:
                summary_label = ParagraphStyle('EngSumLabel', parent=info_label_style, fontSize=15, alignment=TA_RIGHT)
                summary_value = ParagraphStyle('EngSumValue', parent=info_value_style, fontSize=15, alignment=TA_RIGHT)
                summary_total = ParagraphStyle('EngTotal', parent=info_value_style, fontSize=20, alignment=TA_RIGHT, textColor=colors.HexColor('#0d9488'))
                
                summary_data = [
                    [Paragraph("<b>Subtotal</b>", summary_label), Paragraph(f"<b>{transaction_data['subtotal']:,.2f} ฿</b>", summary_value)],
                    [Paragraph("<b>VAT 7%</b>", summary_label), Paragraph(f"<b>{transaction_data['vat']:,.2f} ฿</b>", summary_value)],
                    ['', ''],
                    [Paragraph("<b>Grand Total</b>", summary_total), Paragraph(f"<b>{transaction_data['grand_total']:,.2f} ฿</b>", summary_total)],
                ]
                
                if not is_invoice:
                    summary_data.extend([
                        ['', ''],
                        [Paragraph("<b>Received</b>", summary_label), Paragraph(f"<b>{transaction_data['received_amount']:,.2f} ฿</b>", summary_value)],
                        [Paragraph("<b>Change</b>", summary_label), Paragraph(f"<b>{transaction_data['change_amount']:,.2f} ฿</b>", summary_value)]
                    ])
                else:
                    paid_amount = transaction_data.get('paid_amount', 0)
                    remaining = transaction_data['grand_total'] - paid_amount
                    
                    summary_data.extend([
                        ['', ''],
                        [Paragraph("<b>Paid</b>", summary_label), Paragraph(f"<b>{paid_amount:,.2f} ฿</b>", summary_value)],
                        [Paragraph("<b>Remaining</b>", summary_label), Paragraph(f"<b>{remaining:,.2f} ฿</b>", ParagraphStyle('EngRemain', parent=summary_value, textColor=colors.HexColor('#dc2626')))]
                    ])
            
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
            
            # Footer
            elements.append(self.create_divider(17*cm))
            elements.append(Spacer(1, 15))
            
            # หมายเหตุสำหรับใบวางบิล
            if is_invoice:
                if self.thai_font_available:
                    note_style = ParagraphStyle('ThaiNote', parent=footer_style, fontSize=12, textColor=colors.HexColor('#dc2626'), alignment=TA_LEFT)
                    elements.append(Paragraph(
                        f"<font name='{self.thai_font_name}'><b>**หมายเหตุ: กรุณาชำระเงินภายในวันที่กำหนด | ติดต่อ: {self.shop_settings['phone']}</b></font>", 
                        note_style
                    ))
                else:
                    note_style = ParagraphStyle('EngNote', parent=footer_style, fontSize=12, textColor=colors.HexColor('#dc2626'), alignment=TA_LEFT)
                    elements.append(Paragraph(
                        f"<b>⚠️ Note: Please pay by due date | Contact: {self.shop_settings['phone']}</b>", 
                        note_style
                    ))
                elements.append(Spacer(1, 10))
            
            if self.thai_font_available:
                elements.append(Paragraph(
                    f"<font name='{self.thai_font_name}'><b>ขอบคุณที่ใช้บริการ | Thank you | พิมพ์เมื่อ: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</b></font>", 
                    footer_style
                ))
            else:
                elements.append(Paragraph("<b>Thank you for your business</b>", footer_style))
                elements.append(Spacer(1, 8))
                elements.append(Paragraph(f"Printed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", footer_style))
            
            doc.build(elements)
            
            print(f"✅ {'ใบวางบิล' if is_invoice else 'ใบเสร็จ'}ถูกสร้างด้วยข้อมูล: {self.shop_settings['shop_name']}")
            
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
            
            filename = self.create_receipt(transaction_data, cart_items, is_invoice=False)
            
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
    
    def create_invoice(self, transaction_id, subtotal, vat, grand_total, cart_items, 
                      customer_info, due_days=30):
        """สร้างใบวางบิล/ใบเครดิต"""
        try:
            due_date = (datetime.now() + timedelta(days=due_days)).strftime('%Y-%m-%d')
            
            transaction_data = {
                'transaction_id': transaction_id,
                'datetime': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'due_date': due_date,
                'subtotal': subtotal,
                'vat': vat,
                'grand_total': grand_total,
                'paid_amount': 0,
                'received_amount': 0,
                'change_amount': 0
            }
            
            filename = self.create_receipt(
                transaction_data, 
                cart_items, 
                is_invoice=True,
                customer_info=customer_info
            )
            
            invoice_data = {
                'transaction_id': transaction_id,
                'customer_info': customer_info,
                'datetime': transaction_data['datetime'],
                'due_date': due_date,
                'subtotal': subtotal,
                'vat': vat,
                'grand_total': grand_total,
                'paid_amount': 0,
                'remaining_amount': grand_total,
                'status': 'unpaid',
                'cart_items': cart_items,
                'payment_history': []
            }
            
            self.save_invoice_data(transaction_id, invoice_data)
            
            try:
                os.startfile(filename)
            except AttributeError:
                try:
                    os.system(f"open '{filename}'")
                except:
                    os.system(f"xdg-open '{filename}'")
            
            print(f"✅ สร้างใบวางบิล {transaction_id} สำเร็จ | กำหนดชำระ: {due_date}")
            return filename
            
        except Exception as e:
            raise Exception(f"Error creating invoice: {str(e)}")


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


def test_invoice_system():
    """ทดสอบระบบใบวางบิล"""
    printer = ReceiptPrinter()
    
    test_cart = [
        ['001', 'สินค้า A - Product A', 150.00, 5],
        ['002', 'สินค้า B - Product B', 200.00, 3],
        ['003', 'สินค้า C - Product C', 100.00, 2]
    ]
    
    subtotal = 1550.00
    vat = 108.50
    grand_total = 1658.50
    
    customer_info = {
        'name': 'บริษัท ABC จำกัด / ABC Company Ltd.',
        'phone': '081-234-5678',
        'address': '123 ถนนสุขุมวิท แขวงคลองเตย กรุงเทพฯ 10110'
    }
    
    try:
        print("\n" + "="*60)
        print("🧾 ทดสอบระบบใบวางบิล (Invoice System)")
        print("="*60)
        
        # 1. สร้างใบวางบิล
        print("\n1️⃣ สร้างใบวางบิล INV-001...")
        filename = printer.create_invoice(
            transaction_id="INV-001",
            subtotal=subtotal,
            vat=vat,
            grand_total=grand_total,
            cart_items=test_cart,
            customer_info=customer_info,
            due_days=30
        )
        print(f"   ✅ สร้างไฟล์: {filename}")
        
        # 2. ดูข้อมูลใบวางบิล
        print("\n2️⃣ ข้อมูลใบวางบิล:")
        info = printer.get_invoice_info("INV-001")
        if info:
            print(f"   📋 เลขที่: {info['transaction_id']}")
            print(f"   👤 ลูกค้า: {info['customer_info']['name']}")
            print(f"   💰 ยอดรวม: {info['grand_total']:,.2f} บาท")
            print(f"   📅 กำหนดชำระ: {info['due_date']}")
            print(f"   📊 สถานะ: {info['status']}")
            print(f"   💵 ชำระแล้ว: {info['paid_amount']:,.2f} บาท")
            print(f"   💳 คงเหลือ: {info['remaining_amount']:,.2f} บาท")
        
        # 3. ชำระเงินงวดแรก
        print("\n3️⃣ ชำระเงินงวดที่ 1: 800 บาท...")
        success = printer.update_invoice_payment("INV-001", 800.00)
        if success:
            print("   ✅ บันทึกการชำระเงินสำเร็จ")
            info = printer.get_invoice_info("INV-001")
            print(f"   💵 ชำระแล้ว: {info['paid_amount']:,.2f} บาท")
            print(f"   💳 คงเหลือ: {info['remaining_amount']:,.2f} บาท")
            print(f"   📊 สถานะ: {info['status']}")
        
        # 4. ชำระเงินงวดที่สอง
        print("\n4️⃣ ชำระเงินงวดที่ 2: 858.50 บาท (ชำระครบ)...")
        success = printer.update_invoice_payment("INV-001", 858.50)
        if success:
            print("   ✅ บันทึกการชำระเงินสำเร็จ")
            info = printer.get_invoice_info("INV-001")
            print(f"   💵 ชำระแล้ว: {info['paid_amount']:,.2f} บาท")
            print(f"   💳 คงเหลือ: {info['remaining_amount']:,.2f} บาท")
            print(f"   📊 สถานะ: {info['status']}")
            
            print("\n   📜 ประวัติการชำระเงิน:")
            for idx, payment in enumerate(info['payment_history'], 1):
                print(f"      {idx}. วันที่: {payment['date']}")
                print(f"         จำนวน: {payment['amount']:,.2f} บาท")
                print(f"         คงเหลือ: {payment['remaining']:,.2f} บาท")
        
        # 5. สร้างใบวางบิลใหม่
        print("\n5️⃣ สร้างใบวางบิลใหม่ INV-002...")
        customer_info_2 = {
            'name': 'ร้านค้าปลีก XYZ / XYZ Retail Shop',
            'phone': '082-345-6789',
            'address': '456 ถนนพหลโยธิน จตุจักร กรุงเทพฯ 10900'
        }
        
        test_cart_2 = [
            ['004', 'สินค้า D - Product D', 300.00, 2],
            ['005', 'สินค้า E - Product E', 150.00, 4]
        ]
        
        filename2 = printer.create_invoice(
            transaction_id="INV-002",
            subtotal=1200.00,
            vat=84.00,
            grand_total=1284.00,
            cart_items=test_cart_2,
            customer_info=customer_info_2,
            due_days=15
        )
        print(f"   ✅ สร้างไฟล์: {filename2}")
        
        # 6. ดูรายการค้างชำระ
        print("\n6️⃣ รายการใบวางบิลที่ค้างชำระ:")
        unpaid = printer.get_unpaid_invoices()
        if unpaid:
            for inv_id, inv_data in unpaid.items():
                print(f"\n   📄 {inv_id}")
                print(f"      👤 ลูกค้า: {inv_data['customer_info']['name']}")
                print(f"      💰 ยอดรวม: {inv_data['grand_total']:,.2f} บาท")
                print(f"      💵 ชำระแล้ว: {inv_data['paid_amount']:,.2f} บาท")
                print(f"      💳 คงเหลือ: {inv_data['remaining_amount']:,.2f} บาท")
                print(f"      📅 กำหนดชำระ: {inv_data['due_date']}")
                print(f"      📊 สถานะ: {inv_data['status']}")
        else:
            print("   ✅ ไม่มีใบวางบิลค้างชำระ")
        
        print("\n" + "="*60)
        print("✅ ทดสอบระบบสำเร็จ!")
        print("="*60)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


def demo_all_features():
    """สาธิตฟีเจอร์ทั้งหมด"""
    print("\n" + "="*60)
    print("🎯 RECEIPT PRINTER - FULL DEMO")
    print("="*60)
    
    print("\n📄 Part 1: ใบเสร็จปกติ (Normal Receipt)")
    print("-" * 60)
    test_receipt_printer()
    
    print("\n\n🧾 Part 2: ระบบใบวางบิล (Invoice System)")
    print("-" * 60)
    test_invoice_system()
    
    print("\n" + "="*60)
    print("🎉 DEMO COMPLETED!")
    print("="*60)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        mode = sys.argv[1]
        if mode == "receipt":
            test_receipt_printer()
        elif mode == "invoice":
            test_invoice_system()
        elif mode == "all":
            demo_all_features()
        else:
            print("Usage: python receipt_printer.py [receipt|invoice|all]")
    else:
        demo_all_features()