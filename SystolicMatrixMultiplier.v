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
  localparam integer MAX_N = 256;
  localparam integer LOG2_MAX_N = 8;

  // not sure whether I can/should reuse variables from the outer scope ie the module
  function static [OP_WIDTH-1:0] get_next_a_column_element;
    input [N*N*OP_WIDTH-1:0] a;
    input [LOG2_MAX_N-1:0] row;
    input [2+LOG2_MAX_N-1:0] state;

    if (state >= row && state < row + N)
      get_next_a_column_element = a[OP_WIDTH*((state-row)+N*row)+:OP_WIDTH];
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
    // 3 * N - 1 is the max value it can take on, can be used as done signal later on
    else if (state == 3 * N - 1) state <= state;
    else state <= state + 1;
  end

endmodule
