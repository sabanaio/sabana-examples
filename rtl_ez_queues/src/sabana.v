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
  input  logic a_empty,
  output logic a_pop,
  input  logic [32-1:0] b_in,
  input  logic b_empty,
  output logic b_pop,
  output logic [32-1:0] y_out,
  output logic y_push,
  input  logic y_full
);

  logic state;
  logic is_done;

  always_ff @(posedge clock) begin
    if (reset) begin
       state <= 1'b0;
    end
    else if (start) begin
       state <= 1'b1;
    end
    else if (is_done) begin
       state <= 1'b0;
    end
  end

  assign a_pop = ~y_full & state;
  assign b_pop = ~y_full & state;
  assign y_push = ~a_empty & ~b_empty & state;

  assign y_out = a_in + b_in;
  assign is_done = a_empty & b_empty & state;
  assign finish = is_done;

endmodule