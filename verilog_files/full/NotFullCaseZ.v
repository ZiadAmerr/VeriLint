module NFCaseZ (
   input [1:0] x,
   output y
);
    always @(x) begin
        casez (x)
            2'b01: y = 1;
            2'b11: y = 1;
        endcase
    end
endmodule