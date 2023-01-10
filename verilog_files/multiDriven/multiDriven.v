module VeriLint (input [1:0] x, output out);
    reg y;
    
    // In the 2 following lines, out is multdriven by two assign statements
    assign out = x;
    assign out = 0'b1;

    // In the 2 following always blocks, y is multidriven
    always @(*)
    begin
        y = y + 1;
    end
    always @(*)
    begin
        y = 1'b0;
    end

    // The following casex statement is neither full nor parallel
    always @(x)
    begin
        casex (x)
            2'b0X: y = 0;
            2'bX1: y = 0; 
        endcase
    end
endmodule