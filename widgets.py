"""Переопределённые компоненты окна (PySide6)."""
from datetime import datetime

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView, QComboBox, QDialog, QDialogButtonBox, QFormLayout,
    QGroupBox, QHBoxLayout, QHeaderView, QLabel, QLineEdit, QMainWindow,
    QMessageBox, QProgressBar, QPushButton, QSpinBox, QStatusBar,
    QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget,
)

from custom_map import CustomMap
from models import (ALL_KINDS, SORT_MODES, KindRegistry, SessionRecord)
from storage import ReportWriter, Storage


# 1. QLineEdit: поиск, Esc очищает поле
class SearchEdit(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setPlaceholderText("Поиск по названию или автору…")
        self.setClearButtonEnabled(True)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.clear()
            return
        super().keyPressEvent(event)


# 2. QLineEdit: поле с проверкой на пустоту
class ValidatedEdit(QLineEdit):
    def __init__(self, placeholder="", parent=None):
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        self.textChanged.connect(self._refresh)
        self._refresh()

    def is_valid(self):
        return bool(self.text().strip())

    def _refresh(self):
        self.setStyleSheet("" if self.is_valid() else "border: 1px solid #d9534f;")


# 3. QComboBox: выбор из списка вариантов
class OptionCombo(QComboBox):
    def __init__(self, options, parent=None):
        super().__init__(parent)
        self.addItems(list(options))

    def selected(self):
        return self.currentText()

    def wheelEvent(self, event):
        # не меняем значение случайной прокруткой, пока поле не в фокусе
        if self.hasFocus():
            super().wheelEvent(event)
        else:
            event.ignore()


# 4. QSpinBox: рейтинг «N / 10»
class RatingSpin(QSpinBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setRange(0, 10)
        self.setValue(8)

    def textFromValue(self, value):
        return f"{value} / 10"

    def valueFromText(self, text):
        digits = text.split("/")[0].strip()
        return int(digits) if digits.isdigit() else 0


# 5. QSpinBox: год
class YearSpin(QSpinBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setRange(1800, datetime.now().year + 1)
        self.setValue(2000)
        self.setWrapping(False)


# 6. QPushButton: кнопка с реакцией на наведение
class ActionButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(36)

    def enterEvent(self, event):
        self.setStyleSheet("font-weight: bold;")
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.setStyleSheet("")
        super().leaveEvent(event)


# 7. QLabel: текст описания
class DetailsLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWordWrap(True)
        self.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.show_item(None)

    def show_item(self, item):
        self.setText("Выберите элемент в таблице" if item is None else item.summary())


# 8. QProgressBar: полоса рейтинга
class RatingBar(QProgressBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setRange(0, 10)
        self.setFormat("Рейтинг: %v / 10")
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setValue(0)


# 9. QGroupBox: панель описания
class DetailsPanel(QGroupBox):
    def __init__(self, parent=None):
        super().__init__("Описание", parent)
        self._label = DetailsLabel()
        self._bar = RatingBar()
        layout = QVBoxLayout(self)
        layout.addWidget(self._label, 1)
        layout.addWidget(self._bar)
        self.setMinimumWidth(260)

    def show_item(self, item):
        self._label.show_item(item)
        self._bar.setValue(0 if item is None else item.rating)


# 10. QTableWidget: таблица элементов
class MediaTable(QTableWidget):
    HEADERS = ("Тип", "Название", "Автор", "Год", "Рейтинг", "Параметр")

    def __init__(self, parent=None):
        super().__init__(0, len(self.HEADERS), parent)
        self._items = []
        self.setHorizontalHeaderLabels(list(self.HEADERS))
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setAlternatingRowColors(True)
        self.verticalHeader().setVisible(False)
        header = self.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)

    def fill(self, items):
        self._items = list(items)
        self.clearSelection()
        self.setRowCount(len(self._items))
        for r, item in enumerate(self._items):
            values = (item.kind(), item.title, item.author, str(item.year),
                      f"{item.rating} / 10", item.extra_text())
            for c, value in enumerate(values):
                cell = QTableWidgetItem(value)
                if c >= 3:
                    cell.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.setItem(r, c, cell)

    def current_item(self):
        row = self.currentRow()
        if 0 <= row < len(self._items) and self.selectedItems():
            return self._items[row]
        return None


# 11. QStatusBar: пользователь и статистика
class StatusBarEx(QStatusBar):
    def __init__(self, login, parent=None):
        super().__init__(parent)
        self._stats = QLabel()
        self.addWidget(QLabel(f"Пользователь: {login}"))
        self.addPermanentWidget(self._stats)

    def show_stats(self, stats: CustomMap, average: float):
        self._stats.setText(f"{stats} | Средний рейтинг: {average:.1f}")


# 12. QDialog: вход
class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Вход в MediaShelf")
        self.setMinimumWidth(320)
        self._edit = ValidatedEdit("Введите логин")
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok
                                   | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Логин:"))
        layout.addWidget(self._edit)
        layout.addWidget(buttons)

    @property
    def login(self):
        return self._edit.text().strip()

    @login.setter
    def login(self, value):
        self._edit.setText(value)

    def accept(self):
        if not self._edit.is_valid():
            QMessageBox.warning(self, "Ошибка", "Логин не может быть пустым")
            return
        super().accept()


# 13. QDialog: добавление / редактирование
class ItemDialog(QDialog):
    def __init__(self, parent=None, item=None):
        super().__init__(parent)
        self._item = item
        self._labels = KindRegistry.labels()
        self.setWindowTitle("Редактирование" if item else "Новый элемент")
        self.setMinimumWidth(380)

        self._kind = OptionCombo(KindRegistry.NAMES)
        self._title = ValidatedEdit("Название")
        self._author = ValidatedEdit("Автор / режиссёр / исполнитель")
        self._year = YearSpin()
        self._rating = RatingSpin()
        self._extra = QSpinBox()
        self._extra.setRange(1, 100000)
        self._extra_label = QLabel()

        form = QFormLayout()
        form.addRow("Тип:", self._kind)
        form.addRow("Название:", self._title)
        form.addRow("Автор:", self._author)
        form.addRow("Год:", self._year)
        form.addRow("Рейтинг:", self._rating)
        form.addRow(self._extra_label, self._extra)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok
                                   | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(buttons)

        self._kind.currentTextChanged.connect(self._update_label)
        self._update_label(self._kind.selected())

        if item is not None:
            self._kind.setCurrentText(item.kind())
            self._kind.setEnabled(False)
            self._title.setText(item.title)
            self._author.setText(item.author)
            self._year.setValue(item.year)
            self._rating.setValue(item.rating)
            self._extra.setValue(item.extra)

    @property
    def item(self):
        return self._item

    @item.setter
    def item(self, value):
        self._item = value

    def _update_label(self, kind):
        self._extra_label.setText(f"{self._labels.get(kind, 'Параметр')}:")

    def accept(self):
        if not (self._title.is_valid() and self._author.is_valid()):
            QMessageBox.warning(self, "Ошибка", "Заполните название и автора")
            return
        super().accept()

    def build(self):
        return KindRegistry.create(
            self._kind.selected(), self._title.text(), self._author.text(),
            self._year.value(), self._rating.value(), self._extra.value())

    def apply_to(self, item):
        item.title = self._title.text()
        item.author = self._author.text()
        item.year = self._year.value()
        item.rating = self._rating.value()
        item.extra = self._extra.value()


# 14. QMainWindow: главное окно
class MainWindow(QMainWindow):
    def __init__(self, login, library, data_path, report_path):
        super().__init__()
        self._login = login
        self._library = library
        self._data_path = data_path
        self._report_path = report_path
        self._time_in = datetime.now()

        self.setWindowTitle("MediaShelf — домашняя медиатека")
        self.resize(980, 560)

        self._search = SearchEdit()
        self._kind_filter = OptionCombo((ALL_KINDS,) + KindRegistry.NAMES)
        self._sort_combo = OptionCombo(SORT_MODES)
        self._table = MediaTable()
        self._details = DetailsPanel()
        self._add_btn = ActionButton("Добавить")
        self._edit_btn = ActionButton("Изменить")
        self._delete_btn = ActionButton("Удалить")
        self._status = StatusBarEx(login)
        self.setStatusBar(self._status)

        top = QHBoxLayout()
        top.addWidget(self._search, 3)
        top.addWidget(QLabel("Тип:"))
        top.addWidget(self._kind_filter, 1)
        top.addWidget(QLabel("Сортировка:"))
        top.addWidget(self._sort_combo, 1)

        body = QHBoxLayout()
        body.addWidget(self._table, 3)
        body.addWidget(self._details, 1)

        bottom = QHBoxLayout()
        for button in (self._add_btn, self._edit_btn, self._delete_btn):
            bottom.addWidget(button, 1)

        root = QVBoxLayout()
        root.addLayout(top)
        root.addLayout(body, 1)
        root.addLayout(bottom)
        central = QWidget()
        central.setLayout(root)
        self.setCentralWidget(central)

        self._search.textChanged.connect(self.refresh)
        self._kind_filter.currentTextChanged.connect(self.refresh)
        self._sort_combo.currentTextChanged.connect(self.refresh)
        self._table.itemSelectionChanged.connect(self._on_selection)
        self._add_btn.clicked.connect(self.on_add)
        self._edit_btn.clicked.connect(self.on_edit)
        self._delete_btn.clicked.connect(self.on_delete)

        self.refresh()

    @property
    def login(self):
        return self._login

    @login.setter
    def login(self, value):
        self._login = value

    def refresh(self, *_):
        items = self._library.find(self._kind_filter.selected(),
                                   self._search.text(),
                                   self._sort_combo.selected())
        self._table.fill(items)
        self._details.show_item(None)
        self._status.show_stats(self._library.stats(), self._library.average_rating())

    def _on_selection(self):
        self._details.show_item(self._table.current_item())

    def on_add(self):
        dialog = ItemDialog(self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        try:
            self._library.add(dialog.build())
        except ValueError as error:
            QMessageBox.warning(self, "Ошибка", str(error))
            return
        self.refresh()

    def on_edit(self):
        item = self._table.current_item()
        if item is None:
            QMessageBox.information(self, "Изменить", "Сначала выберите элемент")
            return
        dialog = ItemDialog(self, item)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                dialog.apply_to(item)
            except ValueError as error:
                QMessageBox.warning(self, "Ошибка", str(error))
            self.refresh()

    def on_delete(self):
        item = self._table.current_item()
        if item is None:
            QMessageBox.information(self, "Удалить", "Сначала выберите элемент")
            return
        answer = QMessageBox.question(self, "Удаление", f"Удалить «{item.title}»?")
        if answer == QMessageBox.StandardButton.Yes:
            self._library.remove(item)
            self.refresh()

    def closeEvent(self, event):
        Storage.save_items(self._data_path, self._library.items)
        record = SessionRecord(self._login, self._time_in, datetime.now())
        ReportWriter.append(self._report_path, record)
        event.accept()
