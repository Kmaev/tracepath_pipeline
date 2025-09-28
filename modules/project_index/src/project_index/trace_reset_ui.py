import os
import sys

try:
    from PySide6 import QtCore, QtGui, QtWidgets
except ImportError:
    from PySide2 import QtCore, QtGui, QtWidgets


class TraceResetUI(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(TraceResetUI, self).__init__(parent=parent)
        style_folder = os.environ.get("STYLE_PROJECT_INDEX")
        framework = os.getenv("PR_TRACEPATH_FRAMEWORK")

        self.resize(1400, 900)
        self.setWindowTitle('Trace Reset v0.1.6')
        self.central_widget = QtWidgets.QWidget(self)
        self.central_layout = QtWidgets.QVBoxLayout(self.central_widget)
        self.setCentralWidget(self.central_widget)

        self.splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        self.splitter.setContentsMargins(10, 10, 10, 10)
        self.splitter.setChildrenCollapsible(False)
        self.splitter.setSizes([3, 1])
        self.central_layout.addWidget(self.splitter)
        
        # Display widgets
        # ===============================================================================
        self.display_widget = QtWidgets.QWidget()
        self.display_widget.setMinimumHeight(200)
        self.splitter.addWidget(self.display_widget)
        self.display_layout = QtWidgets.QHBoxLayout()
        self.display_widget.setLayout(self.display_layout)

        # Project List
        self.projects_layout = QtWidgets.QVBoxLayout()
        self.display_layout.addLayout(self.projects_layout)

        self.projects_label = QtWidgets.QLabel("Projects")
        self.projects_layout.addWidget(self.projects_label)

        self.projects = QtWidgets.QListWidget(self)
        self.projects_layout.addWidget(self.projects)

        # Group List
        self.groups_layout = QtWidgets.QVBoxLayout()
        self.display_layout.addLayout(self.groups_layout)

        self.groups_label = QtWidgets.QLabel("Groups")
        self.groups_layout.addWidget(self.groups_label)

        self.groups = QtWidgets.QListWidget(self)
        self.groups_layout.addWidget(self.groups)

        # Item List
        self.items_layout = QtWidgets.QVBoxLayout()
        self.display_layout.addLayout(self.items_layout)

        self.items_label = QtWidgets.QLabel("Items")
        self.items_layout.addWidget(self.items_label)

        self.items = QtWidgets.QListWidget(self)
        self.items_layout.addWidget(self.items)

        # Task List
        self.tasks_layout = QtWidgets.QVBoxLayout()
        self.display_layout.addLayout(self.tasks_layout)

        self.tasks_label = QtWidgets.QLabel("Tasks")
        self.tasks_layout.addWidget(self.tasks_label)

        self.tasks = QtWidgets.QListWidget(self)
        self.tasks_layout.addWidget(self.tasks)

        # Main USD List
        self.main_usd_layout = QtWidgets.QVBoxLayout()
        self.display_layout.addLayout(self.main_usd_layout)

        self.main_usd_label = QtWidgets.QLabel("Main Versions")
        self.main_usd_layout.addWidget(self.main_usd_label)

        self.main_usd = QtWidgets.QListWidget(self)
        self.main_usd_layout.addWidget(self.main_usd)

        # Delete widgets
        # ===============================================================================
        self.delete_widget = QtWidgets.QWidget()
        self.delete_widget.setMinimumHeight(200)
        self.splitter.addWidget(self.delete_widget)

        self.delete_layout = QtWidgets.QVBoxLayout()
        self.delete_widget.setLayout(self.delete_layout)

        # Marked to Delete List
        self.marked_to_del_label = QtWidgets.QLabel("Marked to Delete")
        self.delete_layout.addWidget(self.marked_to_del_label)

        self.marked_to_delete = QtWidgets.QListWidget(self)
        self.delete_layout.addWidget(self.marked_to_delete)

        # Delete Button
        self.delete_btn = QtWidgets.QPushButton("Delete")
        self.delete_layout.addWidget(self.delete_btn)

        # Resize Splitter
        self.splitter.setSizes([int(self.splitter.height() * 0.6), int(self.splitter.height() * 0.4)])

        # Load and set style
        style = ""
        if style_folder:
            style_file = os.path.join(style_folder, "style.qss")
            if os.path.isfile(style_file):
                with open(style_file, 'r') as f:
                    style = f.read()
        self.setStyleSheet(style)

        if self.parent():
            self.parent().setStyleSheet(self.parent().styleSheet())


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = TraceResetUI()
    w.show()
    sys.exit(app.exec())
