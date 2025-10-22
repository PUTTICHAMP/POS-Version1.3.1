from tkinter import *
from tkinter import ttk, messagebox


gui = Tk()
gui.geometry('600x400')
gui.title('ร้านขายอะไร')


# --- ตัวแปร ---
v_title = StringVar()
v_price = StringVar()
v_quantity = StringVar()
v_result = StringVar()


# --- ฟังก์ชันสำหรับปุ่มผลไม้ ---
def product(t, p):
    v_title.set(t)
    v_price.set(str(p))
    v_quantity.set('1')  # ค่าเริ่มต้นจำนวน = 1


# --- ฟังก์ชันคำนวณ ---
def Calculate():
    try:
        title = v_title.get()
        price = float(v_price.get())
        quantity = float(v_quantity.get())
        total = price * quantity
        result = f'สินค้า: {title} | ราคา: {price:,.2f} | จำนวน: {quantity:.0f} | รวม: {total:,.2f} บาท'
        v_result.set(result)
    except:
        messagebox.showerror("Error", "กรุณากรอกตัวเลขในช่อง 'ราคา' และ 'จำนวน' ให้ถูกต้อง")


# --- Frame สำหรับปุ่มผลไม้ ---
F1 = Frame(gui)
F1.place(x=20, y=20)


Label(F1, text='ขายผลไม้', font=(None, 20)).grid(row=0, column=0, columnspan=3)


B1 = ttk.Button(F1, text='Apple', command=lambda: product('Apple', 100))
B1.grid(row=1, column=0, ipadx=10, ipady=20, padx=5)


B2 = ttk.Button(F1, text='Banana', command=lambda: product('Banana', 20))
B2.grid(row=1, column=1, ipadx=10, ipady=20, padx=5)


B3 = ttk.Button(F1, text='Mango', command=lambda: product('Mango', 30))
B3.grid(row=1, column=2, ipadx=10, ipady=20, padx=5)


# --- Frame สำหรับกรอกข้อมูล ---
F2 = Frame(gui)
F2.place(x=350, y=20)


Label(F2, text='สินค้า', font=(None, 14)).pack(anchor='w')
E1 = ttk.Entry(F2, textvariable=v_title)
E1.pack()


Label(F2, text='ราคา', font=(None, 14)).pack(anchor='w')
E2 = ttk.Entry(F2, textvariable=v_price)
E2.pack()


Label(F2, text='จำนวน', font=(None, 14)).pack(anchor='w')
E3 = ttk.Entry(F2, textvariable=v_quantity)
E3.pack()


BC1 = ttk.Button(F2, text='คำนวณ', command=Calculate)
BC1.pack(pady=20, ipady=10, ipadx=10)


# --- แสดงผลลัพธ์ ---
R1 = Label(gui, textvariable=v_result, font=(None, 14), fg='blue')
R1.place(x=20, y=300)


gui.mainloop()