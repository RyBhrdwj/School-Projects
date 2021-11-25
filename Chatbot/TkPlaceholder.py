import tkinter as tk


class Placeholder(tk.Entry):
    def __init__(self, parent, placeholder, highlight, **kwargs):
        tk.Entry.__init__(self, parent)
        self.placeholder = placeholder
        self.configure(**kwargs)
        self.insert(0, self.placeholder)

        self.bind('<FocusIn>', lambda x: self.delete(0, tk.END) if self.get().strip() == self.placeholder
                  else self.insert(0, ''))
        self.bind('<FocusOut>', lambda x: self.insert(0, self.placeholder) if self.get().strip() == '' else None)
        self.bind("<Enter>", lambda x: self.config(bg=highlight))
        self.bind("<Leave>", lambda x: self.config(bg=kwargs['bg']))

    def __repr__(self):
        return "placeholder"
