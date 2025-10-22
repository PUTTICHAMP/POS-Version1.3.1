from tkinter import *
from tkinter import ttk, messagebox

GUI = Tk()
GUI.geometry('700x600')
GUI.title('โปรแกรมร้านชำลุง')

L1 = Label(GUI, text='โปรแกรมร้านชำลุง', font=('tahoma', 24, 'bold'), fg='green')
L1.pack(pady=10)

# กล่องค้นหา
search_var = StringVar()

def filter_products(*args):
    keyword = search_var.get().strip().lower()
    for product, button in product_buttons.items():
        if keyword in product.lower():
            button.grid()
        else:
            button.grid_remove()

search_box = Entry(GUI, textvariable=search_var, font=('tahoma', 14), width=30)
search_box.pack(pady=10)
search_var.trace('w', filter_products)

frame = Frame(GUI)
frame.pack()

product_data = {
    'แอปเปิ้ล': 'นี่คือแอปเปิ้ลนำเข้าจากนิวซีแลนด์ ราคากิโลกรัมละ 100 บาท',
    'มะม่วง': 'มะม่วงเขียวเสวย ราคากิโลกรัมละ 10 บาท',
    'ทุเรียน': 'ทุเรียนหมอนทองพรีเมี่ยม ราคากิโลกรัมละ 300 บาท',
    'องุ่น': 'องุ่นนำเข้าจากญี่ปุ่น ราคากิโลกรัมละ 150 บาท',
    'กล้วย': 'กล้วยน้ำว้าจากสวน ราคาหวีละ 25 บาท',
    'ส้ม': 'ส้มนำเข้าจากออสเตรเลีย ราคากิโลกรัมละ 80 บาท',
    'แตงโม': 'แตงโมเนื้อแดงหวานฉ่ำ ราคากิโลกรัมละ 25 บาท',
    'สับปะรด': 'สับปะรดภูแลจากเชียงราย ราคาผลละ 40 บาท',
    'ฝรั่ง': 'ฝรั่งกิมจู ราคากิโลกรัมละ 30 บาท',
    'มังคุด': 'มังคุดจากใต้ ราคากิโลกรัมละ 70 บาท',
    'ลำไย': 'ลำไยนอกฤดู ราคากิโลกรัมละ 60 บาท',
    'ชมพู่': 'ชมพู่เมืองเพชร ราคากิโลกรัมละ 35 บาท',
    'มะละกอ': 'มะละกอสุกสำหรับส้มตำ ราคากิโลกรัมละ 20 บาท',
    'เงาะ': 'เงาะโรงเรียน ราคากิโลกรัมละ 45 บาท',
    'แคนตาลูป': 'แคนตาลูปเนื้อแน่น ราคากิโลกรัมละ 30 บาท',
    'ขนุน': 'ขนุนหวานกรอบ ราคากิโลกรัมละ 35 บาท',
    'สตรอว์เบอร์รี': 'สตรอว์เบอร์รีจากเชียงใหม่ ราคากล่องละ 60 บาท',
    'บลูเบอร์รี': 'บลูเบอร์รีนำเข้า ราคากล่องละ 90 บาท',
    'มะเฟือง': 'มะเฟืองอินทรีย์ ราคากิโลกรัมละ 40 บาท',
    'มะพร้าว': 'มะพร้าวน้ำหอม ราคาลูกละ 30 บาท',
    'ลูกพลับ': 'ลูกพลับจากเกาหลี ราคาผลละ 50 บาท',
    'กีวี': 'กีวีนิวซีแลนด์ ราคาลูกละ 20 บาท',
    'แตงไทย': 'แตงไทยหอม ราคากิโลกรัมละ 25 บาท',
    'แอปริคอต': 'แอปริคอตสดนำเข้า ราคากล่องละ 100 บาท'
}

def show_product_info(name):
    info = product_data.get(name, 'ไม่พบข้อมูลสินค้า')
    messagebox.showinfo('ข้อมูลสินค้า', info)

# สร้างปุ่มสินค้า
product_buttons = {}
row = 0
col = 0
for product in product_data:
    btn = ttk.Button(frame, text=product, command=lambda p=product: show_product_info(p))
    btn.grid(row=row, column=col, padx=10, pady=10, ipadx=15, ipady=10)
    product_buttons[product] = btn

    col += 1
    if col == 4:
        col = 0
        row += 1

GUI.mainloop()
