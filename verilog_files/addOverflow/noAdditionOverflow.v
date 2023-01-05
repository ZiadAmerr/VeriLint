module counter (
    input clk,
    output [2:0] out
);

reg [2:0] internalReg = 0;

always @(posedge clk) begin
    internalReg = 2'b11 + 2'b11;
end

assign out = internalReg;

endmodule