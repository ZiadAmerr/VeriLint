module multiDriven (output out);
    wire x;
    reg y;
    //here x has multiple drivers which are the 2 assign statements
    assign x = 1'b1; 
    assign x = 1'b0;
    //same thing here with out
    assign out = x;
    assign out = 0'b1;

    //regs are assigned values using an always block while wires are assigned values using assign statements
    always @(*)
    begin
        y = 1'b1;
    end

    always @(*)
    begin
        y = 1'b0;
    end
endmodule