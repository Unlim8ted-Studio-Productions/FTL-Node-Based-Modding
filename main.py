import os
import random
import subprocess
import sys
from collections import defaultdict, deque
import uuid
import json
import xml.etree.ElementTree as ET
# import tempfile
from PySide6 import QtWidgets, QtGui, QtCore
import pyperclip

# from node_editor.connection import Connection
from node_editor.gui.node_list import NodeList
from node_editor.gui.node_widget import NodeScene, NodeWidget
import logging
from node_editor.node import Node

# import os
from pathlib import Path
import importlib
import inspect
from xml.etree.ElementTree import Element, SubElement, tostring
import win32gui
from PySide6.QtWidgets import (
    QLabel,
    QPushButton,
    QVBoxLayout,
    QSlider,
    QColorDialog,
    QInputDialog,
    QHBoxLayout,
    QGraphicsScene,
    QGraphicsView,
    QWidget,
    QComboBox,
    QTextEdit,
    QSizePolicy,
    QDockWidget,
    QFileDialog,
)
from PySide6.QtGui import (
    QKeyEvent,
    QPixmap,
    QPainter,
    QPen,
    QIcon,
    QColor,
    QPalette,
    QBrush,
)
from PySide6.QtCore import Qt, QRect, QTimer, QSize, QPoint
import win32process
from PySide6.QtGui import QKeySequence
from PySide6.QtGui import QShortcut

logging.basicConfig(level=logging.DEBUG)


class NodeEditorTab(QtWidgets.QMainWindow):
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
        load_action.triggered.connect(self.loadproject)
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
        self.scene = {"nodes": [], "connections": []}
        # Widgets
        self.node_list = NodeList(self)
        left_widget = QtWidgets.QWidget()
        self.splitter = QtWidgets.QSplitter()
        self.node_widget = NodeWidget(self)
        self.inspector_panel = Simulator(self.node_widget.save_project())

        # Add Widgets to layouts
        self.splitter.addWidget(left_widget)
        self.splitter.addWidget(self.node_widget)
        self.splitter.addWidget(self.inspector_panel)
        left_widget.setLayout(left_layout)
        left_layout.addWidget(self.node_list)
        main_layout.addWidget(self.splitter)
        self.selected = None

        compilea = QtGui.QAction("Compile to xml format", self)
        compilea.triggered.connect(self.compile_to_ftl)
        file_menu.addAction(compilea)

        self.shortcut = QShortcut(QKeySequence("Ctrl+S"), self)
        self.shortcut.activated.connect(self.save_project)
        # Load the example project
        self.project_path = Path(__file__).parent.resolve() / "nodes"
        self.scenes_path = Path(__file__).parent.resolve() / "scenes"
        self.timer = QTimer(self)
        self.timer.setInterval(200)  # Set the interval to 2000 milliseconds (2 seconds)
        self.timer.timeout.connect(self.setsimulationloc)
        self.timer.start()
        self.load_project(self.project_path, loadscene=False)

        # Restore GUI from last state
        if settings.contains("geometry"):
            self.restoreGeometry(settings.value("geometry"))

            s = settings.value("splitterSize")
            self.splitter.restoreState(s)
            
        # Add dock widget for the output console
        self.dock_console = QDockWidget("Console Output", self)
        self.dock_console.setFeatures(QDockWidget.NoDockWidgetFeatures)
        self.dock_console.setAllowedAreas(QtCore.Qt.BottomDockWidgetArea)
        self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, self.dock_console)

        # Console output widget
        self.console_output = QTextEdit()
        self.console_output.setReadOnly(True)
        self.console_output.setStyleSheet("background-color: black; color: white;")
        self.console_output.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        self.console_output.setMinimumHeight(20)  # Set the minimum height here
        self.dock_console.setWidget(self.console_output)

        # Redirect stdout and stderr to console output
        sys.stdout = StreamRedirect(self.console_output, sys.stdout)
        sys.stderr = StreamRedirect(self.console_output, sys.stderr)

    def setsimulationloc(
        self,
    ):
        if self.node_widget.node_editor._last_selected != None:
            if self.node_widget.node_editor._last_selected != self.selected:
                node = self.node_widget.node_editor._last_selected.uuid
                self.inspector_panel.inspect_node(node)
                self.selected = self.node_widget.node_editor._last_selected

    def compile_to_ftl(self):
        scene = self.node_widget.save_project()
        # path = tempfile.mktemp()
        # jsonv = []
        # with open(path, "w+") as f:
        #    json.dump(scene, f, indent=4)
        #    jsonv = f.readlines()
        # os.remove(path)
        # print(scene)
        # ordered_node_uuids = self.find_order(scene["nodes"], scene["connections"])
        jsnonconverter = JsonToXmlConverter(scene)
        print(jsnonconverter.convert_json_to_xml())
        # TODO: somehow convert {'nodes': [{'type': 'choice_Node', 'x': 5155, 'y': 4866, 'uuid': '2228cbfa-8029-478c-9d62-dc4685a866ae', 'internal-data': {}}, {'type': 'event_Node', 'x': 4817, 'y': 4913, 'uuid': '23e4b45c-461f-4a65-a112-5af01b77df81', 'internal-data': {'text': 'example', 'isunique': True}}, {'type': 'text_Node', 'x': 4973, 'y': 4869, 'uuid': 'a0e8222a-ff19-498f-8c29-93e2f4257e2b', 'internal-data': {'text': 'A zoltan ship hails you'}}, {'type': 'text_Node', 'x': 5380, 'y': 4778, 'uuid': '70ca10c1-dbe8-4673-9e5c-3dce08666aa6', 'internal-data': {'text': 'Tell them about your mission and ask for supplies'}}, {'type': 'text_Node', 'x': 5353, 'y': 4952, 'uuid': '11e6b28e-0473-487f-8480-0069fd412c47', 'internal-data': {'text': 'attack!'}}, {'type': 'playsound_Node', 'x': 5514, 'y': 4927, 'uuid': 'a3e094c7-a188-443e-8a72-b4dd6199f1eb', 'internal-data': {}}, {'type': 'loadsound_Node', 'x': 5348, 'y': 5098, 'uuid': 'bf6b87c6-1d23-4a20-b5a8-34ccd36ffdf1', 'internal-data': {'filepath': ''}}, {'type': 'loadship_Node', 'x': 5699, 'y': 4947, 'uuid': 'b73ad069-3b0f-49ee-aca9-9af33beee56c', 'internal-data': {'text': 'enemy-zoltan', 'ishostile': True}}, {'type': 'text_Node', 'x': 5551, 'y': 4751, 'uuid': '4142a167-4f62-469a-967a-6814ca3c4fc3', 'internal-data': {'text': 'They give you some supplies to help you on your quest'}}, {'type': 'Reward_Node', 'x': 5734, 'y': 4725, 'uuid': '468cf1dc-4d15-46a9-958f-1b27b7353820', 'internal-data': {'amount': 20, 'index': 0}}], 'connections': [{'start_id': '4142a167-4f62-469a-967a-6814ca3c4fc3', 'end_id': '468cf1dc-4d15-46a9-958f-1b27b7353820', 'start_pin': 'Ex Out', 'end_pin': 'Input'}, {'start_id': 'a3e094c7-a188-443e-8a72-b4dd6199f1eb', 'end_id': 'b73ad069-3b0f-49ee-aca9-9af33beee56c', 'start_pin': 'Ex Out', 'end_pin': 'Ex In'}, {'start_id': 'bf6b87c6-1d23-4a20-b5a8-34ccd36ffdf1', 'end_id': 'a3e094c7-a188-443e-8a72-b4dd6199f1eb', 'start_pin': 'Audio', 'end_pin': 'AudioFile'}, {'start_id': '11e6b28e-0473-487f-8480-0069fd412c47', 'end_id': 'a3e094c7-a188-443e-8a72-b4dd6199f1eb', 'start_pin': 'Ex Out', 'end_pin': 'Ex In'}, {'start_id': '70ca10c1-dbe8-4673-9e5c-3dce08666aa6', 'end_id': '4142a167-4f62-469a-967a-6814ca3c4fc3', 'start_pin': 'Ex Out', 'end_pin': 'Ex In'}, {'start_id': '23e4b45c-461f-4a65-a112-5af01b77df81', 'end_id': 'a0e8222a-ff19-498f-8c29-93e2f4257e2b', 'start_pin': 'event_contain', 'end_pin': 'Ex In'}, {'start_id': 'a0e8222a-ff19-498f-8c29-93e2f4257e2b', 'end_id': '2228cbfa-8029-478c-9d62-dc4685a866ae', 'start_pin': 'Ex Out', 'end_pin': 'Ex In'}, {'start_id': '2228cbfa-8029-478c-9d62-dc4685a866ae', 'end_id': '70ca10c1-dbe8-4673-9e5c-3dce08666aa6', 'start_pin': 'Choice Output0', 'end_pin': 'Ex In'}, {'start_id': '2228cbfa-8029-478c-9d62-dc4685a866ae', 'end_id': '11e6b28e-0473-487f-8480-0069fd412c47', 'start_pin': 'Choice Output1', 'end_pin': 'Ex In'}]} to ftl xml format

    # def keyPressEvent(self, event: QKeyEvent) -> None:
    #    self.setsimulationloc()

    def save_project(self):
        path = r"scenes\\" + tab_widget.tabText(tab_widget.currentIndex())
        if os.path.exists(Path(path)):
            dialogue = False
            file_path = path
        else:
            dialogue = True

        if dialogue:
            # print(self.node_widget.scene.items())
            file_dialog = QtWidgets.QFileDialog()
            file_dialog.setAcceptMode(QtWidgets.QFileDialog.AcceptSave)
            file_dialog.setDefaultSuffix("FTL-NODE-SCRIPT")
            file_dialog.setNameFilter("FTL-NODES-SCRIPT files (*.FTL-NODES-SCRIPT)")
            file_path, _ = file_dialog.getSaveFileName(
                caption="Save project",
                dir=str(self.scenes_path.absolute()),
                filter="FTL-NODES-SCRIPT files (*.FTL-NODES-SCRIPT)",
            )
        self.scene = self.node_widget.save_project(file_path, True)
        self.inspector_panel.sr = self.scene
        print(f"project saved to {file_path}")

    def load_project(self, project_path=None, loadscene=True, loadfile=None):
        if not project_path:
            return
        #e = []
        project_path = Path(project_path)
        if project_path.exists() and project_path.is_dir():
            self.project_path = project_path

            self.imports = {}

            for file in project_path.glob("*.py"):
                if not file.stem.endswith("_node"):
                    print("file:", file.stem)
                    continue
                #with open(file, "r") as f:
                #    for i in f.readlines():
                #        e.append(i)
                spec = importlib.util.spec_from_file_location(file.stem, file)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                for name, obj in inspect.getmembers(module):
                    if not name.endswith("_Node"):
                        continue
                    if inspect.isclass(obj):
                        self.imports[obj.__name__] = {"class": obj, "module": module}
            if not loadfile:
                self.node_list.update_project(self.imports)
            #pyperclip.copy(str(e))
            # work on just the first json file. add the ability to work on multiple json files later
            if loadscene:
                for json_path in project_path.glob("*.json"):
                    self.node_widget.load_scene(json_path, self.imports)
                    break
            elif loadfile:
                self.node_widget.load_scene(loadfile, self.imports)

    def get_project_path(self):
        project_path = QtWidgets.QFileDialog.getExistingDirectory(
            None, "Select Project Folder", ""
        )
        if not project_path:
            return

        # self.load_project(project_path)

    def loadproject(self, returnname=False):
        file_dialog = QtWidgets.QFileDialog()
        # file_dialog.setAcceptMode(QtWidgets.QFileDialog.AcceptSave)
        # file_dialog.setDirectory()
        file_dialog.setDefaultSuffix("FTL-NODE-SCRIPT")
        # file_dialog.setNameFilter()
        file_path, _ = file_dialog.getOpenFileName(
            caption="Select project to load or click cancel",
            dir=str(self.scenes_path.absolute()),
            filter="FTL-NODES-SCRIPT files (*.FTL-NODES-SCRIPT)",
        )

        self.load_project(self.project_path, loadscene=False, loadfile=file_path)

        tab_widget.setTabText(tab_widget.currentIndex(), Path(file_path).name)
        self.scene = self.node_widget.save_project(file_path, True)
        self.inspector_panel.sr = self.scene
        if returnname:
            return Path(file_path).name

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

class StreamRedirect(QtCore.QObject):
    def __init__(self, widget, stream):
        super().__init__()
        self.widget = widget
        self.stream = stream
        self.last_line_empty = False

    def write(self, text):
        cursor = self.widget.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        

        # Insert text
        cursor.insertText(text)
        self.widget.setTextCursor(cursor)
        self.widget.ensureCursorVisible()
        
       ## Check if the last line is empty
       #self.last_line_empty = text.endswith("\n")  # Check if the text ends with a newline character
       #if self.last_line_empty:
       #    text=text[:-2]
       #    self.last_line_empty=False

        # Scroll to the bottom
        self.widget.verticalScrollBar().setValue(self.widget.verticalScrollBar().maximum()-20)

    def flush(self):
        pass  # No need to flush in this case

    def fileno(self):
        return self.stream.fileno()

class Simulator(QtWidgets.QWidget):
    def __init__(self, scene, parent=None):
        super().__init__(parent)
        self.layoutt = QtWidgets.QVBoxLayout()
        self.setLayout(self.layoutt)
        self.node = None
        self.current_state = {}  # To keep track of simulation state
        self.scene = self.parse_scene(scene)
        self.sr = None
        self.connections = scene["connections"]

        self.backroundbackroundo = QPixmap("backback.jpg")
        self.backroundbackround = QPixmap("backback.jpg").scaled(
            self.layoutt.sizeHint()
        )
        

        self.originalBackgroundImage = QPixmap("simulator backround.png")
        self.backgroundImage = QPixmap("simulator backround.png").scaled(
            self.layoutt.sizeHint()
        )
        
        self.setStyleSheet("""
            QPushButton {
                border: none;
                background-color: transparent; /* Set transparent background */
                color: black; /* Set default text color */
            }
            
            QPushButton:hover {
                background-color: none; /* Set background color when hovered */
                color: white; /* Set text color when hovered */
            }
        """)
        
        # Center the widget on the screen
        self.setContentsMargins(0, 400, 0, 200)  # Left, top, right, bottom
    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        # Fill the background with the scaled pixmap
        scaledPixmap = self.backroundbackroundo.scaled(
            self.size(),
            QtCore.Qt.AspectRatioMode.IgnoreAspectRatio,
            QtCore.Qt.SmoothTransformation,
        )
        # Calculate starting point to center the image
        startX = (self.width() - scaledPixmap.width()) / 2
        startY = (self.height() - scaledPixmap.height()) / 2
        painter.drawPixmap(QtCore.QPoint(startX, startY), scaledPixmap)

        # Fill the background with the scaled pixmap
        scaledPixmap = self.originalBackgroundImage.scaled(
            self.size(),
            QtCore.Qt.AspectRatioMode.KeepAspectRatio,
            QtCore.Qt.SmoothTransformation,
        )
        # Calculate starting point to center the image
        startX = (self.width() - scaledPixmap.width()) / 2
        startY = (self.height() - scaledPixmap.height()) / 2
        painter.drawPixmap(QtCore.QPoint(startX, startY), scaledPixmap)
        self.setContentsMargins(*self.get_margins(startX,startY,scaledPixmap))

    def find_node_from_uuid(self, node_uuid):
        for uuid, node in self.scene.items():
            if uuid == node_uuid:
                return node
        print(f"Node with UUID {node_uuid} not found")
        return None

    def get_margins(self, startX, startY, scaledPixmap):
        # Get the size of the original pixmap
        originalSize = scaledPixmap.size()
    
        # Calculate the margins
        left_margin = startX
        top_margin = startY
        #right_margin = scaledPixmap.width() - originalSize.width() - left_margin
        bottom_margin = scaledPixmap.height()
    
        return (left_margin, top_margin, 0, bottom_margin)
    def parse_scene(self, scene):
        node_map = {}
        for node in scene["nodes"]:
            node_map[node["uuid"]] = node
        return node_map

    def find_next_node(self, current_node_id, output_pin):
        for connection in self.connections:
            if (
                connection["start_id"] == current_node_id
                and connection["start_pin"] == output_pin
            ):
                return self.scene[connection["end_id"]]
        print("noconnect")
        return None

    def inspect_node(self, node_uuid):
        
        if self.sr:
            self.connections = self.sr["connections"]
            self.scene = self.parse_scene(self.sr)
            self.sr = None
            print(self.scene)
            
        self.clear_inspector()
        try:
            node = self.scene[node_uuid]
        except:
            label = QLabel("to use simulator save project")
            self.layoutt.addWidget(label)

        self.node = node
        # Based on node type, create interactive UI elements
        if node["type"] == "choice_Node":
            self.create_choice_ui(node)
        elif node["type"] == "event_Node":
            self.create_event_ui(node)
        elif node["type"] == "text_Node":
            self.create_text_ui(node)
        # Add other node types as needed

    def find_previous_node(self, current_node_id, input_pin):
        for connection in self.connections:
            if (
                connection["end_id"] == current_node_id
                and connection["end_pin"] == input_pin
            ):
                return self.scene.get(connection["start_id"])
        print("No connection found for the input pin.")
        return None
    
    def clear_inspector(self):
        """Deletes all widgets from the layout.
        Parameters:
            - self (class): The class instance.
        Returns:
            - None: Does not return anything.
        Processing Logic:
            - Reverse range for deletion.
            - Delete widgets.
            - Does not return anything."""
        for i in reversed(range(self.layoutt.count())):
            widget = self.layoutt.itemAt(i).widget()
            if widget:
                widget.deleteLater()
    def create_choice_ui(self, choice_node):
        # Simplified for this example; choices need to be defined properly
        i=0
        while True:
            node=choice_node
            node = self.find_previous_node(node["uuid"], "Ex In")
            print(node)
            if node:
                if node["internal-data"]["text"]:
                    text = node["internal-data"]["text"]
                    break
                else:
                    i+1
            if i>100:
                text="no previouse node"
                break
        label = QtWidgets.QLabel(text)
        
        self.layoutt.addWidget(label)

        # print(choice_node)
        for i in range(10):
            try:
                text = self.findchoicetext(choice_node, i)
                if not text:
                    text = (
                        f"Choice {i} (No connection)"  # Default text if no connection
                    )

                btn = QtWidgets.QPushButton(text)
                btn.clicked.connect(
                    lambda choice=i: self.make_choice(choice_node, choice)
                )
                print(self.layoutt.sizeHint().height())
                btn.setGeometry(btn.x(), 36, btn.width(), btn.height())
                self.layoutt.addWidget(btn)
            except:  # Exception as e:
                None
                # print("error: " + str(e))
                # btn = QtWidgets.QPushButton("error: " + str(e))
                # btn.clicked.connect(
                #    lambda _, choice=i: self.make_choice(choice_node, choice)
                # )
                # self.layoutt.addWidget(btn)

    def create_event_ui(self, event_node):
        label = QtWidgets.QLabel(event_node["internal-data"]["text"])
        self.layoutt.addWidget(label)
        # Add any additional UI elements for event nodes

    def create_text_ui(self, text_node):
        label = QtWidgets.QLabel(text_node["internal-data"]["text"])
        self.layoutt.addWidget(label)

    def make_choice(self, choice_node, choice_index):
        # Simplified for demonstration
        next_node = self.find_next_node(
            choice_node["uuid"], f"Choice Output{choice_index}"
        )
        next_node = self.find_next_node(
            next_node["uuid"], "Ex Out"
        )        
        if next_node:
            self.inspect_node(next_node["uuid"])
        # This would need to fetch the next node object based on ID or reference

    def findchoicetext(self, choice_node, choice_index):
        # Simplified for demonstration
        next_node = self.find_next_node(
            choice_node["uuid"], f"Choice Output{choice_index}"
        )
        # print(
        #    f"next node: {next_node} choicenode: {choice_node} connections: {self.connections}"
        # )
        if next_node["internal-data"]["text"]:
            return next_node["internal-data"]["text"]
        # This would need to fetch the next node object based on ID or reference


class base_node(Node):
    def __init__(self, title, type):
        super().__init__()

        self.title_text = title
        self.type_text = type
        self.set_color(title_color=(0, 128, 0))

        self.add_pin(name="Ex In", is_output=False, execution=True)
        self.add_pin(name="Ex Out", is_output=True, execution=True)

        self.build()


class ImageCreatorWindow(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Image Creator")
        self.layout = QtWidgets.QVBoxLayout()

        self.image_creator_widget = ImageCreatorWidget()
        self.layout.addWidget(self.image_creator_widget)

        self.setLayout(self.layout)


class ImageCreatorWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUI()
        self.setupConnections()

    def setupUI(self):
        self.mainLayout = QHBoxLayout(self)
        self.leftLayout = QVBoxLayout()
        self.rightLayout = QVBoxLayout()

        # Initialize QGraphicsScene and QGraphicsView for image display
        self.scene = QGraphicsScene(self)
        self.view = QGraphicsView(self.scene)
        self.mainLayout.addWidget(self.view, 1)  # Add view with a stretch factor

        # Left layout components
        self.newImageButton = QPushButton("New Image")
        self.loadButton = QPushButton("Load Image")
        self.saveButton = QPushButton("Save Image")
        self.clearButton = QPushButton("Clear Image")
        self.colorButton = QPushButton("Select Color")
        self.colorDisplay = QLabel()
        self.colorDisplay.setFixedSize(20, 20)
        self.colorDisplay.setStyleSheet("background-color: black;")

        self.leftLayout.addWidget(self.newImageButton)
        self.leftLayout.addWidget(self.loadButton)
        self.leftLayout.addWidget(self.saveButton)
        self.leftLayout.addWidget(self.clearButton)
        # Add drawing tools selection
        self.drawingToolsCombo = QComboBox()
        self.drawingToolsCombo.addItems(["Pen", "Spray Paint"])
        self.leftLayout.insertWidget(
            5, self.drawingToolsCombo
        )  # Insert before the color picker

        # Current drawing tool
        self.currentTool = "Pen"

        self.leftLayout.addWidget(self.colorButton)
        self.leftLayout.addWidget(self.colorDisplay)

        # Right layout for filters
        self.filterLabel = QLabel("Filters")
        self.brightnessSlider = QSlider(Qt.Horizontal)
        self.brightnessSlider.setMinimum(-100)
        self.brightnessSlider.setMaximum(100)
        self.brightnessLabel = QLabel("Brightness")

        self.rightLayout.addWidget(self.filterLabel)
        self.rightLayout.addWidget(self.brightnessLabel)
        self.rightLayout.addWidget(self.brightnessSlider)

        self.mainLayout.addLayout(self.leftLayout)
        self.mainLayout.addLayout(self.rightLayout)

        self.pen_color = QColor(Qt.black)

    def setupConnections(self):
        self.newImageButton.clicked.connect(self.newImage)
        self.loadButton.clicked.connect(self.loadImage)
        self.saveButton.clicked.connect(self.saveImage)
        self.clearButton.clicked.connect(self.clearImage)
        self.colorButton.clicked.connect(self.selectColor)

    def newImage(self):
        # Create a new blank image
        size, ok = QInputDialog.getItem(
            self,
            "New Image",
            "Select size:",
            ["640x480", "800x600", "1024x768"],
            0,
            False,
        )
        if ok:
            width, height = map(int, size.split("x"))
            pixmap = QPixmap(width, height)
            pixmap.fill(Qt.white)
            self.scene.clear()
            self.scene.addPixmap(pixmap)
            self.view.fitInView(self.scene.itemsBoundingRect(), Qt.KeepAspectRatio)

    def loadImage(self):
        # Implementation for loading an image into the scene
        pass

    def saveImage(self):
        # Implementation for saving the current image
        pass

    def clearImage(self):
        self.scene.clear()

    def selectColor(self):
        color = QColorDialog.getColor(self.pen_color, self)
        if color.isValid():
            self.pen_color = color
            self.colorDisplay.setStyleSheet(f"background-color: {color.name()};")

    # Update setupConnections to handle tool change
    def setupConnections(self):
        # Connections from previous setup...
        self.drawingToolsCombo.currentTextChanged.connect(self.changeTool)

    def changeTool(self, tool):
        self.currentTool = tool

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.lastPoint = self.view.mapToScene(event.pos())
            self.drawing = True

    def mouseMoveEvent(self, event):
        if (event.buttons() & Qt.MouseButton.LeftButton) & self.drawing:
            currentPoint = self.view.mapToScene(event.pos())
            if self.currentTool == "Pen":
                self.drawLineTo(currentPoint)
            elif self.currentTool == "Spray Paint":
                self.drawSprayPaint(currentPoint)
            self.lastPoint = currentPoint

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drawing = False

    def drawLineTo(self, endPoint):
        painter = QPainter(self.image)
        painter.setPen(QPen(self.pen_color, 3, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        painter.drawLine(self.lastPoint, endPoint)
        self.update(
            QRect(self.lastPoint.toPoint(), endPoint.toPoint())
            .normalized()
            .adjusted(-1, -1, 1, 1)
        )
        self.lastPoint = endPoint

    def drawSprayPaint(self, point):
        painter = QPainter(self.image)
        for _ in range(10):  # Number of dots per spray action
            xOffset = random.randint(-10, 10)
            yOffset = random.randint(-10, 10)
            painter.drawPoint(point.x() + xOffset, point.y() + yOffset)
        self.update()


class AudioCreatorWindow(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Audio Creator")
        self.layout = QtWidgets.QVBoxLayout()

        self.audio_creator_widget = AudioCreatorWidget()
        self.layout.addWidget(self.audio_creator_widget)

        self.setLayout(self.layout)


class AudioCreatorWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)

        # Add widgets for audio creation here

class NodeTabWidget(QtWidgets.QTabWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTabsClosable(True)
        self.tabCloseRequested.connect(self.close_tab)

        self.plus_button = QtWidgets.QPushButton("+")
        self.plus_button.clicked.connect(self.add_new_tab)
        self.setCornerWidget(self.plus_button, QtCore.Qt.TopLeftCorner)

    def close_tab(self, index):
        widget = self.widget(index)
        if widget:
            widget.deleteLater()
            self.removeTab(index)

    def add_new_tab(self):
        dialog = NewTabDialog(self)
        result = dialog.exec_()
        if result == QtWidgets.QDialog.Accepted:
            tab_type = dialog.get_tab_type()
            if tab_type == "Existing Scene":
                file_dialog = QtWidgets.QFileDialog()
                # file_path, _ = file_dialog.getOpenFileName(caption="Select project to load or click cancel", filter="FTL-NODES-SCRIPT files (*.FTL-NODES-SCRIPT)", dir=str(launcher1.project_path.absolute()))
                new_tab = NodeEditorTab()
                name = new_tab.loadproject(True)
                self.addTab(new_tab, name)
                self.setCurrentIndex(self.indexOf(new_tab))
            elif tab_type == "New Scene":
                new_tab = NodeEditorTab()
                self.addTab(new_tab, "New Project")
                self.setCurrentIndex(self.indexOf(new_tab))
            elif tab_type == "Ship Creator":
                new_tab = ShipBuilderWindow()
                self.addTab(new_tab, "Ship Creator")
                self.setCurrentIndex(self.indexOf(new_tab))
            elif tab_type == "Image Creator":
                new_tab = ImageCreatorWindow()
                self.addTab(new_tab, "Image Creator")
                self.setCurrentIndex(self.indexOf(new_tab))
            elif tab_type == "Audio Creator":
                new_tab = AudioCreatorWindow(launcher1.node_widget.scene)
                self.addTab(new_tab, "Audio Creator")
                self.setCurrentIndex(self.indexOf(new_tab))
            elif tab_type == "Simulation Tab":
                new_tab = Simulator()
                self.addTab(new_tab, "Simulation Tab")
                self.setCurrentIndex(self.indexOf(new_tab))
            elif tab_type == "Sector Creator":
                new_tab = SectorCreator()
                self.addTab(new_tab, "Sector Creator")
                self.setCurrentIndex(self.indexOf(new_tab))
            elif tab_type == "XML Converter/Editor":
                new_tab = XMLConverterGUI()
                self.addTab(new_tab, "XML Converter/Editor")
                self.setCurrentIndex(self.indexOf(new_tab))


class NewTabDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("New Tab Options")
        layout = QtWidgets.QVBoxLayout()

        self.radio_existing = QtWidgets.QRadioButton("Load Existing Scene")
        self.radio_new = QtWidgets.QRadioButton("Create New Scene")
        self.radio_ship_builder = QtWidgets.QRadioButton("Ship Creator")
        self.imagecreator = QtWidgets.QRadioButton("Image Creator")
        self.audiocreator = QtWidgets.QRadioButton("Audio Creator")
        self.simulator = QtWidgets.QRadioButton("Simulation Tab")
        self.sector_creator = QtWidgets.QRadioButton("Sector Creator")  # New option
        self.xmleditor = QtWidgets.QRadioButton("XML Converter/Editor")  # New option

        self.radio_existing.setChecked(True)

        button_box = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        layout.addWidget(self.radio_existing)
        layout.addWidget(self.radio_new)
        layout.addWidget(self.radio_ship_builder)
        layout.addWidget(self.imagecreator)
        layout.addWidget(self.audiocreator)
        layout.addWidget(self.simulator)
        layout.addWidget(self.sector_creator)
        layout.addWidget(self.xmleditor)
        layout.addWidget(button_box)
        self.setLayout(layout)

    def get_tab_type(self):
        if self.radio_existing.isChecked():
            return "Existing Scene"
        elif self.radio_new.isChecked():
            return "New Scene"
        if self.radio_ship_builder.isChecked():
            return "Ship Creator"
        if self.imagecreator.isChecked():
            return "Image Creator"
        if self.audiocreator.isChecked():
            return "Audio Creator"
        if self.simulator.isChecked():
            return "Simulation Tab"
        if self.sector_creator.isChecked():  # New option
            return "Sector Creator"
        if self.xmleditor.isChecked():  # New option
            return "XML Converter/Editor"

class XMLConverterGUI(QWidget):
    def __init__(self):
        super().__init__()

        self.text_edit = QTextEdit()
        self.load_button = QPushButton("Load XML File")
        self.load_button.clicked.connect(self.load_xml_file)
        self.convert_button = QPushButton("Convert to JSON")
        self.convert_button.clicked.connect(self.convert_to_json)
        self.save_button = QPushButton("Save Changes")
        self.save_button.clicked.connect(self.save_changes)

        layout = QVBoxLayout()
        layout.addWidget(self.text_edit)
        layout.addWidget(self.load_button)
        layout.addWidget(self.convert_button)
        layout.addWidget(self.save_button)
        self.setLayout(layout)

        self.xml_tree = None

    def load_xml_file(self):
        file_dialog = QFileDialog(self)
        file_dialog.setNameFilter("XML files (*.xml)")
        if file_dialog.exec_():
            file_path = file_dialog.selectedFiles()[0]
            try:
                self.xml_tree = ET.parse(file_path)
                self.text_edit.setPlainText(ET.tostring(self.xml_tree.getroot(), encoding="unicode"))
                print("XML file loaded successfully.")
            except FileNotFoundError:
                print("File not found.")

    def convert_to_json(self):
        
# Load XML text from the text editor
        xml_text = self.text_edit.toPlainText()

        # Parse XML from the loaded text
        self.xml_tree = ET.ElementTree(ET.fromstring(xml_text))

        if self.xml_tree is not None:
            root = self.xml_tree.getroot()
            nodes = []
            connections = []
            node_uuid_map = {}  # Map node names to their UUIDs
            connection_uuid_map = {}  # Map connection IDs to their UUIDs

            # Create nodes and populate node_uuid_map
            max_nodes_per_row = 5
            node_spacing_x = 200
            node_spacing_y = 400
            current_x = 4814
            current_y = 4920
          #  a=[]
            for elem in root.iter():
                try:
                    node_uuid = str(uuid.uuid4())
                    node_name = elem.get("name", "")
                    node_type = elem.tag
                    text = elem.text
                    internal_data = {}
                    #a.append(text)

                    # Populate internal data based on node type
               #     print(node_type)
                    if node_type == "choice":
                        internal_data = {}
                        node_type="choice_Node"
                    elif node_type == "event":
                        internal_data = {"text":elem.get("name",""), "isunique":elem.get("unique", False)}
                        node_type="event_Node"
                    elif node_type == "text":
                        internal_data = {"text":text}
                        node_type="text_Node"
                    elif node_type == "playSound":
                        internal_data = {}
                        node_type="playsound_Node"
                    elif node_type == "quest":
                        places = ["RANDOM", "LAST", "NEXT"]
                        internal_data = {"index":places.index(elem.get("beacon")), "text":elem.get("event")}
                        node_type="quest_Node"
                    elif node_type == "ship":
                        internal_data = {"text":elem.get("name",elem.get("load")), "autoblueprint":elem.get("auto_blueprint",""), "ishostile":elem.get("hostile")}
                        node_type="loadship_Node"
                    elif node_type == "item_modify":
                        internal_data = {}
                        node_type="item_modify_Node"
                    elif node_type == "item":
                        reward_types = ["scrap", "fuel", "drones", "missiles"]
                        internal_data = {"index": reward_types.index(elem.get("type")), "amount": elem.get("amount")}
                        node_type="Reward_Node"
                    elif node_type == "damage":
                        effects = ["random", "all", "fire"]
                        internal_data = {"text": elem.get("amount"), "System": elem.get("system"), "Effect": effects.index(elem.get("effect")), "enemy": False}
                        node_type="Damage_Node"
                    elif node_type == "enemyDamage":
                        effects = ["random", "all", "fire"]
                        internal_data = {"text": elem.get("amount"), "System": elem.get("system"), "Effect": effects.index(elem.get("effect")), "enemy": True}
                        node_type="Damage_Node" #<damage amount="1" system="engines" effect="fire" />
                    elif node_type == "weapon":
                        internal_data = {"amount":elem.get("name")}
                        node_type="giveweapon_Node"
                    elif node_type == "augument":
                        internal_data = {"amount":elem.get("name")}
                        node_type="giveaugument_Node"
                    elif node_type == "status":
                        internal_data = {} #<status type="limit" target="player" system="sensors" amount="1" />
                        node_type=""
                    elif node_type == "autoReward":
                        internal_data = {}
                        node_type=""
                    elif node_type == "surrender":
                        internal_data = {}#<surrender chance="0" min="3" max="4">
                        node_type=""
                    elif node_type == "store":
                        internal_data = {}
                        node_type="store_Node"


                    node = {
                        "type": node_type,
                        "x": current_x,
                        "y": current_y,
                        "uuid": node_uuid,
                        "internal-data": internal_data
                    }
                    nodes.append(node)
                    #node_uuid_map[node] = node_uuid
                    # Update coordinates for the next node
                    current_x += node_spacing_x
                    if current_x >= max_nodes_per_row * node_spacing_x:
                        current_x = 4814
                        current_y += node_spacing_y
                except:
                    continue
            #pyperclip.copy(a)
        
            # Create connections
            for elem in root.iter():
                if elem.tag == "choice":
                    choice_id = elem.get("name")
                    choice_uuid = node_uuid_map.get(choice_id)
                    for event in elem.iter("event"):
                        event_id = event.get("name")
                        event_uuid = node_uuid_map.get(event_id)
                        if choice_uuid and event_uuid:  # Ensure both IDs are not None
                            connection_id = f"{event_id}_{choice_id}"
                            connection_uuid = str(uuid.uuid4())
                            connections.append({
                                "start_id": event_uuid,
                                "end_id": choice_uuid,
                                "start_pin": "Ex Out",
                                "end_pin": "Ex In"
                            })
                            connection_uuid_map[connection_id] = connection_uuid
    
            json_data = {"nodes": nodes, "connections": connections}
            self.text_edit.setPlainText(json.dumps(json_data, indent=4))
            print("XML converted to JSON successfully.")
        else:
            print("No XML file loaded.")

    def save_changes(self):
        if self.xml_tree is not None:
            try:
                new_xml_data = self.text_edit.toPlainText().encode()
                self.xml_tree = ET.ElementTree(ET.fromstring(new_xml_data))
                print("Changes saved successfully.")
            except Exception as e:
                print(f"Error saving changes: {e}")
        else:
            print("No XML file loaded.")

    @staticmethod
    def get_node_id_by_name(nodes, name):
        for node in nodes:
            if "internal-data" in node and "text" in node["internal-data"]:
                if node["internal-data"]["text"] == name:
                    return node["uuid"]
        return None

class ShipBuilderWindow(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Ship Builder")
        self.layout = QtWidgets.QVBoxLayout()

        self.embedded_window = EmbeddedWindow()
        self.layout.addWidget(self.embedded_window)

        self.setLayout(self.layout)


class EmbeddedWindow(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)

        self.process = None
        self.embed_process()

    def embed_process(self):
        exe_path = "shipbuilder\Superluminal Win-32 v2.2.1\superluminal2.exe"
        self.process = subprocess.Popen(
            exe_path,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True,
        )

        # Wait for the process to start and get its window handle
        # self.process.wait(3)  # Adjust the timeout as needed
        hwnd = self.find_hwnd(self.process.pid)
        if hwnd:
            self.embed_window(hwnd)
        else:
            print("Failed to get window handle")

    def embed_window(self, hwnd):
        native_window = QtGui.QWindow.fromWinId(int(hwnd))
        if native_window:
            widget_container = QtWidgets.QWidget.createWindowContainer(native_window)
            self.layout.addWidget(widget_container)

    def find_hwnd(self, process_id):
        def callback(hwnd, hwnds):
            if win32gui.IsWindowVisible(hwnd) and win32gui.IsWindowEnabled(hwnd):
                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                if pid == process_id:
                    hwnds.append(hwnd)
            return True

        hwnds = []
        win32gui.EnumWindows(callback, hwnds)
        return hwnds[0] if hwnds else None


class JsonToXmlConverter:
    def __init__(self, json_data):
        self.json_data = json_data
        self.uuid_to_node = {node["uuid"]: node for node in json_data["nodes"]}
        self.sort_nodes_by_connections()
        # Prepare choice outputs mapping from the JSON data
        self.choice_outputs = defaultdict(list)
        self.prepare_choice_outputs()

    def prepare_choice_outputs(self):
        for conn in self.json_data["connections"]:
            start_node = self.uuid_to_node.get(conn["start_id"])
            if start_node and start_node["type"] == "choice_Node":
                self.choice_outputs[start_node["uuid"]].append(conn)

    def sort_nodes_by_connections(self):
        graph = {node["uuid"]: [] for node in self.json_data["nodes"]}
        in_degree = {node["uuid"]: 0 for node in self.json_data["nodes"]}
        for conn in self.json_data["connections"]:
            graph[conn["start_id"]].append(conn["end_id"])
            in_degree[conn["end_id"]] += 1

        queue = deque([node for node in in_degree if in_degree[node] == 0])
        sorted_nodes = []
        while queue:
            node_id = queue.popleft()
            sorted_nodes.append(node_id)
            for child_id in graph[node_id]:
                in_degree[child_id] -= 1
                if in_degree[child_id] == 0:
                    queue.append(child_id)

        if len(sorted_nodes) != len(self.json_data["nodes"]):
            raise Exception(
                "The graph contains a cycle, which prevents topological sorting."
            )

        self.json_data["nodes"] = [
            self.uuid_to_node[node_id] for node_id in sorted_nodes
        ]

    def convert_json_to_xml(self):
        root = Element("FTL")
        # Assume the first event node is the starting point
        start_node_id = self.json_data["connections"][0]["start_id"]
        start_node = self.uuid_to_node.get(start_node_id)
        for node in self.json_data["nodes"]:
            self.process_node(node, root)
        return tostring(root, encoding="utf-8").decode("utf-8")

    def process_node(self, node, parent_element):
        node_type = node["type"]
        if node_type == "event_Node":
            event_element = SubElement(
                parent_element,
                "event",
                {"name": node.get("internal-data", {}).get("text", "default")},
            )
            self.process_children(node, event_element)
        elif node_type == "text_Node":
            SubElement(parent_element, "text").text = node.get("internal-data", {}).get(
                "text", ""
            )
        elif node_type == "choice_Node":
            self.process_choice_node(node, parent_element)
        elif node_type == "playsound_Node":
            SubElement(
                parent_element,
                "playsound",
                {"file": node.get("internal-data", {}).get("filepath", "default.wav")},
            )
        elif node_type == "loadship_Node":
            SubElement(
                parent_element,
                "ship",
                {
                    "name": node["internal-data"]["text"],
                    "hostile": str(node["internal-data"]["ishostile"]),
                },
            )
        elif node_type == "Reward_Node":
            SubElement(
                parent_element,
                "reward",
                {
                    "amount": str(node["internal-data"]["amount"]),
                    "index": str(node["internal-data"]["index"]),
                },
            )
        elif node_type == "giveweapon_Node":
            SubElement(
                parent_element, "weapon", {"name": node["internal-data"]["text"]}
            )
        elif node_type == "giveaugment_Node":
            SubElement(
                parent_element, "augment", {"name": node["internal-data"]["text"]}
            )
        # Add other node types here as needed

    def process_choice_node(self, choice_node, parent_element):
        outputs = self.choice_outputs[choice_node["uuid"]]
        for conn in outputs:
            end_node = self.uuid_to_node.get(conn["end_id"])
            if end_node and end_node["type"] == "text_Node":
                choice_element = SubElement(parent_element, "choice")
                text_element = SubElement(choice_element, "text")
                text_element.text = end_node.get("internal-data", {}).get("text", "")
                self.process_children(end_node, choice_element)

    def process_children(self, node, parent_element):
        for conn in filter(
            lambda c: c["start_id"] == node["uuid"], self.json_data["connections"]
        ):
            child_node = self.uuid_to_node.get(conn["end_id"])
            if child_node:
                self.process_node(child_node, parent_element)

if __name__ == "__main__":
    import qdarktheme

    app = QtWidgets.QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon("resources\\app.ico"))
    qdarktheme.setup_theme()

    tab_widget = NodeTabWidget()

    launcher1 = NodeEditorTab()
    tab_widget.addTab(launcher1, "Project 1")

    tab_widget.show()
    sys.exit(app.exec())
