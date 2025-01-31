/*
  - Assuming 2x2 Matrices for now
  - Might need a function or similar to convert 1D array to 2D array
  - Potentially better to fix the size of the top-level matrix multiplier module,
  and operating through enas in the gemmIM -> google tpu also does it this way
*/

module SystolicMatrixMultiplier #(
    parameter integer OP_WIDTH  = 8,
    // 32 for now, because it is big enough for most things. Can be finetuned later
    parameter integer ACC_WIDTH = 32
) (
    input clk,
    input reset,
    input [4*OP_WIDTH-1:0] A,
    input [4*OP_WIDTH-1:0] B
);
  // not sure whether I can reuse outer variables
  function static [OP_WIDTH-1:0] get_next_a_element;
    input [4*OP_WIDTH-1:0] a;
    input [5:0] row;
    input [2:0] state;
    input [5:0] n;

    if (state >= row && state < row + n) get_next_a_element = a[OP_WIDTH*(state+row)+:OP_WIDTH];
    else get_next_a_element = 0;
  endfunction

  function static [OP_WIDTH-1:0] get_next_b_element;
    input [4*OP_WIDTH-1:0] b;
    input [5:0] column;
    input [2:0] state;
    input [5:0] n;

    if (state >= column && state < column + n)
      get_next_b_element = b[OP_WIDTH*((state-column)*n+column)+:OP_WIDTH];
    else get_next_b_element = 0;
  endfunction

  // there are 6 states to be distinguished, ie n*3
  reg [2:0] state, next_state;

  // MacManager input
  reg [2*OP_WIDTH-1:0] new_a_column;
  reg [2*OP_WIDTH-1:0] new_b_row;

  MacManager #(
      .OP_WIDTH(OP_WIDTH)
  ) gemm_input_manager (
      .clk(clk),
      .reset(reset),
      .new_a_column(new_a_column),
      .new_b_row(new_b_row)
  );

  assign new_a_column = {get_next_a_element(A, 1, state, 2), get_next_a_element(A, 0, state, 2)};
  assign new_b_row = {get_next_b_element(B, 1, state, 2), get_next_b_element(B, 0, state, 2)};

  always @(posedge clk) begin
    if (reset) state <= 0;
    else if (state >= 5) state <= state;
    else state <= state + 1;
  end

endmodule
