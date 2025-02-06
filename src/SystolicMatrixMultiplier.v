/*
Implements general matrix multiplication using an systolic array approach

Currently, this module receives the inputs in bulk. Its job is to reshape them
as an systolic array and pass the elements of a and b one-by-one to the MacManager.
The MacManager then controls the systolic-array-like flow to the actual MAC units.

Parameters:
  N: The quadratic size of a, b. NxN MACs will be instantiated. However, this does not
    necessarily have to be the shape of the underyling matrices that are being mutliplied.
    One could obtain non-quadratic shapes by adding 0 at indices outside the desired range.
  OP_WIDTH: The width of the numbers in a and b in bits
  ACC_WIDTH: The width of the accumulator ie the result in the MACs

Inputs:
  clk: The clock
  reset: Synchronous active-high reset
  a: NxN matrix in row-major order
  b: NxN matrix in row-major order

*/
module SystolicMatrixMultiplier #(
    parameter integer N = 2,
    parameter integer OP_WIDTH = 8,
    // 32 is big enough for most things. Can be finetuned be on instantiation
    parameter integer ACC_WIDTH = 32
) (
    input clk,
    input reset,
    input [N*N*OP_WIDTH-1:0] a,
    input [N*N*OP_WIDTH-1:0] b
);
  // The maximum values this is planned to work with
  // The choice of these is arbitrary to make a decision about signal width and
  // not grounded in hardware constraints etc. The actual max capacity could be
  // higher or lower
  localparam integer MAX_N = 256;
  localparam integer LOG2_MAX_N = 8;

  // Determines the element in next_a_column for a certain row
  function static [OP_WIDTH-1:0] get_next_a_column_element;
    input [N*N*OP_WIDTH-1:0] a;
    input [LOG2_MAX_N-1:0] row;
    input [2+LOG2_MAX_N-1:0] state;

    if (state >= row && state < row + N)
      get_next_a_column_element = a[OP_WIDTH*((state-row)+N*row)+:OP_WIDTH];
    else get_next_a_column_element = 0;
  endfunction

  // Determines the element in next_b_row for a certain column
  function static [OP_WIDTH-1:0] get_next_b_row_element;
    input [N*N*OP_WIDTH-1:0] b;
    input [LOG2_MAX_N-1:0] column;
    input [2+LOG2_MAX_N-1:0] state;

    if (state >= column && state < column + N)
      get_next_b_row_element = b[OP_WIDTH*((state-column)*N+column)+:OP_WIDTH];
    else get_next_b_row_element = 0;
  endfunction

  // N*3 states need to be distinguished. ie log2(3*n) bits are needed = log2(3) + log2(n) < 2 + log2(n)
  reg [2+LOG2_MAX_N-1:0] state;

  // MacManager input, see the documentation there for more info
  reg [  N*OP_WIDTH-1:0] next_a_column;
  reg [  N*OP_WIDTH-1:0] next_b_row;

  genvar gi;

  MacManager #(
      .N(N),
      .OP_WIDTH(OP_WIDTH),
      .ACC_WIDTH(ACC_WIDTH)
  ) mac_manager (
      .clk(clk),
      .reset(reset),
      .next_a_column(next_a_column),
      .next_b_row(next_b_row)
  );

  generate
    for (gi = 0; gi < N; gi = gi + 1) begin : gen_rowcol_assignments
      assign next_a_column[OP_WIDTH*gi+:OP_WIDTH] = get_next_a_column_element(a, gi, state);
      assign next_b_row[OP_WIDTH*gi+:OP_WIDTH] = get_next_b_row_element(b, gi, state);
    end
  endgenerate

  always @(posedge clk) begin
    if (reset) state <= 0;
    // 3 * N - 1 is the max value it can take on, could be used as done signal
    else if (state == 3 * N - 1) state <= state;
    else state <= state + 1;
  end

endmodule
