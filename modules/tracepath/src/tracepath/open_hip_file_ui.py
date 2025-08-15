import os

import hou
from PySide2 import QtWidgets, QtCore

from tracepath import _houdini


class OpenFileDialog(QtWidgets.QDialog):
    def __init__(self, dcc, parent=None):
        super(OpenFileDialog, self).__init__(parent=parent)
        self.setObjectName('OpenDialog')
        self.resize(800, 500)

        self.central_layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.central_layout)

        self.root_label = QtWidgets.QLabel("Root:")

        self.user_data = _houdini.get_task_context()
        self.user_data = os.path.join(self.user_data, f"{dcc}/scenes")

        self.tree_widget = QtWidgets.QTreeWidget(self)
        self.tree_widget.setHeaderLabels([self.user_data])

        self.load_button = QtWidgets.QPushButton("Load")

        self.central_layout.addWidget(self.root_label)
        self.central_layout.addWidget(self.tree_widget)
        self.central_layout.addWidget(self.load_button)

        self.populate_tree()

        self.load_button.clicked.connect(self.on_load)
        self.tree_widget.itemDoubleClicked.connect(self.on_load)

        style_folder = os.environ.get("STYLE_TRACEPATH")
        style = ""
        if style_folder:
            style_file = os.path.join(style_folder, "style.qss")
            if os.path.isfile(style_file):
                with open(style_file, 'r') as f:
                    style = f.read()
        self.setStyleSheet(style)

    def populate_tree(self):
        root = self.tree_widget.invisibleRootItem()
        hip_folders = [i for i in sorted(os.listdir(self.user_data)) if not i.startswith(".")]

        for hip_folder in hip_folders:

            hip_folder_item = QtWidgets.QTreeWidgetItem(root)
            hip_folder_item.setText(0, hip_folder)

            folder_path = os.path.join(self.user_data, hip_folder)
            hip_files = [i for i in sorted(os.listdir(folder_path)) if not i.startswith(".")]
          
            for hip_file in hip_files:
                hip_file_path = os.path.join(folder_path, hip_file)
                display_name = hip_file.split("/")[-1]
                hip_file_item = QtWidgets.QTreeWidgetItem(hip_folder_item)
                hip_file_item.setText(0, display_name)

                if hip_file.endswith(".hip"):
                    hip_file_item.setData(0, QtCore.Qt.UserRole, hip_file_path)
                    hip_file_item.setText(0, hip_file)

    def on_load(self):
        item = self.tree_widget.selectedItems()[0]
        scene_path = item.data(0, QtCore.Qt.UserRole)
        hou.hipFile.load(scene_path)
        self.close()


dialog = None


def show_houdini():
    import hou
    global dialog
    dialog = OpenFileDialog("houdini", parent=hou.qt.mainWindow())
    dialog.show()
    return dialog
