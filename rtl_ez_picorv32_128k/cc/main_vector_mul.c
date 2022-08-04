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


int main(int argc, char ** argv){

    int length     = *(int*) 0x1fffc;
    int * vector_a = (int*)(*(int*) 0x1fff8);
    int * vector_b = (int*)(*(int*) 0x1fff4);
    int * vector_r = (int*)(*(int*) 0x1fff0);

    for(int i=0; i < length; i++){
        vector_r[i] = vector_a[i] * vector_b[i];
    }
    return 0;
}
