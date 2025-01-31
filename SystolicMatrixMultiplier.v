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
    input [4*OP_WIDTH-1:0] B,
    output [4*OP_WIDTH-1:0] C
);
  parameter integer ACC_WIDTH = 18;

  // there are 6 states to be distinguished, ie n*3
  reg [2:0] state, next_state;

  // GemmInputManager input
  reg [2*OP_WIDTH-1:0] new_a_column;
  reg [2*OP_WIDTH-1:0] new_b_row;
  reg [2-1:0] new_a_column_ena;
  reg [2-1:0] new_b_row_ena;

  // GemmInputManager output and Mac input
  reg mac11_ena, mac12_ena, mac21_ena, mac22_ena;
  reg
      mac11_a_ena,
      mac11_b_ena,
      mac12_a_ena,
      mac12_b_ena,
      mac21_a_ena,
      mac21_b_ena,
      mac22_a_ena,
      mac22_b_ena;

  assign mac11_ena = mac11_a_ena && mac11_b_ena;
  assign mac12_ena = mac12_a_ena && mac12_b_ena;
  assign mac21_ena = mac21_a_ena && mac21_b_ena;
  assign mac22_ena = mac22_a_ena && mac22_b_ena;

  reg [OP_WIDTH-1:0] mac11_a, mac11_b, mac12_a, mac12_b, mac21_a, mac21_b, mac22_a, mac22_b;

  // Mac outpus
  reg [ACC_WIDTH-1:0] mac11_c, mac12_c, mac21_c, mac22_c;

  GemmInputManager #(
      .OP_WIDTH(OP_WIDTH)
  ) gemm_input_manager (
      .clk(clk),
      .reset(reset),
      .new_a_column(new_a_column),
      .new_b_row(new_b_row),
      .new_a_column_ena(new_a_column_ena),
      .new_b_row_ena(new_b_row_ena),
      .mac11_a(mac11_a),
      .mac11_b(mac11_b),
      .mac12_a(mac12_a),
      .mac12_b(mac12_b),
      .mac21_a(mac21_a),
      .mac21_b(mac21_b),
      .mac22_a(mac22_a),
      .mac22_b(mac22_b),
      .mac11_a_ena(mac11_a_ena),
      .mac11_b_ena(mac11_b_ena),
      .mac12_a_ena(mac12_a_ena),
      .mac12_b_ena(mac12_b_ena),
      .mac21_a_ena(mac21_a_ena),
      .mac21_b_ena(mac21_b_ena),
      .mac22_a_ena(mac22_a_ena),
      .mac22_b_ena(mac22_b_ena)
  );

  Mac #(
      .OP_WIDTH (OP_WIDTH),
      .ACC_WIDTH(ACC_WIDTH)
  ) mac_11 (
      .clk(clk),
      .reset(reset),
      .ena(mac11_ena),
      .A(mac11_a),
      .B(mac11_b),
      .C(mac11_c)
  );

  Mac #(
      .OP_WIDTH (OP_WIDTH),
      .ACC_WIDTH(ACC_WIDTH)
  ) mac_12 (
      .clk(clk),
      .reset(reset),
      .ena(mac12_ena),
      .A(mac12_a),
      .B(mac12_b),
      .C(mac12_c)
  );

  Mac #(
      .OP_WIDTH (OP_WIDTH),
      .ACC_WIDTH(ACC_WIDTH)
  ) mac_21 (
      .clk(clk),
      .reset(reset),
      .ena(mac21_ena),
      .A(mac21_a),
      .B(mac21_b),
      .C(mac21_c)
  );

  Mac #(
      .OP_WIDTH (OP_WIDTH),
      .ACC_WIDTH(ACC_WIDTH)
  ) mac_22 (
      .clk(clk),
      .reset(reset),
      .ena(mac22_ena),
      .A(mac22_a),
      .B(mac22_b),
      .C(mac22_c)
  );

  // logic to switch input
  always_comb begin
    // todo
    // - probably case over state
    // - think about how to easily pass values from the array in the GemmInputManager -> fe through smart indexing
    // - gemmIM inputs will be moved into the macs after the next clk
    new_a_column = {A[OP_WIDTH*(state+1)+:OP_WIDTH], A[OP_WIDTH*state+:OP_WIDTH]};
    new_b_row = {B[OP_WIDTH*((state*2)-1)+:OP_WIDTH], B[OP_WIDTH*(state*2)+:OP_WIDTH]};  // 2==n
    new_a_column_ena = {(state + 1 == 2 || state + 1 == 3), (state == 0 || state == 1)};
    new_b_row_ena = {
      (state * 2 - 1 == 1 || state * 2 - 1 == 3), (state * 2 == 0 || state * 2 == 2)
    };
  end

  always @(posedge clk) begin
    if (reset) state <= 0;
    else if (state >= 5) state <= state;
    else state <= state + 1;
  end

endmodule
