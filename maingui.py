from tkinter import *
from tkinter import ttk, messagebox
import os
from basicsql import *

# Color Scheme - สีสำหรับแต่ละ Tab
COLORS = {
    'header': "#475569",
    'sidebar': '#475569',
    'background': '#f8fafc',
    'accent': "#64748b",
    'text_dark': '#0f172a',
    'text_light': '#ffffff',
    'hover': "#e7f3f2",
    'border': '#5eead4',
    'border_dark': '#0d9488',
    'card_bg': "#f7f0f0",
    'success': '#10b981',
    'warning': '#f59e0b',
    'error': "#7A0707",
    'muted': "#f2f5f9",


    # สีสำหรับแต่ละ Tab
    'tab1': "#31b0a5",      # 🟢 Teal
    'tab1_hover': '#0f766e',
    'tab2': '#3b82f6',      # 🔵 Blue
    'tab2_hover': '#2563eb',
    'tab3': '#8b5cf6',      # 🟣 Violet
    'tab3_hover': '#7c3aed',
    'tab4': '#f59e0b',      # 🟡 Amber
    'tab4_hover': '#d97706',
    'tab5': '#64748b',      # ⚫ Slate
    'tab5_hover': '#475569',
    'tab6': '#ec4899',      # 🩷 Pink
    'tab6_hover': '#db2777',
}

# Import แต่ละแท็บ
try:
    from tab1 import SalesTab
    from tab2 import ProductTab  
    from tab3 import DashboardTab
    from tab4 import ProfitTab
    from tab5 import ShopSettingsTab
    from tab6 import CreditManagementTab
    print("✅ All tabs imported successfully")
except ImportError as e:
    print(f"❌ Error importing tabs: {e}")
    print("กรุณาตรวจสอบว่าไฟล์ tab1.py - tab6.py อยู่ในโฟลเดอร์เดียวกัน")
    exit(1)

GUI = Tk()
w = 1000
h = 600

ws = GUI.winfo_screenwidth()
hs = GUI.winfo_screenheight()

x = (ws/2)-(w/2)
y = (hs/2)-(h/2)

GUI.geometry(f'{w}x{h}+{x:.0f}+{y:.0f}')
GUI.title('โปรแกรมขายของสำหรับ POS - Version 1.4.0 (Beta)')
GUI.configure(bg=COLORS['background'])

# กำหนด Style พื้นฐาน
style = ttk.Style()
style.theme_use('clam')
style.configure('TFrame', background=COLORS['background'])
style.configure('TLabel', 
                background=COLORS['background'],
                foreground=COLORS['text_dark'],
                font=('Helvetica', 10))

##########CUSTOM TAB SYSTEM###########
class CustomTabSystem:
    def __init__(self, parent):
        self.parent = parent
        self.tabs = []
        self.tab_frames = []
        self.tab_buttons = []
        self.current_tab = 0
        
        # Container หลัก
        self.container = Frame(parent, bg=COLORS['background'])
        self.container.pack(fill=BOTH, expand=1, padx=10, pady=10)
        
        # Tab Bar (แถบปุ่ม Tab)
        self.tab_bar = Frame(self.container, bg=COLORS['background'], height=50)
        self.tab_bar.pack(fill=X, pady=(0, 5))
        self.tab_bar.pack_propagate(False)
        
        # Content Area (พื้นที่แสดงเนื้อหา)
        self.content_area = Frame(self.container, bg=COLORS['background'])
        self.content_area.pack(fill=BOTH, expand=1)
    
    def add_tab(self, text, color, hover_color, icon_file=None, icon_emoji=None):
        """เพิ่ม Tab ใหม่"""
        # สร้าง Frame สำหรับเนื้อหา
        tab_frame = Frame(self.content_area, bg=COLORS['background'])
        self.tab_frames.append(tab_frame)
        
        # สร้างปุ่ม Tab
        btn_frame = Frame(self.tab_bar, bg=COLORS['background'])
        btn_frame.pack(side=LEFT, padx=2)
        
        # พยายามโหลดไอคอน
        icon_label = None
        try:
            if icon_file and os.path.exists(icon_file):
                icon_img = PhotoImage(file=icon_file)
                icon_label = Label(btn_frame, image=icon_img, bg=color)
                icon_label.image = icon_img  # Keep reference
                icon_label.pack(side=LEFT, padx=(12, 0))
        except:
            # ใช้ emoji แทน
            if icon_emoji:
                icon_label = Label(btn_frame, text=icon_emoji, bg=color, 
                                 fg=COLORS['text_light'], font=('Helvetica', 14))
                icon_label.pack(side=LEFT, padx=(10, 5))
        
        # สร้างปุ่ม
        tab_index = len(self.tabs)
        
        btn = Label(btn_frame, 
                   text=text,
                   bg=color,
                   fg=COLORS['text_light'],
                   font=('Helvetica', 10, 'bold'),
                   padx=20,
                   pady=12,
                   cursor='hand2')
        btn.pack(side=LEFT, fill=BOTH, expand=True)
        
        # Bind events
        btn.bind('<Button-1>', lambda e, idx=tab_index: self.switch_tab(idx))
        btn.bind('<Enter>', lambda e: self.on_hover(btn, hover_color))
        btn.bind('<Leave>', lambda e: self.on_leave(btn, color))
        
        if icon_label:
            icon_label.bind('<Button-1>', lambda e, idx=tab_index: self.switch_tab(idx))
            icon_label.bind('<Enter>', lambda e: self.on_hover_with_icon(btn, icon_label, hover_color))
            icon_label.bind('<Leave>', lambda e: self.on_leave_with_icon(btn, icon_label, color))
        
        self.tab_buttons.append((btn, icon_label, color, hover_color))
        self.tabs.append({
            'text': text,
            'color': color,
            'hover_color': hover_color,
            'frame': tab_frame
        })
        
        # แสดง Tab แรก
        if tab_index == 0:
            self.switch_tab(0)
        
        return tab_frame
    
    def on_hover(self, btn, hover_color):
        if self.tab_buttons.index((btn, None, '', '')) != self.current_tab:
            btn.config(bg=hover_color)
    
    def on_leave(self, btn, color):
        btn_index = next((i for i, (b, _, _, _) in enumerate(self.tab_buttons) if b == btn), -1)
        if btn_index != self.current_tab:
            btn.config(bg=color)
    
    def on_hover_with_icon(self, btn, icon, hover_color):
        btn_index = next((i for i, (b, _, _, _) in enumerate(self.tab_buttons) if b == btn), -1)
        if btn_index != self.current_tab:
            btn.config(bg=hover_color)
            if icon:
                icon.config(bg=hover_color)
    
    def on_leave_with_icon(self, btn, icon, color):
        btn_index = next((i for i, (b, _, _, _) in enumerate(self.tab_buttons) if b == btn), -1)
        if btn_index != self.current_tab:
            btn.config(bg=color)
            if icon:
                icon.config(bg=color)
    
    def switch_tab(self, index):
        """สลับไปยัง Tab ที่เลือก"""
        # ซ่อน Tab เก่า
        if self.current_tab is not None and self.current_tab < len(self.tab_frames):
            self.tab_frames[self.current_tab].pack_forget()
        
        # แสดง Tab ใหม่
        self.tab_frames[index].pack(fill=BOTH, expand=1)
        self.current_tab = index
        
        # อัพเดทสีปุ่ม
        for i, (btn, icon, color, hover_color) in enumerate(self.tab_buttons):
            if i == index:
                # Tab ที่เลือก - สว่างขึ้น
                selected_color = hover_color
                btn.config(bg=selected_color, relief=SOLID, borderwidth=0)
                if icon:
                    icon.config(bg=selected_color)
            else:
                # Tab ที่ไม่ได้เลือก
                btn.config(bg=color, relief=FLAT, borderwidth=0)
                if icon:
                    icon.config(bg=color)
    
    def select(self, frame):
        """สลับไปยัง Tab ตาม Frame"""
        try:
            index = self.tab_frames.index(frame)
            self.switch_tab(index)
        except ValueError:
            pass

# สร้าง Custom Tab System
Tab = CustomTabSystem(GUI)

# เพิ่ม Tabs พร้อมสีที่กำหนด
T1 = Tab.add_tab(' ระบบขายสินค้า ', COLORS['tab1'], COLORS['tab1_hover'], 
                 'tab1.png', '💰')
T2 = Tab.add_tab(' เพิ่มสินค้า ', COLORS['tab2'], COLORS['tab2_hover'], 
                 'tab2.png', '📦')
T3 = Tab.add_tab(' Dashboard ', COLORS['tab3'], COLORS['tab3_hover'], 
                 'tab3.png', '📊')
T4 = Tab.add_tab(' วิเคราะห์กำไร ', COLORS['tab4'], COLORS['tab4_hover'], 
                 'tab4.png', '💹')
T5 = Tab.add_tab(' ตั้งค่าร้านค้า ', COLORS['tab5'], COLORS['tab5_hover'], 
                 'tab5.png', '⚙️')
T6 = Tab.add_tab(' ลูกค้าและบิลเครดิต ', COLORS['tab6'], COLORS['tab6_hover'], 
                 'tab6.png', '💳')

# ฟังก์ชันสำหรับสลับแท็บ
def switch_to_product_tab():
    Tab.select(T2)
    try:
        product_tab.entries['Barcode:'].focus()
    except:
        pass

def switch_to_credit_tab():
    Tab.select(T6)

##########MENU###########
menubar = Menu(GUI, 
               bg=COLORS['header'],
               fg=COLORS['text_light'],
               activebackground=COLORS['accent'],
               activeforeground=COLORS['text_dark'],
               font=('Helvetica', 10))
GUI.config(menu=menubar)

# File Menu
filemenu = Menu(menubar, tearoff=0,
                bg=COLORS['sidebar'],
                fg=COLORS['text_light'],
                activebackground=COLORS['accent'],
                activeforeground=COLORS['text_dark'],
                font=('Helvetica', 10))
menubar.add_cascade(label='File', menu=filemenu)
filemenu.add_command(label='เปิดเมนูเพิ่มสินค้า', command=switch_to_product_tab)
filemenu.add_command(label='จัดการลูกค้าและเครดิต', command=switch_to_credit_tab)
filemenu.add_separator()
filemenu.add_command(label='ออกจากโปรแกรม', command=lambda: GUI.quit())

# About Menu
def AboutMenu(event=None):
    GUI2 = Toplevel()
    w = 500
    h = 520
    
    ws = GUI.winfo_screenwidth()
    hs = GUI.winfo_screenheight()
    
    x = (ws/2)-(w/2)
    y = (hs/2)-(h/2)
    
    GUI2.geometry(f'{w}x{h}+{x:.0f}+{y:.0f}')
    GUI2.configure(bg=COLORS['background'])
    GUI2.title('เกี่ยวกับโปรแกรม')
    
    header_frame = Frame(GUI2, bg=COLORS['header'], height=60)
    header_frame.pack(fill=X)
    header_frame.pack_propagate(False)
    
    Label(header_frame, 
          text='โปรแกรมสำหรับ POS - Point of Sale System',
          bg=COLORS['header'],
          fg=COLORS['text_light'],
          font=('Helvetica', 16, 'bold')).pack(pady=15)
    
    content_frame = Frame(GUI2, bg=COLORS['background'])
    content_frame.pack(fill=BOTH, expand=True, padx=20, pady=20)
    
    try:
        Photo_icon = PhotoImage(file='Sale.png').subsample(2)
        Label(content_frame, image=Photo_icon, bg=COLORS['background']).pack(pady=10)
        GUI2.Photo_icon = Photo_icon
    except:
        pass
    
    info_text = '''Version 1.4 (Beta) - ปรับปรุงล่าสุด: 17 November 2025

ฟีเจอร์ใหม่:
• 🎨 Tab แต่ละอันมีสีเฉพาะตัว
• 💳 ระบบวางบิล (เครดิต)
• 👥 จัดการลูกค้าและวงเงิน
• 📋 ติดตามบิลค้างชำระ
• 📊 Profit Analysis
• ⚡ Reorder Point System


ผู้พัฒนา: พัทธนันท์ เบ้าศิลป์
อีเมล: Phattananbaosinshop@gmail.com
Tel: 090-951-3031'''
    
    Label(content_frame,
          text=info_text,
          bg=COLORS['background'],
          fg=COLORS['text_dark'],
          font=('Helvetica', 11),
          justify=CENTER).pack(pady=10)
    
    close_btn = Button(content_frame,
                      text='ปิด',
                      command=GUI2.destroy,
                      bg=COLORS['accent'],
                      fg=COLORS['text_dark'],
                      font=('Helvetica', 10, 'bold'),
                      relief=FLAT,
                      cursor='hand2',
                      padx=30,
                      pady=8)
    close_btn.pack(pady=10)
    
    GUI2.mainloop()

aboutmenu = Menu(menubar, tearoff=0,
                 bg=COLORS['sidebar'],
                 fg=COLORS['text_light'],
                 activebackground=COLORS['accent'],
                 activeforeground=COLORS['text_dark'],
                 font=('Helvetica', 10))
menubar.add_cascade(label='About', menu=aboutmenu)
aboutmenu.add_command(label='เกี่ยวกับโปรแกรม', command=AboutMenu)

GUI.bind('<F12>', AboutMenu)

# สร้าง instance ของแต่ละแท็บ
try:
    sales_tab = SalesTab(T1)
    product_tab = ProductTab(T2)
    dashboard_tab = DashboardTab(T3)
    profit_tab = ProfitTab(T4)
    shop_settings_tab = ShopSettingsTab(T5)
    credit_tab = CreditManagementTab(T6)
    
    sales_tab.set_references(
        product_tab=product_tab, 
        dashboard_tab=dashboard_tab, 
        profit_tab=profit_tab,
        credit_tab=credit_tab
    )
    
    product_tab.set_references(
        sales_tab=sales_tab, 
        dashboard_tab=dashboard_tab, 
        profit_tab=profit_tab
    )
    
    print("=" * 70)
    print("🎉 โปรแกรมสำหรับ POS Version 1.4 - Custom Colored Tabs")
    print("=" * 70)
    print("✅ เริ่มทำงานเรียบร้อย!")
    print("=" * 70)
    print("🎨 สี Tab:")
    print("   🟢 Tab 1: Teal (เขียวมิ้นท์)")
    print("   🔵 Tab 2: Blue (น้ำเงิน)")
    print("   🟣 Tab 3: Violet (ม่วง)")
    print("   🟡 Tab 4: Amber (ทอง)")
    print("   ⚫ Tab 5: Slate (เทา)")
    print("   🩷 Tab 6: Pink (ชมพู)")
    print("=" * 70)
    
except Exception as e:
    messagebox.showerror("Error", 
                        f"เกิดข้อผิดพลาดในการเริ่มโปรแกรม:\n{str(e)}")
    import traceback
    traceback.print_exc()
    GUI.quit()

GUI.mainloop()