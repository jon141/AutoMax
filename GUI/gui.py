
import sys
from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                               QLabel, QGridLayout, QScrollArea, QGroupBox, QFrame)
from PySide6.QtCore import QTimer
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QPushButton
import json


from widgets import DaySelection, MealSelection, EventName, DatePlaner, Event, RepetitionSelection

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AutoMax Koniguration")
        #self.setMinimumSize(1200, 950)
        self.resize(1250, 950)

        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        self.setStyleSheet("""
                    QWidget {
                        background-color: #1a1a1a;
                        color: #ffffff;
                        font-family: 'Segoe UI', sans-serif;
                    }
                    QGroupBox {
                        font-size: 14px;
                        font-weight: bold;
                        border: 2px solid #333333;
                        border-radius: 8px;
                        margin-top: 10px;
                        padding-top: 10px;
                        background-color: #1f1f1f;
                    }
                    QGroupBox::title {
                        subcontrol-origin: margin;
                        subcontrol-position: top left;
                        padding: 0px;
                        margin-top: -6px; /* reduziert vertikalen Abstand */
                        color: #29b6f6;
                    }
                    QScrollArea {
                        border: none;
                        background-color: #1a1a1a;
                    }
                    QScrollBar:vertical {
                        background: #2a2a2a;
                        width: 12px;
                        border-radius: 6px;
                    }
                    QScrollBar::handle:vertical {
                        background: #555555;
                        border-radius: 6px;
                        min-height: 20px;
                    }
                    QScrollBar::handle:vertical:hover {
                        background: #666666;
                    }
                """)

        testgroup = self.create_group_box('TEST')
        # testgroup.setMinimumSize(1234, 123)

        testgroup_layout = QVBoxLayout()

        self.eventname = EventName()
        testgroup_layout.addWidget(self.eventname)

        self.wochentag = DaySelection()
        testgroup_layout.addWidget(self.wochentag)

        self.gerichte = MealSelection()
        testgroup_layout.addWidget(self.gerichte)

        self.date_planer = DatePlaner()
        testgroup_layout.addWidget(self.date_planer)

        self.interval_input = RepetitionSelection()
        testgroup_layout.addWidget(self.interval_input)

        testgroup.setLayout(testgroup_layout)

        main_layout.addWidget(testgroup)

        # Button hinzufügen
        self.show_days_button = QPushButton("Create Event...")



        self.show_days_button.clicked.connect(lambda: self.create_event(self.eventname.get_event_name(), self.wochentag.get_selected_days(), self.gerichte.get_selected_gerichte(),self.date_planer.get_date_interval(), self.interval_input.get_interval()))
        main_layout.addWidget(self.show_days_button)

        # EVENTS GroupBox und Layout
        self.events = self.create_group_box('EVENTS')
        self.events_layout = QVBoxLayout()
        self.events.setLayout(self.events_layout)

        # ScrollArea anlegen und mit EVENTS GroupBox befüllen
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.events)
        self.scroll_area.setMinimumHeight(300)  # optional, damit ScrollArea sichtbar ist

        main_layout.addWidget(self.scroll_area)  # Hier ScrollArea hinzufügen, NICHT self.events



        self.load_events()

        testgroup_layout.addStretch()
        main_layout.addStretch()

    def create_group_box(self, title):
        """Erstellt eine GroupBox mit einheitlichem Styling"""
        group = QGroupBox(title)
        return group

    def create_event(self, name, wochentage, gerichte, date_planer, interval):

        if wochentage != []:
            event = Event(name, wochentage, gerichte, date_planer[0], date_planer[1], interval, False)
            event.delete_requested.connect(self.remove_event)  # Verbindung herstellen
            self.events_layout.addWidget(event)

    def remove_event(self, event_widget):
        self.events_layout.removeWidget(event_widget)
        event_widget.setParent(None)
        event_widget.deleteLater()

    def load_events(self):
        with open('events.json', 'r', encoding='utf-8') as file:
            events = json.load(file)  # config daten laden

        for event in events:
            id_ = event
            name = events[event]['name']

            wochentage = events[event]['days']
            gerichte = events[event]['gerichte']
            start = events[event]['start']
            end = events[event]['end']
            interval = events[event]['interval']

            this_event = Event(name, wochentage, gerichte, start, end, interval, id_)
            this_event.delete_requested.connect(self.remove_event)  # Verbindung herstellen
            self.events_layout.addWidget(this_event)



    def update_data(self):
        pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())