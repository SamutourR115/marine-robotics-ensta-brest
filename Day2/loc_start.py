from mycontractor import *
from roblib import *


_x,_y=[66,-44,-9,-30,12,-20,0,-50],[-70,55,30,-15,70,0,10,-50]
N=len(_x)
_d=[[0. for i in range(N)] for j in range(N)]
D=[[Interval(-oo,oo) for i in range(N)] for j in range(N)]
X=[Interval(-oo,oo) for i in range(N)]
Y=[Interval(-oo,oo) for i in range(N)]
for i in range(0,N):
	for j in range(0,N):
		if i!=j:
			_d[i][j]=int(round(sqrt((_x[j]-_x[i])**2+(_y[j]-_y[i])**2)))
			D[i][j]=Interval(_d[i][j]-0.5,_d[i][j]+0.5)
		else: D[i][j]=Interval(0,0)


ax=init_figure(-100,100,-100,100)


for i in range(0,3):
	X[i]=Interval(_x[i]-3,_x[i]+3)
	Y[i]=Interval(_y[i]-3,_y[i]+3)
	draw_box_border(X[i].lb,X[i].ub,Y[i].lb,Y[i].ub,'blue',1)

for k in range(10):                    
    for i in range(N):
        for j in range(N):
            if i != j:
                a  = Interval(-oo, oo); b  = Interval(-oo, oo)
                a2 = Interval(-oo, oo); b2 = Interval(-oo, oo); d2 = Interval(-oo, oo)
                a, X[j], X[i]   = cminus(a, X[j], X[i])
                b, Y[j], Y[i]   = cminus(b, Y[j], Y[i])
                a2, a           = csqr(a2, a)
                b2, b           = csqr(b2, b)
                d2, D[i][j]     = csqr(d2, D[i][j])
                d2, a2, b2      = cadd(d2, a2, b2)
                a2, a           = csqr(a2, a)
                b2, b           = csqr(b2, b)
                a, X[j], X[i]   = cminus(a, X[j], X[i])
                b, Y[j], Y[i]   = cminus(b, Y[j], Y[i])

print("_d=",_d)
print("X=",X)
print("Y=",Y)

for i in range(0,N):
	draw_box_border(_x[i]-0.2,_x[i]+0.2,_y[i]-0.2,_y[i]+0.2,'red',2)


pause(10)


