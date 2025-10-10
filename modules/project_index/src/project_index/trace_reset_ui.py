import json
import logging
import os
import shutil
import sys
from functools import partial

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

try:
    from PySide6 import QtCore, QtGui, QtWidgets
except ImportError:
    from PySide2 import QtCore, QtGui, QtWidgets


class TraceResetUI(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(TraceResetUI, self).__init__(parent=parent)
        style_folder = os.environ.get("STYLE_PROJECT_INDEX")
        framework = os.getenv("PR_TRACEPATH_FRAMEWORK")

        self.project_index_path = os.path.join(framework, "config/trace_project_index.json")
        with open(self.project_index_path, "r") as read_file:
            self.pr_index_read = json.load(read_file)

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

        self.projects.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)

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

        # Functions executed on init
        self.populate_project_list()

        # Signals
        self.projects.itemSelectionChanged.connect(self.on_project_changed)
        for widget in (self.projects, self.groups, self.items, self.tasks):
            widget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
            widget.customContextMenuRequested.connect(partial(self.open_mark_to_del_menu, widget))

        self.marked_to_delete.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.marked_to_delete.customContextMenuRequested.connect(self.open_restore_menu)

        self.delete_btn.clicked.connect(self.on_delete_button_exec)

    # Project components browsing

    def get_selection(self, widget):
        selected = widget.selectedItems()
        return selected[0].text() if selected else None

    def selected_project(self):
        return self.get_selection(self.projects)

    def populate_project_list(self):
        for i in self.pr_index_read.keys():
            item = QtWidgets.QListWidgetItem(i)
            preview_path = {f"{i}"}

            item.setData(QtCore.Qt.UserRole, i)
            # Add another data entry for the path preview
            item.setData(QtCore.Qt.UserRole + 1, preview_path)
            self.projects.addItem(item)

    def on_project_changed(self):
        self.groups.clear()
        project = self.selected_project()
        if not project:
            return
        groups = self.pr_index_read[project]["groups"]
        groups = dict(sorted(groups.items()))
        for group, meta in groups.items():
            item = QtWidgets.QListWidgetItem(group)

            preview_path = {f"{project}/{group}"}

            item.setData(QtCore.Qt.UserRole, group)
            # Add another data entry for the path preview
            item.setData(QtCore.Qt.UserRole + 1, preview_path)

            self.groups.addItem(item)

    # TODO implement on_group_changed and on_item_chnaged
    def on_group_changed(self):
        pass

    def in_item_changed(self):
        pass

    # Project data modification:

    def open_mark_to_del_menu(self, widget, position):
        """
        Opens the right-click context menu for the selected item.
        """
        item = widget.itemAt(position)
        menu = QtWidgets.QMenu(self)

        if item:
            mark_to_delete = menu.addAction("Mark to delete")
            mark_to_delete.triggered.connect(partial(self.add_to_delete_list, item))

        menu.exec(widget.viewport().mapToGlobal(position))

    def add_to_delete_list(self, item):

        metadata = item.data(QtCore.Qt.UserRole)

        preview_path = next(iter(item.data(QtCore.Qt.UserRole + 1)))
        item = QtWidgets.QListWidgetItem(preview_path)

        item.setData(QtCore.Qt.UserRole, metadata)
        self.marked_to_delete.addItem(item)

    def open_restore_menu(self, position):
        item = self.marked_to_delete.itemAt(position)
        menu = QtWidgets.QMenu(self)

        if item:
            restore_menu = menu.addAction("Restore item")
            restore_menu.triggered.connect(partial(self.restore_item_from_del_list, item))

        menu.exec(self.marked_to_delete.viewport().mapToGlobal(position))

    def restore_item_from_del_list(self, item):
        self.marked_to_delete.takeItem(self.marked_to_delete.row(item))

    def on_delete_button_exec(self):
        for idx in range(self.marked_to_delete.count()):
            item = self.marked_to_delete.item(idx)
            item_data = item.data(QtCore.Qt.UserRole)

            # Delete item from project index json file
            self.recursive_delete(self.pr_index_read, item_data)

            # Delete folder
            projects = os.environ.get("PR_PROJECTS_PATH")

            folder_to_remove = os.path.join(projects, item.text())
            shutil.rmtree(folder_to_remove)
            # TODO Add UI popup window listing the folders that were deleted
            logging.info(f"Removed: {folder_to_remove}")

        with open(self.project_index_path, "w") as write_file:
            json.dump(self.pr_index_read, write_file, indent=4)

    def recursive_delete(self, meta, key_to_delete):
        """
        Recursively deletes an entry by key from a nested dictionary.
        """
        if isinstance(meta, dict):
            # Attempt to delete the key, returns None if the key is not found in the first step of the iteration
            meta.pop(key_to_delete, None)
            # Iterate over the remaining items to continue the recursion.
            # Iterates over a copy of the keys (list(meta.items()))
            for key, value in list(meta.items()):
                # Recurse into the value if it is another dictionary
                if isinstance(value, dict):
                    self.recursive_delete(value, key_to_delete)

    # TODO All main shot manifest and published data clean up


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = TraceResetUI()
    w.show()
    sys.exit(app.exec())
