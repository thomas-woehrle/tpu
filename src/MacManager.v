/*
Creates MACs and manages the input flow to them

Its goal is to implement a systolic array like behavior. This means that the a inputs
flow through the rows, while the b inputs flow through the columns. At any point in time
there is a next_a_column containing the next input elements to the respective mac_a_rows
and vice versa for b.

Parameters:
  N: The quadratic size of the systolic array.
  OP_WIDTH: The width of the operands in a and b. Passed to the MAC units
  ACC_WIDTH: The width of the accumulators. Passed to the MAC units

Inputs:
  clk: The clock
  reset: Synchronous active-high reset signal
  next_a_column: Next_a_column to be processed
  next_b_row: Next_b_row to be processed
  flat_mac_accumulators: NxN Array of the accumulators, essentially containing the result
*/
module MacManager #(
    parameter integer N = 16,
    parameter integer OP_WIDTH = 8,
    parameter integer ACC_WIDTH = 32
) (
    input clk,
    input reset,
    input [N*OP_WIDTH-1:0] next_a_column,
    input [N*OP_WIDTH-1:0] next_b_row,
    output reg [N*N*ACC_WIDTH-1:0] flat_mac_accumulators
);

  // basically, the current a inputs to the NxN MACs are managed in row-major order
  // while the b inputs to the MACs are managed in column-major order.
  // This means that the "sliding through" behavior of systolic arrays is easy to implement
  reg [OP_WIDTH-1:0] mac_a_rows[N][N];
  reg [OP_WIDTH-1:0] mac_b_columns[N][N];
  reg [ACC_WIDTH-1:0] mac_c[N][N];  // implicity called mac_c_rows
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
          // In the first row/colum, the next input depends on the next row/column.
          // Afterward, the next input depends on the row/column before that
          if (j == 0) begin
            mac_a_rows[i][j] <= next_a_column[i*OP_WIDTH+:OP_WIDTH];
            mac_b_columns[i][j] <= next_b_row[i*OP_WIDTH+:OP_WIDTH];
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
            .ena(1'b1),
            .a(mac_a_rows[gi][gj]),
            .b(mac_b_columns[gj][gi]),
            .c(mac_c[gi][gj])
        );

        // is this synthesizable? -> https://stackoverflow.com/questions/71055554/is-indexing-into-an-array-with-a-signal-synthesizable-in-verilog
        assign flat_mac_accumulators[(gi*N+gj)*ACC_WIDTH+:ACC_WIDTH] = mac_c[gi][gj];
      end
    end
  endgenerate

endmodule
