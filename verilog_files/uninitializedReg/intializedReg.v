module initReg (
    input clk
);
    reg x = 0;

    always @(posedge clk)
    begin
        x = x + 1;
    end

endmodule