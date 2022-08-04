
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

void sabana(const int* a, const int* b, int* c)  {
  #pragma HLS INTERFACE s_axilite port=a bundle=c0
  #pragma HLS INTERFACE s_axilite port=b bundle=c0
  #pragma HLS INTERFACE s_axilite port=c bundle=c0
  #pragma HLS INTERFACE s_axilite port=return bundle=c0
  #pragma HLS INTERFACE m_axi port=a offset=slave bundle=m0
  #pragma HLS INTERFACE m_axi port=b offset=slave bundle=m0
  #pragma HLS INTERFACE m_axi port=c offset=slave bundle=m0
  int bufa [4][4];
  int bufb [4][4];
  int bufc [4][4];

  memcpy(bufa, (const int*)a, 4*4*sizeof(int));
  memcpy(bufb, (const int*)b, 4*4*sizeof(int));

  for (int i = 0; i < 4; i++) {
    for (int j = 0; j < 4; j++) {
      bufc[i][j] = 0;
      for (int k = 0; k < 4; k++) {
        bufc[i][j] += bufa[i][k] * bufb[k][j];
      }
    }
  }

  memcpy((int *)c, bufc, 4*4*sizeof(int));

}