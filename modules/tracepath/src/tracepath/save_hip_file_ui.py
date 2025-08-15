from importlib import reload
from PySide2 import QtWidgets, QtCore
from tracepath import _houdini
import os
import re
reload(_houdini)


class SaveFileDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(SaveFileDialog, self).__init__(parent=parent)
        self.resize(550, 200)

        self.central_layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.central_layout)
        # self.central_layout.setSpacing(10)
        self.central_layout.setAlignment(QtCore.Qt.AlignTop)

        self.input_label = QtWidgets.QLabel("Type scene name to save")
        self.central_layout.addWidget(self.input_label)

        self.name_input = QtWidgets.QLineEdit()
        self.name_input.setPlaceholderText("my_new_houdini_scene")
        self.central_layout.addWidget(self.name_input)

        spacerItem1 = QtWidgets.QSpacerItem(
            40, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        self.central_layout.addItem(spacerItem1)

        self.output_label = QtWidgets.QLabel("Your scene will be saved here:")
        self.central_layout.addWidget(self.output_label)

        self.output_path = QtWidgets.QLineEdit()
        self.output_path.setReadOnly(True)
        # self.output_path.setDisabled(True)
        self.output_path.setObjectName('SaveDialogOutput')
        self.central_layout.addWidget(self.output_path)

        spacerItem2 = QtWidgets.QSpacerItem(
            40, 7, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.MinimumExpanding)
        self.central_layout.addItem(spacerItem2)
        self.save_button = QtWidgets.QPushButton("Save")
        self.central_layout.addWidget(self.save_button)

        self.name_input.textChanged.connect(self.validate_scene_name)
        self.name_input.textChanged.connect(self.get_scene_path_preview)

        self.save_button.clicked.connect(self.save_scene)

        style_folder = os.environ.get("STYLE_TRACEPATH")
        style = ""
        if style_folder:
            style_file = os.path.join(style_folder, "style.qss")
            if os.path.isfile(style_file):
                with open(style_file, 'r') as f:
                    style = f.read()
        self.setStyleSheet(style)

    def get_scene_path_preview(self, text):
        name = re.sub(r'[^a-zA-Z0-9]', '_', text)
        self.scene_path = _houdini.make_scene_path("houdini",scene_name=name)
        self.output_path.setText(self.scene_path)

    def validate_scene_name(self):
        item = self.name_input
        text = item.text()
        safe = re.sub(r'[^A-Za-z0-9_-]+', '_', text)
        if safe != item.text:
            # Block signals to prevent setText() from re-triggering itemChanged
            # and triggering validate_item_name to run again in a loop.
            old = self.name_input.blockSignals(True)
            item.setText(safe)
            self.name_input.blockSignals(old)

    def save_scene(self):
        _houdini.save_scene(self.scene_path)
        self.close()


dialog = None


def show_houdini():
    import hou
    global dialog
    dialog = SaveFileDialog(parent=hou.qt.mainWindow())
    dialog.show()
    return dialog
