program main{

	var a,b,x,y,i,z,j : int;
	begin;
		write("prueba if");

		a := 5;
		b :=  a + 3;
		x := b +5;
		y := x + a;
		z := 1;		

		if( a<=b) then
		{
			i := a*5+(b+4);
			write("caso true");
			write(a);
			for(j:=0;j<a;j++)
			{
				write(b);
				z := i + a;
				write (i);
			}
		}else
		{
			if(y<x) then
			{
				i := x * (b * y);
				write(x);
				write("if anidado");
			}else
			{
				write("ultimo caso");
			}
		}

		write(i);
	end;
}