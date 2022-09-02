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


def create_program(a, b):
    cols = np.array([a.shape[0]], np.int32)
    start = np.ones([1], np.int32)
    finish = np.array([14], np.int32)

    program = Program()
    program.mmio_alloc(name="c0", size=0x00010000, base_address=0xA0000000)
    program.buffer_alloc(name="bufA", size=a.nbytes, mmio_name="c0", mmio_offset=0x28)
    program.buffer_alloc(name="bufB", size=b.nbytes, mmio_name="c0", mmio_offset=0x34)
    program.buffer_alloc(name="bufC", size=b.nbytes, mmio_name="c0", mmio_offset=0x40)
    program.mmio_write(cols, name="c0", offset=0x10)
    program.mmio_write(cols, name="c0", offset=0x18)
    program.mmio_write(cols, name="c0", offset=0x20)
    program.buffer_write(a, name="bufA", offset=0)
    program.buffer_write(b, name="bufB", offset=0)
    program.mmio_write(start, name="c0", offset=0x0)
    program.mmio_wait(finish, name="c0", offset=0x0, timeout=4)
    program.buffer_read(name="bufC", offset=0, dtype=a.dtype.type, shape=a.shape)
    program.mmio_dealloc(name="c0")
    program.buffer_dealloc(name="bufA")
    program.buffer_dealloc(name="bufB")
    program.buffer_dealloc(name="bufC")
    return program


class Driver:
    def __init__(self):
        image_file = Path(__file__).resolve().parent.parent.joinpath("sabana.json")
        self.inst = Instance(image_file=image_file, verbose=True)
        self.inst.up()

    def run(self, program):
        return self.inst.execute(program)

    def __del__(self):
        self.inst.down()


def create_function():
    driver = Driver()

    def func(a, b):
        prog = create_program(a, b)
        res = driver.run(prog)
        return res[3]

    return func


# You need to be authenticated in Sabana to run this code.
# Go to https://sabana.io to sign-up
def test_main():
    """
    This is an example of how to deploy a
    c_axi_systolic_gemm_16x16_int instance.

    This instance implements a General Matrix Multiply (GEMM) operation on int numbers.
    """
    f = create_function()

    a = np.random.randint(0, 8192, size=(16, 16), dtype=np.int32)
    b = np.random.randint(0, 8192, size=(16, 16), dtype=np.int32)
    exp = np.matmul(a, b)
    res = f(a, b)
    np.array_equal(res, exp)
    print("Check OK!")
    print("Multiplication of two random 16x16 int matrices in Sabana successful!")


if __name__ == "__main__":
    test_main()
