module NPCaseFile (
    input [1:0] x,
    output reg y
);

always @(x) begin 
    case (x)
        2'b00: y = 0; 
        2'b0?: y = 1;
        default: y = 0;
    endcase
end
    
endmodule