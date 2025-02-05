// Multiply and Accumulate module
module Mac #(
    parameter integer OP_WIDTH  = 8,
    parameter integer ACC_WIDTH = 32
) (
    input clk,
    input reset,
    input ena,
    input [OP_WIDTH-1:0] a,
    input [OP_WIDTH-1:0] b,
    output [ACC_WIDTH-1:0] c
);
  wire [2*OP_WIDTH-1:0] partial_sum;
  reg  [ ACC_WIDTH-1:0] accumulator;

  assign partial_sum = a * b;

  always @(posedge clk) begin
    if (reset) accumulator <= 0;
    else if (ena) accumulator <= accumulator + partial_sum;
    else accumulator <= accumulator;
  end

  assign c = accumulator;

endmodule
