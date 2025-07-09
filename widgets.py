

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QProgressBar, QCheckBox, QPushButton
from PySide6.QtGui import QPainter, QColor, QFont, QPen
from PySide6.QtCore import Qt, QDate
from PySide6.QtWidgets import (
    QWidget, QLabel, QPushButton, QComboBox, QVBoxLayout, QFrame, QHBoxLayout, QSizePolicy, QLineEdit, QDateEdit, QSpinBox
)
from PySide6.QtCore import Qt
from PySide6.QtCore import Signal
import json

class DaySelection(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(160, 160)
        self.setMaximumHeight(50)  # Begrenze die maximale Höhe
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        self.setup_ui()

    def setup_ui(self):
        self.selection_layout = QHBoxLayout()
        self.setLayout(self.selection_layout)

        tage = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag"]

        for tag in tage:
            tag_box = QCheckBox(tag)
            tag_box.setChecked(False)  # standardmäßig aktiv

            self.selection_layout.addWidget(tag_box)

        #self.selection_layout.addStretch() # nimmt sich nur so viel plazt, wie es bruacht


    def get_selected_days(self):
        selected_days = []
        for i in range(self.selection_layout.count()):
            widget = self.selection_layout.itemAt(i).widget()
            if isinstance(widget, QCheckBox) and widget.isChecked():
                selected_days.append(widget.text())
        return selected_days


class MealSelection(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMaximumHeight(160)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.menues = [
        'Menü1', 'Menü2', 'Saiten, 1 Paar', 'LKW',
        'Schnitzelweck (vegan)', 'Schnitzelweck (Schwein)',
        'Schnitzelweck (Geflügel)', 'Maultaschen',
        'Maultaschen VEGAN', 'Großer Salatteller VEGAN',
        'Kleiner Salat VEGAN', 'Kartoffelsalat VEGAN',
        'Wrap Hühnchen', 'Wrap Tomate/Mozzarella',
        'Wrap Schinken/Käse', 'Wrap Hummus/Gemüse VEGAN',
        'z. Zt. nicht bestellbar Pizzaschnitte vegetarisch',
        'Pizzaschnitte Salami',
        'z. Zt. nicht bestellbar Pizzaschnitte Schinken'
    ]


        self.setup_ui()

    def setup_ui(self):

        self.layout_ = QVBoxLayout() # Vertikales Layout
        self.setLayout(self.layout_) # layout_ als Layout des widgets festlegen

        self.top_layout = QHBoxLayout() # Erste zeile in layout_ : enthält "Gerichte" und +/- nebeneinander

        self.gerichte_lable = QLabel("Gerichte: ") # gerichte Lable

        self.add_button = QPushButton("+") # hinzufügen button
        self.remove_button = QPushButton("-") # entfernen button

        self.add_button.clicked.connect(self.add_box) # Event das ausgelöst wird, wenn button geklickt -> addbox
        self.remove_button.clicked.connect(self.remove_box) # das geliche für remove

        # widgets zum top layout hinzufügem:
        self.top_layout.addWidget(self.gerichte_lable)
        self.top_layout.addWidget(self.add_button)
        self.top_layout.addWidget(self.remove_button)

        # top_layout zum Hauptlayout (layout_) hinzufügem
        self.layout_.addLayout(self.top_layout)

        # layout, das comboboxen enthält darunter (zum hauptlayout hinzufügen):
        self.box_layout = QVBoxLayout()
        self.layout_.addLayout(self.box_layout)

        self.comboboxes = [] # liste der menüauswahlboxen um zu entfernen und daten abzufragen

        self.add_box()
        self.layout_.addStretch()

    def add_box(self):
        box = QComboBox()
        box.addItems(self.menues) # Menüs als auswahl hinzufügen

        self.comboboxes.append(box) # erstellte box zur liste hinzufügen

        self.box_layout.addWidget(box) # box zum layout hinzufügen

    def remove_box(self):
        if self.comboboxes:
            box = self.comboboxes.pop()
            self.box_layout.removeWidget(box)
            box.deleteLater()

    def get_selected_gerichte(self):
        return list(set([box.currentText() for box in self.comboboxes]))


class EventName(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMaximumHeight(160)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)


        self.setup_ui()

    def setup_ui(self):

        self.layout_ = QVBoxLayout() # Vertikales Layout
        self.setLayout(self.layout_) # layout_ als Layout des widgets festlegen

        self.top_layout = QHBoxLayout()

        self.name_lable = QLabel("Eventname: ")
        self.name_entry = QLineEdit("Event")

        # widgets zum top layout hinzufügem:
        self.top_layout.addWidget(self.name_lable)
        self.top_layout.addWidget(self.name_entry)

        # top_layout zum Hauptlayout (layout_) hinzufügem
        self.layout_.addLayout(self.top_layout)

        self.layout_.addStretch()

    def get_event_name(self):
        return self.name_entry.text()

class DatePlaner(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMaximumHeight(160)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)


        self.setup_ui()

    def setup_ui(self):

        self.layout_ = QVBoxLayout() # Vertikales Layout
        self.setLayout(self.layout_) # layout_ als Layout des widgets festlegen

        datetime_layout = QHBoxLayout()
        datetime_layout.addWidget(QLabel('von'))


        self.start_date = QDateEdit()
        self.start_date.setDate(QDate.currentDate())
        self.start_date.setCalendarPopup(True)

        datetime_layout.addWidget(self.start_date)

        datetime_layout.addWidget(QLabel('bis'))


        self.end_date = QDateEdit()
        self.end_date.setDate(QDate.currentDate())
        self.end_date.setCalendarPopup(True)

        datetime_layout.addWidget(self.end_date)

        self.layout_.addLayout(datetime_layout)


        self.layout_.addStretch()

    def get_date_interval(self):
        return [self.start_date.text(), self.end_date.text()]

class RepetitionSelection(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMaximumHeight(160)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)


        self.setup_ui()

    def setup_ui(self):

        self.layout_ = QHBoxLayout() # Vertikales Layout
        self.setLayout(self.layout_) # layout_ als Layout des widgets festlegen

        self.repetition_lable = QLabel('Wiederholungen in Wochen')

        self.interval_spin = QSpinBox()
        self.interval_spin.setMinimum(1)
        self.interval_spin.setMaximum(4)
        self.interval_spin.setValue(1)

        self.layout_.addWidget(self.repetition_lable)
        self.layout_.addWidget(self.interval_spin)

    def get_interval(self):
        return self.interval_spin.text()


class Event(QFrame):
    delete_requested = Signal(QWidget)  # Signal mit eigenem Widget als Parameter
    def __init__(self, name, days: list, gerichte, start, end, interval, id, parent=None):
        super().__init__(parent)
        self.setMaximumHeight(160)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.setFrameShape(QFrame.Box)
        self.setFrameShadow(QFrame.Raised)
        self.setLineWidth(2)


        self.name = name
        self.days = days
        self.gerichte = gerichte
        self.start = start
        self.end = end
        self.interval = interval

        with open('events.json', 'r', encoding='utf-8') as file:
            self.events = json.load(file)  # config daten laden

        if id == False:
            ids = self.events.keys()
            ids_num = []
            for key in ids:
                ids_num.append(int(key))

            #print(ids_num)
            try:
                self.event_id = max(ids_num) + 1
            except:
                self.event_id = 1

            #print(self.event_id)

        else:
            self.event_id = id



        self.setup_ui()

    def setup_ui(self):

        self.layout_ = QVBoxLayout() # Vertikales Layout
        self.setLayout(self.layout_) # layout_ als Layout des widgets festlegen

        #datetime_layout = QHBoxLayout()
        #datetime_layout.addWidget(QLabel('von'))
        day_str = "; ".join(self.days)
        gerichte_str = "; ".join(self.gerichte)

        event_id_text = f'Event ID: {self.event_id}'

        self.event_id_lable = QLabel(event_id_text)

        self.name_lable = QLabel(    f"Eventname   : {self.name}")
        self.days_lable = QLabel(    f"Tage        : {day_str}")
        self.menues_lable = QLabel(  f"Menüs       : {gerichte_str}")
        self.start_lable = QLabel(   f"Start       : {self.start}")
        self.end_lable   = QLabel(   f"End         : {self.end}")
        self.interval_lable = QLabel(f"Interval    : {self.interval}")


        for label in [self.name_lable, self.days_lable, self.menues_lable, self.start_lable, self.end_lable, self.interval_lable]:
            label.setStyleSheet("font-family: 'Courier New', monospace;")
            label.setMinimumHeight(5)

        self.layout_.addWidget(self.event_id_lable)
        self.layout_.addWidget(self.name_lable)
        self.layout_.addWidget(self.days_lable)
        self.layout_.addWidget(self.menues_lable)
        self.layout_.addWidget(self.start_lable)
        self.layout_.addWidget(self.end_lable)
        self.layout_.addWidget(self.interval_lable)

        self.layout_.addStretch()

        self.delete_button = QPushButton("Entfernen")
        self.delete_button.setStyleSheet("""
                    QPushButton {
                        background-color: #d32f2f;
                        color: white;
                        border: none;
                        padding: 6px 12px;
                        border-radius: 4px;
                    }
                    QPushButton:hover {
                        background-color: #b71c1c;
                    }
                    
                    
                """)
        self.delete_button.clicked.connect(self.delete_event)

        self.layout_.addWidget(self.delete_button)

        self.event_speichern()

    def delete_event(self):
        print(f"Delete event requested for: {self.name}")
        self.delete_requested.emit(self)  # Signal aussenden

        with open('events.json', 'r', encoding='utf-8') as file:
            self.events = json.load(file)  # config daten laden

        del self.events[self.event_id]

        with open("events.json", "w", encoding="utf-8") as f:
            json.dump(self.events, f, indent=2, ensure_ascii=False)

    def event_speichern(self):

        event_dict = {
            "name":  self.name,
            "days": self.days,
            "gerichte": self.gerichte,
            "start": self.start,
            "end": self.end,
            "interval": self.interval
        }

        self.events[self.event_id] = event_dict

        with open("events.json", "w", encoding="utf-8") as f:
            json.dump(self.events, f, indent=2, ensure_ascii=False)
