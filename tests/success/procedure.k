program main {
    procedure next_step {
        begin;
            i++;
        end;
    }
    procedure action {
        begin;
            write("HERE");
        end;
    }
    begin;
        for(i := 0; i < 5; next_step()){
            action();
        }
    end;
}