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


# You need to be authenticated in Sabana to run this code.
# Go to https://sabana.io to sign-up
def test_main():
    """
    This is an example of how to deploy a
    c_axi_systolic_gemm_16x16_int instance.

    This instance implements a General Matrix Multiply (GEMM) operation.
    """

    # declare the data
    dt = np.uint32
    n = 16
    m = 255
    shape = (n, n)
    ctrl = "ctrl0"
    bufa = "bufferA"  # Link this buffer to mmio register 0x28
    bufb = "bufferB"  # Link this buffer to mmio register 0x34
    bufc = "bufferC"  # Link this buffer to mmio register 0x40
    a = np.random.randint(m, size=shape, dtype=dt)
    b = np.random.randint(m, size=shape, dtype=dt)
    cols = np.array([n], dt)
    start = np.ones([1], dt)
    done = np.array([14], dt)

    # create program
    program = Program()
    program.mmio_alloc(name=ctrl, size=0x00010000, base_address=0xA0000000)
    program.buffer_alloc(name=bufa, size=a.nbytes, mmio_name=ctrl, mmio_offset=0x28)
    program.buffer_alloc(name=bufb, size=b.nbytes, mmio_name=ctrl, mmio_offset=0x34)
    program.buffer_alloc(name=bufc, size=b.nbytes, mmio_name=ctrl, mmio_offset=0x40)
    program.mmio_write(cols, name=ctrl, offset=0x10)
    program.mmio_write(cols, name=ctrl, offset=0x18)
    program.mmio_write(cols, name=ctrl, offset=0x20)
    program.buffer_write(a, name=bufa, offset=0)
    program.buffer_write(b, name=bufb, offset=0)
    program.mmio_write(start, name=ctrl, offset=0x0)
    program.mmio_wait(done, name=ctrl, offset=0x0, timeout=4)
    program.buffer_read(name=bufc, offset=0, dtype=dt, shape=a.shape)
    program.mmio_dealloc(name=ctrl)
    program.buffer_dealloc(name=bufa)
    program.buffer_dealloc(name=bufb)
    program.buffer_dealloc(name=bufc)

    # deploy instance
    image_file = Path(__file__).resolve().parent.parent.joinpath("sabana.json")
    inst = Instance(image_file=image_file, verbose=True)
    # if you want to test the image without building it
    # uncomment the following line:
    #inst = Instance(image="robot/c_axi_systolic_gemm_16x16_int:0.1.0", verbose=True)
    inst.up()

    # run program
    responses = inst.execute(program)

    # terminate instance
    inst.down()

    # check results
    assert np.array_equal(responses[0], np.matmul(a, b))
    print("Check OK!")
    print("Multiplication of two random 16x16 matrices in Sabana successful!")


if __name__ == "__main__":
    test_main()
