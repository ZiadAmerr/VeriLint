module NPCaseX (
    input [1:0] x,
    output reg y
);

always @(x) begin 
    casex (x)
        2'b0X: y = 0;
        2'bX1: y = 0; 
    endcase
end
    
endmodule