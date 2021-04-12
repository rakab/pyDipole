import subprocess
from pyDipole import Process

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
id K({0}) = (67/18-Pi^2/6)*CA-Tr*Nfl*10/9;\n
'''.format(par1.id)
    else:
        par1_rules += '''\
id Col({0},{0}) = CF;
id Gamm({0}) = CF*3/2;
id K({0}) = (7/2-Pi^2/6)*CF;
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
on stats;

S Alfas, Pi, eps, CF, CA, Tr, Nfl;
CF I, MuFactor, InvGamma, Col,Nu, Gamm, K;
AutoDeclare I i;\n
'''

code += expressions

code += '''\
\nid I(i1?,i2?,0) = -Alfas/(2*Pi)*InvGamma(1-eps)*Col(i1,i1)*Nu(i1)*Col(i1,i2)*MuFactor(i1,i2)^eps;

id Nu(i1?) = Col(i1,i1)*(eps^(-2)-Pi^2/3)+Gamm(i1)*eps^(-1)+Gamm(i1)+K(i1);\n\n
'''

code += par1_rules

code += '''\
\n.sort
Print;
B InvGamma,Alfas,Pi,MuFactor;
.end
'''

form_file_name = '/tmp/FORM_Code.frm'
with open(form_file_name,'w') as f:
    f.write(code)

subprocess.run(["form",form_file_name])
