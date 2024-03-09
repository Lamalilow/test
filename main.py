#db_manager.py
from PySide6.QtSql import QSqlDatabase, QSqlQuery


class DBManager:
    def __init__(self, db_name='todo.db'):
        self.db_name = db_name

        self.conn = QSqlDatabase.addDatabase('QSQLITE')
        self.conn.setDatabaseName(self.db_name)

        if not self.conn.open():
            raise Exception('Не удалось открыть')

        self.create_table()

    def create_table(self):
        query = QSqlQuery()
        query.exec('''CREATE TABLE IF NOT EXISTS tasks (id INTEGER PRIMARY KEY, task TEXT) ''')

    def fetch_tasks(self):
        query = QSqlQuery()
        query.exec('''SELECT * FROM tasks''')
        tasks = []
        while query.next():
            task_id = query.value(0)
            task_name = query.value(1)
            tasks.append((task_id, task_name))

        return tasks

    def add_task(self, task):
        query = QSqlQuery()
        query.prepare('''INSERT INTO tasks (task) VALUES (?)''')
        query.addBindValue(task)
        query.exec()

    def delete_task(self, task_id):
        query = QSqlQuery()
        query.prepare('''DELETE FROM tasks WHERE id = ?''')
        query.addBindValue(task_id)
        query.exec()

    def update_task(self, task_id, new_task):
        query = QSqlQuery()
        query.prepare('''UPDATE tasks SET task = ? WHERE id = ? ''')
        query.addBindValue(new_task)
        query.addBindValue(task_id)
        query.exec()

#main.py
import sys
from functools import partial
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QMessageBox,
    QDialog,
    QDialogButtonBox,
    QHeaderView
)



class TodoApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Todo List')
        self.setGeometry(100, 100, 600, 400)
        self.db_manager = DBManager()
        self.setup_ui()
        self.populate_table()

    def setup_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)
        self.input_layout = QHBoxLayout()
        self.layout.addLayout(self.input_layout)
        self.task_label = QLabel('Task:')
        self.input_layout.addWidget(self.task_label)

        self.task_input = QLineEdit()
        self.input_layout.addWidget(self.task_input)

        self.add_button = QPushButton('Add')
        self.add_button.clicked.connect(self.add_task)
        self.input_layout.addWidget(self.add_button)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(['ID', 'Task', 'Edit', 'Delete'])
        self.layout.addWidget(self.table)

    def populate_table(self):
        tasks = self.db_manager.fetch_tasks()
        self.table.setRowCount(len(tasks))

        for row, (task_id, task_name) in enumerate(tasks):
            self.table.setItem(row, 0, QTableWidgetItem(str(task_id)))
            self.table.setItem(row, 1, QTableWidgetItem(task_name))

            self.table.item(row, 0).setFlags(Qt.ItemIsEnabled)
            self.table.item(row, 1).setFlags(Qt.ItemIsEnabled)

            delete_button = QPushButton('Delete')
            edit_button = QPushButton('Edit')

            delete_button.clicked.connect(partial(self.delete_task, task_id))
            edit_button.clicked.connect(partial(self.edit_task, task_id, task_name))

            edit_widget = QWidget()
            edit_layout = QHBoxLayout(edit_widget)
            edit_layout.addWidget(edit_button)
            edit_layout.setAlignment(Qt.AlignCenter)
            edit_layout.setContentsMargins(0,0,0,0)
            edit_widget.setLayout(edit_layout)

            delete_widget = QWidget()
            delete_layout = QHBoxLayout(delete_widget)
            delete_layout.addWidget(delete_button)
            delete_layout.setAlignment(Qt.AlignCenter)
            delete_layout.setContentsMargins(0, 0, 0, 0)
            delete_widget.setLayout(delete_layout)

            self.table.setCellWidget(row, 2, edit_widget)
            self.table.setCellWidget(row, 3, delete_widget)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def add_task(self):
        task = self.task_input.text()
        if task:
            self.db_manager.add_task(task)
            self.task_input.clear()
            self.populate_table()

    def delete_task(self, task_id):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Question)
        msg.setText('Вы действительно хотите удалить?')
        msg.setWindowTitle('Удалить таск')
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        if msg.exec() == QMessageBox.Yes:
            self.db_manager.delete_task(task_id)
            self.populate_table()

    def edit_task(self, task_id, task_name):
        dialog = EditTaskDialog(task_id, task_name, self)
        if dialog.exec() == QDialog.Accepted:
            print(1)
            new_task_name = dialog.task_input.text()
            if new_task_name:
                print(2)
                self.db_manager.update_task(task_id, new_task_name)
                self.populate_table()


class EditTaskDialog(QDialog):
    def __init__(self, task_id, task_name, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Изменить таск')
        self.layout = QVBoxLayout()
        self.task_label = QLabel('Task:')
        self.layout.addWidget(self.task_label)
        self.task_input = QLineEdit()
        self.task_input.setText(task_name)
        self.layout.addWidget(self.task_input)
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.layout.addWidget(self.button_box)
        self.setLayout(self.layout)


#Запуск приложения
app = QApplication(sys.argv)
window = TodoApp()
window.show()
app.exec()
