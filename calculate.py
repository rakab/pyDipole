import subprocess
from pyDipole import Process
import sympy as sy
import re

proc = Process(['e','ebar'],['u','ubar'])

expressions = ''
par1_rules = ''

for par1 in proc.all_particles:
    if not par1.isQCD:
        continue

    if par1.name == 'g':
        par1_rules += '''\
id Col({0},{0}) = CA;
id Gamm({0}) = CA*11/6-Tr*Nfl;
id K({0}) = (67/18-pi^2/6)*CA-Tr*Nfl*10/9;\n
'''.format(par1.id)
    else:
        par1_rules += '''\
id Col({0},{0}) = CF;
id Gamm({0}) = CF*3/2;
id K({0}) = (7/2-pi^2/6)*CF;
'''.format(par1.id)

    for par2 in proc.all_particles:
        if par1.id == par2.id:
            continue
        if not par2.isQCD:
            continue
        expressions += "L I{0}{1} = I({0},{1},{2:d});\n\n".format(par1.id,par2.id,par1.isMassive)



print(expressions)

code = '''\
#-
off stats;

S Alfas, pi, eps, CF, CA, Tr, Nfl;
CF I, MuFactor, InvGamma, Col,Nu, Gamm, K;
AutoDeclare I i;\n
'''

code += expressions

code += '''\
\nid I(i1?,i2?,0) = -Alfas/(2*pi)*InvGamma(1-eps)*Col(i1,i1)^(-1)*Nu(i1)*Col(i1,i2)*MuFactor(i1,i2)^eps;

id Nu(i1?) = Col(i1,i1)*(eps^(-2)-pi^2/3)+Gamm(i1)*eps^(-1)+Gamm(i1)+K(i1);\n\n
'''

code += par1_rules

code += '''\
\n.sort
Print;
B InvGamma,Alfas,pi,MuFactor;
.end
'''

form_file_name = '/tmp/FORM_Code.frm'
with open(form_file_name,'w') as f:
    f.write(code)

"""
Run FORM, read the result back in python and execute SymPy simplifications
"""

form_res = subprocess.run(["form","-f",form_file_name],capture_output=True,text=True).stdout
form_res=form_res.replace('\n','')
form_res=form_res.replace(' ','')
form_res = form_res.split(';')[:-1]

#Prepare SymPy variables
InvGamma = sy.Function('InvGamma')
MuFactor = sy.Function('MuFactor')
Col = sy.Function('Col')
eps = sy.Symbol('eps')
a_,b_ = map(sy.Wild, 'ab')


eq_dict = dict()
for eq in form_res:
    eq_name = re.search(r"^(.*)=",eq).group(0)[:-1]
    eq_dict[eq_name] = []
    eq = sy.together(sy.sympify(eq.replace(eq_name+'=','')))
    eq = eq.replace(InvGamma(a_),1/sy.gamma(a_))
    series = sy.series(eq,eps,n=0)
    eq_dict[eq_name].append(eq)
    eq_dict[eq_name].append(series.coeff(eps**-2))
    eq_dict[eq_name].append(series.coeff(eps**-1))
