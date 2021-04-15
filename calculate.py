import subprocess
import logging
import sympy as sy
import re

from pyDipole import Process

logging.getLogger().setLevel(logging.INFO)


proc = Process(['e','ebar'],['u','ubar'])

expressions = ''
par1_rules = ''

#SymPy variables
alphas = sy.Symbol('alphas')
ep,pi,mu = sy.symbols('ep pi mu')
mom = dict()
for p in proc.all_particles:
    mom[p.id]=sy.Symbol('p_{0}'.format(p.id))
Col = sy.Function('Col')
Nu = sy.Function('Nu')


def eq_c27(id1, id2):
    global expressions
    expressions += '''\
L I{0}{1} = -Alfas/(2*pi)*InvGamma(1-eps)*denom(Col({0},{0}))*Nu0({0})*Col({0},{1})*Mu0({0},{1})^eps;\n
'''.format(id1,id2)

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

        logging.info('Evaluating I_{0}{1}...'.format(par1.id,par2.id))

        #final fermion
        if (par1.name != 'g' and not par1.initial):
            if not par2.initial:
                if not par1.isMassive and not par2.isMassive:
                    #C.27
                    logging.info('(i,k)=(f,k), massless, using eq C.27')
                    eq_c27(par1.id, par2.id)
                else:
                    #6.16
                    logging.info('(i,k)=(f,k), massive, using eq 6.16')
            else:
                if not par1.isMassive:
                    #C.27
                    logging.info('(i,k)=(f,b), massless, using eq C.27')
                else:
                    #6.52
                    logging.info('(i,k)=(f,b), massive, using eq 6.52')
        #final gluon
        elif (par1.name == 'g' and not par1.initial):
            if not par2.initial:
                if not par1.isMassive and not proc.mF_list:
                    #C.27
                    logging.info('(i,k)=(g,k), massless, using eq C.27')
                else:
                    #6.16
                    logging.info('(i,k)=(g,k), massive, using eq 6.16')
            else:
                if not proc.mF_list:
                    #C.27
                    logging.info('(i,k)=(g,b), massless, using eq C.27')
                else:
                    #6.52
                    logging.info('(i,k)=(g,b), massive, using eq 6.52')
        #initial fermion
        elif (par1.name != 'g' and par1.initial):
            if not par2.initial:
                if not par2.isMassive:
                    #C.27
                    logging.info('(a,k)=(f,k), massless, using eq C.27')
                else:
                    #6.52
                    logging.info('(a,k)=(f,k), massive, using eq 6.52')
            else:
                #C.27
                    logging.info('(a,b)=(f,b), massless, using eq C.27')
        #initial gluon
        elif (par1.name == 'g' and par1.initial):
            if not par2.initial:
                if not par2.isMassive:
                    #C.27
                    logging.info('(a,k)=(g,k), massless, using eq C.27')
                else:
                    #6.52
                    logging.info('(a,k)=(g,k), massive, using eq 6.52')
            else:
                #C.27
                    logging.info('(a,b)=(g,b), massless, using eq C.27')

print(expressions)


code = '''\
#-
off stats;

S Alfas, pi, eps, CF, CA, Tr, Nfl;
CF denom;
CF I, Mu0, InvGamma, Col, Nu0, Gamm, K;
AutoDeclare I i;\n
'''

code += expressions

code += '''\
id Nu0(i1?) = Col(i1,i1)*(eps^(-2)-pi^2/3)+Gamm(i1)*eps^(-1)+Gamm(i1)+K(i1);\n\n
'''

code += par1_rules

code += '''\
\nargument denom;
{0}
endargument;
id denom(?k) = exp_(?k,-1);
.sort
Print;
B InvGamma,Alfas,pi,Mu0;
.end
'''.format(par1_rules)

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
    eq_dict[eq_name].append(series.coeff(eps**-1))
    eq_dict[eq_name].append(series.coeff(eps**-2))
