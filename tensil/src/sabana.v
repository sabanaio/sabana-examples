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
  input                   clock,
  input                   reset,
  // AXI4-Stream send (d0)
  input  logic [128-1:0]  s_axi_d0_tdata,
  input  logic            s_axi_d0_tvalid,
  output logic            s_axi_d0_tready,
  input  logic            s_axi_d0_tlast,
  // AXI4 (m0)
  input  logic            m_axi_m0_awready,
  output logic            m_axi_m0_awvalid,
  output logic [6-1:0]    m_axi_m0_awid,
  output logic [32-1:0]   m_axi_m0_awaddr,
  output logic [8-1:0]    m_axi_m0_awlen,
  output logic [3-1:0]    m_axi_m0_awsize,
  output logic [2-1:0]    m_axi_m0_awburst,
  output logic [2-1:0]    m_axi_m0_awlock,
  output logic [4-1:0]    m_axi_m0_awcache,
  output logic [3-1:0]    m_axi_m0_awprot,
  output logic [4-1:0]    m_axi_m0_awqos,
  output logic            m_axi_m0_awuser,
  input  logic            m_axi_m0_wready,
  output logic            m_axi_m0_wvalid,
  output logic [6-1:0]    m_axi_m0_wid,
  output logic [128-1:0]  m_axi_m0_wdata,
  output logic [16-1:0]   m_axi_m0_wstrb,
  output logic            m_axi_m0_wlast,
  output logic            m_axi_m0_bready,
  input  logic            m_axi_m0_bvalid,
  input  logic [6-1:0]    m_axi_m0_bid,
  input  logic [2-1:0]    m_axi_m0_bresp,
  input  logic            m_axi_m0_arready,
  output logic            m_axi_m0_arvalid,
  output logic [6-1:0]    m_axi_m0_arid,
  output logic [32-1:0]   m_axi_m0_araddr,
  output logic [8-1:0]    m_axi_m0_arlen,
  output logic [3-1:0]    m_axi_m0_arsize,
  output logic [2-1:0]    m_axi_m0_arburst,
  output logic [2-1:0]    m_axi_m0_arlock,
  output logic [4-1:0]    m_axi_m0_arcache,
  output logic [3-1:0]    m_axi_m0_arprot,
  output logic [4-1:0]    m_axi_m0_arqos,
  output logic            m_axi_m0_aruser,
  output logic            m_axi_m0_rready,
  input  logic            m_axi_m0_rvalid,
  input  logic [6-1:0]    m_axi_m0_rid,
  input  logic [128-1:0]  m_axi_m0_rdata,
  input  logic [2-1:0]    m_axi_m0_rresp,
  input  logic            m_axi_m0_rlast,
  // AXI4 (m1)
  input  logic            m_axi_m1_awready,
  output logic            m_axi_m1_awvalid,
  output logic [6-1:0]    m_axi_m1_awid,
  output logic [32-1:0]   m_axi_m1_awaddr,
  output logic [8-1:0]    m_axi_m1_awlen,
  output logic [3-1:0]    m_axi_m1_awsize,
  output logic [2-1:0]    m_axi_m1_awburst,
  output logic [2-1:0]    m_axi_m1_awlock,
  output logic [4-1:0]    m_axi_m1_awcache,
  output logic [3-1:0]    m_axi_m1_awprot,
  output logic [4-1:0]    m_axi_m1_awqos,
  output logic            m_axi_m1_awuser,
  input  logic            m_axi_m1_wready,
  output logic            m_axi_m1_wvalid,
  output logic [6-1:0]    m_axi_m1_wid,
  output logic [128-1:0]  m_axi_m1_wdata,
  output logic [16-1:0]   m_axi_m1_wstrb,
  output logic            m_axi_m1_wlast,
  output logic            m_axi_m1_bready,
  input  logic            m_axi_m1_bvalid,
  input  logic [6-1:0]    m_axi_m1_bid,
  input  logic [2-1:0]    m_axi_m1_bresp,
  input  logic            m_axi_m1_arready,
  output logic            m_axi_m1_arvalid,
  output logic [6-1:0]    m_axi_m1_arid,
  output logic [32-1:0]   m_axi_m1_araddr,
  output logic [8-1:0]    m_axi_m1_arlen,
  output logic [3-1:0]    m_axi_m1_arsize,
  output logic [2-1:0]    m_axi_m1_arburst,
  output logic [2-1:0]    m_axi_m1_arlock,
  output logic [4-1:0]    m_axi_m1_arcache,
  output logic [3-1:0]    m_axi_m1_arprot,
  output logic [4-1:0]    m_axi_m1_arqos,
  output logic            m_axi_m1_aruser,
  output logic            m_axi_m1_rready,
  input  logic            m_axi_m1_rvalid,
  input  logic [6-1:0]    m_axi_m1_rid,
  input  logic [128-1:0]  m_axi_m1_rdata,
  input  logic [2-1:0]    m_axi_m1_rresp,
  input  logic            m_axi_m1_rlast
);

  top_tensil tensil (
    .clock(clock),
    // active low reset
    .reset(~reset),
    .instruction_tdata(s_axi_d0_tdata),
    .instruction_tvalid(s_axi_d0_tvalid),
    .instruction_tready(s_axi_d0_tready),
    .instruction_tlast(s_axi_d0_tlast),
    .m_axi_dram0_awready(m_axi_m0_awready),
    .m_axi_dram0_awvalid(m_axi_m0_awvalid),
    .m_axi_dram0_awid(m_axi_m0_awid),
    .m_axi_dram0_awaddr(m_axi_m0_awaddr),
    .m_axi_dram0_awlen(m_axi_m0_awlen),
    .m_axi_dram0_awsize(m_axi_m0_awsize),
    .m_axi_dram0_awburst(m_axi_m0_awburst),
    .m_axi_dram0_awlock(m_axi_m0_awlock),
    .m_axi_dram0_awcache(m_axi_m0_awcache),
    .m_axi_dram0_awprot(m_axi_m0_awprot),
    .m_axi_dram0_awqos(m_axi_m0_awqos),
    .m_axi_dram0_wready(m_axi_m0_wready),
    .m_axi_dram0_wvalid(m_axi_m0_wvalid),
    .m_axi_dram0_wid(m_axi_m0_wid),
    .m_axi_dram0_wdata(m_axi_m0_wdata),
    .m_axi_dram0_wstrb(m_axi_m0_wstrb),
    .m_axi_dram0_wlast(m_axi_m0_wlast),
    .m_axi_dram0_bready(m_axi_m0_bready),
    .m_axi_dram0_bvalid(m_axi_m0_bvalid),
    .m_axi_dram0_bid(m_axi_m0_bid),
    .m_axi_dram0_bresp(m_axi_m0_bresp),
    .m_axi_dram0_arready(m_axi_m0_arready),
    .m_axi_dram0_arvalid(m_axi_m0_arvalid),
    .m_axi_dram0_arid(m_axi_m0_arid),
    .m_axi_dram0_araddr(m_axi_m0_araddr),
    .m_axi_dram0_arlen(m_axi_m0_arlen),
    .m_axi_dram0_arsize(m_axi_m0_arsize),
    .m_axi_dram0_arburst(m_axi_m0_arburst),
    .m_axi_dram0_arlock(m_axi_m0_arlock),
    .m_axi_dram0_arcache(m_axi_m0_arcache),
    .m_axi_dram0_arprot(m_axi_m0_arprot),
    .m_axi_dram0_arqos(m_axi_m0_arqos),
    .m_axi_dram0_rready(m_axi_m0_rready),
    .m_axi_dram0_rvalid(m_axi_m0_rvalid),
    .m_axi_dram0_rid(m_axi_m0_rid),
    .m_axi_dram0_rdata(m_axi_m0_rdata),
    .m_axi_dram0_rresp(m_axi_m0_rresp),
    .m_axi_dram0_rlast(m_axi_m0_rlast),
    .m_axi_dram1_awready(m_axi_m1_awready),
    .m_axi_dram1_awvalid(m_axi_m1_awvalid),
    .m_axi_dram1_awid(m_axi_m1_awid),
    .m_axi_dram1_awaddr(m_axi_m1_awaddr),
    .m_axi_dram1_awlen(m_axi_m1_awlen),
    .m_axi_dram1_awsize(m_axi_m1_awsize),
    .m_axi_dram1_awburst(m_axi_m1_awburst),
    .m_axi_dram1_awlock(m_axi_m1_awlock),
    .m_axi_dram1_awcache(m_axi_m1_awcache),
    .m_axi_dram1_awprot(m_axi_m1_awprot),
    .m_axi_dram1_awqos(m_axi_m1_awqos),
    .m_axi_dram1_wready(m_axi_m1_wready),
    .m_axi_dram1_wvalid(m_axi_m1_wvalid),
    .m_axi_dram1_wid(m_axi_m1_wid),
    .m_axi_dram1_wdata(m_axi_m1_wdata),
    .m_axi_dram1_wstrb(m_axi_m1_wstrb),
    .m_axi_dram1_wlast(m_axi_m1_wlast),
    .m_axi_dram1_bready(m_axi_m1_bready),
    .m_axi_dram1_bvalid(m_axi_m1_bvalid),
    .m_axi_dram1_bid(m_axi_m1_bid),
    .m_axi_dram1_bresp(m_axi_m1_bresp),
    .m_axi_dram1_arready(m_axi_m1_arready),
    .m_axi_dram1_arvalid(m_axi_m1_arvalid),
    .m_axi_dram1_arid(m_axi_m1_arid),
    .m_axi_dram1_araddr(m_axi_m1_araddr),
    .m_axi_dram1_arlen(m_axi_m1_arlen),
    .m_axi_dram1_arsize(m_axi_m1_arsize),
    .m_axi_dram1_arburst(m_axi_m1_arburst),
    .m_axi_dram1_arlock(m_axi_m1_arlock),
    .m_axi_dram1_arcache(m_axi_m1_arcache),
    .m_axi_dram1_arprot(m_axi_m1_arprot),
    .m_axi_dram1_arqos(m_axi_m1_arqos),
    .m_axi_dram1_rready(m_axi_m1_rready),
    .m_axi_dram1_rvalid(m_axi_m1_rvalid),
    .m_axi_dram1_rid(m_axi_m1_rid),
    .m_axi_dram1_rdata(m_axi_m1_rdata),
    .m_axi_dram1_rresp(m_axi_m1_rresp),
    .m_axi_dram1_rlast(m_axi_m1_rlast)
  );

  assign m_axi_m0_awuser = 1'b0;
  assign m_axi_m0_aruser = 1'b0;
  assign m_axi_m1_awuser = 1'b0;
  assign m_axi_m1_aruser = 1'b0;

endmodule