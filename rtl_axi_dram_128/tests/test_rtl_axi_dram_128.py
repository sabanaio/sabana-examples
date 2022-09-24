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


class Driver:
    def __init__(self, image=None):
        if image:
            self.inst = Instance(image=image, verbose=True)
        else:
            file = Path(__file__).resolve().parent.parent.joinpath("sabana.json")
            self.inst = Instance(image_file=file, verbose=True)

        self.inst.up()

    def run(self, program):
        return self.inst.execute(program)

    def __del__(self):
        self.inst.down()


def test_main():
    pass


if __name__ == "__main__":
    test_main()