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
    m = 64
    dtype = np.int8
    shape = (4,)
    a = np.random.randint(m, size=shape, dtype=dtype)
    b = np.random.randint(m, size=shape, dtype=dtype)
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
    program.mmio_read(name=ctrl, offset=0x20, dtype=dtype, shape=shape)
    program.mmio_dealloc(name=ctrl)
    # deploy instance
    image_file = Path(__file__).resolve().parent.parent.joinpath("sabana.json")
    inst = Instance(image_file=image_file, verbose=True)
    inst.up()
    # run program
    responses = inst.execute(program)
    # terminate instance
    inst.down()
    # check results
    expected = a + b
    assert np.array_equal(expected, responses[0])
    print("Added two numpy arrays successfully")


if __name__ == "__main__":
    test_main()
