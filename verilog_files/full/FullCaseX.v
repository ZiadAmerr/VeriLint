module FCaseX (
    input [1:0] x,
    output y
);

always @(x) begin
    casex (x)
        2'b00: y = 0;
        2'b11: y = 0;
        2'bXX: y = 0;
        default: y = 1;
    endcase
end
endmodule