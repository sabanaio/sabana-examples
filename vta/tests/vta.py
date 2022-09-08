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

import numpy as np


class Instruction:
    def __init__(self):
        self.fields = {}
        self.values = {}
        self.widths = {}

    def set_field(self, key, value):
        if not key in self.values:
            raise VTAError("field {} not found".format(key))
        self.values[key] = value

    def unpackbits(self):
        res = np.array([], dtype=np.uint8)
        for f in self.fields:
            val = np.array([self.values[f]], dtype=np.uint32)
            val = np.frombuffer(val.tobytes(), dtype=np.uint8)
            bit = np.unpackbits(val, bitorder="little", count=self.widths[f])
            res = np.concatenate((res, bit), dtype=np.uint8)
        return res

    def packbits(self):
        res = self.unpackbits()
        return np.packbits(res, bitorder="little")


class VTAError(Exception):
    pass


class MemInstr(Instruction):
    def __init__(self, spec):
        super().__init__()
        self.fields = [
            "opcode",
            "pop_prev_dep",
            "pop_next_dep",
            "push_prev_dep",
            "push_next_dep",
            "mem_type",
            "sram_base",
            "dram_base",
            "empty",
            "y_size",
            "x_size",
            "x_stride",
            "y_pad_0",
            "y_pad_1",
            "x_pad_0",
            "x_pad_1",
        ]
        for f in self.fields:
            self.values[f] = 0
            if f == "opcode":
                self.widths[f] = spec["width"]["opcode"]
            elif (
                f == "pop_prev_dep"
                or f == "pop_next_dep"
                or f == "push_prev_dep"
                or f == "push_next_dep"
            ):
                self.widths[f] = spec["width"]["flag"]
            elif f == "mem_type":
                self.widths[f] = spec["width"]["mem_id"]
            elif f == "sram_base":
                self.widths[f] = spec["width"]["mem_sram"]
            elif f == "dram_base":
                self.widths[f] = spec["width"]["mem_dram"]
            elif f == "y_size":
                self.widths[f] = spec["width"]["mem_size"]
            elif f == "x_size":
                self.widths[f] = spec["width"]["mem_size"]
            elif f == "x_stride":
                self.widths[f] = spec["width"]["mem_stride"]
            elif f == "y_pad_0" or f == "y_pad_1" or f == "x_pad_0" or f == "x_pad_1":
                self.widths[f] = spec["width"]["mem_pad"]
            elif f == "empty":
                self.widths[f] = spec["width"]["mem_empty"]
        assert len(self.values) == len(self.widths) and len(self.values) == len(
            self.fields
        )


class GemmInstr(Instruction):
    def __init__(self, spec):
        super().__init__()
        self.fields = [
            "opcode",
            "pop_prev_dep",
            "pop_next_dep",
            "push_prev_dep",
            "push_next_dep",
            "reset_flag",
            "uop_bgn",
            "uop_end",
            "iter_out",
            "iter_in",
            "empty",
            "dst_factor_out",
            "dst_factor_in",
            "src_factor_out",
            "src_factor_in",
            "wgt_factor_out",
            "wgt_factor_in",
        ]
        for f in self.fields:
            self.values[f] = 0
            if f == "opcode":
                self.widths[f] = spec["width"]["opcode"]
            elif (
                f == "pop_prev_dep"
                or f == "pop_next_dep"
                or f == "push_prev_dep"
                or f == "push_next_dep"
                or f == "reset_flag"
            ):
                self.widths[f] = spec["width"]["flag"]
            elif f == "uop_bgn":
                self.widths[f] = spec["width"]["uop_begin"]
            elif f == "uop_end":
                self.widths[f] = spec["width"]["uop_end"]
            elif f == "iter_out" or f == "iter_in":
                self.widths[f] = spec["width"]["iter"]
            elif f == "dst_factor_out" or f == "dst_factor_in":
                self.widths[f] = spec["width"]["dst_factor"]
            elif f == "src_factor_out" or f == "src_factor_in":
                self.widths[f] = spec["width"]["src_factor"]
            elif f == "wgt_factor_out" or f == "wgt_factor_in":
                self.widths[f] = spec["width"]["wgt_factor"]
            elif f == "empty":
                self.widths[f] = spec["width"]["gemm_empty"]
        assert len(self.values) == len(self.widths) and len(self.values) == len(
            self.fields
        )


class AluInstr(Instruction):
    def __init__(self, spec):
        super().__init__()
        self.fields = [
            "opcode",
            "pop_prev_dep",
            "pop_next_dep",
            "push_prev_dep",
            "push_next_dep",
            "reset_reg",
            "uop_bgn",
            "uop_end",
            "iter_out",
            "iter_in",
            "empty",
            "dst_factor_out",
            "dst_factor_in",
            "src_factor_out",
            "src_factor_in",
            "alu_opcode",
            "use_imm",
            "imm",
        ]
        for f in self.fields:
            self.values[f] = 0
            if f == "opcode":
                self.widths[f] = spec["width"]["opcode"]
            elif (
                f == "pop_prev_dep"
                or f == "pop_next_dep"
                or f == "push_prev_dep"
                or f == "push_next_dep"
                or f == "reset_reg"
                or f == "use_imm"
            ):
                self.widths[f] = spec["width"]["flag"]
            elif f == "uop_bgn":
                self.widths[f] = spec["width"]["uop_begin"]
            elif f == "uop_end":
                self.widths[f] = spec["width"]["uop_end"]
            elif f == "iter_out" or f == "iter_in":
                self.widths[f] = spec["width"]["iter"]
            elif f == "dst_factor_out" or f == "dst_factor_in":
                self.widths[f] = spec["width"]["dst_factor"]
            elif f == "src_factor_out" or f == "src_factor_in":
                self.widths[f] = spec["width"]["src_factor"]
            elif f == "alu_opcode":
                self.widths[f] = spec["width"]["alu_opcode"]
            elif f == "imm":
                self.widths[f] = spec["width"]["alu_imm"]
            elif f == "empty":
                self.widths[f] = spec["width"]["alu_empty"]
        assert len(self.values) == len(self.widths) and len(self.values) == len(
            self.fields
        )


class Finish(GemmInstr):
    def __init__(self, spec):
        super().__init__(spec)
        self.set_field("opcode", spec["value"]["opcode"]["finish"])


class Load(MemInstr):
    def __init__(self, spec):
        super().__init__(spec)
        self.set_field("opcode", spec["value"]["opcode"]["load"])
        self.set_field("mem_type", spec["value"]["mem_id"]["acc"])


class Store(MemInstr):
    def __init__(self, spec):
        super().__init__(spec)
        self.set_field("opcode", spec["value"]["opcode"]["store"])
        self.set_field("mem_type", spec["value"]["mem_id"]["out"])


class Addi(AluInstr):
    def __init__(self, spec):
        super().__init__(spec)
        self.set_field("opcode", spec["value"]["opcode"]["alu"])
        self.set_field("alu_opcode", spec["value"]["alu_opcode"]["add"])
        self.set_field("use_imm", 1)
