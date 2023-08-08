import sqlite3

from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedWidget, QLineEdit

from data.uiSM import Ui_SafeMoney
from data.uiSMsignup import Ui_SafeMoneySignup
from data.uiSMreg import Ui_SafeMoneyreg
from data.uiSMlogin import Ui_SafeMoneyLogin


class SafeMoneyApp(QMainWindow):
    def __init__(self):
        super().__init__()
        global sizes
        sizes = {}
        self.stack = QStackedWidget(self)
        self.reg_form = Ui_SafeMoneyreg()
        self.login_form = Ui_SafeMoneyLogin()
        self.signup_form = Ui_SafeMoneySignup()
        self.main_form = Ui_SafeMoney()
        sizes[self.reg_form] = (self.reg_form.width(), self.reg_form.height())
        sizes[self.login_form] = (self.login_form.width(), self.login_form.height())
        sizes[self.signup_form] = (self.signup_form.width(), self.signup_form.height())
        sizes[self.main_form] = (self.main_form.width(), self.main_form.height())
        self.stack.addWidget(self.reg_form)
        self.stack.addWidget(self.main_form)
        self.stack.addWidget(self.signup_form)
        self.stack.addWidget(self.login_form)
        self.resize(self.reg_form.width(), self.reg_form.height())

        self.reg_form.login_button.clicked.connect(lambda: self.showNewForm(self.login_form, sizes[self.login_form][0],sizes[self.login_form][1]))
        self.login_form.login_button.clicked.connect(self.loginUser)
        self.login_form.back_button.clicked.connect(lambda: self.showNewForm(self.reg_form, sizes[self.reg_form][0],sizes[self.reg_form][1]))
        self.reg_form.signup_button.clicked.connect(lambda: self.showNewForm(self.signup_form, sizes[self.signup_form][0],sizes[self.signup_form][1]))
        self.signup_form.signup_button.clicked.connect(self.signUpUser)
        self.signup_form.back_button.clicked.connect(lambda: self.showNewForm(self.reg_form, sizes[self.reg_form][0],sizes[self.reg_form][1]))

        self.signup_form.name.returnPressed.connect(self.changeCursor)
        self.signup_form.login.returnPressed.connect(self.changeCursor)
        self.signup_form.password.returnPressed.connect(self.changeCursor)
        self.signup_form.repeatpassword.returnPressed.connect(self.changeCursor)
        self.signup_form.balance.returnPressed.connect(self.changeCursor)

        self.login_form.login.returnPressed.connect(self.changeCursor)
        self.login_form.password.returnPressed.connect(self.changeCursor)

        self.setCentralWidget(self.stack)
        self.setWindowTitle(self.reg_form.windowTitle())

    def showNewForm(self, form, w, h):
        self.setFixedSize(w, h)
        self.stack.setCurrentWidget(form)
        current_LineEdit = form.findChild(QLineEdit)
        if current_LineEdit is not None:
            current_LineEdit.setFocus()
        self.setWindowTitle(form.windowTitle())

    def changeCursor(self):
        lineEdits = self.signup_form.findChildren(QLineEdit) if self.signup_form.isVisible() \
            else self.login_form.findChildren(QLineEdit)
        current_line_edit = self.sender()
        current_index = lineEdits.index(current_line_edit)
        if (current_index + 1) != len(lineEdits):
            lineEdits[current_index + 1].setFocus()
        else:
            if self.signup_form.isVisible():
                self.signUpUser()
            else:
                self.loginUser()

    def loginUser(self):
        login = self.login_form.login.text()
        password = self.login_form.password.text()

        if not login:
            self.login_form.status_label.setText("Error : Enter your login")
            self.login_form.login.setFocus()
            return
        if not password:
            self.login_form.status_label.setText("Error : Enter your password")
            self.login_form.password.setFocus()
            return

        conn = sqlite3.connect('moneyBase.db')
        cursor = conn.cursor()
        userData = cursor.execute('SELECT * FROM users WHERE login = ?', (login,)).fetchone()
        print(userData)
        if userData is None:
            self.login_form.status_label.setText("Error : There is no user with this login")
            self.login_form.login.setFocus()
            return
        if password != userData[3]:
            self.login_form.status_label.setText("Error : Incorrect password")
            self.login_form.password.setFocus()
            return
        conn.close()
        self.showNewForm(self.main_form, sizes[self.main_form][0], sizes[self.main_form][1])

    def signUpUser(self):
        name = self.signup_form.name.text()
        login = self.signup_form.login.text()
        password = self.signup_form.password.text()
        repeatpassword = self.signup_form.repeatpassword.text()
        balance = self.signup_form.balance.text()
        conn = sqlite3.connect('moneyBase.db')
        cursor = conn.cursor()
        if not name:
            self.signup_form.status_label.setText("Error : Enter your name")
            self.signup_form.name.setFocus()
            return
        elif not login:
            self.signup_form.status_label.setText("Error : Enter your login")
            self.signup_form.login.setFocus()
            return
        elif not password:
            self.signup_form.status_label.setText("Error : Enter your password")
            self.signup_form.password.setFocus()
            return
        elif not repeatpassword:
            self.signup_form.status_label.setText("Error : Repeat your password")
            self.signup_form.repeatpassword.setFocus()
            return
        elif not balance:
            self.signup_form.status_label.setText("Error : Enter your current balance")
            self.signup_form.balance.setFocus()
            return
        elif password != repeatpassword:
            self.signup_form.status_label.setText("Error : Passwords don't match")
            self.signup_form.repeatpassword.setFocus()
            return

        try:
            float(balance)
        except:
            self.signup_form.status_label.setText("Error : Balance must be a number")
            self.signup_form.balance.setFocus()
            return

        cursor.execute('SELECT * FROM users WHERE login = ?', (login,))
        if cursor.fetchone() is not None:
            self.signup_form.status_label.setText("Error : user with this login already exists")
            conn.close()
            return

        self.signup_form.status_label.setText("Success!")
        cursor.execute('INSERT INTO users (name, login, password, balance) VALUES (?, ?, ?, ?)',
                           (name, login, password, balance))
        cursor.execute(f'''CREATE TABLE {login} (
                       id INTEGER PRIMARY KEY,
                       money REAL,
                       comment TEXT,
                       data DATA)''')
        conn.commit()
        conn.close()
        self.showNewForm(self.main_form, sizes[self.main_form][0], sizes[self.main_form][1])


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = SafeMoneyApp()
    window.show()
    sys.exit(app.exec_())
