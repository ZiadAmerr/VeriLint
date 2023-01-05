module PCaseZ (
    input [1:0] x,
    output y
);
    always @(x) begin
        casez (x)
            2'b00: y = 1;
            2'b1Z: y = 0; 
            default: y = 0;
        endcase
    end
endmodule