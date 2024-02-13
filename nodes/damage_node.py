from PySide6 import QtWidgets

from node_editor.node import Node
from nodes.common_widgets import FloatLineEdit,checkbox


class Damage_Node(Node):
    def __init__(self):
        super().__init__()

        self.title_text = "Damage"
        self.type_text = "XML Nodes"
        self.set_color(title_color=(255, 0, 0))
        self.internaldata = {}
        self.add_pin(name="Ex In", is_output=False, execution=True)
        self.add_pin(name="Ex Out", is_output=True, execution=True)
        self.reward_types = ["Pilot", "Engines", "shields", "sensors", "doors", "weapons"]
        self.effects = ["random", "all", "fire"]

        self.build()

    def init_widget(self):
        self.widget = QtWidgets.QWidget()
        self.widget.setFixedWidth(100)
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.label = QtWidgets.QLabel("Damage amount")
        layout.addWidget(self.label)
        self.scaler_line = FloatLineEdit()#o=self)
        layout.addWidget(self.scaler_line)
        self.labell = QtWidgets.QLabel("Damage Enemy (if unchecked damages player)")
        layout.addWidget(self.labell)
        self.isunique = checkbox()
        layout.addWidget(self.isunique)

        self.type_label = QtWidgets.QLabel("System:")
        layout.addWidget(self.type_label)

        self.reward_type_dropdown = QtWidgets.QComboBox()
        self.reward_type_dropdown.addItems(self.reward_types)
        layout.addWidget(self.reward_type_dropdown)
        
        self.type_llabel = QtWidgets.QLabel("Effect:")
        layout.addWidget(self.type_llabel)

        self.reward_ttype_dropdown = QtWidgets.QComboBox()
        self.reward_ttype_dropdown.addItems(self.effects)
        layout.addWidget(self.reward_ttype_dropdown)
        
        self.widget.setLayout(layout)
    
        proxy = QtWidgets.QGraphicsProxyWidget()
        proxy.setWidget(self.widget)
        proxy.setParentItem(self)
        

        super().init_widget()
        
    def setinternaldata(self):
        self.scaler_line.setText(self.internaldata["text"])
        self.reward_type_dropdown.setCurrentIndex(self.internaldata["System"])
        self.reward_ttype_dropdown.setCurrentIndex(self.internaldata["Effect"])
        self.isunique.setChecked(self.internaldata["enemy"])
        
    def setdata(self):
        self.internaldata["text"] = self.scaler_line.text()
        self.internaldata["System"] = self.reward_type_dropdown.currentIndex()
        self.internaldata["Effect"] = self.reward_ttype_dropdown.currentIndex()
        self.internaldata["enemy"] = self.isunique.isChecked()
         
