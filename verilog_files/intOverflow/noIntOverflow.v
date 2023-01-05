module integerOverflow (
    input clk,
    output [31:0] out
);

integer internalReg = 32'b1111111111111111111111111111110;

always @(posedge clk) begin
    internalReg = 1 + 1;
end

assign out = internalReg;

endmodule