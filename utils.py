from typing import Optional
import os
import re
from PySide2.QtWidgets import QMessageBox, QFileDialog


def open_pdf(relative_path: str) -> None:
    filename = os.path.join(os.path.dirname(__file__), relative_path)
    os.startfile(filename)


def open_save_dialog(file_extension: str) -> Optional[str]:
    file_dialog = QFileDialog()
    file_dialog.setFileMode(QFileDialog.AnyFile)
    file_dialog.setWindowTitle("Zapis")
    file_dialog.setLabelText(QFileDialog.Accept, "Zapisz")
    file_dialog.setNameFilter(f'(*{file_extension})')

    if file_dialog.exec_():
        file_path = file_dialog.selectedFiles()[0]
        file_name = re.search(r"/([^\s\./]+)(\.[^\s\./]+)?$", file_path)
        if file_name is None or file_name.group(1) is None:
            QMessageBox.critical(title='Błąd', text=f'Niepoprawna nazwa pliku.')
            return
        elif file_name.group(2) != file_extension:
            file_path += file_extension
        return file_path
    return
