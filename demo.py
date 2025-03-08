import PATK
import tkinter as tk

demo = tk.Tk()
demo.title("test PATK model")
edit = PATK.EditText(demo)
edit.pack(fill=tk.BOTH, expand=True)


demo.mainloop()

