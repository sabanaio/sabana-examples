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

import sys
from pathlib import Path
import numpy as np
from random import choice
import tempfile
import argparse

from sabana import Instance, Program
from sabana.cc import Build


def create_main(message=None, file=None):
    """
    Creates a c program that prints the string provided in message
    """
    header = "Greetings, I am your RISC-V CPU. This was your message:\\n"
    if message == None:
        select = choice([i for i in range(3)])
        msg = list(["Bubbly beer", "Meerkat flies", "Happy day"])[select]
    else:
        buffer_len = 0x20000 - 0x1FC00 - len(header)
        if len(message) >= buffer_len:
            print(f"ERROR: Select a message shorter than {buffer_len} characters")
            sys.exit(-1)
        else:
            msg = message

    print(f"Message to be sent: {msg}")

    program = '#include "print.h"\n'
    program += "int main(int argc, char ** argv){\n"
    program += f'print_str("{header}");\n'
    program += f'print_str("{msg}");\n'
    program += "return 0;}"

    with open(file, "w") as f:
        f.write(program)
        f.flush()


def create_main_bin(message=None):
    """
    Returns a binary executable inside a ndarray
    """
    cwd = Path(__file__).resolve().parent.parent

    build = Build(toolchain="riscv64-unknown-elf", version="10.2.0", verbose=True)
    cflags = "-c -Qn -Ofast --std=c99 -march=rv32im -mabi=ilp32"
    build.cflags(cflags)
    ldflags = "-Ofast -ffreestanding -nostdlib -lgcc -march=rv32im -mabi=ilp32"
    build.ldflags(ldflags)

    with tempfile.TemporaryDirectory() as tmpdirname:
        temp = Path(tmpdirname).joinpath("main_print.c")
        create_main(message=message, file=temp)
        build.file(temp)
        build.file(cwd.joinpath("cc/print.c"))
        build.file(cwd.joinpath("cc/print.h"))
        build.file(cwd.joinpath("cc/boot.S"))
        build.file(cwd.joinpath("cc/picorv32.ld"), flags="-Bstatic -T")
        try:
            result = build.compile()
        except Exception as e:
            print("ERROR...")
            print(e)
            sys.exit(-1)
        else:
            return result["binarray"]


def create_program(riscv_mainc=None):
    """
    Returns a program to be sent to a Sabana instance
    """
    # create inputs
    dt = np.uint32
    dt8 = np.uint8
    start = np.ones([1], dt)
    finish = np.array([14], dt)

    program = Program()
    program.mmio_alloc(name="c0", size=0x100, base_address=0xA0000000)
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
    # read the print buffer
    program.buffer_read(name="out", offset=0x1FC00, dtype=dt8, shape=(0x400,))
    program.mmio_dealloc(name="c0")
    program.buffer_dealloc(name="in")
    program.buffer_dealloc(name="out")
    return program


def test_main(message=None):
    """
    Print a message in a RISC-V CPU deployed in Sabana.

    You need to be authenticated in Sabana to run this code.
    Go to https://sabana.io to sign-up.
    """

    # compile RISC-V program
    main = create_main_bin(message=message)

    # create program
    program = create_program(main)

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

    # print messsage from CPU
    print("\nRemote message:\n")
    print(responses[0].tobytes().decode("utf-8"), "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=test_main.__doc__)
    parser.add_argument(
        "-m", "--message", type=str, help="message to pass to the RISC-V CPU"
    )

    args = parser.parse_args()
    test_main(message=args.message)
