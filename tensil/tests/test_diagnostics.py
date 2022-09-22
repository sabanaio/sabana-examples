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

from tcu_pynq.data_type import data_type_numpy, one
from tcu_pynq.instruction import DataMoveFlag
from tcu_pynq.util import pad_to
from tcu_sabana.driver import Driver
from collections import namedtuple
import numpy as np
import pytest

TCase = namedtuple("TestCase", ["input", "expected"])


@pytest.fixture(scope="module")
def driver():
    drv = Driver(image="luis/tensil:0.1.0", debug=False)
    yield drv
    drv.close()


def test_local_memory(driver):
    size = driver.arch.local_depth * driver.arch.array_size
    data = np.arange(size, dtype=data_type_numpy(driver.arch.data_type))
    driver.dram0.write(0, data)

    # move data on and off
    program = [
        driver.layout.data_move(
            DataMoveFlag.dram0_to_memory, 0, 0, driver.arch.local_depth - 1
        ),
        driver.layout.data_move(
            DataMoveFlag.memory_to_dram0,
            0,
            driver.arch.local_depth,
            driver.arch.local_depth - 1,
        ),
    ]

    driver.write_instructions(program)
    result = driver.dram0.read(driver.arch.local_depth * driver.arch.array_size, size)
    np.testing.assert_array_equal(result, data)


def test_matmul(driver):
    size = driver.arch.array_size**2
    data = np.arange(size, dtype=data_type_numpy(driver.arch.data_type))
    weights = np.identity(
        driver.arch.array_size,
        dtype=data_type_numpy(driver.arch.data_type),
    ) * one(driver.arch.data_type)
    input_address = 0
    output_address = driver.arch.array_size
    weights_address = driver.arch.local_depth - 1 - driver.arch.array_size
    driver.dram1.write(0, weights)
    driver.dram0.write(0, data)
    program = [
        driver.layout.data_move(
            DataMoveFlag.dram1_to_memory,
            weights_address,
            0,
            driver.arch.array_size - 1,
        ),
        driver.layout.data_move(
            DataMoveFlag.dram0_to_memory,
            input_address,
            0,
            driver.arch.array_size - 1,
        ),
        driver.layout.load_weight(False, weights_address, driver.arch.array_size - 1),
        driver.layout.load_weight(True, 0, 0),
        driver.layout.matmul(False, 0, 0, driver.arch.array_size - 1),
        driver.layout.data_move(
            DataMoveFlag.accumulator_to_memory,
            output_address,
            0,
            driver.arch.array_size - 1,
        ),
        driver.layout.data_move(
            DataMoveFlag.memory_to_dram0,
            output_address,
            output_address,
            driver.arch.array_size - 1,
        ),
    ]
    program += [driver.layout.no_op() for i in range(1000)]
    driver.write_instructions(program)
    result = driver.dram0.read(output_address * driver.arch.array_size, size)
    np.testing.assert_array_equal(result, data)


def test_accumulator_memory(driver):
    size = driver.arch.accumulator_depth * driver.arch.array_size
    data = np.arange(size, dtype=data_type_numpy(driver.arch.data_type))
    driver.dram0.write(0, data)
    program = [
        driver.layout.data_move(
            DataMoveFlag.dram0_to_memory,
            0,
            0,
            driver.arch.accumulator_depth - 1,
        ),
        driver.layout.data_move(
            DataMoveFlag.memory_to_accumulator,
            0,
            0,
            driver.arch.accumulator_depth - 1,
        ),
        driver.layout.data_move(
            DataMoveFlag.accumulator_to_memory,
            driver.arch.accumulator_depth,
            0,
            driver.arch.accumulator_depth - 1,
        ),
        driver.layout.data_move(
            DataMoveFlag.memory_to_dram0,
            driver.arch.accumulator_depth,
            driver.arch.accumulator_depth,
            driver.arch.accumulator_depth - 1,
        ),
    ]
    driver.write_instructions(program)
    result = driver.dram0.read(size, size)
    np.testing.assert_array_equal(result, data)


def test_dram1(driver):
    # write some stuff to dram0
    size = driver.arch.local_depth * driver.arch.array_size
    data = np.arange(size, dtype=data_type_numpy(driver.arch.data_type))
    driver.dram1.write(0, data)
    # move data on and off
    program = [
        driver.layout.data_move(
            DataMoveFlag.dram1_to_memory, 0, 0, driver.arch.local_depth - 1
        ),
        driver.layout.data_move(
            DataMoveFlag.memory_to_dram0,
            0,
            driver.arch.local_depth,
            driver.arch.local_depth - 1,
        ),
    ]
    driver.write_instructions(program)
    # read it from dram0
    result = driver.dram0.read(driver.arch.local_depth * driver.arch.array_size, size)
    np.testing.assert_array_equal(result, data)


def test_xor(driver):
    test_case = [
        TCase(input=(0, 0), expected=(0,)),
        TCase(input=(0, 1), expected=(1,)),
        TCase(input=(1, 0), expected=(1,)),
        TCase(input=(1, 1), expected=(0,)),
    ]
    driver.load_model("./xor4_pb_pynqz1.tmodel")
    for case in test_case:
        dtype = data_type_numpy(driver.arch.data_type)
        input_ = pad_to(np.array(case.input, dtype=dtype), driver.arch.array_size)
        output = driver.run({"x": input_})["Identity"]
        expected = pad_to(np.array(case.expected, dtype=dtype), driver.arch.array_size)
        np.testing.assert_allclose(expected, output, atol=1e-02)
