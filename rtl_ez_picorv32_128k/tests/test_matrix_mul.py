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

# The following example demonstrates how to load arguments to the memory of a
# picorv32 hosted in the Sabana platform.
#
# The memory layout we use to interact with the picorv32 is as follows:
#
# 0x1ffff -- End of BRAM - 131072 bytes
# 0x1fffc -- Sides of square matrices
# 0x1fff8 -- Pointer to the first element of matrix a
# 0x1fff4 -- Pointer to the first element of matrix b
# 0x1fff0 -- Pointer to the first element of matrix r (resutls)
# 0x1ffef -- End of matrix a
# 0x1ff8b -- Start of matrix a
# 0x1ff8a -- End of matrix b
# 0x1ff26 -- Start of matrix b
# 0x1ff25 -- End of matrix r
# 0x1fec1 -- Start of matrix r

from pathlib import Path
import numpy as np
from sabana.cc import Build
from sabana import Program, Instance


# You need to be authenticated in Sabana to run this code.
# Go to https://sabana.io to sign-up


def create_inputs():
    side = 64
    dt = np.uint32
    return {
        "a": np.random.randint(0, 100, [side, side], dtype=dt),
        "b": np.random.randint(0, 100, [side, side], dtype=dt),
    }


def create_main_c():
    cwd = Path(__file__).resolve().parent.parent
    build = Build(toolchain="riscv64-unknown-elf", version="10.2.0", verbose=True)
    cflags = "-c -Qn --std=c99 -march=rv32im -mabi=ilp32"
    build.cflags(cflags)
    ldflags = "-Ofast -ffreestanding -nostdlib -lgcc -march=rv32im -mabi=ilp32"
    build.ldflags(ldflags)
    build.file(cwd.joinpath("cc/main_matrix_mul.c"), flags="-Ofast")
    build.file(cwd.joinpath("cc/boot.S"), flags="-Os")
    build.file(cwd.joinpath("cc/picorv32.ld"), flags="-Bstatic -T")

    result = build.compile()

    return result["binarray"]


def create_program(inputs):
    matrix_a = inputs["a"]
    matrix_b = inputs["b"]
    riscv_mainc = inputs["main"]

    # create inputs
    dt = np.uint32
    start = np.ones([1], dt)
    finish = np.array([14], dt)

    # calculate the offset where the arguments and the data will be placed.
    param_off = 131072 - (4 * 4)
    matrix_a_ptr = param_off - matrix_a.nbytes
    matrix_b_ptr = matrix_a_ptr - matrix_b.nbytes
    matrix_r_ptr = matrix_b_ptr - matrix_b.nbytes

    # create program
    program = Program()
    program.mmio_alloc(name="c0", size=0x100, base_address=0xA0000000)

    # allocate space for the whole 128K memory
    program.buffer_alloc(name="in", size=131072, mmio_name="c0", mmio_offset=0x10)
    program.buffer_alloc(name="out", size=131072, mmio_name="c0", mmio_offset=0x24)

    # copy the full 128K memory.
    program.mmio_write(np.array([32768], dtype=dt), name="c0", offset=0x1C)
    program.mmio_write(np.array([32768], dtype=dt), name="c0", offset=0x30)
    program.buffer_write(riscv_mainc, name="in", offset=0x0)

    # write SW function parameters
    program.buffer_write(
        np.array(
            [matrix_r_ptr, matrix_b_ptr, matrix_a_ptr, matrix_a.shape[0]], dtype=dt
        ),
        name="in",
        offset=param_off,
    )

    # write input matrices
    program.buffer_write(matrix_a, name="in", offset=matrix_a_ptr)
    program.buffer_write(matrix_b, name="in", offset=matrix_b_ptr)

    # start the CPU
    program.mmio_write(start, name="c0", offset=0x0)
    # wait for the CPU to finish
    program.mmio_wait(finish, name="c0", offset=0x0, timeout=10)

    # retrieve results
    program.buffer_read(name="out", offset=matrix_r_ptr, dtype=dt, shape=matrix_a.shape)

    program.mmio_dealloc(name="c0")
    program.buffer_dealloc(name="in")
    program.buffer_dealloc(name="out")
    return program


def check_results(expected, results):
    assert np.array_equal(expected, results[0])


def test_main():
    """
    This is an example of how to deploy a
    rtl_ez_picorv32_128k instance.

    This instance implements a PicoRV32 CPU with 128KBytes of RAM

    This example runs matrix multiplication in the PicoRV32 CPU
    """
    # create inputs
    inputs = create_inputs()

    # compile RISC-V program
    inputs["main"] = create_main_c()

    # create sabana program
    program = create_program(inputs)

    # deploy instance
    image_file = Path(__file__).resolve().parent.parent.joinpath("sabana.json")
    inst = Instance(image_file=image_file, verbose=True)
    # if you want to test the image without building it
    # uncomment the following line:
    #inst = Instance(image="robot/rtl_ez_picorv32_128k:0.1.0", verbose=True)
    inst.up()

    # run program
    responses = inst.execute(program)

    # terminate instance
    inst.down()

    # compute expected
    expected = np.matmul(inputs["a"], inputs["b"])

    # check results
    check_results(expected, responses)

    print()
    print("Matrix multiplication of two 64x64 random integer matrices was")
    print("successfully computed in a picorv32 deployed in Sabana!")
    print()


if __name__ == "__main__":
    test_main()
