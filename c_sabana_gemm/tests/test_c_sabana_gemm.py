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
    start = np.ones([1], np.int32)
    finish = np.array([14], np.int32)
    a = np.random.randint(255, size=(4, 4), dtype=np.int32)
    b = np.random.randint(255, size=(4, 4), dtype=np.int32)
    # create a program
    program = Program()
    program.mmio_alloc(name="c0", size=0x00010000, base_address=0xA0000000)
    program.buffer_alloc(name="a", size=a.nbytes, mmio_name="c0", mmio_offset=0x10)
    program.buffer_alloc(name="b", size=b.nbytes, mmio_name="c0", mmio_offset=0x1C)
    program.buffer_alloc(name="c", size=b.nbytes, mmio_name="c0", mmio_offset=0x28)
    program.buffer_write(a, name="a", offset=0)
    program.buffer_write(b, name="b", offset=0)
    program.mmio_write(start, name="c0", offset=0x0)
    program.mmio_wait(finish, name="c0", offset=0x0, timeout=4)
    program.buffer_read(name="c", offset=0, dtype=np.int32, shape=a.shape)
    program.mmio_dealloc(name="c0")
    program.buffer_dealloc(name="a")
    program.buffer_dealloc(name="b")
    program.buffer_dealloc(name="c")
    # deploy instance
    image_file = Path(__file__).resolve().parent.parent.joinpath("sabana.json")
    inst = Instance(image_file=image_file, verbose=True)
    # if you want to test the image without building it
    # uncomment the following line:
    #inst = Instance(image="robot/c_sabana_gemm:0.1.0", verbose=True)
    inst.up()
    # run program
    responses = inst.execute(program)
    # terminate instance
    inst.down()
    # check results
    assert np.array_equal(responses[0], np.matmul(a, b))
    print("Multiplied two random 4x4 matrices successfully!")


if __name__ == "__main__":
    test_main()
