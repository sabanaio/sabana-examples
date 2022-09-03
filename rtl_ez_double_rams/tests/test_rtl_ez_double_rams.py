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


def test_main():
    # create inputs
    n = 16  # can go up to 64
    m = 10
    dtype = np.int32
    shape = (1, n)
    start = np.ones([1], dtype)
    finish = np.array([14], dtype)
    a = np.random.randint(m, size=shape, dtype=dtype)
    b = np.array([3], dtype=dtype)
    length = np.array([n], dtype=dtype)
    # create a program
    na = "a"
    ny = "y"
    ctrl = "c0"
    program = Program()
    program.mmio_alloc(name=ctrl, size=0x00010000, base_address=0xA0000000)
    program.buffer_alloc(name=na, size=a.nbytes, mmio_name=ctrl, mmio_offset=0x18)
    program.buffer_alloc(name=ny, size=a.nbytes, mmio_name=ctrl, mmio_offset=0x2C)
    program.buffer_write(a, name=na, offset=0)
    program.mmio_write(b, name=ctrl, offset=0x10)
    program.mmio_write(length, name=ctrl, offset=0x24)
    program.mmio_write(length, name=ctrl, offset=0x38)
    program.mmio_write(start, name=ctrl, offset=0x0)
    program.mmio_wait(finish, name=ctrl, offset=0x0, timeout=4)
    program.buffer_read(name=ny, offset=0, dtype=dtype, shape=shape)
    program.mmio_dealloc(name=ctrl)
    program.buffer_dealloc(name=na)
    program.buffer_dealloc(name=ny)
    # deploy instance
    image_file = Path(__file__).resolve().parent.parent.joinpath("sabana.json")
    inst = Instance(image_file=image_file, verbose=True)
    # if you want to test the image without building it
    # uncomment the following line:
    # inst = Instance(image="robot/rtl_ez_double_rams:0.1.0", verbose=True)
    inst.up()
    # run program
    responses = inst.execute(program)
    # terminate instance
    inst.down()
    # check results
    expected = a + b[0]
    assert np.array_equal(expected, responses[2])
    print("Added constant to numpy array successfully")


if __name__ == "__main__":
    test_main()
