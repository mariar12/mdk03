import sys
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtGui import QPixmap
import mysql.connector
from aut import Ui_Form as Ui_AuthForm
from usr import Ui_Form as Ui_UserForm
from usrz import Ui_Form as Ui_UserAppsForm
from admin import Ui_Form as Ui_AdminForm
from tm import Ui_Form1
from mer import Ui_Form2
from pitt import Ui_Form3
from zaiv import Ui_Form4

# Подключение к базе данных
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="event_booking_system"
)
cursor = db.cursor()

class AuthForm(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_AuthForm()
        self.ui.setupUi(self)

        self.ui.pushButton.setText("Пользователь")
        self.ui.pushButton_2.setText("Администратор")

        self.ui.pushButton.clicked.connect(self.open_user_view)
        self.ui.pushButton_2.clicked.connect(self.open_admin_view)

    def open_user_view(self):
        self.user_form = UserForm()
        self.user_form.show()
        self.hide()

    def open_admin_view(self):
        # Проверка пароля (в реальном приложении нужно реализовать нормальную аутентификацию)
        password, ok = QtWidgets.QInputDialog.getText(
            self, 'Авторизация', 'Введите пароль администратора:',
            QtWidgets.QLineEdit.EchoMode.Password
        )

        if ok and password == "admin123":  # Простая проверка пароля
            self.admin_form = AdminForm()
            self.admin_form.show()
            self.hide()
        elif ok:
            QMessageBox.warning(self, "Ошибка", "Неверный пароль администратора")


class AdminForm(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_AdminForm()
        self.ui.setupUi(self)

        self.load_applications()

        # Подключаем кнопки
        self.ui.pushButton.clicked.connect(self.change_status)
        self.ui.pushButton_2.clicked.connect(self.add_event)

        # Добавляем кнопку "Назад"
        self.back_button = QtWidgets.QPushButton("Назад", self)
        self.back_button.setGeometry(QtCore.QRect(20, 270, 75, 23))
        self.back_button.clicked.connect(self.go_back)

    def load_applications(self):
        try:
            cursor.execute("""
                SELECT a.id, u.name, e.title, e.date_time, c.name, a.people_count, a.status 
                FROM applications a
                JOIN users u ON a.user_id = u.id
                JOIN events e ON a.event_id = e.id
                LEFT JOIN catering c ON a.catering_id = c.id
                ORDER BY a.id DESC
            """)
            applications = cursor.fetchall()

            text = ""
            for app in applications:
                text += f"""ID: {app[0]}
Пользователь: {app[1]}
Мероприятие: {app[2]}
Дата: {app[3].strftime('%d.%m.%Y %H:%M')}
Питание: {app[4]}
Количество: {app[5]}
Статус: {app[6]}

------------------------
"""
            self.ui.textBrowser.setText(text)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить заявки: {str(e)}")

    def change_status(self):
        app_id, ok = QtWidgets.QInputDialog.getInt(
            self, 'Изменение статуса', 'Введите ID заявки:'
        )
        if ok:
            new_status, ok = QtWidgets.QInputDialog.getItem(
                self, 'Изменение статуса', 'Выберите новый статус:',
                ['новый', 'подтверждено', 'отклонено', 'завершено'], 0, False
            )
            if ok:
                try:
                    cursor.execute(
                        "UPDATE applications SET status = %s WHERE id = %s",
                        (new_status, app_id)
                    )
                    db.commit()
                    QMessageBox.information(self, "Успех", "Статус заявки обновлен")
                    self.load_applications()
                except Exception as e:
                    db.rollback()
                    QMessageBox.critical(self, "Ошибка", f"Не удалось обновить статус: {str(e)}")

    def add_event(self):
        # Здесь можно реализовать добавление мероприятий
        QMessageBox.information(self, "Информация", "Функция добавления мероприятий в разработке")

    def go_back(self):
        self.close()
        auth_form = AuthForm()
        auth_form.show()


class UserForm(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_UserForm()
        self.ui.setupUi(self)

        self.ui.pushButton.setText("Создать заявку")
        self.ui.pushButton_2.setText("Мои заявки")

        self.ui.pushButton.clicked.connect(self.create_application)
        self.ui.pushButton_2.clicked.connect(self.view_applications)

    def create_application(self):
        self.type_form = TypeForm()
        self.type_form.show()
        self.hide()

    def view_applications(self):
        self.apps_form = UserAppsForm()
        self.apps_form.show()
        self.hide()


class UserAppsForm(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_UserAppsForm()
        self.ui.setupUi(self)

        self.load_user_applications()

    def load_user_applications(self):
        try:
            # Для примера используем user_id = 1
            user_id = 1

            cursor.execute("""
                SELECT a.id, e.title, e.date_time, c.name, a.people_count, a.status 
                FROM applications a
                JOIN events e ON a.event_id = e.id
                LEFT JOIN catering c ON a.catering_id = c.id
                WHERE a.user_id = %s
            """, (user_id,))

            applications = cursor.fetchall()

            text = ""
            for app in applications:
                text += f"""ID: {app[0]}
Мероприятие: {app[1]}
Дата: {app[2].strftime('%d.%m.%Y %H:%M')}
Питание: {app[3]}
Количество: {app[4]}
Статус: {app[5]}

------------------------
"""
            self.ui.textBrowser.setText(text)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить заявки: {str(e)}")


class TypeForm(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Form1()
        self.ui.setupUi(self)

        # Заполняем кнопки типами мероприятий из БД
        cursor.execute("SELECT name FROM event_types")
        event_types = cursor.fetchall()

        buttons = [self.ui.pushButton, self.ui.pushButton_2, self.ui.pushButton_3]
        for i, (event_type,) in enumerate(event_types[:3]):
            buttons[i].setText(event_type)
            buttons[i].clicked.connect(self.select_event_type)

        self.next_form = None

    def select_event_type(self):
        sender = self.sender()
        selected_type = sender.text()

        # Получаем ID выбранного типа
        cursor.execute("SELECT id FROM event_types WHERE name = %s", (selected_type,))
        type_id = cursor.fetchone()[0]

        # Переходим к форме выбора мероприятия
        self.next_form = EventForm(type_id)
        self.next_form.show()
        self.hide()


class EventForm(QtWidgets.QWidget):
    def __init__(self, type_id):
        super().__init__()
        self.ui = Ui_Form2()
        self.ui.setupUi(self)
        self.type_id = type_id
        self.selected_event = None

        # Загружаем мероприятия из БД
        self.load_events()

        self.ui.pushButton_4.clicked.connect(self.go_back)

    def load_events(self):
        cursor.execute("""
            SELECT e.id, e.title, e.date_time 
            FROM events e 
            WHERE e.type_id = %s
            LIMIT 3
        """, (self.type_id,))
        events = cursor.fetchall()

        buttons = [self.ui.pushButton, self.ui.pushButton_2, self.ui.pushButton_3]

        for i, (event_id, title, date_time) in enumerate(events):
            # Просто устанавливаем текст на кнопке
            buttons[i].setText(f"{title}\n{date_time.strftime('%d.%m.%Y %H:%M')}")

            # Сохраняем данные мероприятия
            buttons[i].event_data = {
                'id': event_id,
                'title': title,
                'date_time': date_time
            }
            buttons[i].clicked.connect(self.select_event)

    def select_event(self):
        sender = self.sender()
        self.selected_event = sender.event_data
        self.next_form = CateringForm(self.selected_event)
        self.next_form.show()
        self.hide()

    def go_back(self):
        self.parent().show()
        self.hide()

class CateringForm(QtWidgets.QWidget):
    def __init__(self, event_data):
        super().__init__()
        self.ui = Ui_Form3()
        self.ui.setupUi(self)
        self.event_data = event_data
        self.selected_catering = None

        # Заполняем кнопки вариантами питания
        cursor.execute("SELECT name FROM catering")
        catering_options = cursor.fetchall()

        buttons = [self.ui.pushButton, self.ui.pushButton_2, self.ui.pushButton_3]
        for i, (catering,) in enumerate(catering_options[:3]):
            buttons[i].setText(catering)
            buttons[i].catering_name = catering
            buttons[i].clicked.connect(self.select_catering)

        self.ui.pushButton_4.clicked.connect(self.go_back)
        self.next_form = None

    def select_catering(self):
        sender = self.sender()
        self.selected_catering = sender.catering_name

        # Переходим к форме подтверждения
        self.next_form = ConfirmationForm(self.event_data, self.selected_catering)
        self.next_form.show()
        self.hide()

    def go_back(self):
        self.parent().show()
        self.hide()


class ConfirmationForm(QtWidgets.QWidget):
    def __init__(self, event_data, catering):
        super().__init__()
        self.ui = Ui_Form4()
        self.ui.setupUi(self)
        self.event_data = event_data
        self.catering = catering

        # Отображаем выбранные данные
        info = f"""Мероприятие: {event_data['title']}
Дата и время: {event_data['date_time'].strftime('%d.%m.%Y %H:%M')}
Питание: {catering}"""

        self.ui.textBrowser.setText(info)
        self.ui.pushButton.clicked.connect(self.create_application)

    def create_application(self):
        # Получаем ID пользователя (для примера используем 1)
        user_id = 1

        # Получаем ID выбранного питания
        cursor.execute("SELECT id FROM catering WHERE name = %s", (self.catering,))
        catering_result = cursor.fetchone()

        if not catering_result:
            QMessageBox.critical(self, "Ошибка", "Не удалось найти выбранное питание")
            return

        catering_id = catering_result[0]

        # Создаем заявку (без image_id)
        try:
            cursor.execute("""
                INSERT INTO applications 
                (user_id, event_id, catering_id, people_count, status) 
                VALUES (%s, %s, %s, %s, %s)
            """, (
                user_id,
                self.event_data['id'],
                catering_id,
                1,  # Количество людей
                'новый'  # Статус заявки
            ))
            db.commit()

            QMessageBox.information(self, "Успех", "Заявка успешно создана!")
            self.close()

            # Возвращаемся к главной форме пользователя
            user_form = None
            for widget in QtWidgets.QApplication.topLevelWidgets():
                if isinstance(widget, UserForm):
                    user_form = widget
                    break
            if user_form:
                user_form.show()

        except Exception as e:
            db.rollback()
            QMessageBox.critical(self, "Ошибка", f"Не удалось создать заявку: {str(e)}")

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    auth_form = AuthForm()
    auth_form.show()
    sys.exit(app.exec())