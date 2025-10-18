import json
import logging
import os
import shutil
import sys
from functools import partial, reduce
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

try:
    from PySide6 import QtCore, QtGui, QtWidgets
except ImportError:
    from PySide2 import QtCore, QtGui, QtWidgets


# TODO:
# 1. Change UI layout: The tasks list widget and main_usd list widget should be in a separate group widget
# and appear one on top of the other, as both are populated when an item is selected in the items list widget.

# 2. Add a right-click context menu to items in the main_usd list  widget to allow exploring the content of the USD file.
# Possible scenarios:
# A. Add a text edit area to output the USD file content.
# B. Add an 'Open in USD View' action for file inspection.
# C. Implement both options (A and B).


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

        self.pr_projects_path = os.environ.get("PR_PROJECTS_PATH")

        self.central_widget = QtWidgets.QWidget(self)
        self.central_layout = QtWidgets.QVBoxLayout(self.central_widget)
        self.setCentralWidget(self.central_widget)

        self.splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        self.splitter.setContentsMargins(10, 10, 10, 10)
        self.splitter.setChildrenCollapsible(False)
        self.splitter.setSizes([3, 1])
        self.central_layout.addWidget(self.splitter)

        # DISPLAY WIDGETS ---------------------------------
        self.display_widget = QtWidgets.QWidget()
        self.display_widget.setMinimumHeight(200)
        self.splitter.addWidget(self.display_widget)
        self.display_layout = QtWidgets.QVBoxLayout()
        self.display_widget.setLayout(self.display_layout)

        # Project elements layout
        self.project_elements_layout = QtWidgets.QHBoxLayout()
        self.display_layout.addLayout(self.project_elements_layout)

        # Project List
        self.projects_layout = QtWidgets.QVBoxLayout()
        self.project_elements_layout.addLayout(self.projects_layout)

        self.projects_label = QtWidgets.QLabel("Projects")
        self.projects_layout.addWidget(self.projects_label)

        self.projects = QtWidgets.QListWidget(self)
        self.projects_layout.addWidget(self.projects)

        self.projects.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.projects.setMinimumHeight(300)

        # Group List
        self.groups_layout = QtWidgets.QVBoxLayout()
        self.project_elements_layout.addLayout(self.groups_layout)

        self.groups_label = QtWidgets.QLabel("Groups")
        self.groups_layout.addWidget(self.groups_label)

        self.groups = QtWidgets.QListWidget(self)
        self.groups_layout.addWidget(self.groups)

        # Item List
        self.items_layout = QtWidgets.QVBoxLayout()
        self.project_elements_layout.addLayout(self.items_layout)

        self.items_label = QtWidgets.QLabel("Items")
        self.items_layout.addWidget(self.items_label)

        self.items = QtWidgets.QListWidget(self)
        self.items_layout.addWidget(self.items)

        # Task List
        self.tasks_layout = QtWidgets.QVBoxLayout()
        self.project_elements_layout.addLayout(self.tasks_layout)

        self.tasks_label = QtWidgets.QLabel("Tasks")
        self.tasks_layout.addWidget(self.tasks_label)

        self.tasks = QtWidgets.QListWidget(self)
        self.tasks_layout.addWidget(self.tasks)

        # Item Versions Data  layout
        self.versions_data = QtWidgets.QVBoxLayout()
        self.display_layout.addLayout(self.versions_data)

        # Main USD List
        self.main_usd_layout = QtWidgets.QVBoxLayout()
        self.versions_data.addLayout(self.main_usd_layout)

        self.main_usd_label = QtWidgets.QLabel("Main Versions")
        self.main_usd_layout.addWidget(self.main_usd_label)

        self.main_usd = QtWidgets.QListWidget(self)
        self.main_usd_layout.addWidget(self.main_usd)

        # Main USD data
        self.usd_data_layout = QtWidgets.QVBoxLayout()
        self.versions_data.addLayout(self.usd_data_layout)

        self.usd_data_label = QtWidgets.QLabel("Detail View")
        self.main_usd_layout.addWidget(self.usd_data_label)

        self.usd_data = QtWidgets.QTextEdit()
        self.main_usd_layout.addWidget(self.usd_data)

        # DELETE WIDGETS ---------------------------------
        self.delete_widget = QtWidgets.QWidget()
        self.delete_widget.setMinimumHeight(150)
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
        self.splitter.setSizes([int(self.splitter.height() * 0.8), int(self.splitter.height() * 0.2)])

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

        # FUNCTIONS EXECUTED ON INIT ---------------------------------
        self.populate_project_list()

        # SIGNALS ---------------------------------
        self.projects.itemSelectionChanged.connect(self.on_project_changed)
        self.groups.itemSelectionChanged.connect(self.on_group_changed)
        self.items.itemSelectionChanged.connect(self.on_pr_item_changed)

        for widget in (self.projects, self.groups, self.items, self.tasks, self.main_usd):
            widget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
            widget.customContextMenuRequested.connect(partial(self.open_mark_to_del_menu, widget))

        self.marked_to_delete.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.marked_to_delete.customContextMenuRequested.connect(self.open_restore_menu)

        self.delete_btn.clicked.connect(self.on_del_exec)
        self.delete_btn.clicked.connect(self.clean_up_ui)

        # PROJECT COMPONENTS BROWSING ---------------------------------

    def get_selection(self, widget):
        selected = widget.selectedItems()
        return selected[0].text() if selected else None

    def selected_project(self):
        return self.get_selection(self.projects)

    def selected_group(self):
        return self.get_selection(self.groups)

    def selected_item(self):
        return self.get_selection(self.items)

    def selected_task(self):
        return self.get_selection(self.tasks)

    def create_list_item(self, item_name: str, parent_widget: object, metadata: dict):
        """
        Creates a QListWidgetItem, embeds metadata, and adds it to the parent widget.
        The function modifies the provided metadata by adding the 'item_name'.
        """
        item = QtWidgets.QListWidgetItem(item_name)
        metadata["item_name"] = item_name
        item.setData(QtCore.Qt.UserRole, metadata)
        parent_widget.addItem(item)

    def populate_project_list(self):
        for i in self.pr_index_read.keys():
            meta = {"preview_path": i, "project": i, "type": "project"}
            self.create_list_item(i, self.projects, meta)

    def get_nested_data(self, data: dict, data_keys: list) -> dict or None:
        """
        Retrieve data from the nested dictionary (project_index)
        """
        if not isinstance(data, dict):
            logging.warning("Invalid data provided; data must be a dictionary.")
            return
        result = reduce(lambda df, data_key: df.get(data_key) if isinstance(df, dict) else None, data_keys,
                        data)
        return result

    def on_project_changed(self):
        """
        Executes when the user changes the project selection.
        Clears all dependent widgets and, based on the newly selected project,
        populates the groups QListWidget.
        """
        self.main_usd.clear()
        self.tasks.clear()
        self.items.clear()
        self.groups.clear()
        project = self.selected_project()
        if not project:
            return
        data_keys = [project, "groups"]

        groups = self.get_nested_data(self.pr_index_read, data_keys)
        if not groups:
            logging.warning(f"No 'groups' data found in the index for project: '{project}'. Skipping population.")
            return
        for group, meta in groups.items():
            meta = {"preview_path": f"{project}/{group}", "project": project, "type": "group"}
            self.create_list_item(group, self.groups, meta)

    def on_group_changed(self):
        """
        Executes when the user changes the group selection.
        Clears all dependent widgets and, based on the newly selected group,
        populates the items QListWidget.
        """
        self.main_usd.clear()
        self.tasks.clear()
        self.items.clear()
        project = self.selected_project()
        group = self.selected_group()
        if not group or not project:
            return

        data_keys = [project, "groups", group, "items"]

        pr_items = self.get_nested_data(self.pr_index_read, data_keys)
        if not pr_items:
            logging.warning(
                f"No 'items' data found in the index for project: '{project}', group: '{group}'. Skipping population.")
            return
        for pr_item, meta in pr_items.items():
            meta = {"preview_path": f"{project}/{group}/{pr_item}", "project": project, "type": "item"}
            self.create_list_item(pr_item, self.items, meta)

    def read_published_data(self, show_data):
        """
        Reads project published data file
        """
        try:
            with open(show_data, "r") as data_read:
                published_data = json.load(data_read)
            return published_data
        except FileNotFoundError:
            logging.error(f"Show data file \n{self.pr_projects_path} is not found")
            return None

    def on_pr_item_changed(self):
        """
        Executes when the user changes the item selection.
        Clears all dependent widgets and, based on the newly selected item,
        populates the tasks and main_usd QListWidgets.
        Tasks and Main USD are populated at the same time because Main USD versioning
        is handled on a per-item basis and combines all the latest task edits.
        """
        self.main_usd.clear()
        self.tasks.clear()
        project = self.selected_project()
        group = self.selected_group()
        pr_item = self.selected_item()
        if not pr_item or not group or not project:
            return

        data_keys = [project, "groups", group, "items", pr_item, "tasks"]
        pr_tasks = self.get_nested_data(self.pr_index_read, data_keys)
        if pr_tasks:
            for pr_task, meta in pr_tasks.items():
                meta = {"preview_path": f"{project}/{group}/{pr_item}/{pr_task}",
                        "project": project, "type": "task"}
                self.create_list_item(pr_task, self.tasks, meta)
        else:
            logging.warning(
                f"No 'tasks' data found in the index for project: '{project}', group: '{group}', "
                f"item: '{pr_item}'. Skipping population.")

        show_data = os.path.join(self.pr_projects_path, project, "show_data/published_data.json")

        published_data = self.read_published_data(show_data)

        if not published_data:
            logging.warning(f"Failed to read published data file for project: '{project}'. Skipping version load.")
            return

        data_key = f"{group}_{pr_item}"
        if not data_key in published_data.keys():
            logging.warning(f"No published versions found for key '{group}_{pr_item}' in project data.")
            return

        for version in published_data[data_key].keys():
            ver_preview_name = version.split("/")[-1]

            meta = {"preview_path": version,
                    "project": project, "type": "main_usd"}
            self.create_list_item(ver_preview_name, self.main_usd, meta)

    # TODO Add main usd version data display, should output the content of selected main usd file
    def on_main_usd_version_changed(self):
        pass

    # PROJECT FOLDERS AND DATA MODIFICATION ---------------------------------
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

    def add_to_delete_list(self, orig_item):
        """
        Stages an item for deletion, creating a copy of the item in the marked_to_delete list.
        """
        metadata = orig_item.data(QtCore.Qt.UserRole)

        preview_path = metadata["preview_path"]

        item = QtWidgets.QListWidgetItem(preview_path)
        item.setData(QtCore.Qt.UserRole + 1, metadata)
        self.marked_to_delete.addItem(item)

    def open_restore_menu(self, position):
        """
        Opens the right-click context menu for the selected item to restore the item from the marked to delete list
        """
        item = self.marked_to_delete.itemAt(position)
        menu = QtWidgets.QMenu(self)

        if item:
            restore_menu = menu.addAction("Restore item")
            restore_menu.triggered.connect(partial(self.restore_item_from_del_list, item))

        menu.exec(self.marked_to_delete.viewport().mapToGlobal(position))

    def restore_item_from_del_list(self, item):
        self.marked_to_delete.takeItem(self.marked_to_delete.row(item))

    def _restore_selection(self, parent_widget, prev_selection):
        item_count = parent_widget.count()
        if not item_count:
            return
        if item_count > 0:
            for idx in range(item_count):
                item = parent_widget.item(idx)
                if item.text() == prev_selection:
                    parent_widget.setCurrentItem(item)
                    break
                else:
                    parent_widget.setCurrentRow(0)

    def clean_up_ui(self):
        """
        Executed after all data modifications (folders on disk, project_index, and show_data) are complete.
        Saves the current project, group, and item selections in temporary variables and clears all QListWidgets.
        Runs a new query on projects using the latest updated data, and then restores the previous selection.
        """
        self.marked_to_delete.clear()

        _cur_pr = self.selected_project()
        _cur_gr = self.selected_group()
        _cur_itm = self.selected_item()  # Use standard Python casing

        self.main_usd.clear()
        self.tasks.clear()
        self.items.clear()
        self.groups.clear()

        self.projects.clear()

        self.populate_project_list()

        self._restore_selection(self.projects, _cur_pr)
        self._restore_selection(self.groups, _cur_gr)
        self._restore_selection(self.items, _cur_itm)

        QtWidgets.QMessageBox.information(
            self,
            "Information",
            f"Selected items successfully removed"
        )

    def on_del_exec(self):
        """
        Called when delete button is executed. Modifies data on disk, project index
        """
        items_to_process = [self.marked_to_delete.item(i) for i in range(self.marked_to_delete.count())]

        for item in items_to_process:
            marked_item_meta = item.data(QtCore.Qt.UserRole + 1)

            path_to_remove = Path(self.pr_projects_path) / item.text()
            try:
                if marked_item_meta["type"] == "main_usd":
                    show_data = os.path.join(self.pr_projects_path, marked_item_meta["project"],
                                             "show_data/published_data.json")
                    published_data = self.read_published_data(show_data)
                    self.remove_meta_key_recursive(published_data, item.text())
                    with open(show_data, "w") as write_file:
                        json.dump(published_data, write_file, indent=4)

                self.remove_filesystem_item(path_to_remove)

                self.remove_meta_key_recursive(self.pr_index_read, marked_item_meta["item_name"])


            except Exception as e:
                logging.error(f"Failed to delete {path_to_remove} or update index: {e}")
                continue  # Move to the next item
        with open(self.project_index_path, "w") as write_file:
            json.dump(self.pr_index_read, write_file, indent=4)

    def remove_filesystem_item(self, path_to_remove):
        """
        Removes files from disk
        """
        if not path_to_remove.exists():
            logging.error(f"File not found: {path_to_remove}")
            raise FileNotFoundError(f"File not found: {path_to_remove}")
        try:
            if path_to_remove.is_file():
                parent = path_to_remove.parent
                path_to_remove.unlink()
                if not any(parent.iterdir()):
                    parent.rmdir()
                logging.info(f"Successfully removed file: {path_to_remove}")
            elif path_to_remove.is_dir():
                shutil.rmtree(path_to_remove)
                logging.info(f"Successfully removed folder: {path_to_remove}")
            else:
                logging.info(f"Skipped removal as it is not folder or file\n: {path_to_remove}")

        except PermissionError as e:
            logging.error(f"Permission denied while removing {path_to_remove}\n{e}")

    def remove_meta_key_recursive(self, meta, key_to_delete):
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
                    self.remove_meta_key_recursive(value, key_to_delete)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = TraceResetUI()
    w.show()
    sys.exit(app.exec())
