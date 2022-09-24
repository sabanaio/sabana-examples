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
  // AXI4-Lite (c0)
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
  output logic [128-1:0]   m_axi_m0_wdata,
  output logic [16-1:0]    m_axi_m0_wstrb,
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
  input  logic [128-1:0]   m_axi_m0_rdata,
  input  logic [2-1:0]    m_axi_m0_rresp,
  input  logic            m_axi_m0_rlast
);
  // your code here
endmodule