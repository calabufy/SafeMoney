import sqlite3

from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QIntValidator, QPainter, QPen, QBrush, QColor
from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedWidget, QLineEdit, QFrame, QTableWidgetItem
from PyQt5 import QtCore

from uiSM import Ui_SafeMoney
from uiSMsignup import Ui_SafeMoneySignup
from uiSMreg import Ui_SafeMoneyreg
from uiSMlogin import Ui_SafeMoneyLogin


class frame(QFrame):
    def set_data(self, data):
        self.data = data
        self.expense = {}
        self.colors = {'health (✚)' : 'red', 'free time (⚽)' : 'blue', 'home (☗)': 'brown', 'cafe (☕)': 'cyan',
                       'education (√)': 'green', 'gifts (🎁)': 'yellow', 'products (🍲)': 'magenta', 'no type (⊘)' : 'gray'}
        for op in self.data:
            if op[1] == 'expense':
                if op[2] not in self.expense.keys():
                    self.expense[op[2]] = op[0]
                else:
                    self.expense[op[2]] += op[0]
        self.total = sum(self.expense.values())
        self.repaint()

    def paintEvent(self, event):
        painter = QPainter()
        start_angle = 0
        for type in self.expense.keys():
            money = self.expense[type]
            angle = int(money / self.total * 360)
            painter.setBrush(QBrush(QColor(self.colors[type])))
            painter.drawPie(self.rect(), start_angle * 16, angle * 16)
            start_angle += angle
        self.update()


class SafeMoneyApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.sizes = {}
        self.period = "Today"
        self.userid = None
        self.stack = QStackedWidget(self)
        self.reg_form = Ui_SafeMoneyreg()
        self.login_form = Ui_SafeMoneyLogin()
        self.signup_form = Ui_SafeMoneySignup()
        self.main_form = Ui_SafeMoney()

        self.main_form.frame = frame(self.main_form.Main)
        self.main_form.frame.setGeometry(QtCore.QRect(9, 60, 318, 200))
        self.main_form.frame.setMinimumSize(QtCore.QSize(0, 0))
        self.main_form.frame.setObjectName("frame")

        self.sizes[self.reg_form] = (self.reg_form.width(), self.reg_form.height())
        self.sizes[self.login_form] = (self.login_form.width(), self.login_form.height())
        self.sizes[self.signup_form] = (self.signup_form.width(), self.signup_form.height())
        self.sizes[self.main_form] = (self.main_form.width(), self.main_form.height())
        self.stack.addWidget(self.reg_form)
        self.stack.addWidget(self.main_form)
        self.stack.addWidget(self.signup_form)
        self.stack.addWidget(self.login_form)
        self.resize(self.reg_form.width(), self.reg_form.height())

        self.reg_form.login_button.clicked.connect(lambda: self.showNewForm(self.login_form, self.sizes[self.login_form][0],self.sizes[self.login_form][1]))
        self.login_form.login_button.clicked.connect(self.loginUser)
        self.login_form.back_button.clicked.connect(lambda: self.showNewForm(self.reg_form, self.sizes[self.reg_form][0],self.sizes[self.reg_form][1]))
        self.reg_form.signup_button.clicked.connect(lambda: self.showNewForm(self.signup_form, self.sizes[self.signup_form][0],self.sizes[self.signup_form][1]))
        self.signup_form.signup_button.clicked.connect(self.signUpUser)
        self.signup_form.back_button.clicked.connect(lambda: self.showNewForm(self.reg_form, self.sizes[self.reg_form][0],self.sizes[self.reg_form][1]))

        self.signup_form.name.returnPressed.connect(self.changeCursor)
        self.signup_form.login.returnPressed.connect(self.changeCursor)
        self.signup_form.password.returnPressed.connect(self.changeCursor)
        self.signup_form.repeatpassword.returnPressed.connect(self.changeCursor)
        self.signup_form.balance.returnPressed.connect(self.changeCursor)

        self.login_form.login.returnPressed.connect(self.changeCursor)
        self.login_form.password.returnPressed.connect(self.changeCursor)

        self.main_form.money_lineEdit.setValidator(QIntValidator())
        self.main_form.changeuser_button.clicked.connect(lambda: self.showNewForm(self.reg_form, self.sizes[self.reg_form][0],self.sizes[self.reg_form][1]))

        self.main_form.today_button.clicked.connect(self.changePeriod)
        self.main_form.month_button.clicked.connect(self.changePeriod)
        self.main_form.year_button.clicked.connect(self.changePeriod)
        self.main_form.alltime_button.clicked.connect(self.changePeriod)

        self.main_form.operation_box.addItem('expense (-)')
        self.main_form.operation_box.addItem('income (+)')

        self.main_form.typeBox.addItem('health (✚)')
        self.main_form.typeBox.addItem('free time (⚽)')
        self.main_form.typeBox.addItem('home (☗)')
        self.main_form.typeBox.addItem('cafe (☕)')
        self.main_form.typeBox.addItem('education (√)')
        self.main_form.typeBox.addItem('gifts (🎁)')
        self.main_form.typeBox.addItem('products (🍲)')
        self.main_form.typeBox.addItem('no type (⊘)')

        self.main_form.submit_button.clicked.connect(self.pushMoney)

        self.main_form.balance_table.horizontalHeader().setVisible(False)

        current_date = QDate.currentDate()
        self.main_form.dateEdit.setDate(current_date)

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
        if userData is None:
            self.login_form.status_label.setText("Error : There is no user with this login")
            self.login_form.login.setFocus()
            return
        if password != userData[3]:
            self.login_form.status_label.setText("Error : Incorrect password")
            self.login_form.password.setFocus()
            return
        self.userid = cursor.execute('SELECT id FROM users WHERE login = ?', (login,)).fetchone()[0]
        conn.close()
        self.showNewForm(self.main_form, self.sizes[self.main_form][0], self.sizes[self.main_form][1])
        self.initMainWindow()

    def signUpUser(self):
        name = self.signup_form.name.text()
        login = self.signup_form.login.text()
        password = self.signup_form.password.text()
        repeatpassword = self.signup_form.repeatpassword.text()
        self.balance = self.signup_form.balance.text()
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
        elif not self.balance:
            self.signup_form.status_label.setText("Error : Enter your current balance")
            self.signup_form.balance.setFocus()
            return
        elif password != repeatpassword:
            self.signup_form.status_label.setText("Error : Passwords don't match")
            self.signup_form.repeatpassword.setFocus()
            return

        try:
            float(self.balance)
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
                           (name, login, password, self.balance))
        self.userid = cursor.execute('SELECT id FROM users WHERE login = ?', (login,)).fetchone()[0]
        conn.commit()
        conn.close()
        self.showNewForm(self.main_form, self.sizes[self.main_form][0], self.sizes[self.main_form][1])
        self.initMainWindow()

    def drawDiagram(self):
        dif = self.getMoney()
        self.main_form.frame.set_data(dif)
        # self.update()

    def initMainWindow(self):
        conn = sqlite3.connect('moneyBase.db')
        cursor = conn.cursor()
        name, self.balance = cursor.execute('SELECT name, balance FROM users WHERE id = ?', (self.userid,)).fetchone()
        self.main_form.username_label.setText(name)
        self.main_form.total_label.setText(str(self.balance) + ' RUB')
        self.drawDiagram()
        current_date = QDate.currentDate()
        self.main_form.dateEdit.setDate(current_date)
        self.fillTable()
        conn.close()

    def pushMoney(self):
        if self.main_form.money_lineEdit.text() == '0':
            self.main_form.error_label.setText('Error : Enter the number of money')
            self.main_form.money_lineEdit.setFocus()
            return
        conn = sqlite3.connect('moneyBase.db')
        cursor = conn.cursor()

        money = int(self.main_form.money_lineEdit.text())
        operation = self.main_form.operation_box.currentText()[:-4]
        type = self.main_form.typeBox.currentText()
        comment = self.main_form.comment_textEdit.toPlainText()
        if not comment:
            comment = '[No comment]'
        date = self.main_form.dateEdit.date().toString("yyyy-MM-dd")
        cursor.execute('INSERT INTO operations (userid, money, operation, type, comment, date) VALUES '
                       '(?, ?, ?, ?, ?, ?)', (self.userid, money, operation, type, comment, date))
        self.balance = self.balance + (money * (-1, 1)[int(operation == "income")])
        cursor.execute('UPDATE users SET balance = ? WHERE id = ?', (self.balance, self.userid))
        conn.commit()
        conn.close()
        self.initMainWindow()
        self.main_form.tabWidget.setCurrentIndex(0)

    def changePeriod(self):
        self.period = self.sender().text()
        self.fillTable()
        self.drawDiagram()

    def fillTable(self):
        conn = sqlite3.connect('moneyBase.db')
        cursor = conn.cursor()
        data = self.getMoney()
        formatData = []
        dif = 0
        for op in data:
            formatData.append((('-', '+')[op[1] == 'income'] + str(op[0]), op[2][-2:-1], op[3], op[4]))
            dif += op[0] * (-1, 1)[op[1] == 'income']

        self.main_form.balance_table.setRowCount(0)

        for row_num, row_data in enumerate(formatData):
            self.main_form.balance_table.insertRow(row_num)
            for col_num, cell_data in enumerate(row_data):
                self.main_form.balance_table.setItem(row_num, col_num, QTableWidgetItem(str(cell_data)))
                self.main_form.balance_table.resizeColumnToContents(col_num)

        self.main_form.dif_label.setText(('', '+')[dif >= 0] + str(dif) + ' RUB')
        if dif >= 0:
            self.main_form.dif_label.setStyleSheet("color: green;")
        else:
            self.main_form.dif_label.setStyleSheet("color: red;")
        conn.close()

    def getMoney(self):
        conn = sqlite3.connect('moneyBase.db')
        cursor = conn.cursor()

        if self.period == 'Today':
            data = cursor.execute('SELECT money, operation, type, comment, date FROM operations '
                                  'WHERE userid = ? AND date = ? ORDER BY date DESC',
                                  (self.userid, QDate.currentDate().toString("yyyy-MM-dd"))).fetchall()
        elif self.period == "Month":
            data = cursor.execute('SELECT money, operation, type, comment, date FROM operations '
                                  'WHERE userid = ? AND strftime("%m", date) = ? AND strftime("%Y", date) = ? '
                                  'ORDER BY date DESC',
                                  (self.userid, str(QDate.currentDate().month()).zfill(2), str(QDate.currentDate().year()))).fetchall()
        elif self.period == "Year":
            data = cursor.execute('SELECT money, operation, type, comment, date FROM operations '
                                  'WHERE userid = ? AND strftime("%Y", date) = ? ORDER BY date DESC',
                                  (self.userid, str(QDate.currentDate().year()))).fetchall()
        else:
            data = cursor.execute('SELECT money, operation, type, comment, date FROM operations '
                                  'WHERE userid = ? ORDER BY date DESC',
                                  (self.userid,)).fetchall()

        return data


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = SafeMoneyApp()
    window.show()
    sys.exit(app.exec_())
