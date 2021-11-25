# RICKY BHARDWAJ : XII A : CS PROJECT
# BOARD R.NO : 26613930

# PRECAUTION : Front end code is messy due to lack of time for deadline (started working on UI late),
# and due to constant errors (mainly related to sql and some due to tkinter limitations).

import TkPlaceholder
import tkinter.messagebox as mb
import mysql.connector as sql
import tkinter as tk
import datetime
import random
import pickle
import json
import os

# ================================================== BACK END ========================================================== #

'''
TODO
STATUS -- DONE

Login Function
Signup Function
Retrieve Mails
Send Mail
UI will be in a separate tkinter window.

SQL USER TABLE
From, To, Subject, Text, Attachments, Datetime '''

# global variables
user_id = ''
table = ''


def connect_to_sql(statements, fetchall=True, commit=False):
    """To do all sql related stuff through this function."""
    # TODO : Connect, Run the query, Close the connection and return data.

    with open("mail.json", "r") as file:
        details = json.load(file)["sql"]

    connection = sql.connect(host="localhost", user=details[0], passwd=details[1], database="neomail")
    cur = connection.cursor()

    if type(statements) == str:
        cur.execute(statements)  # Form connection and execute the statement is there is only one.

    # Else multiple statements are there in form of list, executes them in the order they're placed in the list.
    else:
        for statement in statements:
            cur.execute(statement, commit=commit)

    if commit:
        connection.commit()  # Commit actions if required.
    try:
        data = cur.fetchall() if fetchall else cur.fetchone()
    except sql.errors.InterfaceError:
        data = None
    cur.close()
    connection.close()
    return data  # Fetch the data, Close the cursor and connection and Return the data.


def generate_id():
    """Generates a new unique id for new user"""
    id_s = connect_to_sql("select unique_id from user_data")
    while True:
        new_id = random.randint(100000, 999999)
        if new_id not in id_s:
            return new_id


def signup(username, password, first_name, last_name, email):
    """To save all the details in the sql and make an account successfully"""
    unique_id = str(generate_id())
    user_data = f"insert into user_data values ('{username}', '{password}', " \
                f"'{first_name}', '{last_name}', '{email}', {unique_id})"
    connect_to_sql(user_data, commit=True)
    user_table = f"CREATE TABLE `{email}` (mail_id VARCHAR(255) PRIMARY KEY, from_mail VARCHAR(255), to_mail VARCHAR(" \
                 f"255), subject VARCHAR(255), message TEXT, date DATETIME) "
    connect_to_sql(user_table, commit=True)
    return None


def login(username, password):
    global user_id
    """To check if the username/mail and password entered are correct."""
    query = "select username, email, password, unique_id from user_data"
    data_set = connect_to_sql(query)
    for data in data_set:
        if username == data[1]:
            if password == data[2]:
                user_id = data[3]
                return True
            else:
                return "Email and Password don't match."
    else:
        return f"No Email named {username} is found."


def save_quick_login(username, password):
    """Saves binary file for any user stamps containing their information to keep them logged in."""
    with open('login.dat', 'wb') as file:
        pickle.dump([username, password], file)
    return None


def quick_login():
    """Checks binary file for any user stamps containing their information to keep them logged in."""
    if os.path.isfile('login.dat'):
        with open('login.dat', 'rb') as file:
            details = pickle.load(file)
        if login(*details):
            return details[0]
        else:
            return False
    else:
        return False


def logout():
    global message, user_id, table
    """"To exit out of the main program back to the login page, and also clear the specific account from binary file
    so that they aren't logged in next time the program is opened."""
    answer = mb.askyesno(title="Log Out", message="Are you sure you want to log out ?")
    if answer is True:
        if os.path.isfile('login.dat'):
            os.remove('login.dat')
            message = ""
            user_id = ""
            table = ""
        return login_page()


# ---------------------------------------- Mail related functions ------------------------------------------------------


def fetch_mails(username):
    """To fetch preview(sender, subject) of mail to show in menu."""
    statement = f"SELECT from_mail, subject, date FROM {username}"
    preview = connect_to_sql(statement)
    return preview

def send_mail(mail_id, receiver, subject, content):
    """To send a mail to the receiver(s)"""
    dt_format = '%Y-%m-%d %H:%M:%S'
    date = datetime.datetime.now().strftime(dt_format)
    sender = connect_to_sql(f"select email from user_data where unique_id='{user_id}'")[0][0]
    query = f"insert into `{receiver}` values ('{mail_id}', '{sender}', '{receiver}', '{subject}', '{content}', '{date}') "
    connect_to_sql(query, commit=True)
    if receiver != sender:
        query2 = f"insert into `{sender}` values ('{mail_id}', '{sender}', '{receiver}', '{subject}', '{content}', '{date}') "
        connect_to_sql(query2, commit=True)
    return True


# ==================================================== FRONT END ======================================================= #


def sign_up_page():
    """Creates the signup page."""
    global entry_config, win, login_frame, sign_up, image, signup_frame, signup_error, image, logo

    login_frame.destroy()
    sign_up_frame = tk.Frame(win, bg='#ffffff', height=768, width=1366)
    sign_up_frame.pack()
    sign_up_frame.pack_propagate(False)

    neomail = tk.Label(sign_up_frame, image=logo, bg='#ffffff')
    neomail.image = logo
    neomail.place(x=600, y=25)

    tk.Label(bg='#ffffff', text="@neomail.com", font=('calibri', 18)).place(x=700, y=225)
    TkPlaceholder.Placeholder(sign_up_frame, 'Mail', **entry_config).place(x=450, y=225)
    TkPlaceholder.Placeholder(sign_up_frame, 'Last Name', **entry_config).place(x=750, y=150)
    TkPlaceholder.Placeholder(sign_up_frame, 'First Name', **entry_config).place(x=450, y=150)
    TkPlaceholder.Placeholder(sign_up_frame, 'Confirm Password', **entry_config).place(x=750, y=300)
    TkPlaceholder.Placeholder(sign_up_frame, 'Password', **entry_config).place(x=450, y=300)

    signup_error = tk.Label(sign_up_frame, text='', font=('calibri', 18), fg='red', bg='#ffffff')
    signup_error.place(x=450, y=375)

    f = tk.Button(sign_up_frame, image=sign_up, command=check_signup, relief='flat', bg='white', borderwidth=0)
    f.image = sign_up
    f.place(x=600, y=450)

    tk.Label(sign_up_frame, bg='#ffffff', text="Already have an account ? ", font=('blogger sans', 18)) \
        .place(x=450, y=550)
    s = tk.Button(sign_up_frame, relief='flat', borderwidth=0, image=image, command=login_page)
    s.image = image
    s.place(x=750, y=550)


def check_signup():
    global signup_frame, signup_error
    account_details = []
    for frame in win.pack_slaves():
        for widget in frame.place_slaves():
            if 'placeholder' in str(widget):
                account_details.append(widget.get())

    placeholders = ['Password', 'Confirm Password', 'First Name', 'Last Name', 'Mail']
    if account_details != placeholders:
        empty_fields = list(set(account_details).intersection(set(placeholders)))
        if len(empty_fields) > 0:
            error = f"Please enter the data in all the fields"
            signup_error.config(text=error)
            signup_error.config(text="First Name, Last Name and Mail can't contain '@'")
        else:
            for i in account_details:
                if '@' in i:
                    signup_error.config(text="First Name, Last Name, Email can't contain '@'")
                    return
            else:
                signup_error.config(text='')
                mails = connect_to_sql('select email from user_data')
                user_data = [y[0] for y in mails]
                account_details[4] += "@neomail.com"
                for account in user_data:
                    if account_details[4] == account:
                        signup_error.config(text=f'Mail ID {account_details[4]} has already been taken.')
                        break
                else:
                    password = account_details[1]
                    if account_details[0] == account_details[1]:
                        if len(password) > 7 and password.isalnum():
                            signup_error.config(text='')
                            account_details[0] = f"{account_details[2]} {account_details[3]}"
                            signup(*account_details)
                            mb.showinfo(title="Account creation successful",
                                        message=f"Your account {account_details[0]} has been successfully created.")
                            login_page()
                        else:
                            signup_error.config(text='Password must be 8 characters long and should contain a number.')
                    else:
                        signup_error.config(text="Password doesn't match confirm password")
    else:
        signup_error.config(text='Please enter all the fields')


def login_page():
    global login_frame, error_label, login, log_in_var, win, entry_config, sign_up, image, entry_config
    for child in win.pack_slaves():
        child.destroy()
    login_frame = tk.Frame(win, bg='#ffffff', height=768, width=1366)
    login_frame.pack()
    login_frame.pack_propagate(False)

    neomail2 = tk.Label(login_frame, bg='#ffffff', image=logo)
    neomail2.image = logo
    neomail2.place(x=600, y=25)

    TkPlaceholder.Placeholder(login_frame, 'password', **entry_config).place(x=600, y=200)
    TkPlaceholder.Placeholder(login_frame, 'mail', **entry_config).place(x=600, y=150)
    log_in_var = tk.IntVar()
    login_ = tk.Checkbutton(login_frame, bg='white', text="Remember me", font=('calibri', 14), variable=log_in_var)
    login_.place(x=600, y=250)

    error_label = tk.Label(login_frame, font=('calibri', 18), text="", bg='#ffffff', fg='red')
    error_label.place(x=580, y=350)

    tk.Label(login_frame, bg='#ffffff', text="Don't have an account ? ", font=('blogger sans', 18)).place(x=600, y=450)
    sign_up = tk.PhotoImage(file='sign_up.png')
    s = tk.Button(login_frame, relief='flat', borderwidth=0, bg='white', image=sign_up, command=sign_up_page)
    s.image = sign_up
    s.place(x=620, y=500)

    image = tk.PhotoImage(file='sign_in.png')
    a = tk.Button(login_frame, image=image, command=check_login, relief='flat', borderwidth=0)
    a.image = image
    a.place(x=620, y=290)


def check_login():
    global login_frame, error_label, login, log_in_var
    login_details = []
    for widget in login_frame.place_slaves():
        if 'placeholder' in str(widget):
            login_details.append(widget.get())
    _message_ = login(*login_details)
    if _message_ is not True:
        if login_details == ['username', 'password']:
            error_label.config(text='Please enter the login details.')
        elif login_details[0] == 'username':
            error_label.config(text='Please enter your username or mail id.')
        elif login_details[1] == 'password':
            error_label.config(text='Please enter your password.')
        else:
            error_label.config(text=str(_message_))
    else:
        if log_in_var.get() == 1:
            save_quick_login(login_details[0], login_details[1])
        home(login_details[0])


def home(username):
    global win, logo, entry_config_2, mail_frame_2, primary_bg_color, secondary_bg_color, fg_color, table, \
        side_menu_config

    table = connect_to_sql(f"select email from user_data where unique_id='{user_id}'")[0][0]
    win.bind("<Button-1>", show_mail)
    for frame in win.pack_slaves():
        frame.destroy()

    homepage = tk.Frame(win, bg=primary_bg_color, width=1366, height=786)
    homepage.pack_propagate(False)
    homepage.pack()
    neomail_logo = tk.Label(homepage, bg=primary_bg_color, image=logo)
    neomail_logo.logo = logo
    neomail_logo.place(x=0, y=-40)

    if '@' in username:
        mail = username
        username = connect_to_sql(f"select username from user_data where email='{username}'")
        tk.Label(homepage, font=('blogger sans', 20, 'bold'), bg=primary_bg_color,
                 text=f"Welcome {username[0][0]}", fg=fg_color).place(x=300, y=25)
    else:
        mail = connect_to_sql(f"select email from user_data where username='{username}'")
        tk.Label(homepage, font=('blogger sans', 20, 'bold'), bg=primary_bg_color,
                 text=f"Welcome {username}").place(x=300, y=25)

    side_menu = tk.Label(homepage, bg=secondary_bg_color)
    side_menu.place(x=0, y=130)

    menu_button_config = {'bg': primary_bg_color, 'width': 20, 'height': 1,
                          'font': ('calibri', 20, 'bold'), 'relief': 'flat', 'borderwidth': 0,
                          'activebackground': secondary_bg_color}

    buttons = [(mail, None), ('Compose', compose_email), ('All', show_all_mails), ('Sent', show_sent_mails),
               ('Received', show_received_mails), ('Settings', show_settings),
               ('Log Out', logout)]

    for x in range(len(buttons)):
        tk.Button(side_menu, **menu_button_config, text=buttons[x][0], command=buttons[x][1], fg=fg_color).pack(pady=1)

    win.bind("<Enter>", lambda z: z.widget.config(bg=highlight)
    if 'button' in str(z.widget) and z.widget.master == side_menu else None)
    win.bind("<Leave>", lambda z: z.widget.config(bg=menu_button_config['bg'])
    if 'button' in str(z.widget) and z.widget.master == side_menu else None)

    mail_frame = tk.Frame(homepage, width=1060, height=580, bg=secondary_bg_color)
    mail_frame.place(x=295, y=130)
    mail_frame_2 = tk.Frame(mail_frame, bg=primary_bg_color, height=570, width=1050)
    mail_frame_2.pack(fill=tk.Y, pady=5, padx=5)
    mail_frame_2.pack_propagate(False)


def clean_frame(frame):
    for object_ in frame.winfo_children():
        object_.destroy()


def compose_email():
    """Creates the UI to write a mail."""
    global mail_frame_2, primary_bg_color, secondary_bg_color, fg_color, entry_config_2, text
    clean_frame(mail_frame_2)
    variables = ['To', "Subject"]
    for i in range(len(variables)):
        width = 25 if i == 0 else 88
        TkPlaceholder.Placeholder(mail_frame_2, placeholder=variables[i], **entry_config_2,
                                  width=width).pack(side='top', anchor='w', pady=1, padx=2)
    tk.Label(mail_frame_2, text="@neomail.com", bg=primary_bg_color, font=("calibri", 18),
             fg=fg_color).place(x=312, y=0)
    text = tk.Text(mail_frame_2, height=15, width=87, bg=secondary_bg_color, font=('calibri', 18), borderwidth=0,
                   selectbackground='blue', fg=fg_color, highlightcolor=highlight, relief='flat')

    text.bind("<Enter>", lambda x: text.config(bg=highlight))
    text.bind("<Leave>", lambda x: text.config(bg=secondary_bg_color))
    text.bind("<FocusIn>", lambda x: text.delete("1.0", tk.END)
    if text.get("1.0", tk.END).strip() == "Write here..." else None)
    text.pack(side='top', padx=2, pady=1)
    text.pack_propagate(False)

    a = tk.Scrollbar(text)
    a.pack(side='right', fill=tk.Y)
    text.config(yscrollcommand=a)
    a.config(command=text.yview)

    text.insert("1.0", "Write here...")
    tk.Button(mail_frame_2, relief='flat', text='Send', font=('calibri', 16, 'bold'), bg=primary_bg_color,
              fg=fg_color, borderwidth=0, command=confirm_mail_info).pack(side='left', pady=4, padx=5)


def confirm_mail_info():
    """Checks mail info and sends it to the receiver."""
    global text, mail_frame_2

    info = []
    message_ = ''
    for widget in mail_frame_2.pack_slaves():
        if 'placeholder' in str(widget):
            info.append(widget.get())
        elif 'text' in str(widget):
            message_ = widget.get("1.0", tk.END)

    address_list = [x[0] for x in connect_to_sql("select email from user_data")]

    if info[0] == '' or info[0].split('@')[0] + '@neomail.com' not in address_list:
        mb.showerror("Mail not sent.", message="Invalid Neomail Address. Please write a correct neomail address.")
    else:
        info[0] = info[0].split('@')[0] + '@neomail.com'
        if info[1].strip() == '' or info[1] == 'Subject':
            info[1] = "<No Subject>"
        if message_.strip() == '' or message_.strip('\n') == 'Write here...':
            message_ = "<No Message>"
        number = connect_to_sql(f"select count(mail_id) from `{info[0]}`")[0][0]
        receiver_id = connect_to_sql(f"select unique_id from user_data where email='{info[0]}'")[0][0]
        mail_id = f'{user_id}{receiver_id}{number + 1}'
        send_mail(mail_id, info[0], info[1], content=message_)
        receiver = connect_to_sql(f"select email from user_data where unique_id='{receiver_id}'")[0][0]
        mb.showinfo("Mail Sent", f"Your mail to {receiver} has been successfully sent.")


def show_all_mails():
    global mail_frame_2, primary_bg_color, fg_color, secondary_bg_color
    clean_frame(mail_frame_2)
    table = connect_to_sql(f"select email from user_data where unique_id='{user_id}'")[0][0]
    previews = connect_to_sql(f"select mail_id, subject, from_mail, date from `{table}`")

    mail_canvas = tk.Canvas(mail_frame_2, bg=primary_bg_color)
    email_frame = tk.Frame(mail_canvas, bg=primary_bg_color)
    scrollbar = tk.Scrollbar(mail_canvas, orient="vertical", command=mail_canvas.yview, bg='black')
    mail_canvas.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    mail_canvas.create_window((0, 0), window=email_frame)
    email_frame.pack_propagate(False)

    mail_canvas.pack(fill=tk.BOTH, expand=1)
    email_frame.pack(fill=tk.BOTH, expand=1)

    email_frame_2 = tk.Frame(email_frame, bg=secondary_bg_color, name='mail_frame')
    email_frame_2.pack(fill=tk.BOTH, expand=1)

    for preview in previews:
        username = connect_to_sql(f"select username from user_data where email='{preview[2]}'")[0][0]
        preview = list(preview)
        preview[2] = username
        add_preview(email_frame_2, preview)


def show_sent_mails():
    global table
    find_mails(f"select mail_id, subject, from_mail, date from `{table}` where from_mail='{table}'")


def show_received_mails():
    find_mails(f"select mail_id, subject, from_mail, date from `{table}` where to_mail='{table}'")


def find_mails(statement=None):
    global mail_frame_2, primary_bg_color, fg_color, secondary_bg_color, table
    clean_frame(mail_frame_2)

    mail_canvas = tk.Canvas(mail_frame_2, bg=primary_bg_color)
    email_frame = tk.Frame(mail_canvas, bg=primary_bg_color)
    scrollbar = tk.Scrollbar(mail_canvas, orient="vertical", command=mail_canvas.yview, bg='black')
    mail_canvas.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    mail_canvas.create_window((0, 0), window=email_frame)
    email_frame.pack_propagate(False)

    mail_canvas.pack(fill=tk.BOTH, expand=1)
    email_frame.pack(fill=tk.BOTH, expand=1)

    email_frame_2 = tk.Frame(email_frame, bg=secondary_bg_color, name='mail_frame')
    email_frame_2.pack(fill=tk.BOTH, expand=1)

    previews = connect_to_sql(statement)

    for preview in previews:
        username = connect_to_sql(f"select username from user_data where email='{preview[2]}'")[0][0]
        preview = list(preview)
        preview[2] = username
        add_preview(email_frame_2, preview)


def add_preview(frame, preview):
    global primary_bg_color, secondary_bg_color, fg_color, highlight

    preview_button_config = {'bg': primary_bg_color, 'width': 20, 'height': 1,
                             'font': ('calibri', 15, 'bold'), 'relief': 'flat', 'borderwidth': 0,
                             'activebackground': secondary_bg_color}

    dialogue = f"{preview[2]}        {preview[1].upper()}"

    preview_button_config['fg'] = fg_color
    a = tk.Button(frame, **preview_button_config, text=dialogue, anchor='w',
                  name=preview[0])
    a.pack(fill=tk.X, pady=1)


def show_mail(event=None):
    """Shows the full mail when you click on it."""
    global primary_bg_color, secondary_bg_color, fg_color, entry_config, highlight, win
    value = str(event.widget).split('.')[-1]
    if value.isnumeric() and len(value) > 12:
        table_name = connect_to_sql(f"select email from user_data where unique_id='{user_id}'")[0][0]
        mail = connect_to_sql(f"select * from `{table_name}` where mail_id='{value}'")[0][1:]
        from_, to_, subject, mssg, date = mail

        mailbox = tk.Toplevel(win, width=960, height=480, bg=secondary_bg_color)
        mailbox.title(subject)
        mailbox.pack_propagate(False)

        tk.Label(mailbox, text=from_, bg=primary_bg_color,
                 fg=fg_color, font=('calibri', 18, 'bold'), width=74, anchor=tk.W).place(x=0, y=0)
        tk.Label(mailbox, text=date, bg=primary_bg_color,
                 fg=fg_color, font=('calibri', 18, 'bold'), width=74, anchor=tk.W).place(x=0, y=36)
        tk.Label(mailbox, text=subject, bg=primary_bg_color,
                 fg=fg_color, font=('calibri', 18, 'bold'), width=74, anchor=tk.W).place(x=0, y=72)
        text_ = tk.Text(mailbox, height=16, width=96, bg=primary_bg_color, font=('calibri', 14), borderwidth=0,
                        selectbackground='blue', fg=fg_color, highlightcolor=highlight, relief='flat')
        text_.place(x=0, y=110)
        text_.insert("1.0", mssg)
        text_.config(state=tk.DISABLED)
        text_.pack_propagate(False)

        scrollbar = tk.Scrollbar(text_, orient="vertical", command=text_.yview)
        text_.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)


def show_settings():
    global mail_frame_2, primary_bg_color, fg_color, highlight, secondary_bg_color
    clean_frame(mail_frame_2)
    config_ = {'bg': secondary_bg_color, 'width': 20, 'height': 1,
               'font': ('calibri', 20, 'bold'), 'relief': 'flat', 'borderwidth': 0,
               'activebackground': highlight, 'fg': fg_color}
    tk.Label(mail_frame_2, text="No settings in this version.", bg=primary_bg_color, fg=fg_color).pack(pady=10)


def launch_app():
    """Creates the UI and manages global functions"""
    global win, logo, entry_config, primary_bg_color, secondary_bg_color, fg_color, entry_config_2, highlight

    win = tk.Tk()
    win.title("Neomail")
    win.config(bg='#ffffff')
    win.state('zoomed')
    logo = tk.PhotoImage(file='neomail.png')

    with open('mail.json', 'r') as file:
        file = json.load(file)['settings']
        mode = file['mode']
        settings = file[mode]
        primary_bg_color = settings['bg primary color']
        secondary_bg_color = settings['bg secondary color']
        highlight = settings['highlight']
        fg_color = settings['fg color']

    entry_config = {'highlight': '#c49cd9', 'bg': '#c1c8de', 'highlightcolor': 'yellow',
                    'highlightthickness': '3', 'relief': 'flat',
                    'font': ('calibri', 18), 'takefocus': True}

    entry_config_2 = {'highlight': highlight, 'bg': secondary_bg_color, 'highlightcolor': 'yellow',
                      'highlightthickness': '1', 'relief': 'flat',
                      'font': ('calibri', 18), 'takefocus': True, 'fg': fg_color}

    if quick_login() is not False:
        home(quick_login())
    else:
        login_page()
    win.mainloop()


def main_():
    info = {
        "sql": ["", ""],
        "settings": {
            "mode": "dark mode",
            "dark mode": {
                "bg primary color": "#1f1e1d",
                "bg secondary color": "#474542",
                "highlight": "#363432",
                "fg color": "#ffffff"
            }
        }
    }
    
    if not os.path.isfile("mail.json"):  # Creates color config files if they're not present.
        with open("mail.json", "w") as file:
            json.dump(info, file, indent=2)

    while True:  # Creates database, user_table if they don't exist.
        with open("mail.json", 'r') as file:
            db_info = json.load(file)["sql"]
        try:
            mydb = sql.connect(user=db_info[0], passwd=db_info[1], host="localhost")
        except BaseException:
            print("Either username or password for accessing sql is incorrect. \nPlease enter the details again.")
            username = str(input("Enter username : "))
            password = str(input("Enter password : "))
            with open("mail.json", 'w') as file:
                new_info = info
                new_info["sql"] = [username, password]
                json.dump(new_info, file, indent=2)
        else:
            cur = mydb.cursor()
            cur.execute("show databases")
            if not ("neomail",) in cur.fetchall():
                cur.execute("create database neomail")
                cur.close()
                mydb.close()

            if ("user_data",) not in connect_to_sql("show tables"):
                table_ = "CREATE TABLE user_data(username varchar(255), password varchar(255), FirstName varchar(255), LastName varchar(255), email varchar(255), unique_id varchar(255) PRIMARY KEY)"
                connect_to_sql(table_, commit=True)
            launch_app()
            break


if __name__ == '__main__':
    main_()
