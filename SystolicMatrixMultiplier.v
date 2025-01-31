/*
  - Assuming 2x2 Matrices for now
  - Might need a function or similar to convert 1D array to 2D array
  - Potentially better to fix the size of the top-level matrix multiplier module,
  and operating through enas in the gemmIM -> google tpu also does it this way
*/

module SystolicMatrixMultiplier #(
    parameter integer OP_WIDTH = 8
) (
    input clk,
    input reset,
    input [4*OP_WIDTH-1:0] A,
    input [4*OP_WIDTH-1:0] B
);
  parameter integer ACC_WIDTH = 18;

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

  // temporary:
  reg [OP_WIDTH-1:0] new_a_column0, new_a_column1, new_b_row0, new_b_row1;

  // logic to switch input
  always_comb begin
    // todo
    // - probably case over state
    // - think about how to easily pass values from the array in the GemmInputManager -> fe through smart indexing
    // - gemmIM inputs will be moved into the macs after the next clk
    if (state == 0 || state == 1) new_a_column0 = A[OP_WIDTH*state+:OP_WIDTH];
    else new_a_column0 = 0;

    if (state + 1 == 2 || state + 1 == 3) new_a_column1 = A[OP_WIDTH*(state+1)+:OP_WIDTH];
    else new_a_column1 = 0;

    if (state * 2 == 0 || state * 2 == 2) new_b_row0 = B[OP_WIDTH*(state*2)+:OP_WIDTH];
    else new_b_row0 = 0;

    if (state * 2 - 1 == 1 || state * 2 - 1 == 3) new_b_row1 = B[OP_WIDTH*((state*2)-1)+:OP_WIDTH];
    else new_b_row1 = 0;
  end

  assign new_a_column = {new_a_column1, new_a_column0};
  assign new_b_row = {new_b_row1, new_b_row0};

  always @(posedge clk) begin
    if (reset) state <= 0;
    else if (state >= 5) state <= state;
    else state <= state + 1;
  end

endmodule
