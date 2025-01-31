/*
  - hardcoded for 2x2 as first step
*/


module MacManager #(
    parameter integer N = 16,
    parameter integer OP_WIDTH = 8,
    parameter integer ACC_WIDTH = 32
) (
    input clk,
    input reset,
    input [2*OP_WIDTH-1:0] new_a_column,
    input [2*OP_WIDTH-1:0] new_b_row
);
  reg [OP_WIDTH-1:0] mac_a_rows[2][2];
  reg [OP_WIDTH-1:0] mac_b_columns[2][2];
  reg [OP_WIDTH-1:0] mac_c[2][2];
  wire [ACC_WIDTH-1:0] mac11_c, mac12_c, mac21_c, mac22_c;
  integer i;
  genvar gi, gj;

  always @(posedge clk) begin
    if (reset)
      for (i = 0; i < 2; i = i + 1) begin
        mac_a_rows[i][0] <= 0;
        mac_a_rows[i][1] <= 0;

        mac_b_columns[i][0] <= 0;
        mac_b_columns[i][1] <= 0;
      end
    else
      for (i = 0; i < 2; i = i + 1) begin
        // i stands for the i-th row (a) or the i-th column (b)
        mac_a_rows[i][0] <= new_a_column[i*OP_WIDTH+:OP_WIDTH];
        mac_a_rows[i][1] <= mac_a_rows[i][0];

        mac_b_columns[i][0] <= new_b_row[i*OP_WIDTH+:OP_WIDTH];
        mac_b_columns[i][1] <= mac_b_columns[i][0];
      end
  end

  generate
    for (gi = 0; gi < N; gi = gi + 1) begin : gen_row
      for (gj = 0; gj < N; gj = gj + 1) begin : gen_col
        Mac #(
            .OP_WIDTH (OP_WIDTH),
            .ACC_WIDTH(ACC_WIDTH)
        ) mac_inst (
            .clk(clk),
            .reset(reset),
            .ena(1),
            .A(mac_a_rows[gi][gj]),
            .B(mac_b_columns[gj][gi]),
            .C(mac_c[gi][gj])
        );
      end
    end
  endgenerate

  // temporary:
  assign mac11_c = mac_c[0][0];
  assign mac12_c = mac_c[0][1];
  assign mac21_c = mac_c[1][0];
  assign mac22_c = mac_c[1][1];

endmodule
