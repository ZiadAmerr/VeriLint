module unreachableState (
    input clk
);
    //these are our states in the finite state machine
    localparam [1:0] READY = 2'b00;
    localparam [1:0] SET = 2'b01;
    localparam [1:0] GO = 2'b10;
    
    //in an fsm we do not directly change the current state of the machine.
    //insead we assign the value to the next state register and each cycle in an always block the value 
    //in the next state reg is assigned to the current state.
    reg [1:0] current_state;
    reg [1:0] next_state;

    //this always block assigns the next state to the current state synchronized with the clock
    always @(posedge clk) begin
        current_state <= next_state;
    end

    //this always block decides what the next state will be
    //here the GO state is unreachable simply because no state transitions into it
    always @(*) begin
        case (current_state)
            READY:
            begin
                next_state = 2'b01;
            end
            SET:
            begin
                next_state = 2'b00; 
            end
            GO: 
            begin
                next_state = SET;
            end
            default: 
                next_state = READY;
        endcase
    end
    endmodule