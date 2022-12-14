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
  input  logic            clock,
  input  logic            reset,
  input  logic            s_axi_c0_awvalid,
  output logic            s_axi_c0_awready,
  input  logic [32-1:0]   s_axi_c0_awaddr,
  input  logic            s_axi_c0_wvalid,
  output logic            s_axi_c0_wready,
  input  logic [32-1:0]   s_axi_c0_wdata,
  input  logic [4-1:0]    s_axi_c0_wstrb,
  input  logic            s_axi_c0_arvalid,
  output logic            s_axi_c0_arready,
  input  logic [32-1:0]   s_axi_c0_araddr,
  output logic            s_axi_c0_rvalid,
  input  logic            s_axi_c0_rready,
  output logic [32-1:0]   s_axi_c0_rdata,
  output logic [2-1:0]    s_axi_c0_rresp,
  output logic            s_axi_c0_bvalid,
  input  logic            s_axi_c0_bready,
  output logic [2-1:0]    s_axi_c0_bresp,
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
  output logic [64-1:0]   m_axi_m0_wdata,
  output logic [8-1:0]    m_axi_m0_wstrb,
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
  input  logic [64-1:0]   m_axi_m0_rdata,
  input  logic [2-1:0]    m_axi_m0_rresp,
  input  logic            m_axi_m0_rlast
);

  XilinxShell vta (
    .ap_clk(clock),
    .ap_rst_n(~reset),
    .m_axi_gmem_AWVALID(m_axi_m0_awvalid),
    .m_axi_gmem_AWREADY(m_axi_m0_awready),
    .m_axi_gmem_AWADDR(m_axi_m0_awaddr),
    .m_axi_gmem_AWID(m_axi_m0_awid),
    .m_axi_gmem_AWUSER(m_axi_m0_awuser),
    .m_axi_gmem_AWLEN(m_axi_m0_awlen),
    .m_axi_gmem_AWSIZE(m_axi_m0_awsize),
    .m_axi_gmem_AWBURST(m_axi_m0_awburst),
    .m_axi_gmem_AWLOCK(m_axi_m0_awlock),
    .m_axi_gmem_AWCACHE(m_axi_m0_awcache),
    .m_axi_gmem_AWPROT(m_axi_m0_awprot),
    .m_axi_gmem_AWQOS(m_axi_m0_awqos),
    .m_axi_gmem_AWREGION(),
    .m_axi_gmem_WVALID(m_axi_m0_wvalid),
    .m_axi_gmem_WREADY(m_axi_m0_wready),
    .m_axi_gmem_WDATA(m_axi_m0_wdata),
    .m_axi_gmem_WSTRB(m_axi_m0_wstrb),
    .m_axi_gmem_WLAST(m_axi_m0_wlast),
    .m_axi_gmem_WID(m_axi_m0_wid),
    .m_axi_gmem_WUSER(),
    .m_axi_gmem_BVALID(m_axi_m0_bvalid),
    .m_axi_gmem_BREADY(m_axi_m0_bready),
    .m_axi_gmem_BRESP(m_axi_m0_bresp),
    .m_axi_gmem_BID(m_axi_m0_bid),
    .m_axi_gmem_BUSER(),
    .m_axi_gmem_ARVALID(m_axi_m0_arvalid),
    .m_axi_gmem_ARREADY(m_axi_m0_arready),
    .m_axi_gmem_ARADDR(m_axi_m0_araddr),
    .m_axi_gmem_ARID(m_axi_m0_arid),
    .m_axi_gmem_ARUSER(m_axi_m0_aruser),
    .m_axi_gmem_ARLEN(m_axi_m0_arlen),
    .m_axi_gmem_ARSIZE(m_axi_m0_arsize),
    .m_axi_gmem_ARBURST(m_axi_m0_arburst),
    .m_axi_gmem_ARLOCK(m_axi_m0_arlock),
    .m_axi_gmem_ARCACHE(m_axi_m0_arcache),
    .m_axi_gmem_ARPROT(m_axi_m0_arprot),
    .m_axi_gmem_ARQOS(m_axi_m0_arqos),
    .m_axi_gmem_ARREGION(),
    .m_axi_gmem_RVALID(m_axi_m0_rvalid),
    .m_axi_gmem_RREADY(m_axi_m0_rready),
    .m_axi_gmem_RDATA(m_axi_m0_rdata),
    .m_axi_gmem_RRESP(m_axi_m0_rresp),
    .m_axi_gmem_RLAST(m_axi_m0_rlast),
    .m_axi_gmem_RID(m_axi_m0_rid),
    .m_axi_gmem_RUSER(),
    .s_axi_control_AWVALID(s_axi_c0_awvalid),
    .s_axi_control_AWREADY(s_axi_c0_awready),
    .s_axi_control_AWADDR(s_axi_c0_awaddr[15:0]),
    .s_axi_control_WVALID(s_axi_c0_wvalid),
    .s_axi_control_WREADY(s_axi_c0_wready),
    .s_axi_control_WDATA(s_axi_c0_wdata),
    .s_axi_control_WSTRB(s_axi_c0_wstrb),
    .s_axi_control_BVALID(s_axi_c0_bvalid),
    .s_axi_control_BREADY(s_axi_c0_bready),
    .s_axi_control_BRESP(s_axi_c0_bresp),
    .s_axi_control_ARVALID(s_axi_c0_arvalid),
    .s_axi_control_ARREADY(s_axi_c0_arready),
    .s_axi_control_ARADDR(s_axi_c0_araddr[15:0]),
    .s_axi_control_RVALID(s_axi_c0_rvalid),
    .s_axi_control_RREADY(s_axi_c0_rready),
    .s_axi_control_RDATA(s_axi_c0_rdata),
    .s_axi_control_RRESP(s_axi_c0_rresp)
  );

endmodule
