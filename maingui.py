from tkinter import *
from tkinter import ttk, messagebox
import os
from basicsql import *
from elements import SalesTab, ProductTab, DashboardTab

# Import แต่ละแท็บ
try:
    from tab1 import SalesTab
    from tab2 import ProductTab  
    from tab3 import DashboardTab
    from tab4 import ProfitTab
except ImportError as e:
    print(f"Error importing tabs: {e}")
    print("กรุณาตรวจสอบว่าไฟล์ tab1.py, tab2.py, tab3.py, tab4.py อยู่ในโฟลเดอร์เดียวกัน")
    print("และติดตั้ง tkcalendar: pip install tkcalendar")
    exit(1)

# PATH = os.getcwd()
# print(PATH)
# p1 = os.path.join(PATH,'tab1.png')

GUI = Tk()
w = 1000
h = 600

ws = GUI.winfo_screenwidth()
hs = GUI.winfo_screenheight()

x = (ws/2)-(w/2)
y = (hs/2)-(h/2)

GUI.geometry(f'{w}x{h}+{x:.0f}+{y:.0f}')
# GUI.geometry('700x600')
GUI.title('โปรแกรมขายของสำหรับ POS - Version 1.1 Beta')

##########MENU###########
menubar = Menu(GUI)
GUI.config(menu=menubar)

#File Menu
filemenu = Menu(menubar,tearoff=0)
menubar.add_cascade(label='File',menu=filemenu)
filemenu.add_command(label='เปิดเมนูเพิ่มสินค้า',command=lambda: print('Add Product'))
filemenu.add_command(label='ออกจากโปรแกรม',command=lambda: GUI.quit())

#About Menu
def AboutMenu(event=None):
    GUI2 = Toplevel()
    w = 500
    h = 300
    
    ws = GUI.winfo_screenwidth()
    hs = GUI.winfo_screenheight()
    
    x = (ws/2)-(w/2)
    y = (hs/2)-(h/2)
    
    GUI2.geometry(f'{w}x{h}+{x:.0f}+{y:.0f}')
    
    try:
        uncle_icon = PhotoImage(file='Sale.png').subsample(2) # .subsample(2) resize down / 2
        Label(GUI2,image=uncle_icon).pack()
    except:
        pass  # ถ้าไม่มีไฟล์ไอคอนก็ข้าม
    
    Label(GUI2,text='โปรแกรมสำหรับ POS Version 1.1 beta \n\nฟีเจอร์ใหม่:\n• แท็บ Profit Analysis\n• Reorder Point System\n• Supplier Management\n• Smart Alerts\n\nTel: 090-951-3031 | Email: Phattananbaosin@gmail.com',
          font=(None, 11)).pack(pady=20)
    
    GUI2.mainloop()

aboutmenu = Menu(menubar,tearoff=0)
menubar.add_cascade(label='About',menu=aboutmenu)
aboutmenu.add_command(label='เกี่ยวกับโปรแกรม',command=AboutMenu)

GUI.bind('<F12>',AboutMenu)

##########TAB###########
Tab = ttk.Notebook(GUI)
Tab.pack(fill=BOTH,expand=1)

# สร้าง Frame สำหรับแต่ละแท็บ
T1 = Frame(Tab)
T2 = Frame(Tab)
T3 = Frame(Tab)
T4 = Frame(Tab)

# โหลดไอคอนแท็บ (มี error handling)
try:
    tab_icon1 = PhotoImage(file='tab1.png')
    tab_icon2 = PhotoImage(file='tab2.png')
    tab_icon3 = PhotoImage(file='tab3.png')
    tab_icon4 = PhotoImage(file='tab4.png')  # สร้างไอคอนนี้ถ้าต้องการ
    
    # เพิ่มแท็บพร้อมไอคอน
    Tab.add(T1,text='เมนูขาย',image=tab_icon1,compound='left')
    Tab.add(T2,text='เพิ่มสินค้า',image=tab_icon2,compound='left')
    Tab.add(T3,text='Dashboard',image=tab_icon3,compound='left')
    Tab.add(T4,text='Profit',image=tab_icon4,compound='left')
    
except:
    # ถ้าไม่มีไอคอน ใช้แค่ข้อความ
    Tab.add(T1,text='เมนูขาย')
    Tab.add(T2,text='เพิ่มสินค้า')
    Tab.add(T3,text='Dashboard')
    Tab.add(T4,text='Profit')
    print("หมายเหตุ: ไม่พบไฟล์ไอคอน กำลังรันโดยไม่มีไอคอน")

# สร้าง instance ของแต่ละแท็บ
try:
    sales_tab = SalesTab(T1)
    product_tab = ProductTab(T2)
    dashboard_tab = DashboardTab(T3)
    profit_tab = ProfitTab(T4)
    
    # ตั้งค่า reference ระหว่างแท็บ (เรียกหลังสร้างทุกแท็บแล้ว)
    sales_tab.set_references(product_tab=product_tab, dashboard_tab=dashboard_tab, profit_tab=profit_tab)
    product_tab.set_references(sales_tab=sales_tab, dashboard_tab=dashboard_tab, profit_tab=profit_tab)
    
    print("โปรแกรมสำหรับ POS Version 1.1 Bera เริ่มทำงานเรียบร้อย!")
    print("ฟีเจอร์สำหรับ Demo : Profit Analysis, Reorder Point, Supplier Management")
    
except Exception as e:
    messagebox.showerror("Error", f"เกิดข้อผิดพลาดในการเริ่มโปรแกรม:\n{str(e)}\n\nกรุณาตรวจสอบ:\n1. ไฟล์ tab1.py-tab4.py\n2. ไฟล์ basicsql.py\n3. ติดตั้ง tkcalendar")
    GUI.quit()

GUI.mainloop()