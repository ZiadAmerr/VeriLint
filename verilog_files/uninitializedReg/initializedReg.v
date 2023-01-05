module initReg (
    input clk
);
    reg [0:0] x = 0;
    reg [1:0] y;

    always @(posedge clk)
    begin
        y = x + 1;
    end

endmodule