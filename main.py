from PySide6 import QtWidgets, QtGui, QtCore
from node_editor.connection import Connection
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
        self.project_path = Path(__file__).parent.resolve() / "nodes"
        self.load_project(self.project_path)

        # Restore GUI from last state
        if settings.contains("geometry"):
            self.restoreGeometry(settings.value("geometry"))

            s = settings.value("splitterSize")
            self.splitter.restoreState(s)

    def save_project(self):
        print(self.node_widget.scene.items())
        file_dialog = QtWidgets.QFileDialog()
        file_dialog.setAcceptMode(QtWidgets.QFileDialog.AcceptSave)
        file_dialog.setDefaultSuffix("json")
        file_dialog.setNameFilter("JSON files (*.json)")
        file_path, _ = file_dialog.getSaveFileName()
        self.node_widget.save_project(file_path)

    def load_project(self, project_path=None, loadscene=True):
        if not project_path:
            return

        project_path = Path(project_path)
        if project_path.exists() and project_path.is_dir():
            self.project_path = project_path

            self.imports = {}

            for file in project_path.glob("*.py"):
                if not file.stem.endswith("_node"):
                    print("file:", file.stem)
                    continue
                spec = importlib.util.spec_from_file_location(file.stem, file)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                for name, obj in inspect.getmembers(module):
                    if not name.endswith("_Node"):
                        continue
                    if inspect.isclass(obj):
                        self.imports[obj.__name__] = {"class": obj, "module": module}

            self.node_list.update_project(self.imports)

            # work on just the first json file. add the ability to work on multiple json files later
            if loadscene:
                for json_path in project_path.glob("*.json"):
                    self.node_widget.load_scene(json_path, self.imports)
                    break

    def get_project_path(self):
        project_path = QtWidgets.QFileDialog.getExistingDirectory(
            None, "Select Project Folder", ""
        )
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
        if dialog.exec_():
            node, filepath = dialog.create_node()
            if node:
                self.load_project(self.project_path, False)

    def opensuperluminal2(self):
        """ "This function opens the Superluminal 2 software and returns a message indicating whether the software was successfully opened or not.
        Parameters:
            - self (object): The object instance of the Superluminal 2 software.
        Returns:
            - str: A message indicating whether the software was successfully opened or not.
        Processing Logic:
            - Checks if the Superluminal 2 software is installed.
            - If installed, opens the software.
            - If not installed, returns an error message.
            - If successfully opened, returns a success message."""
        pass  # wont work for some reason


class NodeCreationDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Create New Node")
        layout = QtWidgets.QVBoxLayout()

        self.name_label = QtWidgets.QLabel("Node Name:")
        self.name_edit = QtWidgets.QLineEdit()
        self.type_label = QtWidgets.QLabel("Node Type:")
        self.type_edit = QtWidgets.QLineEdit()

        self.create_button = QtWidgets.QPushButton("Create")
        self.create_button.clicked.connect(self.accept)

        layout.addWidget(self.name_label)
        layout.addWidget(self.name_edit)
        layout.addWidget(self.type_label)
        layout.addWidget(self.type_edit)
        layout.addWidget(self.create_button)

        self.setLayout(layout)

    def create_node(self):
        # node_type = self.type_combo.currentText()
        node_name = self.name_edit.text()
        node_type = self.type_edit.text()

        node = base_node(node_name, node_type)  # , filename=node_name+r"_node.py")

        return node, r"/node" + node_name + r"_node.py"


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


from node_editor.node import Node


class base_node(Node):
    def __init__(self, title, type):
        super().__init__()

        self.title_text = title
        self.type_text = type
        self.set_color(title_color=(0, 128, 0))

        self.add_pin(name="Ex In", is_output=False, execution=True)
        self.add_pin(name="Ex Out", is_output=True, execution=True)

        self.build()


if __name__ == "__main__":
    import sys

    import qdarktheme

    app = QtWidgets.QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon("resources\\app.ico"))
    qdarktheme.setup_theme()

    launcher = NodeEditor()
    launcher.show()
    sys.exit(app.exec())
