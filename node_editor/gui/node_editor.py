from contextlib import suppress

from PySide6 import QtCore, QtWidgets, QtGui
from PySide6.QtCore import Qt

from node_editor.connection import Connection
from node_editor.node import Node
from node_editor.pin import Pin
from PySide6.QtGui import QKeySequence
from PySide6.QtGui import QShortcut
#from node_editor.gui.node_widget import NodeScene


class NodeEditor(QtCore.QObject):
    """
    The main class of the node editor. This class handles the logic for creating, connecting, and deleting
    nodes and connections.
        :ivar connection: A Connection object representing the current connection being created.
    :vartype connection: Connection
    :ivar port: A Pin object representing the current port being clicked for a new connection.
    :vartype port: Pin
    :ivar scene: The QGraphicsScene on which the nodes and connections are drawn.
    :vartype scene: QGraphicsScene
    :ivar _last_selected: The last Node object that was selected.
    :vartype _last_selected: Node
    """

    def __init__(self, parent):
        """
        Constructor for NodeEditor.

        :param parent: The parent widget.
        :type parent: QWidget
        """

        super().__init__(parent)
        self.connection = None
        self.port = None
        self.scene = None
        self._last_selected = None
        self.selection_rect_item = None


    def install(self, scene):
        """
        Installs the NodeEditor into a QGraphicsScene.

        :param scene: The QGraphicsScene to install the NodeEditor into.
        :type scene: QGraphicsScene
        """

        self.scene = scene
        self.scene.installEventFilter(self)

    def item_at(self, position):
        """
        Returns the QGraphicsItem at the given position.

        :param position: The position to check for a QGraphicsItem.
        :type position: QPoint
        :return: The QGraphicsItem at the position, or None if no item is found.
        :rtype: QGraphicsItem
        """

        items = self.scene.items(
            QtCore.QRectF(position - QtCore.QPointF(1, 1), QtCore.QSizeF(3, 3))
        )
        return items[0] if items else None

    def selectall(self):
        print("hi")
        for item in self.scene.items():
            if isinstance(item, Node):
                item.select_connections(True)
 
    def eventFilter(self, watched, event):
        """
        Filters events from the QGraphicsScene.

        :param watched: The object that is watched.
        :type watched: QObject
        :param event: The event that is being filtered.
        :type event: QEvent
        :return: True if the event was filtered, False otherwise.
        :rtype: bool
        """
        if type(event) == QtWidgets.QWidgetItem:
            return False

        if event.type() == QtCore.QEvent.Type.GraphicsSceneMousePress:
            if event.button() == QtCore.Qt.LeftButton:
                item = self.item_at(event.scenePos())
                if not item:
                    self.start_pos = event.scenePos()
                    self.selection_rect_item = QtWidgets.QGraphicsRectItem(QtCore.QRectF(self.start_pos, QtCore.QSizeF(0, 0)))
                    self.selection_rect_item.setPen(QtGui.QPen(QtCore.Qt.GlobalColor.white, 3, QtCore.Qt.DotLine))
                    self.scene.addItem(self.selection_rect_item)
                if isinstance(item, Pin):
                    self.connection = Connection(None)
                    self.scene.addItem(self.connection)
                    self.port = item
                    self.connection.start_pos = item.scenePos()
                    self.connection.end_pos = event.scenePos()
                    self.connection.update_path()
                    return True

                if isinstance(item, Connection):
                    self.connection = Connection(None)
                    self.connection.start_pos = item.start_pos
                    self.scene.addItem(self.connection)
                    self.port = item.start_pin
                    self.connection.end_pos = event.scenePos()
                    self.connection.update_start_and_end_pos()  # to fix the offset
                    return True

                if self._last_selected:
                    # If we clear the scene, we lose the last selection
                    with suppress(RuntimeError):
                        self._last_selected.select_connections(False)

                if isinstance(item, Node):
                    item.select_connections(True)
                    self._last_selected = item
                else:
                    self._last_selected = None

            elif event.button() == QtCore.Qt.MouseButton.RightButton:
                # context menu
                pass

        elif event.type() == QtCore.QEvent.Type.KeyPress:
            if event.key() == QtCore.Qt.Key.Key_Delete:
                for item in self.scene.selectedItems():
                    if isinstance(item, (Connection, Node)):
                        item.delete()

                return True

        elif event.type() == QtCore.QEvent.Type.GraphicsSceneMouseMove:
            if self.connection:
                self.connection.end_pos = event.scenePos()
                self.connection.update_path()
                return True
            if self.selection_rect_item:
                current_pos = event.scenePos()
                rect = QtCore.QRectF(self.start_pos, current_pos).normalized()
                self.selection_rect_item.setRect(rect)
                return True

        elif event.type() == QtCore.QEvent.Type.GraphicsSceneMouseRelease:
            item = self.item_at(event.scenePos())
            #print(self.selection_rect_item)
            if self.selection_rect_item:
                selected_items = self.scene.collidingItems(self.selection_rect_item, Qt.ItemSelectionMode.IntersectsItemShape)
                self.scene.removeItem(self.selection_rect_item)
                #print(selected_items)
                self.selection_rect_item=None
                for item in selected_items:
                    if isinstance(item, Node):
                        item.setSelected(True)
            if self.connection and event.button() == QtCore.Qt.MouseButton.LeftButton:
                # connecting a port
                if isinstance(item, Pin):
                    if self.port.can_connect_to(item):
                        # print("Making connection")

                        # delete existing connection on the new port
                        if item.connection:
                            item.connection.delete()

                        # delete existing connection to the original port
                        self.port.clear_connection()
                        item.clear_connection()

                        self.connection.set_start_pin(self.port)
                        self.connection.set_end_pin(item)
                        self.connection.update_start_and_end_pos()
                    else:
                        # print("Deleting connection")
                        self.connection.delete()

                    self.connection = None

                if self.connection:
                    self.connection.delete()
                self.connection = None
                self.port = None
                return True

        elif event.type() == QtCore.QEvent.Type.GraphicsSceneMousePress:
            if event.button() == QtCore.Qt.LeftButton:
                item = self.item_at(event.scenePos())

                # Check if Shift key is held down for deselecting
                if event.modifiers() == QtCore.Qt.KeyboardModifier.ShiftModifier:
                    if isinstance(item, Node):
                        if item.isSelected():
                            item.setSelected(False)
                        else:
                            item.setSelected(True)
                    return True

                if isinstance(item, Pin):
                    self.connection = Connection(None)
                    self.scene.addItem(self.connection)
                    self.port = item
                    self.connection.start_pos = item.scenePos()
                    self.connection.end_pos = event.scenePos()
                    self.connection.update_path()
                    return True

                if isinstance(item, Connection):
                    self.connection = Connection(None)
                    self.connection.start_pos = item.start_pos
                    self.scene.addItem(self.connection)
                    self.port = item.start_pin
                    self.connection.end_pos = event.scenePos()
                    self.connection.update_start_and_end_pos()  # to fix the offset
                    return True

                if self._last_selected:
                    # If we clear the scene, we lose the last selection
                    with suppress(RuntimeError):
                        self._last_selected.select_connections(False)

                if isinstance(item, Node):
                    item.select_connections(True)
                    self._last_selected = item
                else:
                    self._last_selected = None

            elif event.button() == QtCore.Qt.MouseButton.RightButton:
                # context menu
                pass

        elif event.type() == QtCore.QEvent.Type.KeyPress:
            if event.key() == QtCore.Qt.Key.Key_Delete:
                for item in self.scene.selectedItems():
                    if isinstance(item, (Connection, Node)):
                        item.delete()

                return True

        elif event.type() == QtCore.QEvent.Type.GraphicsSceneMouseMove:
            if self.connection:
                self.connection.end_pos = event.scenePos()
                self.connection.update_path()
                return True

        elif event.type() == QtCore.QEvent.Type.GraphicsSceneMouseRelease:
            if self.connection and event.button() == QtCore.Qt.MouseButton.LeftButton:
                item = self.item_at(event.scenePos())

                # connecting a port
                if isinstance(item, Pin):
                    if self.port.can_connect_to(item):
                        # print("Making connection")

                        # delete existing connection on the new port
                        if item.connection:
                            item.connection.delete()

                        # delete existing connection to the original port
                        self.port.clear_connection()
                        item.clear_connection()

                        self.connection.set_start_pin(self.port)
                        self.connection.set_end_pin(item)
                        self.connection.update_start_and_end_pos()
                    else:
                        # print("Deleting connection")
                        self.connection.delete()

                    self.connection = None

                if self.connection:
                    self.connection.delete()
                self.connection = None
                self.port = None
                return True

        return super().eventFilter(watched, event)
