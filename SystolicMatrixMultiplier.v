module SystolicMatrixMultiplier #(
    parameter integer N = 2,
    // MAX_N and LOG2_MAX_N are fixed, so they shouldn't be here, I believe
    parameter integer MAX_N = 256,
    parameter integer LOG2_MAX_N = 8,
    parameter integer OP_WIDTH = 8,
    // 32 for now, because it is big enough for most things. Can be finetuned later
    parameter integer ACC_WIDTH = 32
) (
    input clk,
    input reset,
    input [N*N*OP_WIDTH-1:0] A,
    input [N*N*OP_WIDTH-1:0] B
);

  // not sure whether I can/should reuse variables from the outer scope ie the module
  function static [OP_WIDTH-1:0] get_next_a_column_element;
    input [N*N*OP_WIDTH-1:0] a;
    input [LOG2_MAX_N-1:0] row;
    input [2+LOG2_MAX_N-1:0] state;

    // a could also use index (state-row)+n*row -> similar to how b is calculated
    if (state >= row && state < row + N)
      get_next_a_column_element = a[OP_WIDTH*(state+row)+:OP_WIDTH];
    else get_next_a_column_element = 0;
  endfunction

  function static [OP_WIDTH-1:0] get_next_b_row_element;
    input [N*N*OP_WIDTH-1:0] b;
    input [LOG2_MAX_N-1:0] column;
    input [2+LOG2_MAX_N-1:0] state;

    if (state >= column && state < column + N)
      get_next_b_row_element = b[OP_WIDTH*((state-column)*N+column)+:OP_WIDTH];
    else get_next_b_row_element = 0;
  endfunction

  // there N*3 states to be distinguished. ie log2(3*n) bits are needed = log2(3) + log2(n) < 2 + log2(n)
  reg [2+LOG2_MAX_N-1:0] state;

  // MacManager input
  reg [  N*OP_WIDTH-1:0] new_a_column;
  reg [  N*OP_WIDTH-1:0] new_b_row;

  genvar gi;

  MacManager #(
      .N(2),
      .OP_WIDTH(OP_WIDTH)
  ) mac_manager (
      .clk(clk),
      .reset(reset),
      .new_a_column(new_a_column),
      .new_b_row(new_b_row)
  );

  generate
    for (gi = 0; gi < N; gi = gi + 1) begin : gen_rowcol_assignments
      assign new_a_column[OP_WIDTH*gi+:OP_WIDTH] = get_next_a_column_element(A, gi, state);
      assign new_b_row[OP_WIDTH*gi+:OP_WIDTH] = get_next_b_row_element(B, gi, state);
    end
  endgenerate

  always @(posedge clk) begin
    if (reset) state <= 0;
    // 3 * N - 1 is the max value it can take on, can be used as done signal later on
    else if (state == 3 * N - 1) state <= state;
    else state <= state + 1;
  end

endmodule
