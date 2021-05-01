from PySide2 import QtWidgets, QtCore

from box_manager import core

class BBOXManagerWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super(BBOXManagerWindow, self).__init__()
        self.scene_nodes = None
        self.setup_ui()

    def setup_ui(self):
        self.setMinimumSize(600, 800)
        
        self.widget_layout = QtWidgets.QVBoxLayout()
        self.main_widget = QtWidgets.QWidget(parent=self)
        
        self.main_widget.setLayout(self.widget_layout)
        self.setCentralWidget(self.main_widget)

        self.setWindowTitle("Bounding Box Manager")
        self.title_lable = QtWidgets.QLabel()
        self.title_lable.setText("BBOX Manager")

        self.selection_button = QtWidgets.QPushButton("Get Selection")
        self.selection_button.clicked.connect(self.get_scene_nodes_from_selection)

        self.bbox_button = QtWidgets.QPushButton("Setup Bounding Boxes")
        self.bbox_button.clicked.connect(self.run_setup_bbox_on_clicked)

        self.refresh_tree_button = QtWidgets.QPushButton("Refresh Tree Widget")
        self.refresh_tree_button.clicked.connect(self.setup_treewidget)

        self.treeview = QtWidgets.QTreeWidget()
        self.treeview.setColumnCount(1)
        self.treeview.setHeaderLabels(["Nodes"])
        self.treeview.itemChanged.connect(self.checkbox_checked)

        self.widget_layout.addWidget(self.title_lable)
        self.widget_layout.addWidget(self.selection_button)
        self.widget_layout.addWidget(self.bbox_button)
        self.widget_layout.addWidget(self.refresh_tree_button)
        self.widget_layout.addWidget(self.treeview)

    def get_scene_nodes_from_selection(self):
        root_node = core.get_selection()
        if root_node is None:
            QtWidgets.QMessageBox.about(
                None, "Warning", "Please select the root node first."
            )
            return

        self.scene_nodes = core.get_scene_nodes(root_node)

    def setup_treeview_if_bboxes_exist(self):
        if core.bboxes_exist_in_scene():
            self.setup_treewidget()

    def run_setup_bbox_on_clicked(self):
        
        if self.scene_nodes is None:
            QtWidgets.QMessageBox.about(
                None, "Warning", "Please select the root node first."
            )
        else:
            core.setup_bbox_hierarchy(self.scene_nodes)

        self.setup_treewidget()  

    def checkbox_checked(self, item, column):
        if item.checkState(column) == QtCore.Qt.Checked:
            self.set_children_state(item, QtCore.Qt.Checked)
            core.change_bbox_visibility(item.text(0), hide_object=False)
        elif item.checkState(column) == QtCore.Qt.Unchecked:
            self.set_children_state(item, QtCore.Qt.Unchecked)
            core.change_bbox_visibility(item.text(0), hide_object=True)

    def set_children_state(self, item, state):
        for i in range(item.childCount()):
            item.child(i).setCheckState(0, state)
    
    def setup_treewidget(self):
        if self.scene_nodes is None:
            QtWidgets.QMessageBox.about(
                None,
                "Warning",
                "Please select the root node first and click the 'Get Selection' button."
            )

        previous = None
        for node in sorted(self.scene_nodes, key=len):
            parent = core.get_node_parent(node)
            name = node.split("|")[-1]

            # Add root node to tree widget
            if not parent:
                root_tree_item = QtWidgets.QTreeWidgetItem(self.treeview, [name])
                root_tree_item.setCheckState(0, QtCore.Qt.Checked)
                previous = root_tree_item
                continue

            # Add non-root nodes to tree widget.
            previous = self.treeview.findItems(
                parent[0], QtCore.Qt.MatchRecursive, 0
            )
            tree_item = QtWidgets.QTreeWidgetItem(previous[0], [name])
            tree_item.setCheckState(0, QtCore.Qt.Checked)


def main():
    global window
    window = BBOXManagerWindow()
    window.show()


if __name__ == "__main__":
    main()
