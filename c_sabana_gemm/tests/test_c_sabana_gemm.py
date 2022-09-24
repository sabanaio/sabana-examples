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


class Driver:
    def __init__(self, image=None):
        if image:
            self.inst = Instance(image=image, verbose=True)
        else:
            file = Path(__file__).resolve().parent.parent.joinpath("sabana.json")
            self.inst = Instance(image_file=file, verbose=True)

        self.inst.up()

    def run(self, program):
        return self.inst.execute(program)

    def __del__(self):
        self.inst.down()


def create_program(a, b):
    start = np.ones([1], dtype=np.uint32)
    finish = np.array([14], dtype=np.uint32)
    program = Program()
    program.mmio_alloc(name="c0", size=0x00010000, base_address=0xA0000000)
    program.buffer_alloc(name="a", size=a.nbytes, mmio_name="c0", mmio_offset=0x10)
    program.buffer_alloc(name="b", size=b.nbytes, mmio_name="c0", mmio_offset=0x1C)
    program.buffer_alloc(name="c", size=b.nbytes, mmio_name="c0", mmio_offset=0x28)
    program.buffer_write(a, name="a", offset=0)
    program.buffer_write(b, name="b", offset=0)
    program.mmio_write(start, name="c0", offset=0x0)
    program.mmio_wait(finish, name="c0", offset=0x0, timeout=4)
    program.buffer_read(name="c", offset=0, dtype=np.uint32, shape=a.shape)
    program.mmio_dealloc(name="c0")
    program.buffer_dealloc(name="a")
    program.buffer_dealloc(name="b")
    program.buffer_dealloc(name="c")
    return program


def create_function(image=None):
    driver = Driver(image)

    def func(a, b):
        prog = create_program(a, b)
        res = driver.run(prog)
        return res[3]

    return func


def test_main():
    n = 4
    m = 32
    a = np.random.randint(m, size=(n, n), dtype=np.uint32)
    b = np.random.randint(m, size=(n, n), dtype=np.uint32)
    f = create_function()
    res = f(a, b)
    assert np.array_equal(res, np.matmul(a, b))
    print("Matrix multiplication passed")


if __name__ == "__main__":
    test_main()