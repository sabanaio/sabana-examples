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
from sabana.cc import Build
from sabana import Instance, Program


# You need to be authenticated in Sabana to run this code.
# Go to https://sabana.io to sign-up


def create_main_c():
    cwd = Path(__file__).resolve().parent.parent
    mainc = str(cwd.joinpath("cc/main_mul_by_six.c"))
    boots = str(cwd.joinpath("cc/boot.S"))
    picld = str(cwd.joinpath("cc/picorv32.ld"))

    build = Build(toolchain="riscv64-unknown-elf", version="10.2.0", verbose=True)
    cflags = "-c -Qn --std=c99 -march=rv32im -mabi=ilp32"
    build.cflags(cflags)
    ldflags = "-Ofast -ffreestanding -nostdlib -lgcc -march=rv32im -mabi=ilp32"
    build.ldflags(ldflags)
    build.file(mainc, flags="-Ofast")
    build.file(boots, flags="-Os")
    build.file(picld, flags="-Bstatic -T")

    result = build.compile()

    return result["binarray"]


def create_program(inputs):
    riscv_mainc = inputs["main"]

    # create inputs
    dt = np.uint32
    start = np.ones([1], dt)
    finish = np.array([14], dt)

    program = Program()
    program.mmio_alloc(name="c0", size=0x10000, base_address=0xA0000000)
    # allocate space for the whole 128K memory
    program.buffer_alloc(name="in", size=131072, mmio_name="c0", mmio_offset=0x10)
    program.buffer_alloc(name="out", size=131072, mmio_name="c0", mmio_offset=0x24)
    # copy the full 128K memory.
    program.mmio_write(np.array([32768], dtype=dt), name="c0", offset=0x1C)
    program.mmio_write(np.array([32768], dtype=dt), name="c0", offset=0x30)
    program.buffer_write(riscv_mainc, name="in", offset=0x0)
    # start the CPU
    program.mmio_write(start, name="c0", offset=0x0)
    # wait for the CPU to finish
    program.mmio_wait(finish, name="c0", offset=0x0, timeout=10)
    program.buffer_read(name="out", offset=0x7FFC, dtype=dt, shape=(1,))
    program.mmio_dealloc(name="c0")
    program.buffer_dealloc(name="in")
    program.buffer_dealloc(name="out")
    return program


def check_results(expected, results):
    assert results[0][0] == expected


def test_main():
    """
    This is an example of how to deploy a
    rtl_ez_picorv32_128k instance.

    This instance implements a PicoRV32 CPU with 128KBytes of RAM

    This example runs a constant multiplication operation in the PicoRV32 CPU
    """
    # compile RISC-V program
    inputs = {"main": create_main_c()}

    # create program
    program = create_program(inputs)

    # deploy instance
    image_file = Path(__file__).resolve().parent.parent.joinpath("sabana.json")
    inst = Instance(image_file=image_file, verbose=True)
    inst.up()

    # run program
    responses = inst.execute(program)

    # terminate instance
    inst.down()

    # compute expected
    expected = 18

    # check results
    check_results(expected, responses)

    print()
    print("Multiplication of two constants was successfully ")
    print("computed in a picorv32 deployed in Sabana!")
    print()


if __name__ == "__main__":
    test_main()
