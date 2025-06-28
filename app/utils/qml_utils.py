from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtCore import QUrl
from pathlib import Path

def handle_qml_warnings(warnings):
    for w in warnings:
        print(f"[QML WARNING] {w.toString()}")

def init_engine(qml_path: Path, context_props: dict) -> QQmlApplicationEngine:
    engine = QQmlApplicationEngine()
    engine.warnings.connect(handle_qml_warnings)

    ctx = engine.rootContext()
    for name, obj in context_props.items():
        ctx.setContextProperty(name, obj)

    engine.load(QUrl.fromLocalFile(str(qml_path)))
    return engine

def set_window_title(root, title: str):
    """Set window title for QML root object, supporting various Qt types."""
    if hasattr(root, 'setTitle'):
        root.setTitle(title)
    elif hasattr(root, 'windowTitle'):
        root.windowTitle = title
    elif hasattr(root, 'title'):
        root.title = title
