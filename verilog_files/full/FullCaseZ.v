module FCaseZ (
   input [1:0] x,
   output y
);
    always @(x) begin
        casez (x)
            2'bZZ: y = 1; 
        endcase
    end
endmodule