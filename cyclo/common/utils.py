from typing import Optional
import os
import re

from PySide2.QtWidgets import QWidget, QFileDialog
from common.message_handler import MessageHandler

from config import dependencies_path

def open_pdf(relative_path: str) -> None:
    filename = dependencies_path(relative_path)
    os.startfile(filename)

def open_save_dialog(parent: QWidget, file_extension: str) -> Optional[str]:
    file_dialog = QFileDialog(parent)
    file_dialog.setFileMode(QFileDialog.AnyFile)
    file_dialog.setWindowTitle("Zapis")
    file_dialog.setLabelText(QFileDialog.Accept, "Zapisz")
    file_dialog.setNameFilter(f'(*{file_extension})')

    if file_dialog.exec_():
        file_path = file_dialog.selectedFiles()[0]
        file_name = re.search(r"/([^\s\./]+)(\.[^\s\./]+)?$", file_path)
        if file_name is None or file_name.group(1) is None:
            MessageHandler.critical(file_dialog, title='Błąd', message=f'Niepoprawna nazwa pliku.')
            return
        elif file_name.group(2) != file_extension:
            file_path += file_extension
        return file_path
    return
