#ifndef __MMULT_H
#define __MMULT_H

extern "C" void mmult(const int* a, // Read-Only Matrix A
           const int* b, // Read-Only Matrix B
           int* c,       // Output Result
           int a_row,    // Matrix A Row Size
           int a_col,    // Matrix A Col Size
           int b_col     // Matrix B Col Size
           );

#endif // __MMULT_H
