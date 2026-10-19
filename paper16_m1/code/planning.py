"""Hypothetical Gaussian animal-effect scenarios; no empirical neural inputs."""
import csv,io
from scipy.stats import t,chi2
from scipy.special import ndtr
from scipy.integrate import quad

def hypothetical_power(n,sd,delta,alpha):
 df=n-1;critical=t.ppf(1-alpha/2,df);nc=delta*n**.5/sd
 # Integrate the defining independent normal/chi-square representation.
 return quad(lambda v:(ndtr(nc-critical*(v/df)**.5)+ndtr(-nc-critical*(v/df)**.5))*chi2.pdf(v,df),0,float('inf'),epsabs=1e-11,epsrel=1e-11)[0]

def hypothetical_interval_resolution(n,sd,delta,meaningful):
 df=n-1;critical=t.ppf(.975,df);nc=(delta-meaningful)*n**.5/sd
 return quad(lambda v:ndtr(nc-critical*(v/df)**.5)*chi2.pdf(v,df),0,float('inf'),epsabs=1e-11,epsrel=1e-11)[0]

def table():
 out=io.StringIO(newline='');w=csv.writer(out,lineterminator='\n')
 w.writerow(['n_mice','hypothetical_mouse_SD','hypothetical_mean','hypothetical_t95_full_width','hypothetical_two_sided_power_alpha_05','hypothetical_power_bonferroni_5','hypothetical_probability_tCI_lower_gt_primary_002','hypothetical_probability_tCI_lower_gt_secondary_001'])
 for n in [6,12,18,24,27]:
  for sd in [.002,.005,.01,.02]:
   for delta in [0,.001,.002,.005,.01]:
    power=lambda alpha:hypothetical_power(n,sd,delta,alpha)
    w.writerow([n,sd,delta,format(2*t.ppf(.975,n-1)*sd/n**.5,'.12g'),format(power(.05),'.12g'),format(power(.05/5),'.12g'),format(hypothetical_interval_resolution(n,sd,delta,.002),'.12g'),format(hypothetical_interval_resolution(n,sd,delta,.001),'.12g')])
 return out.getvalue()

if __name__=='__main__':print(table(),end='')
