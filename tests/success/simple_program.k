program main { 
    var arr[5], i, a, b, c: int;
    var x, y: float;
    var ch: char;
    var flag: bool;
    procedure assign_array_value {
        begin;
            arr[i] := i * 2;
        end;
    }
        procedure print_array_value {
        begin;
            write(arr[i]);
        end;
    }
    begin;
        write(true or false);
        for(i := 0; i < 5 + 3 and i > 3 * 3 or i / 4 <= 2; i++) {
            assign_array_value();
            print_array_value();
        }
        while (i > 0) do {
            write(arr[i]);
            i := i - 1;
        }
        if (i == 0) then {
            write("Done!");
        } else {
            if (i < 0) then {
                write("Error: i is negative");
            }
            if (i > 0) then {
                write("Error: i is positive");
            }
        }
    end;
}