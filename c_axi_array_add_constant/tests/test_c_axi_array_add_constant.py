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
    """
    This is an example of how to deploy a
    c_axi_array_add_constant instance.

    This instance adds 100 to a vector of integers.
    """

    # declare the data
    dt = np.uint32
    a = np.random.randint(255, size=(50,), dtype=dt)
    start = np.ones([1], dt)
    finish = np.array([14], dt)

    # create program
    program = Program()
    program.mmio_alloc(name="c0", size=0x00010000, base_address=0xA0000000)
    program.buffer_alloc(name="buff_a", size=a.nbytes, mmio_name="c0", mmio_offset=0x18)
    # write the size of the input (50 is the max, see: sabana.cc)
    program.mmio_write(np.array([50], dt), name="c0", offset=0x10)
    program.buffer_write(a, name="buff_a", offset=0)
    program.mmio_write(start, name="c0", offset=0x0)
    program.mmio_wait(finish, name="c0", offset=0x0, timeout=4)
    program.buffer_read(name="buff_a", offset=0, dtype=dt, shape=a.shape)
    program.mmio_dealloc(name="c0")
    program.buffer_dealloc(name="buff_a")

    # deploy instance
    image_file = Path(__file__).resolve().parent.parent.joinpath("sabana.json")
    inst = Instance(image_file=image_file, verbose=True)
    # if you want to test the image without building it
    # uncomment the following line:
    # inst = Instance(image="robot/c_axi_array_add_constant:0.1.0", verbose=True)
    inst.up()

    # run program
    responses = inst.execute(program)

    # terminate instance
    inst.down()

    # check results
    assert np.array_equal(responses[1], a + 100)
    print("Check OK!")
    print("Adding 100 to a vector of random integers was successful in Sabana!")


if __name__ == "__main__":
    test_main()
