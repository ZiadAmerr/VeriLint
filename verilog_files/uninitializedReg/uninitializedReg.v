module uninitReg (
    input clk
);
    reg x;

    always @(posedge clk)
    begin
        x = x + 1;
    end

endmodule