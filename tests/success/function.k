program main {
    var i: int;
    function next_step() {
        begin;
            i++;
        end;
    }
    function action() {
        begin;
            write("HERE");
            write(i);
        end;
    }
    begin;
        for(i := 0; i < 5; next_step()){
            action();
        }
    end;
}