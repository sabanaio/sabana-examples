# Copyright 2022 Sabana Technologies, Inc
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from pathlib import Path
import numpy as np
from sabana import Instance, Program
from random import randint
import pyrtl
from pyrtl_muladd import muladd


def create_program(a, b, c):
    ai = np.array([a], dtype=np.int32)
    bi = np.array([b], dtype=np.int32)
    ci = np.array([c], dtype=np.int32)
    start = np.array([1], dtype=np.int32)
    finish = np.array([14], dtype=np.int32)
    program = Program()
    program.mmio_alloc(name="c0", size=0x00010000, base_address=0xA0000000)
    program.mmio_write(ai, name="c0", offset=0x10)
    program.mmio_write(bi, name="c0", offset=0x18)
    program.mmio_write(ci, name="c0", offset=0x20)
    program.mmio_write(start, name="c0", offset=0x0)
    program.mmio_wait(finish, name="c0", offset=0x0, timeout=1)
    program.mmio_read(name="c0", offset=0x28, dtype=np.int32, shape=(1,))
    program.mmio_dealloc(name="c0")
    return program


class Driver:
    def __init__(self):
        print("Every run is a round-trip to a cloud FPGA...")
        print("Initializing instance...")
        image_file = Path(__file__).resolve().parent.parent.joinpath("sabana.json")
        self.inst = Instance(image_file=image_file)
        self.inst.up()

    def run(self, program):
        return self.inst.execute(program)

    def __del__(self):
        print("Terminating instance...")
        self.inst.down()


def create_function():
    driver = Driver()

    def func(a, b, c):
        prog = create_program(a, b, c)
        res = driver.run(prog)
        return res[0][0]

    return func


def test_main():
    f = create_function()
    m = 4
    y = muladd()
    s = pyrtl.Simulation()
    for i in range(8):
        a = randint(0, m)
        b = randint(0, m)
        c = randint(0, m)
        s.step({"a": a, "b": b, "c": c})
        sim = s.value[y]
        res = f(a, b, c)
        exp = a * b + c
        print(f"run:{i} python:{exp} sim:{sim} fpga:{res}")


if __name__ == "__main__":
    test_main()
