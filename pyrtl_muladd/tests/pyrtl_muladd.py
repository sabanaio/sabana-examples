import io
import pyrtl
from pathlib import Path


def muladd():
    a = pyrtl.Input(32, "a")
    b = pyrtl.Input(32, "b")
    c = pyrtl.Input(32, "c")
    y = pyrtl.Output(32, "y")
    y <<= a * b + c
    return y


if __name__ == "__main__":
    y = muladd()
    path = Path(__file__).resolve().parent.parent.joinpath("src", "pyrtl.v")
    with open(path, "w") as f:
        pyrtl.output_to_verilog(f)
