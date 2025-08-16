import os
import re
from importlib import reload

import hou
from PySide2 import QtWidgets, QtCore

from tracepath import _houdini

reload(_houdini)


class SaveFileDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(SaveFileDialog, self).__init__(parent=parent)

        self.scene_path = None
        self.resize(950, 220)
        self.setWindowTitle("Save File - TRACE")

        self.central_layout = QtWidgets.QVBoxLayout()
        self.central_layout.setAlignment(QtCore.Qt.AlignCenter)
        self.setLayout(self.central_layout)

        self.version_up_layout = QtWidgets.QHBoxLayout()
        self.version_up_layout.setAlignment(QtCore.Qt.AlignLeft)
        self.central_layout.addLayout(self.version_up_layout)

        self.version_up_label = QtWidgets.QLabel(self)
        self.version_up_label.setText("Version Up")
        self.version_up_layout.addWidget(self.version_up_label)

        self.version_up_check = QtWidgets.QCheckBox()
        self.version_up_check.setChecked(_houdini.is_fresh_scene())
        self.version_up_check.setDisabled(_houdini.is_fresh_scene())
        self.version_up_layout.addWidget(self.version_up_check)

        self.input_label = QtWidgets.QLabel("Auto versioning is enabled - you can’t edit the name.")
        self.central_layout.addWidget(self.input_label)

        self.name_input = QtWidgets.QLineEdit()
        self.name_input.setPlaceholderText("my_new_scene")
        self.name_input.setText(_houdini.get_current_file_name())
        self.name_input.setObjectName("scene_name")
        self.name_input.setDisabled(_houdini.is_fresh_scene())
        self.central_layout.addWidget(self.name_input)

        spacerItem1 = QtWidgets.QSpacerItem(
            40, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        self.central_layout.addItem(spacerItem1)

        self.output_label = QtWidgets.QLabel("Your scene will be saved here:")
        self.central_layout.addWidget(self.output_label)

        self.output_path = QtWidgets.QLineEdit()
        self.output_path.setDisabled(True)
        self.output_path.setObjectName('SaveDialogOutput')
        self.central_layout.addWidget(self.output_path)

        spacerItem2 = QtWidgets.QSpacerItem(
            40, 7, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.MinimumExpanding)
        self.central_layout.addItem(spacerItem2)
        self.save_button = QtWidgets.QPushButton("Save")
        self.central_layout.addWidget(self.save_button)

        # Run on init
        self.get_scene_path_preview(self.name_input.text())
        
        # Signal connections
        self.name_input.textChanged.connect(self.validate_scene_name)
        self.name_input.textChanged.connect(self.get_scene_path_preview)
        self.version_up_check.toggled.connect(self.on_version_up_toggled)
        self.save_button.clicked.connect(self.save_scene)

        # Style
        style_folder = os.environ.get("STYLE_TRACEPATH")
        style = ""
        if style_folder:
            style_file = os.path.join(style_folder, "style.qss")
            if os.path.isfile(style_file):
                with open(style_file, 'r') as f:
                    style = f.read()
        self.setStyleSheet(style)

    def on_version_up_toggled(self, checked: bool):
        self.name_input.setDisabled(checked)
        self.name_input.setPlaceholderText("my_new_scene" if not checked else "")
        self.name_input.setText(_houdini.get_current_file_name() if checked else "")
        self.input_label.setText(
            "Auto versioning is enabled - you can’t edit the name."
            if checked else
            "Type your scene name"
        )

    def get_scene_path_preview(self, text):
        name = re.sub(r'[^a-zA-Z0-9]', '_', text)

        self.scene_path = _houdini.make_scene_path("houdini", scene_name=name)
        self.output_path.setText(self.scene_path or "")

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
        if self.name_input.text():
            _houdini.save_scene(self.scene_path)
            self.close()
        else:
            hou.ui.displayMessage(
                f"Scene name is empty. Please enter a valid scene name.",
                severity=hou.severityType.Error
            )


dialog = None


def show_houdini():
    import hou
    global dialog
    dialog = SaveFileDialog(parent=hou.qt.mainWindow())
    dialog.show()
    return dialog
