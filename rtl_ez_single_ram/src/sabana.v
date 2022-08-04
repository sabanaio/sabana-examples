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
  input  logic [32-1:0] y_in,
  output logic [32-1:0] y_out,
  output logic [6-1:0] y_addr,
  output logic y_we
);

    logic [6-1:0] addr;

    typedef enum logic [1:0] {
        IDLE,
        READ,
        WRITE,
        DONE
    } state_t;

    state_t state, next;

    always_ff @(posedge clock) begin
        if (reset) begin
            addr <= 0;
        end else if (state == WRITE) begin
            addr <= addr + 1'b1;
        end
    end

    always_ff @(posedge clock) begin
        if (reset) begin
            state <= IDLE;
        end else begin
            state <= next;
        end
    end

    always_comb begin
        case(state)
            IDLE: begin
                if (start) begin
                    next = READ;
                end else begin
                    next = IDLE;
                end
            end
            READ: begin
                next = WRITE;
            end
            WRITE: begin
                if (&addr) begin
                    next = DONE;
                end else begin
                    next = READ;
                end
            end
            DONE: begin
                next = DONE;
            end
        endcase
    end

    assign y_we = (state == WRITE);
    assign y_addr = addr;
    assign y_out = y_in + a_in;
    assign finish = (state == DONE);

endmodule