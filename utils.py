import os


def open_pdf(relative_path: str) -> None:
    filename = os.path.join(os.path.dirname(__file__), relative_path)
    os.startfile(filename)
