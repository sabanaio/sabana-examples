# Deploying PyRTL hardware to Sabana
The following example shows how to deploy [PyRTL](https://pyrtl.readthedocs.io/en/latest/) generated
hardware to Sabana

## Deploy steps

* Install Sabana CLI and SDK, instructions [here](https://docs.sabana.io/get-started/installation)
* Install PyRTL, in case something fails docs are [here](https://pyrtl.readthedocs.io/en/latest/)
```bash
python3 -m pip install pyrtl
```
* Generate PyRTL hardware
```bash
python3 tests/pyrtl_muladd.py
```
* Build the image
```bash
sabana push
```
* Run test and compare with PyRTL simulation and FPGA
```bash
python3 tests/test_pyrtl_muladd.py
```
