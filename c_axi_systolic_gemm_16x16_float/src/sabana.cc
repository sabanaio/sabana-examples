
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

#include <stdio.h>
#include <string.h>
#include "mmult.h"

void sabana(int a_row, int a_col, int b_col, const float* a, const float* b, float* c)  {
  #pragma HLS INTERFACE s_axilite port=a_row bundle=c0
  #pragma HLS INTERFACE s_axilite port=a_col bundle=c0
  #pragma HLS INTERFACE s_axilite port=b_col bundle=c0
  #pragma HLS INTERFACE s_axilite port=a bundle=c0
  #pragma HLS INTERFACE s_axilite port=b bundle=c0
  #pragma HLS INTERFACE s_axilite port=c bundle=c0
  #pragma HLS INTERFACE s_axilite port=return bundle=c0
  #pragma HLS INTERFACE m_axi port=a offset=slave bundle=m0
  #pragma HLS INTERFACE m_axi port=b offset=slave bundle=m0
  #pragma HLS INTERFACE m_axi port=c offset=slave bundle=m0
  // your code here
  #pragma HLS inline recursive
  mmult(a, b, c, a_row, a_col, b_col);
}
