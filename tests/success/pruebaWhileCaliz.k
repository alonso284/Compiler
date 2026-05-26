program main{
	var i,n,x,j,m :int;
	begin;
		write("prueba while");
		n :=5;
		x := 1;
		while (n>=1) do
		{
			x := x * n;
			n--;
		}
		m := n;
		j := 3;
		while ( m > 0) do
		{
			x := x + j;
			m--;
		}
		write(x);
	end;
}