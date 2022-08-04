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
  input  logic [32-1:0] b_in,
  output logic [32-1:0] y_out,
  output logic y_valid
);

  logic [32-1:0] ar;
  logic [32-1:0] br;
  logic [32-1:0] yr;
  logic d0;

  always_ff @ (posedge clock)
    if (reset)
      begin
        yr <= 0;
        ar <= 0;
        br <= 0;
        d0 <= 0;
      end
    else
      begin
        ar <= a_in;
        br <= b_in;
        yr <= ar + br;
        d0 <= start;
      end

  assign y_out = yr;
  assign y_valid = d0;
  assign finish = d0;

endmodule