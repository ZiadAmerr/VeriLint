module NPCaseZ (
    input [1:0] x,
    output y
);

always @(x) begin
    casez (x)
        2'b00: y = 0;
        2'b0Z: y = 1; 
        default: y = 0;
    endcase
end
    
endmodule