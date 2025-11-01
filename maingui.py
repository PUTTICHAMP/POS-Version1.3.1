from tkinter import *
from tkinter import ttk, messagebox
import os
from basicsql import *
from elements import SalesTab, ProductTab, DashboardTab

# Color Scheme
COLORS = {
    'header': '#0d9488',        # Teal-600 - Header, ปุ่มหลัก
    'sidebar': '#475569',       # Slate-600 - Sidebar, Panel
    'background': '#f8fafc',    # Slate-50 - พื้นหลังหลัก
    'accent': '#14b8a6',        # Teal-500 - ปุ่มเน้น, Highlights
    'text_dark': '#0f172a',     # Slate-900 - ข้อความเข้ม
    'text_light': '#ffffff',    # White - ข้อความสว่าง
    'hover': "#48b4ab",         # Teal-700 - สีเมื่อ hover
    'border': '#5eead4',        # Teal-300 - Light Border
    'border_dark': '#0d9488',   # Teal-600 - Dark Border
    'card_bg': '#ffffff',       # White - Card Background
    'success': '#10b981',       # Emerald-500 - Success
    'warning': '#f59e0b',       # Amber-500 - Warning
    'error': "#7A0707",         # Red-500 - Error
    'muted': "#f2f5f9"          # Slate-400 - Muted Text
}

# Import แต่ละแท็บ
try:
    from tab1 import SalesTab
    from tab2 import ProductTab  
    from tab3 import DashboardTab
    from tab4 import ProfitTab
    from tab5 import ShopSettingsTab  # เพิ่ม Tab5
except ImportError as e:
    print(f"Error importing tabs: {e}")
    print("กรุณาตรวจสอบว่าไฟล์ tab1.py, tab2.py, tab3.py, tab4.py, tab5.py อยู่ในโฟลเดอร์เดียวกัน")
    print("และติดตั้ง tkcalendar: pip install tkcalendar")
    exit(1)

GUI = Tk()
w = 1000
h = 600

ws = GUI.winfo_screenwidth()
hs = GUI.winfo_screenheight()

x = (ws/2)-(w/2)
y = (hs/2)-(h/2)

GUI.geometry(f'{w}x{h}+{x:.0f}+{y:.0f}')
GUI.title('โปรแกรมขายของสำหรับ POS - Version 1.3.0')  # เพิ่มเวอร์ชั่น
GUI.configure(bg=COLORS['background'])

# กำหนด Style สำหรับ ttk widgets
style = ttk.Style()
style.theme_use('clam')

# Style สำหรับ Notebook (Tab container)
style.configure('TNotebook', 
                background=COLORS['background'],
                borderwidth=0,
                tabmargins=[2, 5, 2, 0])
style.configure('TNotebook.Tab', 
                background=COLORS['header'],
                foreground=COLORS['text_light'],
                padding=[35, 12],  # ปรับ padding ให้เหมาะกับ 5 แท็บ
                font=('Helvetica', 11, 'bold'),
                width=18)  # ลดความกว้างเล็กน้อย
style.map('TNotebook.Tab',
          background=[('selected', COLORS['accent'])],
          foreground=[('selected', COLORS['text_dark'])],
          padding=[('selected', [35, 12])],
          expand=[('selected', [0, 0, 0, 0])])

# Style สำหรับ Frame
style.configure('TFrame', background=COLORS['background'])

# Style สำหรับ Label
style.configure('TLabel', 
                background=COLORS['background'],
                foreground=COLORS['text_dark'],
                font=('Helvetica', 10))
style.configure('Header.TLabel',
                background=COLORS['header'],
                foreground=COLORS['text_light'],
                font=('Helvetica', 14, 'bold'),
                padding=10)
style.configure('Sidebar.TLabel',
                background=COLORS['sidebar'],
                foreground=COLORS['text_light'],
                font=('Helvetica', 10))

# Style สำหรับ Button
style.configure('TButton',
                background=COLORS['header'],
                foreground=COLORS['text_light'],
                borderwidth=0,
                focuscolor='none',
                font=('Helvetica', 10, 'bold'),
                padding=[15, 8])
style.map('TButton',
          background=[('active', COLORS['hover']),
                     ('pressed', COLORS['accent'])])

style.configure('Accent.TButton',
                background=COLORS['accent'],
                foreground=COLORS['text_dark'],
                font=('Helvetica', 11, 'bold'),
                padding=[20, 10])
style.map('Accent.TButton',
          background=[('active', COLORS['hover']),
                     ('pressed', COLORS['header'])])

# Style สำหรับ Entry
style.configure('TEntry',
                fieldbackground='white',
                foreground=COLORS['text_dark'],
                borderwidth=2,
                relief='solid')

##########MENU###########
menubar = Menu(GUI, 
               bg=COLORS['header'],
               fg=COLORS['text_light'],
               activebackground=COLORS['accent'],
               activeforeground=COLORS['text_dark'],
               font=('Helvetica', 10))
GUI.config(menu=menubar)

#File Menu
filemenu = Menu(menubar, tearoff=0,
                bg=COLORS['sidebar'],
                fg=COLORS['text_light'],
                activebackground=COLORS['accent'],
                activeforeground=COLORS['text_dark'],
                font=('Helvetica', 10))
menubar.add_cascade(label='File', menu=filemenu)
filemenu.add_command(label='เปิดเมนูเพิ่มสินค้า', command=lambda: print('Add Product'))
filemenu.add_command(label='ออกจากโปรแกรม', command=lambda: GUI.quit())

#About Menu
def AboutMenu(event=None):
    GUI2 = Toplevel()
    w = 500
    h = 450
    
    ws = GUI.winfo_screenwidth()
    hs = GUI.winfo_screenheight()
    
    x = (ws/2)-(w/2)
    y = (hs/2)-(h/2)
    
    GUI2.geometry(f'{w}x{h}+{x:.0f}+{y:.0f}')
    GUI2.configure(bg=COLORS['background'])
    GUI2.title('เกี่ยวกับโปรแกรม')
    
    # Header
    header_frame = Frame(GUI2, bg=COLORS['header'], height=60)
    header_frame.pack(fill=X)
    header_frame.pack_propagate(False)
    
    Label(header_frame, 
          text='โปรแกรมสำหรับ POS - Point of Sale System',
          bg=COLORS['header'],
          fg=COLORS['text_light'],
          font=('Helvetica', 16, 'bold')).pack(pady=15)
    
    # Content
    content_frame = Frame(GUI2, bg=COLORS['background'])
    content_frame.pack(fill=BOTH, expand=True, padx=20, pady=20)
    
    try:
        uncle_icon = PhotoImage(file='Sale.png').subsample(2)
        Label(content_frame, image=uncle_icon, bg=COLORS['background']).pack(pady=10)
        GUI2.uncle_icon = uncle_icon  # เก็บ reference ไว้
    except:
        pass
    
    info_text = '''Version 1.3 Beta

ฟีเจอร์ใหม่:
• แท็บ Profit Analysis
• Reorder Point System
• Supplier Management
• Shop Settings (ตั้งค่าข้อมูลร้าน)
• Smart Alerts

Tel: 090-951-3031
Email: Phattananbaosin@gmail.com'''
    
    Label(content_frame,
          text=info_text,
          bg=COLORS['background'],
          fg=COLORS['text_dark'],
          font=('Helvetica', 11),
          justify=CENTER).pack(pady=10)
    
    # Close Button
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

##########TAB###########
Tab = ttk.Notebook(GUI)
Tab.pack(fill=BOTH, expand=1, padx=10, pady=10)

# สร้าง Frame สำหรับแต่ละแท็บ
T1 = ttk.Frame(Tab)
T2 = ttk.Frame(Tab)
T3 = ttk.Frame(Tab)
T4 = ttk.Frame(Tab)
T5 = ttk.Frame(Tab)  # เพิ่ม Tab5

# โหลดไอคอนแท็บ (มี error handling)
try:
    tab_icon1 = PhotoImage(file='tab1.png')
    tab_icon2 = PhotoImage(file='tab2.png')
    tab_icon3 = PhotoImage(file='tab3.png')
    tab_icon4 = PhotoImage(file='tab4.png')
    tab_icon5 = PhotoImage(file='tab5.png')
    
    # เพิ่มแท็บพร้อมไอคอน
    Tab.add(T1, text=' ระบบขายสินค้า ', image=tab_icon1, compound='left')
    Tab.add(T2, text=' เพิ่มสินค้า ', image=tab_icon2, compound='left')
    Tab.add(T3, text=' Dashboard', image=tab_icon3, compound='left')
    Tab.add(T4, text='  Profit  ', image=tab_icon4, compound='left')
    Tab.add(T5, text=' ตั้งค่าข้อมูลร้านค้า', image=tab_icon5, compound='left')
    
    # เก็บ reference ไว้
    GUI.tab_icon1 = tab_icon1
    GUI.tab_icon2 = tab_icon2
    GUI.tab_icon3 = tab_icon3
    GUI.tab_icon4 = tab_icon4
    GUI.tab_icon5 = tab_icon5
    
except:
    # ถ้าไม่มีไอคอน ใช้ emoji แทน
    Tab.add(T1, text=' 💰 เมนูขาย ')
    Tab.add(T2, text=' 📦 เพิ่มสินค้า')
    Tab.add(T3, text=' 📊 Dashboard')
    Tab.add(T4, text=' 💹 Profit ')
    Tab.add(T5, text=' ⚙️ ตั้งค่าร้าน')
    print("หมายเหตุ: ไม่พบไฟล์ไอคอน กำลังรันโดยใช้ emoji แทน")

# สร้าง instance ของแต่ละแท็บ
try:
    sales_tab = SalesTab(T1)
    product_tab = ProductTab(T2)
    dashboard_tab = DashboardTab(T3)
    profit_tab = ProfitTab(T4)
    shop_settings_tab = ShopSettingsTab(T5)  # เพิ่ม Tab5
    
    # ตั้งค่า reference ระหว่างแท็บ (ใช้ try-except เพื่อรองรับทั้ง method เก่าและใหม่)
    try:
        sales_tab.set_references(product_tab=product_tab, dashboard_tab=dashboard_tab, 
                               profit_tab=profit_tab, shop_settings_tab=shop_settings_tab)
    except TypeError:
        # ถ้า set_references ไม่รองรับ shop_settings_tab ให้ใช้แบบเก่า
        sales_tab.set_references(product_tab=product_tab, dashboard_tab=dashboard_tab, 
                               profit_tab=profit_tab)
        print("⚠️ Warning: SalesTab.set_references() ไม่รองรับ shop_settings_tab parameter")
    
    try:
        product_tab.set_references(sales_tab=sales_tab, dashboard_tab=dashboard_tab, 
                                 profit_tab=profit_tab, shop_settings_tab=shop_settings_tab)
    except TypeError:
        # ถ้า set_references ไม่รองรับ shop_settings_tab ให้ใช้แบบเก่า
        product_tab.set_references(sales_tab=sales_tab, dashboard_tab=dashboard_tab, 
                                 profit_tab=profit_tab)
        print("⚠️ Warning: ProductTab.set_references() ไม่รองรับ shop_settings_tab parameter")
    
    print("=" * 60)
    print("โปรแกรมสำหรับ POS Version 1.3 Beta")
    print("เริ่มทำงานเรียบร้อย! ✓")
    print("=" * 60)
    print("ฟีเจอร์: Profit Analysis, Reorder Point, Supplier Management")
    print("ฟีเจอร์ใหม่: Shop Settings - ตั้งค่าข้อมูลร้านค้า")
    print("Color Theme: Modern Green")
    print("=" * 60)
    
except Exception as e:
    messagebox.showerror("Error", 
                        f"เกิดข้อผิดพลาดในการเริ่มโปรแกรม:\n{str(e)}\n\n"
                        "กรุณาตรวจสอบ:\n"
                        "1. ไฟล์ tab1.py-tab5.py\n"
                        "2. ไฟล์ basicsql.py\n"
                        "3. ติดตั้ง tkcalendar")
    import traceback
    traceback.print_exc()
    GUI.quit()

GUI.mainloop()