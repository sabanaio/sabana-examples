# Tensil example

To run this example submodules need to be initialized:

```bash
git clone --recurse-submodules git@github.com:sabanaio/sabana-examples.git
```

Using version `v1.0.15` of the tensil respository.

# Tests

## get_cifar

to get the cifar dataset run

```bash
cd tests
bash get_cifar.sh
```

## driver_tests

to run the diagnostic tests using Sabana:

```bash
cd tests
bash driver_tests.sh
```

## resnet

to run the resnet example using Sabana:

```bash
bash resnet.sh
```
