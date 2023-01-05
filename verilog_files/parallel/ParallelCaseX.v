module PCaseX (
    input [1:0] x,
    output reg y
);

always @(x) begin 
    case (x)
        2'b0X: y = 0;
        2'b1X: y = 0; 
    endcase
end
    
endmodule