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


def create_program(ai, bi):
    a = np.array([ai], dtype=np.int32)
    b = np.array([bi], dtype=np.int32)
    start = np.array([1], dtype=np.int32)
    finish = np.array([14], dtype=np.int32)
    # create a program
    ctrl = "c0"
    program = Program()
    program.mmio_alloc(name=ctrl, size=0x00010000, base_address=0xA0000000)
    program.mmio_write(a, name=ctrl, offset=0x10)
    program.mmio_write(b, name=ctrl, offset=0x18)
    program.mmio_write(start, name=ctrl, offset=0x0)
    program.mmio_wait(finish, name=ctrl, offset=0x0, timeout=1)
    program.mmio_read(name=ctrl, offset=0x20, dtype=a.dtype.type, shape=a.shape)
    program.mmio_dealloc(name=ctrl)
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

    def func(a, b):
        prog = create_program(a, b)
        res = driver.run(prog)
        return res[0][0]

    return func


def test_main():
    f = create_function()
    m = 8192

    for i in range(5):
        a = randint(0, m)
        b = randint(0, m)
        exp = a + b
        res = f(a, b)
        print(f"run:{i} python:{exp} fpga:{res}")
        assert exp == res


if __name__ == "__main__":
    test_main()
