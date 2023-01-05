module multiDriven (output out);
    wire x;
    reg y;
    assign x = 1'b0;
    assign out = 0'b1;

    always @(*)
    begin
        y = 1'b0;
    end
endmodule