program main{

	var i,n,x,j,m : int;
	begin;
		write("prueba for");		
		n:=5;
		j := 0;
		x := 1;
		for (i:=1;i<n;i++){
			x := x * i;
			for(j:=1;j<n;j++){
				m := i + j;
				write(i);
				write(j);
				write(m);
			}
		}
		write(x);
	end;
}