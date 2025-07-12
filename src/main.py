import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget, QPushButton, QFileDialog, QMessageBox, QTreeWidgetItemIterator
from PyQt6.QtCore import Qt, QUrl, QMimeData
from pathlib import Path
import pyperclip  # Retained for fallback, but unused here

class FileTree(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("File Selector")
        self.setGeometry(100, 100, 800, 600)
        central = QWidget()
        layout = QVBoxLayout(central)
        
        self.tree = QTreeWidget()
        self.tree.setHeaderLabel("Files")
        self.tree.itemExpanded.connect(self.expand_item)
        layout.addWidget(self.tree)
        
        browse_btn = QPushButton("Browse Directory")
        browse_btn.clicked.connect(self.browse_dir)
        layout.addWidget(browse_btn)
        
        copy_btn = QPushButton("Copy Selected Files")
        copy_btn.clicked.connect(self.copy_selected)
        layout.addWidget(copy_btn)
        
        self.setCentralWidget(central)
        self.root_path = None

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
            self.expand_item(root_item)  # Initial load

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

    def copy_selected(self):
        if not self.root_path:
            QMessageBox.warning(self, "Warning", "No directory selected")
            return
        urls = []
        iterator = QTreeWidgetItemIterator(self.tree, QTreeWidgetItemIterator.IteratorFlag.Checked)
        while iterator.value():
            item = iterator.value()
            path = item.data(0, Qt.ItemDataRole.UserRole)
            if path.is_file():  # and path.suffix.lower() in ['.txt', '.py', '.md', '.rs', '.cs', '.js', '.html', '.css', '.json', '.razor']:  # Uncomment/filter if needed
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