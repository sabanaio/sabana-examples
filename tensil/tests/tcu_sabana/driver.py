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
from sabana import Instance, Program
from tcu_pynq.util import (
    div_ceil,
    parent_dir,
    vector_to_fixed_point,
    vector_from_fixed_point,
)

from tcu_pynq.data_type import data_type_numpy
from tcu_pynq.instruction import Layout
from tcu_pynq.instruction import DataMoveFlag
from tcu_pynq.config import Register, Constant
from tcu_pynq.model import model_from_json
from tcu_pynq.data_type import DataType
from tcu_pynq.architecture import Architecture


tensil = Architecture(
    data_type=DataType.FP16BP8,
    array_size=8,
    dram0_depth=1048576,
    dram1_depth=1048576,
    local_depth=8192,
    accumulator_depth=2048,
    simd_registers_depth=1,
    stride0_depth=8,
    stride1_depth=8,
    number_of_threads=1,
    thread_queue_depth=8,
)


def buffer_chunk_write(data=None, buffer=None, inst=None, offset=None, chunk_size=None):
    """
    Executes buffer writes in chunks of 1MBytes, the largest
    supported payload by xfer in Sabana
    """
    if not isinstance(data, np.ndarray):
        raise RuntimeError("Buffer chunk write error: data must be a numpy array")
    if (not isinstance(buffer, str)) or (len(buffer) == 0):
        raise RuntimeError("Buffer chunk write error: buffer must be non empty string")
    if not isinstance(offset, int) or offset < 0:
        raise RuntimeError(
            "Buffer chunk write error: offset needds to be a positive integer"
        )
    if not isinstance(inst, Instance):
        raise RuntimeError(
            "Buffer chunk write error: inst must be of type sabana.Instance"
        )
    if not inst.is_up:
        raise RuntimeError(
            "Buffer chunk write error: the instance must be up before invoking buffer-chunk-write"
        )

    max_chunk_size = 1 << 20
    if chunk_size is None:
        chunk_size = max_chunk_size
    else:
        if chunk_size > max_chunk_size:
            raise RuntimeError(
                f"Chunk size must be a positive integer smaller than: {max_chunk_size}"
            )
    total_length = data.nbytes
    bytes_left = total_length
    for i in range(div_ceil(total_length, chunk_size)):
        prog = Program()
        iter_offset = i * chunk_size
        chunk = chunk_size if bytes_left > chunk_size else bytes_left
        top = iter_offset + chunk
        prog.buffer_write(
            data=data[iter_offset:top], name=buffer, offset=offset + iter_offset
        )
        try:
            inst.execute(program=prog)
        except Exception as e:
            print(f"Failed buffer chunk write on iteration {i}")
            print(str(e))
            inst.down()
            raise RuntimeError() from e
        else:
            bytes_left = bytes_left - chunk


class Mem:
    """
    Mem provides a read and write interface to buffer a memory.
    """

    def __init__(
        self,
        inst,
        data_type,
        name,
        debug=False,
    ):
        """
        Instantiates the contiguous array of memory that will be accessible to the fabric,
        configures the AXI memory port and computes offsets.

        Parameters
        ----------
        inst : Instance
            A Sabana instance object
        data_type : DataType
            The data type of the scalars to be stored e.g. DataType.FP16BP8
        name : String
            The name of the buffer to use in the deployed instance
        debug: bool
            Whether to print debug messages
        """
        if isinstance(inst, Instance):
            self.inst = inst
        else:
            raise RuntimeError("inst is not a sabana Instance object")

        if isinstance(name, str) and len(name) > 0:
            self.name = name
        else:
            raise RuntimeError("name must be a non-empty string")

        self.data_type = data_type
        self.debug = debug
        self.data_type_numpy = data_type_numpy(self.data_type)
        self.data_type_numpy_size_bytes = self.data_type_numpy(0).nbytes

    def write(self, offset, data):
        """
        data must be an np.array of type self.data_type_numpy
        offset is an index of this np.array
        """
        if data.dtype != self.data_type_numpy:
            raise MemException(
                "data type must be {}, got {}".format(self.data_type_numpy, data.dtype)
            )
        if not isinstance(offset, int) or offset < 0:
            raise RuntimeError("offset must be a positive integer")
        else:
            offset_bytes = offset * self.data_type_numpy_size_bytes
        if self.debug:
            print(f"{self.name} Mem: doing write of {data.nbytes} bytes")
        buffer_chunk_write(
            data=data, buffer=self.name, offset=offset_bytes, inst=self.inst
        )

    def write_bytes(self, offset_bytes, data):
        """
        writes bytes to this mem object
        data must be a bytes object
        offset_bytes must be a positive int
        """
        if offset_bytes % self.data_type_numpy_size_bytes != 0:
            raise MemException(
                "offset {} is not aligned with Mem's data type {} of size {} bytes".format(
                    offset_bytes,
                    self.data_type,
                    self.data_type_numpy_size_bytes,
                )
            )
        if not isinstance(data, bytes):
            raise MemException("data needs to be bytes fro write_bytes")
        data = np.frombuffer(data, dtype=np.uint8)
        if self.debug:
            print(f"{self.name} Mem: doing write-bytes of {data.nbytes} bytes")
        buffer_chunk_write(
            data=data, buffer=self.name, offset=offset_bytes, inst=self.inst
        )

    def read(self, offset, size):
        """returns an np.array of type self.data_type_numpy"""
        if not isinstance(offset, int) or offset < 0:
            raise RuntimeError("offset must be a positive integer")
        else:
            offset_bytes = offset * self.data_type_numpy_size_bytes
        prog = Program()
        prog.buffer_read(
            name=self.name,
            offset=offset_bytes,
            dtype=self.data_type_numpy,
            shape=(size,),
        )
        return self.inst.execute(prog)[0]

    def compare(self, offset, data):
        """returns boolean"""
        if data.dtype != self.data_type_numpy:
            raise MemException(
                "data type must be {}, got {}".format(self.data_type_numpy, data.dtype)
            )
        if not isinstance(offset, int) or offset < 0:
            raise RuntimeError("offset must be a positive integer")
        else:
            offset_bytes = offset * self.data_type_numpy_size_bytes

        res = self.read(offset, data.size)
        data = data.reshape((-1,))
        return np.array_equal(res, data)


class MemException(Exception):
    pass


class Driver:
    """
    Driver provides methods for interacting with a Sabana image containing a TPU.
    Communication occurs via requests using the Sabana SDK.
    A DMA resource is used for instructions, 2 memory buffers exist for data.

    Parameters
    ----------
    image : String
        a triple string pointing to a Sabana image to use for deployment
    debug : bool
        whether to print debug messages
    """

    def __init__(
        self,
        image,
        debug=False,
    ):
        """
        Sets up drivers for the AXI DMA core using the Xlnk memory mapper helper
        and then uses it to instantiate the DRAMs.

        Parameters
        ----------
        arch : Architecture
            An instance of Architecture containing architecture parameters
        debug : bool (optional)
            Enable debug messages
        """
        if debug:
            print("initializing instance")

        if not isinstance(image, str) or len(image) == 0:
            raise RuntimeError("image must be a non-empty string")
        self.inst = Instance(image=image, verbose=debug)
        self.is_up = False
        self.arch = tensil
        self.dma_name = "inst"
        self.dram0_name = "d0"
        self.dram1_name = "d1"
        self.array_size_in_scalar = self.arch.array_size
        self.scalar_bytes = data_type_numpy(self.arch.data_type)(0).nbytes
        self.array_size_in_bytes = self.array_size_in_scalar * self.scalar_bytes
        self.debug = debug
        self.model = None

        self.layout = Layout(self.arch)
        if self.debug:
            print("Instruction size in bits, operand sizes in bits:")
            print(self.layout)

        tcu_block_size = Constant.TCU_BLOCK_SIZE.value
        depth = (self.arch.dram0_depth + self.arch.dram1_depth) * self.arch.array_size
        # 16 bytes are 128 bits
        total_bytes = self.arch.dram0_depth * self.arch.array_size * 16

        if self.debug:
            print(f"TCU block size is: {tcu_block_size}")
            print(f"Array-size is {self.array_size_in_scalar} scalars (uint16)")
            print(f"Total depth including both drams is {depth} scalars (uint16)")
            print(f"Total bytes in dram's are {total_bytes}")

        # allocate resources in remote instance
        prog = Program()
        prog.buffer_alloc(name=self.dram0_name, size=total_bytes)
        prog.buffer_alloc(name=self.dram1_name, size=total_bytes)
        prog.dma_send_alloc(name=self.dma_name)

        try:
            # deploy instance
            self.inst.up()
            print("Instance deployed...")
            res = self.inst.execute(prog)
        except Exception as e:
            print(str(e))
            print("resource allocation failed")
            print(str(e))
            self.inst.down()
            raise RuntimeError("Aborted driver configuration")
        else:
            # response from buffer_alloc instructions contains a numpy array
            # of a single element with the phy-address of the buffer allocated
            self.dram0_phy_addr = int(res[0])
            self.dram1_phy_addr = int(res[1])

        self.dram0_addr_offset = div_ceil(self.dram0_phy_addr, tcu_block_size)
        self.dram1_addr_offset = div_ceil(self.dram1_phy_addr, tcu_block_size)
        if self.debug:
            print(
                "DRAM0: offset = {}, phy: {}".format(
                    self.dram0_addr_offset, self.dram0_phy_addr
                )
            )
            print(
                "DRAM1: offset = {}, phy: {}".format(
                    self.dram1_addr_offset, self.dram1_phy_addr
                )
            )

        # instantiate DRAMs
        self.dram0 = Mem(
            self.inst,
            self.arch.data_type,
            self.dram0_name,
            debug=self.debug,
        )
        self.dram1 = Mem(
            self.inst,
            self.arch.data_type,
            self.dram1_name,
            debug=self.debug,
        )

        if self.debug:
            print(f"dram0 instruction offset: {self.dram0_addr_offset}")
            print(f"dram1 instruction offset: {self.dram1_addr_offset}")
        # set address offsets
        self.configure(
            (Register.DRAM0_ADDRESS_OFFSET, self.dram0_addr_offset),
            (Register.DRAM1_ADDRESS_OFFSET, self.dram1_addr_offset),
            (Register.TIMEOUT, 100),
        )
        if self.debug:
            print("tensil driver initialization done")

    def __del__(self):
        self.close()

    def close(self):
        if isinstance(self.inst, Instance) and self.inst.is_up:
            self.inst.down()
            self.inst = None
            self.is_up = False

    def dma_write(self, data):
        """
        Writes a numpy array to the instructions DMA
        """
        # TODO: Improve handling dealloc if anything fails
        if self.debug:
            print("-- dma-write")
        sprog = Program()
        buffer_name = "b_inst"
        sprog.buffer_alloc(name=buffer_name, size=data.nbytes)

        try:
            self.inst.execute(program=sprog)
        except Exception as e:
            msg = "Error during buffer allocation for dma-write"
            print(msg)
            print(str(e))
            raise RuntimeError(msg)

        buffer_chunk_write(data=data, buffer=buffer_name, offset=0, inst=self.inst)

        sprog = Program()
        sprog.dma_send_write(name=self.dma_name, src="b_inst")
        sprog.dma_send_wait(name=self.dma_name, timeout=3)
        sprog.buffer_dealloc(name="b_inst")
        try:
            self.inst.execute(program=sprog)
        except Exception as e:
            msg = "Error during dma write for dma-write"
            print(msg)
            print(str(e))
            raise RuntimeError(msg)

    def write_instructions(self, instructions):
        """instructions should be a sequence of ints"""
        if self.debug:
            print("-- write instructions")
        prog = bytes()
        for i in instructions:
            prog = prog + self.layout.to_bytes(i)

        if self.debug:
            print("Instruction Size Bytes: ", self.layout.instruction_size_bytes)
        prog_numpy = np.frombuffer(prog, dtype=np.uint8)
        self.dma_write(prog_numpy)

    def configure(self, *pairs):
        if self.debug:
            print("-- configure")
            print(pairs)
        program = [
            self.layout.configure(register.value, value) for register, value in pairs
        ] + self.prepare_flush_probe()
        self.write_instructions(program)
        self.wait_for_flush()

    def run_load_consts(self, offset, size):
        if self.debug:
            print("loading constants to local")
        program = [
            self.layout.data_move(
                DataMoveFlag.dram1_to_memory, offset, offset, size - 1
            )
        ] + self.prepare_flush_probe()
        self.write_instructions(program)
        self.wait_for_flush()

    def load_model(self, model_filename):
        self.model_filename = model_filename
        with open(self.model_filename, "r") as f:
            self.model = model_from_json(f.read())
        # check that model arch matches driver arch
        if not (self.model.arch == self.arch):
            raise Exception(
                "model requires architecture {} but current architecture is {}".format(
                    self.model.arch, self.arch
                )
            )
        # load consts and program
        d = parent_dir(self.model_filename) + "/"
        for const in self.model.consts:
            with open(d + const.file_name, "rb") as f:
                self.dram1.write_bytes(
                    const.base
                    * self.arch.array_size
                    * self.dram1.data_type_numpy_size_bytes,
                    f.read(),
                )
            if self.model.load_consts_to_local:
                self.run_load_consts(const.base, const.size)
        with open(d + self.model.prog.file_name, "rb") as f:
            self.program = f.read()

    def scalar_address(self, array_address):
        return array_address * self.arch.array_size

    def prepare_flush_probe(self):
        if self.debug:
            print("-- prepare flush probe")
        # initialize flush probe
        self.probe_source_array_addr = self.arch.dram0_depth - 1
        self.probe_target_array_addr = self.arch.dram0_depth - 2
        self.local_address = self.arch.local_depth - 1
        self.probe_source = np.full(
            self.arch.array_size,
            np.iinfo(data_type_numpy(self.arch.data_type)).max,
            dtype=data_type_numpy(self.arch.data_type),
        )
        self.probe_target = np.full(
            self.arch.array_size, 0, dtype=data_type_numpy(self.arch.data_type)
        )

        # write flush probe
        self.dram0.write(
            self.scalar_address(self.probe_source_array_addr), self.probe_source
        )
        self.dram0.write(
            self.scalar_address(self.probe_target_array_addr), self.probe_target
        )

        # flush probe instructions
        return [
            self.layout.data_move(
                DataMoveFlag.dram0_to_memory,
                self.local_address,
                self.probe_source_array_addr,
                0,
            ),
            self.layout.data_move(
                DataMoveFlag.memory_to_dram0,
                self.local_address,
                self.probe_target_array_addr,
                0,
            ),
        ]

    def wait_for_flush(self):
        while not self.dram0.compare(
            self.scalar_address(self.probe_source_array_addr), self.probe_source
        ):
            if self.debug:
                print("-- wait for flush")
            pass

    def to_fixed(self, arr):
        return vector_to_fixed_point(
            self.arch.data_type.value.width, self.arch.data_type.value.binary_point
        )(arr)

    def from_fixed(self, arr):
        return vector_from_fixed_point(
            self.arch.data_type.value.width, self.arch.data_type.value.binary_point
        )(arr)

    def run(self, inputs):
        """
        Runs the model and returns outputs as a dict.

        inputs must be a dictionary containing a key for every input
        specified in the tmodel file. Each value in the dict must be
        a numpy array
        """
        import time

        if self.debug:
            print("-- doing run")

        start = time.time()
        prev = start

        def timestamp(event):
            nonlocal prev
            now = time.time()
            print("{}\t{:.3}s\t{:.3}s".format(event, now - prev, now - start))
            prev = now

        if self.model is None:
            raise Exception("model not loaded: please run driver.load_model first")

        # load inputs
        for inp in self.model.inputs:
            data = self.to_fixed(inputs[inp.name]).astype(
                data_type_numpy(self.arch.data_type)
            )
            self.dram0.write(self.scalar_address(inp.base), data)
        timestamp("wrote inputs")

        # append flush probe instructions
        prog = self.program
        for i in self.prepare_flush_probe():
            prog = prog + self.layout.to_bytes(i)

        # write program
        prog_numpy = np.frombuffer(prog, dtype=np.uint8)
        if self.debug:
            print(f"writing flush program, of length {prog_numpy.nbytes} bytes")
        self.dma_write(prog_numpy)

        self.wait_for_flush()
        timestamp("wrote program")

        # return outputs
        outputs = dict()
        for out in self.model.outputs:
            data = self.from_fixed(
                self.dram0.read(
                    self.scalar_address(out.base), self.scalar_address(out.size)
                )
            )
            if out.name in outputs:
                outputs[out.name] = np.concatenate([outputs[out.name], data])
            else:
                outputs[out.name] = data
        timestamp("read outputs")
        return outputs
