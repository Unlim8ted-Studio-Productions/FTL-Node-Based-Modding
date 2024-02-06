from PySide6 import QtWidgets, QtGui, QtCore
from node_editor.gui.node_list import NodeList
from node_editor.gui.node_widget import NodeWidget
import logging
import os
from pathlib import Path
import importlib
import inspect

logging.basicConfig(level=logging.DEBUG)


class NodeEditor(QtWidgets.QMainWindow):
    OnProjectPathUpdate = QtCore.Signal(Path)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = None
        self.project_path = None
        self.imports = None  # we will store the project import node types here for now.

        icon = QtGui.QIcon("resources\\app.ico")
        self.setWindowIcon(icon)

        self.setWindowTitle("FTL Node Based Modding")
        settings = QtCore.QSettings("node-editor", "NodeEditor")

        # create a "File" menu and add an "Export CSV" action to it
        file_menu = QtWidgets.QMenu("File", self)
        self.menuBar().addMenu(file_menu)

        load_action = QtGui.QAction("Load Project", self)
        load_action.triggered.connect(self.get_project_path)
        file_menu.addAction(load_action)

        save_action = QtGui.QAction("Save Project", self)
        save_action.triggered.connect(self.save_project)
        file_menu.addAction(save_action)
                
        create_ship_action = QtGui.QAction("Create New Ship", self)
        create_ship_action.triggered.connect(self.opensuperluminal2)
        file_menu.addAction(create_ship_action)

        create_node_action = QtGui.QAction("Create Node", self)
        create_node_action.triggered.connect(self.create_node)
        file_menu.addAction(create_node_action)

        # Layouts
        main_widget = QtWidgets.QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QtWidgets.QHBoxLayout()
        main_widget.setLayout(main_layout)
        left_layout = QtWidgets.QVBoxLayout()
        left_layout.setContentsMargins(0, 0, 0, 0)

        # Widgets
        self.node_list = NodeList(self)
        left_widget = QtWidgets.QWidget()
        self.splitter = QtWidgets.QSplitter()
        self.node_widget = NodeWidget(self)
        self.inspector_panel = NodeInspector()

        # Add Widgets to layouts
        self.splitter.addWidget(left_widget)
        self.splitter.addWidget(self.node_widget)
        self.splitter.addWidget(self.inspector_panel)
        left_widget.setLayout(left_layout)
        left_layout.addWidget(self.node_list)
        main_layout.addWidget(self.splitter)

        # Load the example project
        example_project_path = (Path(__file__).parent.resolve() / 'Example_project')
        self.load_project(example_project_path)

        # Restore GUI from last state
        if settings.contains("geometry"):
            self.restoreGeometry(settings.value("geometry"))

            s = settings.value("splitterSize")
            self.splitter.restoreState(s)

    def save_project(self):
        file_dialog = QtWidgets.QFileDialog()
        file_dialog.setAcceptMode(QtWidgets.QFileDialog.AcceptSave)
        file_dialog.setDefaultSuffix("json")
        file_dialog.setNameFilter("JSON files (*.json)")
        file_path, _ = file_dialog.getSaveFileName()
        self.node_widget.save_project(file_path)

    def load_project(self, project_path=None):
        if not project_path:
            return

        project_path = Path(project_path)
        if project_path.exists() and project_path.is_dir():
            self.project_path = project_path

            self.imports = {}

            for file in project_path.glob("*.py"):
                if not file.stem.endswith('_node'):
                    print('file:', file.stem)
                    continue
                spec = importlib.util.spec_from_file_location(file.stem, file)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                for name, obj in inspect.getmembers(module):
                    if not name.endswith('_Node'):
                        continue
                    if inspect.isclass(obj):
                        self.imports[obj.__name__] = {"class": obj, "module": module}

            self.node_list.update_project(self.imports)

            # work on just the first json file. add the ability to work on multiple json files later
            for json_path in project_path.glob("*.json"):
                self.node_widget.load_scene(json_path, self.imports)
                break

    def get_project_path(self):
        project_path = QtWidgets.QFileDialog.getExistingDirectory(None, "Select Project Folder", "")
        if not project_path:
            return

        self.load_project(project_path)

    def closeEvent(self, event):
        """
        Handles the close event by saving the GUI state and closing the application.

        Args:
            event: Close event.

        Returns:
            None.
        """

        # debugging lets save the scene:
        # self.node_widget.save_project("C:/Users/Howard/simple-node-editor/Example_Project/test.json")

        self.settings = QtCore.QSettings("node-editor", "NodeEditor")
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.setValue("splitterSize", self.splitter.saveState())
        QtWidgets.QWidget.closeEvent(self, event)

    def create_node(self):
        dialog = NodeCreationDialog(self)
        dialog.exec_()


class NodeCreationDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Create New Node")
        layout = QtWidgets.QVBoxLayout()

        self.type_label = QtWidgets.QLabel("Node Type:")
        self.type_combo = QtWidgets.QComboBox()
        self.type_combo.addItems(["Dropdown", "Text Input", "Number Input", "Slider", "Checkbox", "File Input"])

        self.name_label = QtWidgets.QLabel("Node Name:")
        self.name_edit = QtWidgets.QLineEdit()

        self.create_button = QtWidgets.QPushButton("Create")
        self.create_button.clicked.connect(self.create_node)

        layout.addWidget(self.type_label)
        layout.addWidget(self.type_combo)
        layout.addWidget(self.name_label)
        layout.addWidget(self.name_edit)
        layout.addWidget(self.create_button)

        self.setLayout(layout)

    def create_node(self):
        node_type = self.type_combo.currentText()
        node_name = self.name_edit.text()

        # Depending on node_type, create specific node
        if node_type == "Dropdown":
            node = DropdownNode(name=node_name)
        elif node_type == "Text Input":
            node = TextInputNode(name=node_name)
        elif node_type == "Number Input":
            node = NumberInputNode(name=node_name)
        elif node_type == "Slider":
            node = SliderNode(name=node_name)
        elif node_type == "Checkbox":
            node = CheckboxNode(name=node_name)
        elif node_type == "File Input":
            node = FileInputNode(name=node_name)

        # Do something with the created node, for example, add it to the node editor widget
        # self.parent().node_widget.add_node(node)

        self.close()


# Define specific node classes for each type
class DropdownNode(QtWidgets.QWidget):
    def __init__(self, name="", parent=None):
        super().__init__(parent)
        self.name = name
        # Add necessary widgets and layout for dropdown node


class TextInputNode(QtWidgets.QWidget):
    def __init__(self, name="", parent=None):
        super().__init__(parent)
        self.name = name
        # Add necessary widgets and layout for text input node


class NumberInputNode(QtWidgets.QWidget):
    def __init__(self, name="", parent=None):
        super().__init__(parent)
        self.name = name
        # Add necessary widgets and layout for number input node


class SliderNode(QtWidgets.QWidget):
    def __init__(self, name="", parent=None):
        super().__init__(parent)
        self.name = name
        # Add necessary widgets and layout for slider node


class CheckboxNode(QtWidgets.QWidget):
    def __init__(self, name="", parent=None):
        super().__init__(parent)
        self.name = name
        # Add necessary widgets and layout for checkbox node


class FileInputNode(QtWidgets.QWidget):
    def __init__(self, name="", parent=None):
        super().__init__(parent)
        self.name = name
        # Add necessary widgets and layout for file input node


class NodeInspector(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Node Inspector")
        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)
        self.node = None

    def inspect_node(self, node):
        self.clear_inspector()
        self.node = node
        # Add inspector widgets based on the type of node

    def clear_inspector(self):
        self.node = None
        for i in reversed(range(self.layout.count())):
            widget = self.layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()


if __name__ == "__main__":
    import sys

    import qdarktheme

    app = QtWidgets.QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon("resources\\app.ico"))
    qdarktheme.setup_theme()

    launcher = NodeEditor()
    launcher.show()
    sys.exit(app.exec())
