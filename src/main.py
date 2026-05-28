import sys
import json
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QPushButton,
    QFileDialog,
    QMessageBox,
    QTreeWidgetItemIterator,
    QListWidget,
    QSplitter,
    QMenuBar,
    QMenu
)
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt, QUrl, QMimeData
from pathlib import Path
import pyperclip

class FileTree(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("File Selector")
        self.setGeometry(100, 100, 800, 600)

        # File menu setup
        menubar = self.menuBar()
        file_menu = menubar.addMenu("File")
        new_project = QAction("New Project", self)
        new_project.triggered.connect(self.new_project)
        file_menu.addAction(new_project)
        load_project = QAction("Load Project", self)
        load_project.triggered.connect(self.load_project)
        file_menu.addAction(load_project)
        save_project = QAction("Save Project", self)
        save_project.triggered.connect(self.save_project)
        file_menu.addAction(save_project)

        central = QWidget()
        main_layout = QHBoxLayout(central)
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left column: Selected items list and remove button
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        self.selected_list = QListWidget()
        self.selected_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        left_layout.addWidget(self.selected_list)
        remove_btn = QPushButton("Remove Selected")
        remove_btn.clicked.connect(self.remove_from_selection)
        left_layout.addWidget(remove_btn)
        splitter.addWidget(left_widget)

        # Right column: Tree and buttons
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        self.tree = QTreeWidget()
        self.tree.setHeaderLabel("Files")
        self.tree.itemExpanded.connect(self.expand_item)
        self.tree.itemChanged.connect(self.update_selected_list)
        right_layout.addWidget(self.tree)
        browse_btn = QPushButton("Browse Directory")
        browse_btn.clicked.connect(self.browse_dir)
        right_layout.addWidget(browse_btn)
        copy_btn = QPushButton("Copy Selected Files")
        copy_btn.clicked.connect(self.copy_selected)
        right_layout.addWidget(copy_btn)
        splitter.addWidget(right_widget)

        splitter.setSizes([200, 600])
        main_layout.addWidget(splitter)
        self.setCentralWidget(central)
        self.root_path = None
        self.project_file = None

    def new_project(self):
        self.tree.clear()
        self.selected_list.clear()
        self.root_path = None
        self.project_file = None
        self.setWindowTitle("File Selector - Untitled Project")

    def load_project(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Load Project", "", "JSON Files (*.json)")
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    project_data = json.load(f)
                self.root_path = Path(project_data.get("root_path", ""))
                if not self.root_path.exists():
                    QMessageBox.warning(self, "Error", "Project root directory not found")
                    return
                self.project_file = Path(file_path)
                self.tree.clear()
                root_item = QTreeWidgetItem([self.root_path.name])
                root_item.setData(0, Qt.ItemDataRole.UserRole, self.root_path)
                root_item.setChildIndicatorPolicy(QTreeWidgetItem.ChildIndicatorPolicy.ShowIndicator)
                self.tree.addTopLevelItem(root_item)
                self.tree.expandItem(root_item)
                self.expand_item(root_item)
                self.setWindowTitle(f"File Selector - {self.project_file.name}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load project: {str(e)}")

    def save_project(self):
        if not self.root_path:
            QMessageBox.warning(self, "Warning", "No directory selected")
            return
        if not self.project_file:
            file_path, _ = QFileDialog.getSaveFileName(self, "Save Project", "", "JSON Files (*.json)")
            if not file_path:
                return
            self.project_file = Path(file_path)
        project_data = {
            "root_path": str(self.root_path),
            "selected_files": []
        }
        try:
            with open(self.project_file, 'w') as f:
                json.dump(project_data, f, indent=4)
            self.setWindowTitle(f"File Selector - {self.project_file.name}")
            QMessageBox.information(self, "Success", "Project saved successfully")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save project: {str(e)}")

    def browse_dir(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Select Directory")
        if dir_path:
            self.root_path = Path(dir_path)
            self.tree.clear()
            root_item = QTreeWidgetItem([self.root_path.name])
            root_item.setData(0, Qt.ItemDataRole.UserRole, self.root_path)
            root_item.setChildIndicatorPolicy(QTreeWidgetItem.ChildIndicatorPolicy.ShowIndicator)
            self.tree.addTopLevelItem(root_item)
            self.tree.expandItem(root_item)
            self.expand_item(root_item)

    def expand_item(self, item):
        path = item.data(0, Qt.ItemDataRole.UserRole)
        if path.is_dir() and item.childCount() == 0:
            for sub in sorted(path.iterdir()):
                child = QTreeWidgetItem([sub.name])
                child.setData(0, Qt.ItemDataRole.UserRole, sub)
                if sub.is_dir():
                    child.setChildIndicatorPolicy(QTreeWidgetItem.ChildIndicatorPolicy.ShowIndicator)
                else:
                    child.setCheckState(0, Qt.CheckState.Unchecked)
                item.addChild(child)

    def update_selected_list(self, item, column):
        self.selected_list.clear()
        iterator = QTreeWidgetItemIterator(self.tree, QTreeWidgetItemIterator.IteratorFlag.Checked)
        while iterator.value():
            path = iterator.value().data(0, Qt.ItemDataRole.UserRole)
            if path.is_file():
                self.selected_list.addItem(str(path))
            iterator += 1

    def remove_from_selection(self):
        selected = self.selected_list.selectedItems()
        if not selected:
            return
        path_str = selected[0].text()
        iterator = QTreeWidgetItemIterator(self.tree)
        while iterator.value():
            item = iterator.value()
            if str(item.data(0, Qt.ItemDataRole.UserRole)) == path_str:
                item.setCheckState(0, Qt.CheckState.Unchecked)
                break
            iterator += 1
        self.update_selected_list(None, 0)

    def copy_selected(self):
        if not self.root_path:
            QMessageBox.warning(self, "Warning", "No directory selected")
            return
        urls = []
        iterator = QTreeWidgetItemIterator(self.tree, QTreeWidgetItemIterator.IteratorFlag.Checked)
        while iterator.value():
            item = iterator.value()
            path = item.data(0, Qt.ItemDataRole.UserRole)
            if path.is_file():
                urls.append(QUrl.fromLocalFile(str(path)))
            iterator += 1
        if urls:
            mime = QMimeData()
            mime.setUrls(urls)
            QApplication.clipboard().setMimeData(mime)
            QMessageBox.information(self, "Success", f"{len(urls)} files copied to clipboard")
        else:
            QMessageBox.warning(self, "Warning", "No files selected")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = FileTree()
    window.show()
    sys.exit(app.exec())