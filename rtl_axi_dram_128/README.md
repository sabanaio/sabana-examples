# AXI4 128-bit shell

This quick note gives guidance on how to get started with the AXI4 128-bit shell to package your hardware in Sabana.

## Requirements

You will need three elements to complete this guide:

- The Sabana CLI tool: [installation guide here](https://docs.sabana.io/get-started/installation#cli-v0.1.5)
- The Sabana Python SDK: [pip command for install here](https://docs.sabana.io/get-started/installation#sdk-v0.1.22)
- A Sabana account: [request to join the waitlist here](https://forms.gle/uePrgDD5x1mkCYkq6)

## Creating a project with the AXI4 128-bit shell

In this section we outline the steps to create the skeleton project.

```
Alternatively you can skip these steps and use the empty skeleton on this folder for convenience.
```

To get started use the Sabana CLI to create a new project:

```bash
sabana new my-axi128-project
```

Select the following options to the CLI prompts:

```
✔ Select a language · Verilog
✔ Select shell type · AXI4
✔ Select a starting point · AXI4-Lite and Axi4 (128 bit) shell
```

After this an empty skeleton will be created, for which the `sabana.v` file is the entry point to integrate your hardware module. Please note that the empty skeleton on it's own does not yield a valid image.

## Hardware interfaces

The `sabana.v` file will have the following interfaces:

```verilog
module sabana (
  input  logic            clock,
  input  logic            reset,

  // AXI4-Lite interface
  input  logic            s_axi_c0_awvalid,
  output logic            s_axi_c0_awready,
  // ...
  output logic            s_axi_c0_bvalid,
  input  logic            s_axi_c0_bready,
  output logic [2-1:0]    s_axi_c0_bresp,

  // AXI4 interface
  input  logic            m_axi_m0_awready,
  output logic            m_axi_m0_awvalid,
  // ...
  input  logic [128-1:0]   m_axi_m0_rdata,
  input  logic [2-1:0]    m_axi_m0_rresp,
  input  logic            m_axi_m0_rlast
);
```

We have the following interfaces:

- Control flags: `clock`, `reset`
- AXI4-Lite `c0`: for controlling the hardware
- AXI4-128bits `m0`: for direct DRAM access

## Building your image

These are the steps required:

1. Copy the source files into the `src` directory. Supported extensions are: `.v`, `.vh`, `.sv`.
2. Instantiate your top module in `sabana.v`.
3. Push your code with:

```bash
sabana push
```

## Deploying your image

You can deploy and interact with your image in Sabana using our [Python SDK](https://docs.sabana.io/reference/python-sdk).

These are the steps involved:

1. Create a [driver program](https://github.com/sabanaio/sabana-examples/blob/main/c_axi_systolic_gemm_16x16_int/tests/test_c_axi_systolic_gemm_16x16_int.py#L20-L42)
2. Create a [test](https://github.com/sabanaio/sabana-examples/blob/main/c_axi_systolic_gemm_16x16_int/tests/test_c_axi_systolic_gemm_16x16_int.py#L71-L86)
3. Run the test

```bash
python3 test_rtl_axi_dram_128.py
```

## Help

If you need any support reach us in our [Discord](https://discord.gg/TwzbFDBFcm) server.
