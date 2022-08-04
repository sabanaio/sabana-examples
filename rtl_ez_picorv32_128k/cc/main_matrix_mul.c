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

// Currently we only support square matrix of shape: (side, side)
int * ret_array(int * pointer, int row, int col, int len){
    return pointer + (row * len + col);
}

int main(int argc, char ** argv){

    int side     = *(int*) 0x1fffc;
    int * matrix_a = (int*)(*(int*) 0x1fff8);
    int * matrix_b = (int*)(*(int*) 0x1fff4);
    int * matrix_r = (int*)(*(int*) 0x1fff0);

    for(int i=0; i < side; i++){
        for(int j=0; j < side; j++){
            *(ret_array(matrix_r, i, j,side)) = 0;
            for(int k=0; k < side; k++){
                *(ret_array(matrix_r, i, j,side)) +=
                *(ret_array(matrix_a, i, k, side)) *
                *(ret_array(matrix_b, k, j, side));
            }
        }
    }
    return 0;
}
