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
import json
from vta import Load, Addi, Store, Finish


class Driver:
    def __init__(self, image=None):
        if image:
            self.inst = Instance(image=image, verbose=False)
        else:
            file = Path(__file__).resolve().parent.parent.joinpath("sabana.json")
            self.inst = Instance(image_file=file, verbose=False)

        self.inst.up()

    def run(self, program):
        return self.inst.execute(program)

    def __del__(self):
        self.inst.down()


def finish(spec):
    def vta_program(spec):
        finish = Finish(spec)
        program = finish.packbits()
        return program

    def init(vta_program):
        size = vta_program.shape[0]
        num = np.array([size // 16], dtype=np.uint32)
        prog = Program()
        prog.mmio_alloc(name="c0", size=0x00010000, base_address=0xA0000000)
        prog.buffer_alloc(name="instr", size=size)
        prog.buffer_write(vta_program, name="instr", offset=0)
        prog.mmio_write(num, name="c0", offset=0x8)
        return prog

    def run(addr):
        start = np.array([1], dtype=np.uint32)
        finish = np.array([2], dtype=np.uint32)
        prog = Program()
        prog.mmio_write(np.array([addr], dtype=np.uint32), name="c0", offset=0xC)
        prog.mmio_write(start, name="c0", offset=0x0)
        prog.mmio_wait(finish, name="c0", offset=0x0, timeout=1)
        return prog

    def finalize():
        prog = Program()
        prog.mmio_dealloc(name="c0")
        prog.buffer_dealloc(name="instr")
        return prog

    print("[test_finish] begin")
    driver = Driver()
    print("Copying program...")
    res = driver.run(init(vta_program(spec)))
    instr_addr = res[0]
    print("Running program...")
    res = driver.run(run(instr_addr))
    print("Cleaning up...")
    res = driver.run(finalize())
    print("[test_finish] end")


def load_store(spec):
    def gen_data():
        inp = []
        for i in range(64):
            inp.append(i)
            inp = inp + 3 * [0]
        inp = np.array(inp, dtype=np.uint8)
        return inp

    def init_data(data):
        prog = Program()
        prog.buffer_alloc(name="inp", size=256)
        prog.buffer_alloc(name="out", size=256)
        prog.buffer_write(data, name="inp", offset=0)
        return prog

    def vta_program(spec, load_addr, store_addr):
        # normalize addreesses
        laddr = load_addr // 64
        saddr = store_addr // 16
        load = Load(spec)
        load.set_field("dram_base", laddr)
        load.set_field("y_size", 1)
        load.set_field("x_size", 1)
        addi = Addi(spec)
        addi.set_field("uop_end", 1)
        addi.set_field("push_next_dep", 1)
        addi.set_field("iter_in", 1)
        addi.set_field("iter_out", 1)
        store = Store(spec)
        store.set_field("dram_base", saddr)
        store.set_field("y_size", 1)
        store.set_field("x_size", 1)
        store.set_field("pop_prev_dep", 1)
        store.set_field("push_prev_dep", 1)
        finish = Finish(spec)
        finish.set_field("pop_next_dep", 1)
        program = load.packbits()
        program = np.concatenate((program, addi.packbits()), dtype=np.uint8)
        program = np.concatenate((program, store.packbits()), dtype=np.uint8)
        program = np.concatenate((program, finish.packbits()), dtype=np.uint8)
        return program

    def init_prog(vta_program):
        size = vta_program.shape[0]
        num = np.array([size // 16], dtype=np.uint32)
        prog = Program()
        prog.mmio_alloc(name="c0", size=0x00010000, base_address=0xA0000000)
        prog.buffer_alloc(name="instr", size=size)
        prog.buffer_write(vta_program, name="instr", offset=0)
        prog.mmio_write(num, name="c0", offset=0x8)
        return prog

    def run(addr):
        start = np.array([1], dtype=np.uint32)
        finish = np.array([2], dtype=np.uint32)
        prog = Program()
        prog.mmio_write(np.array([addr], dtype=np.uint32), name="c0", offset=0xC)
        prog.mmio_write(start, name="c0", offset=0x0)
        prog.mmio_wait(finish, name="c0", offset=0x0, timeout=4)
        prog.buffer_read(name="out", offset=0, dtype=np.uint8, shape=(256,))
        return prog

    def finalize():
        prog = Program()
        prog.mmio_dealloc(name="c0")
        prog.buffer_dealloc(name="instr")
        prog.buffer_dealloc(name="inp")
        prog.buffer_dealloc(name="out")
        return prog

    print("[test_load_store] begin")
    driver = Driver()
    print("Copying data...")
    exp = gen_data()
    res = driver.run(init_data(exp))
    print("Copying program...")
    load_addr = res[0]
    store_addr = res[1]
    res = driver.run(init_prog(vta_program(spec, load_addr, store_addr)))
    print("Running program...")
    instr_addr = res[0]
    res = driver.run(run(instr_addr))
    result = res[0]
    print("Cleaning up...")
    res = driver.run(finalize())
    np.array_equal(result[0:16], np.arange(16, dtype=np.uint8))
    print("[test_load_store] end")


def test_isa():
    spec = Path(__file__).resolve().parent.joinpath("vta_spec.json")
    with open(spec, "r") as f:
        spec = json.loads(f.read())

    finish(spec)
    load_store(spec)


if __name__ == "__main__":
    test_isa()
