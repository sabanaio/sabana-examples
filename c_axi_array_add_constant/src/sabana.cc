
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
#define MAX_SIZE 50

void sabana(int size, int* a)  {
  #pragma HLS INTERFACE s_axilite port=size bundle=c0
  #pragma HLS INTERFACE s_axilite port=a bundle=c0
  #pragma HLS INTERFACE s_axilite port=return bundle=c0
  #pragma HLS INTERFACE m_axi port=a offset=slave bundle=m0
  // your code here
  int buff[MAX_SIZE];

  memcpy(buff, (const int*)a, MAX_SIZE*sizeof(int));

  for(int i = 0; i <= size; i++){
    buff[i] = buff[i] + 100;
  }

  memcpy((int *)a, buff, MAX_SIZE*sizeof(int));
}
