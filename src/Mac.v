/*
Multiply and accumulate module

Parameters:
  OP_WIDTH: The width of the two operands a and b in bits
  ACC_WIDTH: Thw width of the accumulator c in bits. Generally, this should be
    at least 2*OP_WIDTH + log2(<number of expected accumulations>)

Inputs:
  clk: The clock
  reset: Synchronous active high reset signal. Resets c to 0
  ena: Enable signal. If not set, c will stay the same unless reset
  a: The first operand
  b: The second operand

Outpus:
  c: The accumulated value
*/
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
