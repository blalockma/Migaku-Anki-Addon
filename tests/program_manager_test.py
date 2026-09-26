import importlib.util
import os
import sys
import types
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]


def load_program_manager():
    src_package = types.ModuleType("src")
    src_package.__path__ = [str(ROOT_DIR / "src")]
    sys.modules["src"] = src_package

    connection_package = types.ModuleType("src.migaku_connection")
    connection_package.__path__ = [str(ROOT_DIR / "src" / "migaku_connection")]
    sys.modules["src.migaku_connection"] = connection_package

    aqt = types.ModuleType("aqt")
    aqt.qt = types.SimpleNamespace(QObject=object, QThread=object)
    sys.modules["aqt"] = aqt

    anki = types.ModuleType("anki")
    anki_utils = types.ModuleType("anki.utils")
    anki_utils.is_lin = False
    anki_utils.is_mac = True
    anki_utils.is_win = False
    sys.modules["anki"] = anki
    sys.modules["anki.utils"] = anki_utils

    appdirs = types.ModuleType("appdirs")
    appdirs.user_data_dir = lambda *_args: "/shared"
    sys.modules["appdirs"] = appdirs

    requests = types.ModuleType("requests")
    requests.HTTPError = OSError
    sys.modules["requests"] = requests

    util = types.ModuleType("src.util")
    util.user_path = lambda name: os.path.join("/addon", name)
    util.show_critical = lambda message: critical_messages.append(message)
    sys.modules["src.util"] = util
    sys.modules["src.config"] = types.ModuleType("src.config")

    spec = importlib.util.spec_from_file_location(
        "src.migaku_connection.program_manager",
        ROOT_DIR / "src" / "migaku_connection" / "program_manager.py",
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


critical_messages = []
program_manager = load_program_manager()

manager = program_manager.ProgramManager.__new__(program_manager.ProgramManager)
manager.program_name = "ffmpeg"
manager.program_executable_name = "ffmpeg"
manager.local_program_path = "/addon/ffmpeg"
manager.shared_user_program_name = "/shared/ffmpeg"

checked_paths = []
manager.check_set_program_path = (
    lambda path: checked_paths.append(path) or path == "/opt/homebrew/bin/ffmpeg"
)
downloads = []
manager.start_download = lambda: downloads.append(True)
manager.make_available()

assert checked_paths == [
    "ffmpeg",
    "/addon/ffmpeg",
    "/shared/ffmpeg",
    "/opt/homebrew/bin/ffmpeg",
]
assert not downloads

checked_paths.clear()
manager.check_set_program_path = lambda path: checked_paths.append(path) or False
program_manager.platform.machine = lambda: "arm64"
manager.make_available()

assert checked_paths[-3:] == [
    "/opt/homebrew/bin/ffmpeg",
    "/usr/local/bin/ffmpeg",
    "/opt/local/bin/ffmpeg",
]
assert "brew install ffmpeg" in critical_messages[-1]
assert not downloads

program_manager.platform.machine = lambda: "x86_64"
manager.make_available()
assert downloads == [True]

print("✓ macOS program discovery finds Homebrew and avoids Intel downloads on arm64")
