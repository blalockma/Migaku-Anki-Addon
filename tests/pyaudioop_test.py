import importlib.util
import struct
from pathlib import Path


root = Path(__file__).parents[1]
spec = importlib.util.spec_from_file_location(
    "pyaudioop", root / "src" / "lib" / "shared" / "pydub" / "pyaudioop.py"
)
pyaudioop = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pyaudioop)

samples = struct.pack("=hh", -3, 4)
assert pyaudioop._sample_count(samples, 2) == 2
assert pyaudioop.rms(samples, 2) == 3

print("✓ pyaudioop counts complete samples as integers")
