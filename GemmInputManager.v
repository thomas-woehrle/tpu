/*
  - hardcoded for 2x2 as first step
  - managing a and b ena signals separately for each index is the foundation for
  handling non-quadratic matrices later on
*/


module GemmInputManager #(
    parameter integer OP_WIDTH = 8
) (
    input clk,
    input reset,
    input [2*OP_WIDTH-1:0] new_a_column,
    input [2*OP_WIDTH-1:0] new_b_row,
    input [2-1:0] new_a_column_ena,
    input [2-1:0] new_b_row_ena,
    output reg [OP_WIDTH-1:0] mac11_a,
    mac11_b,
    mac12_a,
    mac12_b,
    mac21_a,
    mac21_b,
    mac22_a,
    mac22_b,
    output reg mac11_a_ena,
    mac11_b_ena,
    mac12_a_ena,
    mac12_b_ena,
    mac21_a_ena,
    mac21_b_ena,
    mac22_a_ena,
    mac22_b_ena
);
  reg [OP_WIDTH-1:0] mac_a_rows[2][2];
  reg [OP_WIDTH-1:0] mac_b_columns[2][2];
  reg mac_a_rows_ena[2][2];
  reg mac_b_columns_ena[2][2];
  integer i;

  always @(posedge clk) begin
    if (reset)
      for (i = 0; i < 2; i = i + 1) begin
        mac_a_rows[i][0] <= 0;
        mac_a_rows[i][1] <= 0;
        mac_a_rows_ena[i][0] <= 0;
        mac_a_rows_ena[i][1] <= 0;

        mac_b_columns[i][0] <= 0;
        mac_b_columns[i][1] <= 0;
        mac_b_columns_ena[i][0] <= 0;
        mac_b_columns_ena[i][1] <= 0;
      end
    else
      for (i = 0; i < 2; i = i + 1) begin
        // i stands for the i-th row (a) or the i-th column (b)
        mac_a_rows[i][0] <= new_a_column[i*OP_WIDTH+:OP_WIDTH];
        mac_a_rows[i][1] <= mac_a_rows[i][0];
        mac_a_rows_ena[i][0] <= new_a_column_ena[i];
        mac_a_rows_ena[i][1] <= mac_a_rows_ena[i][0];

        mac_b_columns[i][0] <= new_b_row[i*OP_WIDTH+:OP_WIDTH];
        mac_b_columns[i][1] <= mac_b_columns[i][0];
        mac_b_columns_ena[i][0] <= new_b_row_ena[i];
        mac_b_columns_ena[i][1] <= mac_b_columns_ena[i][0];
      end
  end

  always_comb begin
    mac11_a = mac_a_rows[0][0];
    mac11_b = mac_b_columns[0][0];
    mac21_a = mac_a_rows[1][0];
    mac21_b = mac_b_columns[0][1];
    mac12_a = mac_a_rows[0][1];
    mac12_b = mac_b_columns[1][0];
    mac22_a = mac_a_rows[1][1];
    mac22_b = mac_b_columns[1][1];

    mac11_a_ena = mac_a_rows_ena[0][0];
    mac11_b_ena = mac_b_columns_ena[0][0];
    mac21_a_ena = mac_a_rows_ena[1][0];
    mac21_b_ena = mac_b_columns_ena[0][1];
    mac12_a_ena = mac_a_rows_ena[0][1];
    mac12_b_ena = mac_b_columns_ena[1][0];
    mac22_a_ena = mac_a_rows_ena[1][1];
    mac22_b_ena = mac_b_columns_ena[1][1];
  end

endmodule
