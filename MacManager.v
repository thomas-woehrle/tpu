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
  // temporary like this, hardcoded for 2x2 matrix
  wire [ACC_WIDTH-1:0] mac11_c, mac12_c, mac21_c, mac22_c;
  integer i, j;
  genvar gi, gj;

  always @(posedge clk) begin
    if (reset)
      for (i = 0; i < N; i = i + 1) begin
        for (j = 0; j < N; j = j + 1) begin
          // i is row, j is column for a and vice versa for b -> allows for simple assignment
          mac_a_rows[i][j] <= 0;
          mac_b_columns[i][j] <= 0;
        end
      end
    else
      for (i = 0; i < N; i = i + 1) begin
        for (j = 0; j < N; j = j + 1) begin
          // same as in reset case
          if (j == 0) begin
            mac_a_rows[i][j] <= new_a_column[i*OP_WIDTH+:OP_WIDTH];
            mac_b_columns[i][j] <= new_b_row[i*OP_WIDTH+:OP_WIDTH];
          end else begin
            mac_a_rows[i][j] <= mac_a_rows[i][j-1];
            mac_b_columns[i][j] <= mac_b_columns[i][j-1];
          end
        end
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
