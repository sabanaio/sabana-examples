// Generated automatically via PyRTL
// As one initial test of synthesis, map to FPGA with:
//   yosys -p "synth_xilinx -top toplevel" thisfile.v

module toplevel(clk, rst, a, b, c, y);
    input clk;
    input rst;
    input[31:0] a;
    input[31:0] b;
    input[31:0] c;
    output[31:0] y;

    wire const_0_0;
    wire[63:0] tmp0;
    wire[31:0] tmp1;
    wire[63:0] tmp2;
    wire[64:0] tmp3;
    wire[31:0] tmp4;

    // Combinational
    assign const_0_0 = 0;
    assign tmp0 = a * b;
    assign tmp1 = {const_0_0, const_0_0, const_0_0, const_0_0, const_0_0, const_0_0, const_0_0, const_0_0, const_0_0, const_0_0, const_0_0, const_0_0, const_0_0, const_0_0, const_0_0, const_0_0, const_0_0, const_0_0, const_0_0, const_0_0, const_0_0, const_0_0, const_0_0, const_0_0, const_0_0, const_0_0, const_0_0, const_0_0, const_0_0, const_0_0, const_0_0, const_0_0};
    assign tmp2 = {tmp1, c};
    assign tmp3 = tmp0 + tmp2;
    assign tmp4 = {tmp3[31], tmp3[30], tmp3[29], tmp3[28], tmp3[27], tmp3[26], tmp3[25], tmp3[24], tmp3[23], tmp3[22], tmp3[21], tmp3[20], tmp3[19], tmp3[18], tmp3[17], tmp3[16], tmp3[15], tmp3[14], tmp3[13], tmp3[12], tmp3[11], tmp3[10], tmp3[9], tmp3[8], tmp3[7], tmp3[6], tmp3[5], tmp3[4], tmp3[3], tmp3[2], tmp3[1], tmp3[0]};
    assign y = tmp4;

endmodule

