module counter (
    input clk,
    output [2:0] out
);

reg [2:0] internalReg = 0;

always @(posedge clk) begin
    internalReg = internalReg + 1;
end

assign out = internalReg;

endmodule