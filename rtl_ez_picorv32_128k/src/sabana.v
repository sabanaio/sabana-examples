// Copyright 2022 Sabana Technologies, Inc
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

module sabana (
  input  logic clock,
  input  logic reset,
  input  logic start,
  output logic finish,
  input  logic [32-1:0] a_in,
  output logic [32-1:0] a_out,
  output logic [15-1:0] a_addr,
  output logic a_we
);

  logic picorv32_nreset;
    logic trap;
    logic        mem_valid;
    logic [31:0] mem_addr;
    logic [31:0] mem_wdata;
    logic [ 3:0] mem_wstrb;
    logic        mem_ready;
    logic [31:0] mem_rdata;
    logic [31:0] timeout;

  picorv32 #(
        .ENABLE_MUL          (1),
        .ENABLE_FAST_MUL     (1)
	) picorv32_core (
        .clk      (clock),
        .resetn   (picorv32_nreset),
        .trap     (trap),

        .mem_valid(mem_valid),
        .mem_addr (mem_addr ),
        .mem_wdata(mem_wdata),
        .mem_wstrb(mem_wstrb),
        .mem_instr(mem_instr),
        .mem_ready(mem_ready),
        .mem_rdata(mem_rdata),

        .pcpi_valid(),
        .pcpi_insn (),
        .pcpi_rs1  (),
        .pcpi_rs2  (),
        .pcpi_wr   (1'b0),
        .pcpi_rd   (32'b0),
        .pcpi_wait (1'b0),
        .pcpi_ready(1'b0),
        .irq(32'd0),
        .eoi(),

        .trace_valid(),
        .trace_data ()

    );

typedef enum logic [1:0] {
        CPU_IDLE,
        CPU_RUN,
        CPU_DONE
    } cpu_state_t;
    cpu_state_t cpu_state, cpu_next;

    // Very simple watchdog counter
    always_ff @(posedge clock) begin
        if (reset) begin
            cpu_state <= CPU_IDLE;
            timeout <= 0;
        end else begin
            cpu_state <= cpu_next;
            timeout <= timeout + 1'b1;
        end
    end

    // Controls for the CPU
    always_comb begin
        case(cpu_state)
            CPU_IDLE: begin
                if (start) begin
                    cpu_next = CPU_RUN;
                end else begin
                    cpu_next = CPU_IDLE;
                end
            end
            CPU_RUN: begin
                if (trap) begin
                    cpu_next = CPU_DONE;
                end else begin
                    cpu_next = CPU_RUN;
                end
            end
            CPU_DONE: begin
                cpu_next = CPU_IDLE;
            end
            default: begin
                cpu_next = CPU_IDLE;
            end
        endcase
    end

    typedef enum logic [1:0] {
        MEM_IDLE,
        MEM_READ,
        MEM_WRITE
    } mem_state_t;
    mem_state_t mem_state, mem_next;

    // Memory interface adaptater
    always_ff @(posedge clock) begin
        if (reset) begin
            mem_state <= MEM_IDLE;
        end else begin
            mem_state <= mem_next;
        end
    end

    always_comb begin
        case(mem_state)
            MEM_IDLE: begin
                if (mem_valid) begin
                    if (mem_wstrb == 4'b1111) begin
                        mem_next = MEM_WRITE;
                    end else begin
                        mem_next = MEM_READ;
                    end
                end else begin
                    mem_next = MEM_IDLE;
                end
            end
            MEM_READ: begin
                if (|mem_wstrb) begin
                    mem_next = MEM_WRITE;
                end else begin
                    mem_next = MEM_IDLE;
                end
            end
            MEM_WRITE: begin
                mem_next = MEM_IDLE;
            end
            default: begin
                mem_next = MEM_IDLE;
            end
        endcase
    end

    assign a_we = |mem_wstrb & mem_state == MEM_WRITE;
    assign mem_ready = (mem_state == MEM_WRITE) | (mem_wstrb == 4'd0 & mem_state == MEM_READ);
    assign a_addr = mem_addr[16:2];
    assign mem_rdata = a_in;

    genvar i;
    generate
        for (i = 0; i < 4; i = i + 1) begin
            assign a_out[(i*8+7):(i*8)] = mem_wstrb[i] ? mem_wdata[(i*8+7):(i*8)] : a_in[(i*8+7):(i*8)];
        end
    endgenerate

    assign picorv32_nreset = cpu_state == CPU_RUN;
    assign finish = cpu_state == CPU_DONE;
endmodule
