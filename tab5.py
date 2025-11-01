# tab5.py - Shop Settings Tab (Optimized Layout)
from tkinter import *
from tkinter import ttk, messagebox
import json
import os

class ShopSettingsTab:
    def __init__(self, parent):
        self.parent = parent
        self.settings_file = "shop_settings.json"
        
        # Color scheme (ใช้สีเดียวกับโปรแกรมหลัก)
        self.COLORS = {
            'header': '#0d9488',
            'sidebar': '#475569',
            'background': '#f8fafc',
            'accent': '#14b8a6',
            'text_dark': '#0f172a',
            'text_light': '#ffffff',
            'hover': "#48b4ab",
            'card_bg': '#ffffff',
            'success': '#10b981',
            'border': '#e2e8f0'
        }
        
        # โหลดข้อมูลร้านค้า
        self.load_settings()
        
        # สร้าง UI
        self.create_ui()
    
    def load_settings(self):
        """โหลดข้อมูลร้านค้าจากไฟล์"""
        default_settings = {
            'shop_name': 'ร้านค้าสำหรับ..POS..',
            'address': '29/25 หมู่2 ตำบลสะเดียง เพชรบูรณ์ 67000',
            'phone': '090-951-3031',
            'email': 'Phattananbaosin@shop.com'
        }
        
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    self.settings = json.load(f)
            else:
                self.settings = default_settings
                self.save_settings()
        except Exception as e:
            print(f"Error loading settings: {e}")
            self.settings = default_settings
    
    def save_settings(self):
        """บันทึกข้อมูลร้านค้าลงไฟล์"""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            print(f"Error saving settings: {e}")
            return False
    
    def get_settings(self):
        """ดึงข้อมูลร้านค้าปัจจุบัน"""
        return self.settings
    
    def create_ui(self):
        """สร้างหน้า UI แบบพอดีกรอบ"""
        # Main Container - ใช้ Canvas สำหรับ Scrollbar
        main_canvas = Canvas(self.parent, bg=self.COLORS['background'], highlightthickness=0)
        scrollbar = Scrollbar(self.parent, orient=VERTICAL, command=main_canvas.yview)
        
        scrollable_frame = Frame(main_canvas, bg=self.COLORS['background'])
        scrollable_frame.bind(
            "<Configure>",
            lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        )
        
        main_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        main_canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack Canvas และ Scrollbar
        main_canvas.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)
        
        # Header - ลดขนาด
        header_frame = Frame(scrollable_frame, bg=self.COLORS['header'], height=60)
        header_frame.pack(fill=X, pady=(0, 10))
        header_frame.pack_propagate(False)
        
        Label(header_frame,
              text='⚙️ ตั้งค่าข้อมูลร้านค้า',
              font=('Helvetica', 17, 'bold'),
              bg=self.COLORS['header'],
              fg=self.COLORS['text_light']).pack(side=LEFT, padx=20, pady=15)
        
        Label(header_frame,
              text='ข้อมูลนี้จะแสดงบนใบเสร็จอัตโนมัติ',
              font=('Helvetica', 11),
              bg=self.COLORS['header'],
              fg='#e0f2fe').pack(side=LEFT, padx=5)
        
        # Main Content Frame
        content_container = Frame(scrollable_frame, bg=self.COLORS['background'])
        content_container.pack(fill=BOTH, expand=True, padx=15, pady=5)
        
        # Left Column - Icon และ Preview
        left_frame = Frame(content_container, bg=self.COLORS['card_bg'], relief=SOLID, bd=1, borderwidth=1)
        left_frame.pack(side=LEFT, fill=BOTH, padx=(0, 8), pady=0, expand=False)
        
        # Icon/Logo Area
        icon_frame = Frame(left_frame, bg=self.COLORS['card_bg'])
        icon_frame.pack(pady=15, padx=15)
        
        try:
            shop_icon = PhotoImage(file='shop_icon.png')
            icon_label = Label(icon_frame, image=shop_icon, bg=self.COLORS['card_bg'])
            icon_label.image = shop_icon
            icon_label.pack()
        except:
            Label(icon_frame,
                  text='🏪',
                  font=('Helvetica', 40),
                  bg=self.COLORS['card_bg']).pack()
        
        Label(left_frame,
              text='ข้อมูลร้านค้า',
              font=('Helvetica', 13, 'bold'),
              bg=self.COLORS['card_bg'],
              fg=self.COLORS['text_dark']).pack(pady=(0, 5))
        
        Label(left_frame,
              text='กรอกข้อมูลทางด้านขวา\nเพื่อแสดงบนใบเสร็จ',
              font=('Helvetica', 9),
              bg=self.COLORS['card_bg'],
              fg=self.COLORS['sidebar'],
              justify=CENTER).pack(pady=(0, 15), padx=10)
        
        # Preview Button
        preview_btn = Button(left_frame,
                           text='👁️ ดูตัวอย่าง',
                           font=('Helvetica', 10, 'bold'),
                           bg=self.COLORS['header'],
                           fg=self.COLORS['text_light'],
                           relief=FLAT,
                           cursor='hand2',
                           padx=20,
                           pady=8,
                           command=self.preview_receipt)
        preview_btn.pack(pady=(0, 15), padx=15)
        preview_btn.bind('<Enter>', lambda e: preview_btn.configure(bg=self.COLORS['hover']))
        preview_btn.bind('<Leave>', lambda e: preview_btn.configure(bg=self.COLORS['header']))
        
        # Right Column - Form
        right_frame = Frame(content_container, bg=self.COLORS['card_bg'], relief=SOLID, bd=1, borderwidth=1)
        right_frame.pack(side=LEFT, fill=BOTH, expand=True, padx=(8, 0), pady=0)
        
        # Inner Form Frame with padding
        form_frame = Frame(right_frame, bg=self.COLORS['card_bg'])
        form_frame.pack(fill=BOTH, expand=True, padx=20, pady=15)
        
        # Form Title
        Label(form_frame,
              text='📝 กรอกข้อมูลร้านค้า',
              font=('Helvetica', 14, 'bold'),
              bg=self.COLORS['card_bg'],
              fg=self.COLORS['text_dark'],
              anchor=W).pack(fill=X, pady=(0, 10))
        
        # Form Fields - ใช้ Grid สำหรับจัดเรียง
        fields_data = [
            ('shop_name', '🏪 ชื่อร้านค้า', 'ร้านค้าของฉัน', False),
            ('address', '📍 ที่อยู่', 'ที่อยู่ร้านค้าเต็ม', True),
            ('phone', '📞 เบอร์โทรศัพท์', '0XX-XXX-XXXX', False),
            ('email', '📧 อีเมล', 'shop@email.com', False)
        ]
        
        self.entries = {}
        
        for idx, (key, label_text, placeholder, is_multiline) in enumerate(fields_data):
            # Field Container
            field_frame = Frame(form_frame, bg=self.COLORS['card_bg'])
            field_frame.pack(fill=X, pady=5)
            
            # Label
            Label(field_frame,
                  text=label_text,
                  font=('Helvetica', 11, 'bold'),
                  bg=self.COLORS['card_bg'],
                  fg=self.COLORS['text_dark'],
                  anchor=W).pack(fill=X, pady=(0, 4))
            
            # Entry with border
            entry_container = Frame(field_frame, bg=self.COLORS['border'], relief=FLAT)
            entry_container.pack(fill=X)
            
            if is_multiline:
                # Text widget สำหรับที่อยู่
                entry = Text(entry_container,
                           font=('Helvetica', 11),
                           bg='white',
                           fg=self.COLORS['text_dark'],
                           relief=FLAT,
                           height=2,
                           padx=10,
                           pady=8,
                           wrap=WORD)
                entry.pack(fill=X, padx=1, pady=1)
                entry.insert('1.0', self.settings.get(key, ''))
            else:
                # Entry widget ปกติ
                entry = Entry(entry_container,
                            font=('Helvetica', 11),
                            bg='white',
                            fg=self.COLORS['text_dark'],
                            relief=FLAT)
                entry.pack(fill=X, padx=1, pady=1, ipady=8, ipadx=10)
                entry.insert(0, self.settings.get(key, ''))
            
            # Placeholder hint - เล็กลง
            Label(field_frame,
                  text=f'ตัวอย่าง: {placeholder}',
                  font=('Helvetica', 8, 'italic'),
                  bg=self.COLORS['card_bg'],
                  fg='#94a3b8',
                  anchor=W).pack(fill=X, pady=(2, 0))
            
            self.entries[key] = entry
        
        # Button Frame - อยู่ด้านล่างของ form
        button_frame = Frame(form_frame, bg=self.COLORS['card_bg'])
        button_frame.pack(fill=X, pady=(15, 5))
        
        # Save Button
        save_btn = Button(button_frame,
                         text='💾 บันทึก',
                         font=('Helvetica', 11, 'bold'),
                         bg=self.COLORS['accent'],
                         fg=self.COLORS['text_dark'],
                         relief=FLAT,
                         cursor='hand2',
                         padx=25,
                         pady=4,
                         command=self.save_shop_settings)
        save_btn.pack(side=LEFT, padx=(0, 5))
        
        # Reset Button
        reset_btn = Button(button_frame,
                          text='🔄 รีเซ็ต',
                          font=('Helvetica', 11, 'bold'),
                          bg=self.COLORS['sidebar'],
                          fg=self.COLORS['text_light'],
                          relief=FLAT,
                          cursor='hand2',
                          padx=25,
                          pady=4,
                          command=self.reset_to_default)
        reset_btn.pack(side=LEFT, padx=5)
        
        # Hover effects
        for btn, default_color in [(save_btn, self.COLORS['accent']), 
                                     (reset_btn, self.COLORS['sidebar'])]:
            btn.bind('<Enter>', lambda e, b=btn: b.configure(bg=self.COLORS['hover']))
            btn.bind('<Leave>', lambda e, b=btn, c=default_color: b.configure(bg=c))
        
        # Status bar - ด้านล่างสุด
        status_container = Frame(scrollable_frame, bg=self.COLORS['background'])
        status_container.pack(fill=X, pady=(5, 5), padx=15)
        
        status_border = Frame(status_container, bg=self.COLORS['border'], height=1)
        status_border.pack(fill=X, pady=(0, 5))
        
        self.status_label = Label(status_container,
                                 text='📌 พร้อมใช้งาน - ข้อมูลร้านค้าถูกโหลดแล้ว',
                                 font=('Helvetica', 9),
                                 bg=self.COLORS['background'],
                                 fg=self.COLORS['sidebar'],
                                 anchor=W)
        self.status_label.pack(fill=X, padx=5)
        
        # Mouse wheel scrolling
        def _on_mousewheel(event):
            main_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        main_canvas.bind_all("<MouseWheel>", _on_mousewheel)
    
    def save_shop_settings(self):
        """บันทึกการตั้งค่าร้านค้า"""
        try:
            # ดึงข้อมูลจากฟอร์ม
            for key, entry in self.entries.items():
                if isinstance(entry, Text):
                    self.settings[key] = entry.get('1.0', 'end-1c').strip()
                else:
                    self.settings[key] = entry.get().strip()
            
            # ตรวจสอบว่ากรอกข้อมูลครบ
            if not all(self.settings.values()):
                messagebox.showwarning('คำเตือน', 'กรุณากรอกข้อมูลให้ครบทุกช่อง')
                return
            
            # บันทึกลงไฟล์
            if self.save_settings():
                self.status_label.config(
                    text='✅ บันทึกข้อมูลสำเร็จ! ข้อมูลจะแสดงบนใบเสร็จถัดไป',
                    fg=self.COLORS['success']
                )
                messagebox.showinfo('สำเร็จ', 'บันทึกข้อมูลร้านค้าเรียบร้อย!\nข้อมูลจะถูกใช้ในใบเสร็จถัดไป')
            else:
                raise Exception("ไม่สามารถบันทึกไฟล์ได้")
                
        except Exception as e:
            self.status_label.config(
                text=f'❌ เกิดข้อผิดพลาด: {str(e)}',
                fg='#dc2626'
            )
            messagebox.showerror('ข้อผิดพลาด', f'ไม่สามารถบันทึกข้อมูลได้\n{str(e)}')
    
    def reset_to_default(self):
        """รีเซ็ตค่าเริ่มต้น"""
        if messagebox.askyesno('ยืนยัน', 'ต้องการรีเซ็ตข้อมูลเป็นค่าเริ่มต้นหรือไม่?'):
            default_settings = {
                'shop_name': 'ร้านค้าสำหรับ..POS..',
                'address': '29/25 หมู่2 ตำบลสะเดียง เพชรบูรณ์ 67000',
                'phone': '090-951-3031',
                'email': 'Phattananbaosin@shop.com'
            }
            
            for key, entry in self.entries.items():
                if isinstance(entry, Text):
                    entry.delete('1.0', END)
                    entry.insert('1.0', default_settings[key])
                else:
                    entry.delete(0, END)
                    entry.insert(0, default_settings[key])
            
            self.status_label.config(
                text='🔄 รีเซ็ตข้อมูลเป็นค่าเริ่มต้นแล้ว (ยังไม่ได้บันทึก)',
                fg=self.COLORS['sidebar']
            )
    
    def preview_receipt(self):
        """แสดงตัวอย่างใบเสร็จ"""
        try:
            # ดึงข้อมูลปัจจุบันจากฟอร์ม
            preview_settings = {}
            for key, entry in self.entries.items():
                if isinstance(entry, Text):
                    preview_settings[key] = entry.get('1.0', 'end-1c').strip()
                else:
                    preview_settings[key] = entry.get().strip()
            
            # แสดง preview window
            preview_window = Toplevel(self.parent)
            preview_window.title('ตัวอย่างข้อมูลบนใบเสร็จ')
            preview_window.geometry('550x380')
            preview_window.configure(bg='white')
            preview_window.resizable(False, False)
            
            # Center window
            preview_window.update_idletasks()
            x = (preview_window.winfo_screenwidth() // 2) - (550 // 2)
            y = (preview_window.winfo_screenheight() // 2) - (380 // 2)
            preview_window.geometry(f'550x380+{x}+{y}')
            
            # Header
            Label(preview_window,
                  text='📄 ตัวอย่างข้อมูลที่จะแสดงบนใบเสร็จ',
                  font=('Helvetica', 14, 'bold'),
                  bg=self.COLORS['header'],
                  fg=self.COLORS['text_light'],
                  pady=15).pack(fill=X)
            
            # Content
            content = Frame(preview_window, bg='white', padx=30, pady=20)
            content.pack(fill=BOTH, expand=True)
            
            # Display settings
            Label(content,
                  text=preview_settings.get('shop_name', ''),
                  font=('Helvetica', 18, 'bold'),
                  bg='white',
                  fg=self.COLORS['text_dark']).pack(pady=8)
            
            Label(content,
                  text=preview_settings.get('address', ''),
                  font=('Helvetica', 11),
                  bg='white',
                  fg='#64748b',
                  wraplength=450,
                  justify=CENTER).pack(pady=4)
            
            info_text = f"โทร: {preview_settings.get('phone', '')} | อีเมล: {preview_settings.get('email', '')}"
            Label(content,
                  text=info_text,
                  font=('Helvetica', 10),
                  bg='white',
                  fg='#64748b').pack(pady=4)
            
            # Divider
            Frame(content, bg=self.COLORS['border'], height=1).pack(fill=X, pady=15)
            
            # Info text
            Label(content,
                  text='ข้อมูลข้างต้นจะปรากฏที่ส่วนหัวของใบเสร็จ PDF\nหลังจากคุณกดปุ่ม "บันทึก" และทำการขายสินค้า',
                  font=('Helvetica', 9, 'italic'),
                  bg='white',
                  fg='#94a3b8',
                  justify=CENTER).pack(pady=10)
            
            # Close button
            Button(preview_window,
                   text='ปิด',
                   font=('Helvetica', 10, 'bold'),
                   bg=self.COLORS['accent'],
                   fg=self.COLORS['text_dark'],
                   relief=FLAT,
                   cursor='hand2',
                   padx=30,
                   pady=8,
                   command=preview_window.destroy).pack(pady=15)
            
        except Exception as e:
            messagebox.showerror('ข้อผิดพลาด', f'ไม่สามารถแสดงตัวอย่างได้\n{str(e)}')

# สำหรับทดสอบแยกต่างหาก
if __name__ == '__main__':
    root = Tk()
    root.title('ทดสอบ Shop Settings')
    root.geometry('1000x600')
    
    tab = ShopSettingsTab(root)
    
    root.mainloop()