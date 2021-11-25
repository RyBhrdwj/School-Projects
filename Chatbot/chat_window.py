from configparser import ConfigParser

from spammer import Spammer
import webbrowser as w
import pyautogui as p
import tkinter as tk
import random
import time
import csv
import os


class ChatGUI(tk.Tk):
    def __init__(self, messages=None):
        super().__init__()

        self.title("ChatBot v1.1")
        self.geometry('600x450')
        self.resizable(False, True)

        if not messages:
            self.messages = []
        else:
            self.messages = messages

        self.new_messages = []

        # =========================================Code for Menu bar================================== #

        self.menubar = tk.Menu(self)

        self.tools_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label='Tools', menu=self.tools_menu)
        self.tools_menu.add_command(label="New", command=self.destroy)
        self.tools_menu.add_command(label="Clear Chat", command=self.clear_chat)

        self.menubar.add_command(label='Dark Mode', command=self.toggle_mode)

        # self.customize_menu = tk.Menu(self.menubar, tearoff=0)
        # self.menubar.add_cascade(label="Customize", menu=self.customize_menu)

        self.help_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Help", menu=self.help_menu)

        self.config(menu=self.menubar)

        # =====================================Code for Main frame==================================== #

        self.message_canvas = tk.Canvas(self, bg='white')  # 1 - main frame(containing messages)
        self.message_frame = tk.Frame(self.message_canvas, bg='white')  # from config -- bg=chat_color

        def get_time():
            a, month, date, hour, minute, second, g, h, i = time.localtime()
            months = {1: "January", 2: "February", 3: "March", 4: "April", 5: "May", 6: "June", 7: "July",
                      8: "August", 9: "September", 10: "October", 11: "November", 12: "December"}
            c_time = f'{date} {months[month]}, {hour}:{minute}'
            return c_time

        self.message_frame_2 = tk.Label(self.message_frame, bg='#DFEFFF', width=82, height=0,
                                        font=("Arial", 9), text=get_time())
        self.message_frame_2.pack(anchor='n')
        self.msg_box_frame = tk.Frame(self, height=30, width=600, bg='#bfb5f0')  # 2 - frame containing message box

        self.scrollbar = tk.Scrollbar(self.message_canvas, orient="vertical", command=self.message_canvas.yview)
        self.message_canvas.configure(yscrollcommand=self.scrollbar.set)
        self.message_create = tk.Text(self.msg_box_frame, height=1, width=57, bg="#b4b5f0", fg="black",
                                      font=("Times", 15), relief='flat')

        self.message_canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.message_canvas.create_window((0, 0), window=self.message_frame)
        self.message_create.pack(side=tk.LEFT)
        self.msg_box_frame.pack_propagate(False)
        self.msg_box_frame.pack(side=tk.LEFT)
        self.message_create.focus_set()

        self.image = tk.PhotoImage(file='send_btn.png')
        self.button = tk.Button(self.msg_box_frame, bg='#b4b5f0', image=self.image, height=25, width=25,
                                relief='flat', command=self.add_user_message)
        self.button.pack(side=tk.LEFT)

        self.bind("<Return>", self.add_user_message)
        self.bind("<Configure>", self.on_frame_configure)

        self.retrieve_messages()

    def toggle_mode(self):
        pass

    def on_frame_configure(self, event=None):
        self.message_canvas.configure(scrollregion=self.message_canvas.bbox("all"))

    def clear_chat(self):
        with open('messages.csv', 'w') as chat:
            chat.write('')
        for widget in self.message_frame.winfo_children():
            widget.pack_forget()
        self.message_frame_2.pack()

    def add_user_message(self, event=None):
        """Adds user message to the frame."""

        message_text = self.message_create.get(1.0, tk.END).strip()  # Takes all the input in message box.
        if len(message_text) > 0:
            print(message_text)
            self.message_create.delete(1.0, tk.END)  # Empties the message box.

            tk.Label(self.message_frame, text=message_text, bg='pink', font=("Helvetica", 12)).pack(anchor='ne')
            tk.Label(self.message_frame, height=1, bg='white').pack(anchor='ne')

            self.new_messages.append(message_text)  # Adds user message to a list so that bot can access it.

            # code to add these messages to csv file

            user = 'user'
            user_message = user, message_text

            with open('messages.csv', 'a', newline='') as messages:
                writer = csv.writer(messages)
                writer.writerow(user_message)

            self.add_bot_message()

    def add_bot_message(self, event=None):
        """Calls another function to get the reply and adds that reply to the frame."""

        self.generate_reply()  # Runs a function which generates a reply.
        tk.Label(self.message_frame, text=message, bg='blue', fg='white', pady=2, font=("Helvetica", 12))\
            .pack(anchor='nw')

        # code to add these messages to csv file

        user = 'bot'
        user_message = user, message

        with open('messages.csv', 'a', newline='') as messages:
            writer = csv.writer(messages)
            writer.writerow(user_message)

    message = "I don't know."

    def retrieve_user_message(self, message_text=None):
        """Gets the old user messages and adds them to the frame."""
        tk.Label(self.message_frame, text=message_text, bg='pink', font=("Helvetica", 12)).pack(anchor='ne')
        tk.Label(self.message_frame, height=1, bg='white').pack(anchor='ne')

    def retrieve_bot_message(self, message_text=None):
        """Gets the old bot messages and adds them to the frame."""
        tk.Label(self.message_frame, text=message_text, bg='blue', fg='white', pady=2, font=("Helvetica", 12))\
            .pack(anchor='nw')

    def retrieve_messages(self, event=None):
        """Access the old messages, checks if they belong to bot or user and
         run their respective functions to add those messages to frame."""

        z = {'user': self.retrieve_user_message, 'bot': self.retrieve_bot_message}

        with open('messages.csv', 'r', newline='') as messages:
            reader = csv.reader(messages)
            for line in reader:
                z[line[0]](message_text=line[1])

    # ============================= Code for Bot ================================================= #

    def generate_reply(self, event=None):
        """Contains a lot of nested functions and pre-defined keywords.
        Checks for any specific keyword in user message and if it matches with pre-defined keywords,
        Then the function returns the nested function associated with that keyword."""

        global message
        user_query = self.new_messages[-1].lower()  # gets the latest user message.

        with open('replies.txt', 'r') as f:

            for line in f:
                a = line.rstrip('\n').lstrip().split(',')

                for keyword in a[1:]:  # 

                    if keyword in user_query:
                        keyword_type = a[0]
                        break

        def greet():
            """Generates a random greeting."""
            greets = ['Hey', 'Hello', 'Aloha', 'Namaste', 'Hii :D']
            greets_2 = ['', ', How can I help you ?', ', Need some help ?']

            text = f"{random.choice(greets)}{random.choice(greets_2)}"
            return text

        def open_website():
            website = user_query.split('open ' and '#')[1]
            basic_websites = {'google': 'https://www.google.com/', 'facebook': 'https://www.facebook.com/',
                              'instagram': 'https://www.instagram.com/', 'quora': 'https://www.quora.com/',
                              'youtube': 'https://www.youtube.com/', 'wikipedia': 'https://www.wikipedia.org/',
                              'yahoo': 'https://in.yahoo.com/', 'reddit': 'https://www.reddit.com/',
                              'amazon': 'https://www.amazon.in/', 'flipkart': 'https://www.flipkart.com/',
                              'vedantu': 'https://www.vedantu.com/', 'cbse': 'http://www.cbse.nic.in/',
                              'whatsapp': 'https://web.whatsapp.com/'}

            if website in basic_websites:
                w.open(basic_websites[website])

            else:
                w.open(f'https://www.google.com/search?q={website}')

            text = f'opening {website}'

            return text

        def google():
            w.open(f'https://www.google.com/search?q={user_query}')
            return 'Hope you got what you were looking for :D'

        def open_program():
            program = user_query.lstrip('launch ' and 'start ' and '@')
            text = f'starting {program}'

            p.sleep(1)
            p.press('winleft')
            p.sleep(1)
            p.typewrite(program)
            p.sleep(3)
            p.press('enter')

            return text  

        def spam_app():
            Spammer(self)

        replies = {'greetings': greet, 'websites': open_website, 'programs': open_program,
                   'spamming': spam_app, 'google': google}
        message = replies[keyword_type]()

        return message  # returns the inner function


if __name__ == '__main__':

    config = ConfigParser()  # Default Settings

    config['UI'] = {
        'chat_bg': '#ffffff',
        'message_box_bg': '#ffffff',
        'send_btn': 'send_btn.png'
    }

    categories = """questions,how are you,what is your favourite,do you
greetings,hey,hi,hello
spamming,spam
programs,launch,start,@
websites,open,#
google,why,how,search
remainders,save a day,save an occasion,save an event
    """

    if not os.path.isfile("bot_settings.ini"):
        with open('bot_settings.ini', 'w') as f:
            config.write(f)

    if not os.path.isfile("replies.txt"):
        with open('replies.txt', 'w') as f:
            f.write(categories)

    if not os.path.isfile("messages.csv"):
        with open('messages.csv', 'w'):
            pass

bot = ChatGUI()
bot.mainloop()
