// Multiply and Accumulate module

module Mac #(
    parameter integer OP_WIDTH  = 8,
    parameter integer ACC_WIDTH = 32
) (
    input clk,
    input reset,
    input ena,
    input [OP_WIDTH-1:0] A,
    input [OP_WIDTH-1:0] B,
    output [ACC_WIDTH-1:0] C
);
  wire [2*OP_WIDTH-1:0] partial_sum;
  reg  [ ACC_WIDTH-1:0] accumulator;

  assign partial_sum = A * B;

  always @(posedge clk) begin
    if (reset) accumulator <= 0;
    else if (ena) accumulator <= accumulator + partial_sum;
    else accumulator <= accumulator;
  end

  assign C = accumulator;

endmodule
