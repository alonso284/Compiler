program main{
    var a, b, c, d: bool;

    begin;
        a := true;
        b := false;
        c := !a || (b and true);
        d := not b && (a or false);
        a := (a && b) or (not c);
        b := (a and d) || (!b);
    end;
}
