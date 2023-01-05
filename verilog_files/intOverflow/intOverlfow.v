module integerOverflow (
    input clk,
    output [31:0] out
);

integer [31:0] internalReg = 32'b1111111111111111111111111111110;

always @(posedge clk) begin
    internalReg = internalReg + 1;
end

assign out = internalReg;

endmodule