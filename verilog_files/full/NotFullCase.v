module CaseFile (
    input [1:0] x,
    output reg y
);

always @(x) begin
    case (x)
        2'b00: y = 0;
        2'b01: y = 1;
        2'b0X: y = 0;
        2'b0Z: y = 1;
        2'b10: y = 0;
        2'b11: y = 1;
        2'b1Z: y = 0;
        2'b1X: y = 1;
        2'bXX: y = 0;
        2'bXZ: y = 1;
        2'bX1: y = 0;
        2'bX0: y = 1;
        2'bZ0: y = 0;
        2'bZ1: y = 1;
        2'bZX: y = 0;
        
    endcase
end
    
endmodule