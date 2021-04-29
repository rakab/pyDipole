import subprocess
import logging
import sympy as sy
import re

from pyDipole import Process

logging.getLogger().setLevel(logging.INFO)


proc = Process(['e','ebar'],['t','tbar'])

expressions = ''
par1_rules = ''
par1_defs = 'S '
nu_rules = ''
gamma6_rules = ''

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
L I{0}{1} = -Alfas/(2*pi)*InvGamma(1-eps)*Denom(Col({0},{0}))*Nu0({0})*Col({0},{1})*Mu0({0},{1})^eps;\n
'''.format(id1,id2)

def eq_616(id1,id2):
    global expressions
    expressions += '''\
L I{0}{1} = -Alfas*(4*pi)**eps/(2*pi)*InvGamma(1-eps)*Denom(Col({0},{0}))*Col({0},{1})*(Col({0},{0})*(mu^2*s({0},{1})^-1)^eps*
(Nu616({0},{1})-pi^2/3)+Gamma616({0})+Gamm({0})*log(mu^2*s({0},{1})^-1)+Gamm({0})+K({0}));
'''.format(id1,id2)

def eq_652(id1,id2):
    pass

for par1 in proc.all_particles:
    if not par1.isQCD:
        continue

    par1_defs += 'm{0}, p{0}, '.format(par1.id)

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
                    eq_616(par1.id, par2.id)
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

        #Nu replacement rules
        if (par1.isMassive and par2.isMassive):
            nu_rules += '''\
id Nu616S({0},{1}) = Denom(v({0},{1}))*(eps^-1*log(rho({0},{1}))-
1/4*log(rhon({0},{1},{0})^2)^2-1/4*log(rhon({0},{1},{1})^2)^2-pi^2/6+
log(rho({0},{1}))*log(Qij({0},{1})^2/s({0},{1})));
'''.format(par1.id, par2.id)
        elif (par1.isMassive and not par2.isMassive):
            nu_rules += '''\
id Nu616S({0},{1}) = eps^-2/2+eps^-1/2*log(m({0})^2/s({0},{1}))-
1/4*log(m({0})^2/s({0},{1}))-pi^2/12-1/2*log(m({0})^2/s({0},{1}))*log(s({0},{1})*Qij({0},{1})^-2)-
1/2*log(m({0})^2*Qij({0},{1})^-2)*log(s({0},{1})*Qij({0},{1})^-2);
'''.format(par1.id, par2.id)
        elif (not par1.isMassive and par2.isMassive):
            nu_rules += '''\
id Nu616S({1},{0}) = eps^-2/2+eps^-1/2*log(m({0})^2/s({0},{1}))-
1/4*log(m({0})^2/s({0},{1}))-pi^2/12-1/2*log(m({0})^2/s({0},{1}))*log(s({0},{1})*Qij({0},{1})^-2)-
1/2*log(m({0})^2*Qij({0},{1})^-2)*log(s({0},{1})*Qij({0},{1})^-2);
'''.format(par2.id, par1.id)
        elif (not par1.isMassive and not par2.isMassive):
            nu_rules += '''\
id Nu616S({0},{1}) = eps^-2;
'''.format(par1.id, par2.id)

        #gamma616 replacement rules (singular part only)
        if not par1.isMassive:
            gamma6_rules += 'id Gamma616({0}) = eps^-1*Gamm({0});\n'.format(par1.id)
        else:
            gamma6_rules += 'id Gamma616({0}) = eps^-1*CF;\n'.format(par1.id)

print(expressions)


code = '''\
#-
off stats;

S Alfas, pi, eps, CF, CA, Tr, Nfl, mu;
CF Denom;
CF I,InvGamma, Col, Nu0, Nu616 Gamm, K, Gamma616;
CF Nu616S, Nu616Ns;
CF Mu0, Mu616, log;
CF Qij, s, rho, rhon, v, m;
CF NuSmm, NuSmz, NuSzm;
CF NuNSmm, NuNSmz, NuNSzm;
CF sqrt, mun;
AutoDeclare I i;
'''

par1_defs = par1_defs[:-2]+';\n\n'
code += par1_defs

code += expressions+'\n\n'

code += '''\
id Nu0(i1?) = Col(i1,i1)*(eps^(-2)-pi^2/3)+Gamm(i1)*eps^(-1)+Gamm(i1)+K(i1);
id Nu616(?k) = Nu616Ns(?k) + Nu616S(?k);
\n\n
'''

code += nu_rules

rep_rules = '''\
id rho(i1?,i2?) = sqrt((1-v(i1,i2))*Denom(1+v(i1,i2)));
id rhon(i1?,i2?,i3?) = sqrt((1-v(i1,i2)+2*mun(i1,i2,i3)^2*Denom(1-mun(i1,i2,i1)^2-mun(i1,i2,i2)^2))*
Denom(1+v(i1,i2)+2*mun(i1,i2,i3)^2*Denom(1-mun(i1,i2,i1)^2-mun(i1,i2,i2)^2)));

id v(i1?,i2?) = (s(i1,i2))^(-1)*sqrt((s(i1,i2))^(2)-(4*m(i1)^2*m(i2)^2) );
id mun(i1?,i2?,i3?) = m(i3)*Denom(Qij(i1,i2));
id Qij(i1?,i2?) = sqrt(s(i1,i2) + m(i1)^2 + m(i2)^2);

'''

code += '''\
argument log;
{0}
endargument;

argument Denom;
{0}
endargument;

argument sqrt;
{0}
endargument;

argument log;
argument sqrt;
{0}
endargument;
endargument;

argument log;
argument Denom;
{0}
endargument;
endargument;

argument sqrt;
argument Denom;
{0}
endargument;
endargument;

argument log;
argument sqrt;
argument Denom;
{0}
endargument;
endargument;
endargument;

{0}
\n\n
'''.format(rep_rules)

code += gamma6_rules+'\n\n'

code += par1_rules

code += '''\
\nargument Denom;
{0}
endargument;
id Denom(?k) = exp_(?k,-1);
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
Denom = sy.Function('Denom')


eq_dict = dict()
for eq in form_res:
    eq_name = re.search(r"^(.*)=",eq).group(0)[:-1]
    eq_dict[eq_name] = []
    eq = sy.together(sy.sympify(eq.replace(eq_name+'=','')))
    eq = eq.replace(InvGamma(a_),1/sy.gamma(a_))
    eq = eq.replace(Denom(a_),1/a_)
    series = sy.series(eq,eps,n=0)
    eq_dict[eq_name].append(eq)
    eq_dict[eq_name].append(series.coeff(eps**-1).simplify())
    eq_dict[eq_name].append(series.coeff(eps**-2).simplify())
