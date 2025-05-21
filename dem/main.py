from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import QTableWidgetItem, QMessageBox
from main_ad import Ui_Form
from zex import Ui_Form2
from new_allpr import Ui_Form as Ui_Form_Products
from newpr import Ui_Form as Ui_Form_NewProduct
from newpr2 import Ui_Form as Ui_Form_EditProduct
from zaiv import Ui_Form as Ui_Form_Application
import mysql.connector

class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)

        # Подключение к БД
        self.db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="aaa"
        )

        # Подключение кнопок главного меню
        self.ui.pushButton.clicked.connect(self.show_products)  # Все продукты
        self.ui.pushButton_2.clicked.connect(self.show_workshops)  # Все цехи
        self.ui.pushButton_3.clicked.connect(self.show_application_form)  # Создать заявку
        self.ui.pushButton_5.clicked.connect(self.close)  # Выход

    def show_application_form(self):
        """Показывает форму создания заявки"""
        try:
            self.application_form = QtWidgets.QWidget()
            self.application_ui = Ui_Form_Application()
            self.application_ui.setupUi(self.application_form)

            # Заполняем выпадающие списки
            self.fill_partners_combo()
            self.fill_materials_combo()
            self.fill_products_combo()

            # Подключаем кнопки
            self.application_ui.pushButton.clicked.connect(self.create_application)
            self.application_ui.pushButton_2.clicked.connect(self.application_form.close)

            self.application_form.show()

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось открыть форму заявки: {e}")

    def fill_partners_combo(self):
        """Заполняет комбобокс партнерами"""
        cursor = self.db.cursor()
        cursor.execute("SELECT partner_id, company_name FROM partners")
        self.application_ui.comboBox.clear()
        for partner_id, company_name in cursor:
            self.application_ui.comboBox.addItem(company_name, partner_id)
        cursor.close()

    def fill_materials_combo(self):
        """Заполняет комбобокс материалами"""
        cursor = self.db.cursor()
        cursor.execute("SELECT material_id, material_name FROM materials")
        self.application_ui.comboBox_2.clear()
        for material_id, material_name in cursor:
            self.application_ui.comboBox_2.addItem(material_name, material_id)
        cursor.close()

    def fill_products_combo(self):
        """Заполняет комбобокс продуктами"""
        cursor = self.db.cursor()
        cursor.execute("SELECT product_id, product_name FROM products")
        self.application_ui.comboBox_3.clear()
        for product_id, product_name in cursor:
            self.application_ui.comboBox_3.addItem(product_name, product_id)
        cursor.close()

    def create_application(self):
        """Создает новую заявку в БД"""
        try:
            # Получаем данные из формы
            partner_id = self.application_ui.comboBox.currentData()
            material_id = self.application_ui.comboBox_2.currentData()
            product_id = self.application_ui.comboBox_3.currentData()
            quantity = self.application_ui.lineEdit.text().strip()

            # Проверяем данные
            if not all([partner_id, material_id, product_id, quantity]):
                QMessageBox.warning(self.application_form, "Ошибка", "Заполните все поля")
                return

            try:
                quantity = float(quantity)
                if quantity <= 0:
                    raise ValueError
            except ValueError:
                QMessageBox.warning(self.application_form, "Ошибка", "Введите корректное количество")
                return

            # Сохраняем заявку в БД
            cursor = self.db.cursor()
            cursor.execute("""
                INSERT INTO applications 
                (partner_id, product_id, material_id, quantity) 
                VALUES (%s, %s, %s, %s)
            """, (partner_id, product_id, material_id, quantity))
            self.db.commit()

            QMessageBox.information(self.application_form, "Успех", "Заявка успешно создана")
            self.application_form.close()

        except mysql.connector.Error as err:
            QMessageBox.critical(self.application_form, "Ошибка", f"Не удалось создать заявку: {err}")
        except Exception as e:
            QMessageBox.critical(self.application_form, "Ошибка", f"Произошла ошибка: {e}")

    def show_products(self):
        """Форма со списком продуктов"""
        self.products_form = QtWidgets.QWidget()
        self.products_ui = Ui_Form_Products()
        self.products_ui.setupUi(self.products_form)

        # Загрузка данных
        self.load_products_data()

        # Подключение кнопок
        self.products_ui.pushButton.clicked.connect(self.add_product)
        self.products_ui.pushButton_2.clicked.connect(self.edit_product)
        self.products_ui.pushButton_3.clicked.connect(self.load_products_data)  # Обновление таблицы

        self.products_form.show()

    def load_products_data(self):
        """Загрузка и отображение данных о продуктах"""
        try:
            cursor = self.db.cursor(dictionary=True)
            cursor.execute("""
                SELECT p.*, pt.type_name 
                FROM products p JOIN product_types pt ON p.type_id = pt.type_id
            """)
            products = cursor.fetchall()

            # Настройка таблицы
            self.products_ui.tableWidget.setColumnCount(7)
            self.products_ui.tableWidget.setHorizontalHeaderLabels([
                "ID", "Название", "Артикул", "Тип", "Цена", "Параметры", "Время"
            ])

            self.products_ui.tableWidget.setRowCount(len(products))
            for row, p in enumerate(products):
                for col, val in enumerate([
                    p['product_id'], p['product_name'], p['article'],
                    p['type_name'], p['min_price'],
                    f"{p['param1']}x{p['param2']}", p['total_production_time']
                ]):
                    self.products_ui.tableWidget.setItem(row, col, QTableWidgetItem(str(val)))

        except mysql.connector.Error as err:
            QMessageBox.critical(self.products_form, "Ошибка", f"Не удалось загрузить продукты: {err}")
        except Exception as e:
            QMessageBox.critical(self.products_form, "Ошибка", f"Произошла ошибка: {e}")

    def add_product(self):
        """Форма добавления продукта"""
        form = QtWidgets.QWidget()
        ui = Ui_Form_NewProduct()
        ui.setupUi(form)

        # Заполнение типов продуктов
        cursor = self.db.cursor()
        cursor.execute("SELECT type_id, type_name FROM product_types")
        ui.comboBox.clear()
        for id, name in cursor:
            ui.comboBox.addItem(name, id)

        # Сохранение
        def save():
            try:
                data = (
                    ui.lineEdit.text(), ui.lineEdit_2.text(),
                    ui.comboBox.currentData(), float(ui.lineEdit_3.text()),
                    float(ui.lineEdit_4.text()), float(ui.lineEdit_5.text())
                )

                cursor.execute("""
                    INSERT INTO products (product_name, article, type_id, min_price, param1, param2)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, data)
                self.db.commit()
                QMessageBox.information(form, "Успех", "Продукт добавлен")
                form.close()
            except Exception as e:
                QMessageBox.warning(form, "Ошибка", f"Ошибка: {e}")

        ui.pushButton_2.clicked.connect(save)
        ui.pushButton.clicked.connect(form.close)
        form.show()

    def edit_product(self):
        """Форма редактирования продукта"""
        form = QtWidgets.QWidget()
        ui = Ui_Form_EditProduct()
        ui.setupUi(form)

        # Заполнение списка продуктов
        cursor = self.db.cursor()
        cursor.execute("SELECT product_id, product_name FROM products")
        ui.comboBox.clear()
        for id, name in cursor:
            ui.comboBox.addItem(name, id)

        # Загрузка данных при выборе
        def load_data():
            cursor.execute("""
                SELECT p.*, pt.type_name FROM products p
                JOIN product_types pt ON p.type_id = pt.type_id
                WHERE p.product_id = %s
            """, (ui.comboBox.currentData(),))
            p = cursor.fetchone()

            if p:
                ui.lineEdit.setText(p[1])  # Название
                ui.lineEdit_2.setText(p[2])  # Артикул
                ui.lineEdit_3.setText(str(p[4]))  # Цена
                ui.lineEdit_4.setText(str(p[5]))  # Длина
                ui.lineEdit_5.setText(str(p[6]))  # Ширина

                # Заполнение типов
                cursor.execute("SELECT type_id, type_name FROM product_types")
                ui.comboBox_2.clear()
                for id, name in cursor:
                    ui.comboBox_2.addItem(name, id)
                    if id == p[3]:  # Выбор текущего типа
                        ui.comboBox_2.setCurrentIndex(ui.comboBox_2.count() - 1)

        # Сохранение
        def save():
            try:
                data = (
                    ui.lineEdit.text(), ui.lineEdit_2.text(),
                    ui.comboBox_2.currentData(), float(ui.lineEdit_3.text()),
                    float(ui.lineEdit_4.text()), float(ui.lineEdit_5.text()),
                    ui.comboBox.currentData()
                )

                cursor.execute("""
                    UPDATE products SET
                    product_name=%s, article=%s, type_id=%s,
                    min_price=%s, param1=%s, param2=%s
                    WHERE product_id=%s
                """, data)
                self.db.commit()
                QMessageBox.information(form, "Успех", "Изменения сохранены")
                form.close()
            except Exception as e:
                QMessageBox.warning(form, "Ошибка", f"Ошибка: {e}")

        ui.comboBox.currentIndexChanged.connect(load_data)
        ui.pushButton_2.clicked.connect(save)
        ui.pushButton.clicked.connect(form.close)
        form.show()

    def show_workshops(self):
        """Форма со списком цехов"""
        try:
            # Создаем форму
            self.workshops_form = QtWidgets.QWidget()
            self.workshops_ui = Ui_Form2()
            self.workshops_ui.setupUi(self.workshops_form)

            # Получаем данные из БД
            cursor = self.db.cursor(dictionary=True)
            cursor.execute("SELECT * FROM workshops")
            workshops = cursor.fetchall()

            # Настраиваем таблицу
            self.workshops_ui.tableWidget.setColumnCount(4)
            self.workshops_ui.tableWidget.setHorizontalHeaderLabels([
                "Название цеха", "Кол-во рабочих",
                "Базовое время", "Описание"
            ])
            self.workshops_ui.tableWidget.setRowCount(len(workshops))

            # Заполняем таблицу
            for row, workshop in enumerate(workshops):
                self.workshops_ui.tableWidget.setItem(row, 0, QTableWidgetItem(workshop['workshop_name']))
                self.workshops_ui.tableWidget.setItem(row, 1, QTableWidgetItem(str(workshop['workers_count'])))
                self.workshops_ui.tableWidget.setItem(row, 2, QTableWidgetItem(str(workshop['base_processing_time'])))
                self.workshops_ui.tableWidget.setItem(row, 3, QTableWidgetItem(workshop['description']))

            # Подключаем кнопку "Назад"
            self.workshops_ui.pushButton.clicked.connect(self.workshops_form.close)

            # Показываем форму
            self.workshops_form.show()

        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить цехи: {err}")


if __name__ == "__main__":

    app = QtWidgets.QApplication([])
    window = MainWindow()
    window.show()
    app.exec()