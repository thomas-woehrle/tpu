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
  reg [OP_WIDTH-1:0] mac_a_rows[N][N];
  reg [OP_WIDTH-1:0] mac_b_columns[N][N];
  reg [ACC_WIDTH-1:0] mac_c[N][N];  // implicity mac_c_rows
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
