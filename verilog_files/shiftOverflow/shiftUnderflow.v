module shiftLeft (
    input clk,
    output [2:0] out
);

reg [2:0] internalReg = 1;

// always @(*) begin
//     if(internalReg == 0)
//         internalReg = 1;
// end


always @(posedge clk) begin
    internalReg <= internalReg >> 1;
end

assign out = internalReg;

endmodule
