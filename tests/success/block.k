program main {
    var i, j: int;
    begin;
        for(i := 0; i < 5; i++) {
            for(j := 0; j < 5; j++) {
                if((i * 5 + j)%2 == 1) then {
                    write("ODD");
                } else {
                    if((i * 5 + j)/2%2 == 1) then {
                        write("2 MULTIPLE");
                    } else {
                        write("4 MULTIPLE");
                    }
                }
            }
        }

        i := 0;
        while(i < 5) do {
            j := 0;
            while(j < 5) do {
                write(i * 5 + j);
                j++;
            }
            i++;
        }

    end;
}