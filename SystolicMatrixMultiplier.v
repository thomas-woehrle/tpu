
// Assuming 2x2 Matrices for now

module SystolicMatrixMultiplier #(
    parameter integer OP_WIDTH
) (
    input clk,
    input reset,
    input [4*OP_WIDTH-1:0] A,
    input [4*OP_WIDTH-1:0] B,
    output [4*OP_WIDTH-1:0] C
);
  parameter integer ACC_WIDTH = 18;
  genvar g;
  wire mac11_ena, mac12_ena, mac21_ena, mac22_ena;
  wire mac11_ena_next, mac12_ena_next, mac21_ena_next, mac22_ena_next;
  wire [OP_WIDTH-1:0] mac11_a, mac11_b, mac12_a, mac12_b, mac21_a, mac21_b, mac22_a, mac22_b;
  wire [OP_WIDTH-1:0] mac11_a_next, mac11_b_next, mac12_a_next, mac12_b_next,
                    mac21_a_next, mac21_b_next, mac22_a_next, mac22_b_next;

  wire [ACC_WIDTH-1:0] mac11_c, mac12_c, mac21_c, mac22_c;
  wire [2:0] state, next_state;  // there are 6 states to be distinguished

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

  // logic to switch ena_mac, a_mac, b_mac
  always_comb begin
    case (state)
      0: begin
        mac11_ena_next = 1;
        mac12_ena_next = 0;
        mac21_ena_next = 0;
        mac22_ena_next = 0;

        mac11_a_next   = A[0*OP_WIDTH+:OP_WIDTH];
        mac11_b_next   = B[0*OP_WIDTH+:OP_WIDTH];
        mac12_a_next   = mac12_a;
        mac12_b_next   = mac12_b;
        mac21_a_next   = mac21_a;
        mac21_b_next   = mac21_b;
        mac22_a_next   = mac22_a;
        mac22_b_next   = mac22_b;
      end
      1: begin
        mac11_ena_next = 1;
        mac12_ena_next = 1;
        mac21_ena_next = 1;
        mac22_ena_next = 0;

        mac11_a_next   = A[1*OP_WIDTH+:OP_WIDTH];
        mac11_b_next   = B[2*OP_WIDTH+:OP_WIDTH];
        mac12_a_next   = A[0*OP_WIDTH+:OP_WIDTH];
        mac12_b_next   = B[1*OP_WIDTH+:OP_WIDTH];
        mac21_a_next   = A[2*OP_WIDTH+:OP_WIDTH];
        mac21_b_next   = B[0*OP_WIDTH+:OP_WIDTH];
        mac22_a_next   = mac22_a;
        mac22_b_next   = mac22_b;
      end
      2: begin
        mac11_ena_next = 0;
        mac12_ena_next = 1;
        mac21_ena_next = 1;
        mac22_ena_next = 1;

        mac11_a_next   = mac11_a;
        mac11_b_next   = mac11_b;
        mac12_a_next   = A[1*OP_WIDTH+:OP_WIDTH];
        mac12_b_next   = B[3*OP_WIDTH+:OP_WIDTH];
        mac21_a_next   = A[3*OP_WIDTH+:OP_WIDTH];
        mac21_b_next   = B[2*OP_WIDTH+:OP_WIDTH];
        mac22_a_next   = A[2*OP_WIDTH+:OP_WIDTH];
        mac22_b_next   = B[1*OP_WIDTH+:OP_WIDTH];
      end
      3: begin
        mac11_ena_next = 0;
        mac12_ena_next = 0;
        mac21_ena_next = 0;
        mac22_ena_next = 1;

        mac11_a_next   = mac11_a;
        mac11_b_next   = mac11_b;
        mac12_a_next   = mac12_a;
        mac12_b_next   = mac12_b;
        mac21_a_next   = mac21_a;
        mac21_b_next   = mac21_b;
        mac22_a_next   = A[3*OP_WIDTH+:OP_WIDTH];
        mac22_b_next   = B[3*OP_WIDTH+:OP_WIDTH];
      end
      4: begin
        mac11_ena_next = 0;
        mac12_ena_next = 0;
        mac21_ena_next = 0;
        mac22_ena_next = 0;

        mac11_a_next   = 0;
        mac11_b_next   = 0;
        mac12_a_next   = 0;
        mac12_b_next   = 0;
        mac21_a_next   = 0;
        mac21_b_next   = 0;
        mac22_a_next   = 0;
        mac22_b_next   = 0;
      end
      5: ;  // ?
      default: ;
    endcase
  end

  always @(posedge clk) begin
    if (reset) state <= 0;
    else if (state >= 5) state <= state;
    else state <= state + 1;
  end

endmodule
