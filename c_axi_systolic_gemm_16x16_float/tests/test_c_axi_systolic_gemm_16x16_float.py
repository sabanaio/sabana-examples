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
    c_axi_systolic_gemm_16x16_float instance.

    This instance implements a General Matrix Multiply (GEMM) operation on float numbers.
    """

    # declare the data
    dt = np.uint32
    dtf = np.float32
    n = 16
    m = 255
    shape = (n, n)
    ctrl = "ctrl0"
    bufa = "bufferA"  # Link this buffer to mmio register 0x28
    bufb = "bufferB"  # Link this buffer to mmio register 0x34
    bufc = "bufferC"  # Link this buffer to mmio register 0x40
    a = np.random.random(size=shape).astype(dtf) * m
    b = np.random.random(size=shape).astype(dtf) * m
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
    program.buffer_read(name=bufc, offset=0, dtype=dtf, shape=a.shape)
    program.mmio_dealloc(name=ctrl)
    program.buffer_dealloc(name=bufa)
    program.buffer_dealloc(name=bufb)
    program.buffer_dealloc(name=bufc)

    # deploy instance
    image_file = Path(__file__).resolve().parent.parent.joinpath("sabana.json")
    inst = Instance(image_file=image_file, verbose=True)
    inst.up()

    # run program
    responses = inst.execute(program)

    # terminate instance
    inst.down()

    # check results
    np.testing.assert_allclose(responses[0], np.matmul(a, b), rtol=1e-3)
    print("Check OK!")
    print("Multiplication of two random 16x16 float matrices in Sabana successful!")


if __name__ == "__main__":
    test_main()
