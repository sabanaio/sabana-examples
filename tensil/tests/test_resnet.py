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

from tcu_sabana.driver import Driver
import numpy as np
import pickle
import time


def driver():
    drv = Driver(image="luis/tensil:0.1.0", debug=False)
    yield drv
    drv.close()


def get_img(driver, data, n):
    data_norm = data.astype("float32") / 255
    data_mean = np.mean(data_norm, axis=0)
    data_norm -= data_mean
    img = np.transpose(data_norm[n].reshape((3, 32, 32)), axes=[1, 2, 0])
    img = np.pad(
        img,
        [(0, 0), (0, 0), (0, driver.arch.array_size - 3)],
        "constant",
        constant_values=0,
    )
    return img.reshape((-1, driver.arch.array_size))


def get_label(labels, label_names, n):
    label_idx = labels[n]
    name = label_names[label_idx]
    return (label_idx, name)


def unpickle(file):
    with open(file, "rb") as fo:
        d = pickle.load(fo, encoding="bytes")
    return d


def test_resnet(driver):
    """
    requires workflow.sh to have been run,
    for the dataset to be available
    """
    print("Unpickling data...")
    cifar = unpickle("./deploy/test_batch")
    data = cifar[b"data"]
    labels = cifar[b"labels"]

    data = data[10:20]
    labels = labels[10:20]

    cifar_meta = unpickle("./deploy/batches.meta")
    label_names = [b.decode() for b in cifar_meta[b"label_names"]]

    n = 7
    img = get_img(driver, data, n)
    label_idx, label = get_label(labels, label_names, n)

    print("Loading model into TCU...")
    driver.load_model("./resnet20v2_cifar_onnx_tensil.tmodel")
    print("Model load done")
    inputs = {"x:0": img}

    print("Starting run...")
    print()
    start = time.time()
    outputs = driver.run(inputs)
    end = time.time()
    print("Ran inference in {:.4}s".format(end - start))
    print()

    classes = outputs["Identity:0"][:10]
    result_idx = np.argmax(classes)
    result = label_names[result_idx]
    print("Output activations:")
    print(classes)
    print()
    print("Result: {} (idx = {})".format(result, result_idx))
    print("Actual: {} (idx = {})".format(label, label_idx))


if __name__ == "__main__":
    try:
        drv = Driver(image="robot/tensil:0.1.0", debug=False)
        test_resnet(drv)
    finally:
        if isinstance(drv, Driver):
            drv.close()
