module GemmInputManager #(
    parameter integer OP_WIDTH
) (
    input clk,
    input reset,
    input [2*OP_WIDTH-1:0] new_a_column,
    input [2*OP_WIDTH-1:0] new_b_row,
    input [2-1:0] new_a_column_ena,
    input [2-1:0] new_b_row_ena
);
  // hardcoded for 2x2 as first step
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

endmodule
