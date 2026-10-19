# Prospective primary and five secondary comparisons

Target:heldout BO animals under the fixed Development-selected model/λ policy and newly C-fitted mouse-local states. Primary d_m=LL(B4)−LL(B1),each mouse summed joint logscore difference divided by its actual valid scored unit-bin count;then equal-mouse mean. Report all7absolute model scores andall6gains,counts/exposure/denominators. No unit/bin/presentation/probe pseudoreplication.

Primary two-sided mouse sign-flip test at.05 withpositive directional interpretation. Five secondaries in one Holm5family: B4−B2,B4−B3,D−B4,C−B4,D−S,two-sided. All raw/adjusted p andeffects reported regardless of primary outcome;any narrow positive secondary category requires the primary positive gate. This prospective serial gate prevents opportunistic positive secondary families. It is not confirmation of biology.

Sortnumericmouse IDs. Test statistic absolute mean;exact2^n signs for n≤16,otherwise99999PCG64sign arrays seed16041 using rng.integers(0,2,size=(99999,n))*2−1,shared across6effects;MCp=(1+#absreference≥absobserved)/100000,exact p=exactfraction. Validity requires independent null-symmetric animal differences;not guaranteed by observational prediction or protocol allocation. Bootstrap10000whole-mouse resamples,rng.integers(0,n,size=(10000,n)),PCG64seed16042,shared indices;95%percentileCI,np.quantile(method='linear'). Assumes exchangeable BOtarget animals conditional source/admission,notrandom population sampling. Report source/batch/genotype/sex/probe concentration,LOMO eachmouse andBO/FCDev diagnostics. No independent-lab replication.

Meaningful-effect planning targets:primaryΔ=.002nats/20msunit-bin,secondaryΔ=.001each. These are prospective interpretability targets,not biological constants or pilot-estimated P16effects (primary corresponds.096nats per complete8-unit6-bin presentation). Actual meaningful biological interpretation remains limited. Do not use arbitrary absolute CI-width PASS. Report fullwidth/precision and assess whether own95%CI lower exceeds registeredΔ. The earlier superseded draft .004width rule belongs to an unexecuted old contract and remains archived;the latest owner explicitly requires justified precision design. No neural outcome motivated this prospective redesign.

PRECISION_POWER_SCENARIOS has100 hypothetical Gaussian-mouse scenarios,n6/12/18/24/27,SD.002/.005/.01/.02,means0/.001/.002/.005/.01. Width=2*t_.975,n−1*SD/sqrt(n),noncentral-t power by direct normal/chi-square integration (1e−11absolute/relative tolerance),.05andconservative.05/5. These are not empirical P16 variance,actual sign-flip/bootstrap power or a confirmation guarantee. E.g.27mice,SD.005,mean.002 gives about.52two-sided power at.05;cohort27alone does not establish adequate power. Entire track is therefore prospectively descriptive/exploratory evenif significant.

|Contrast|Own effect/interval|p rule|LOMO|Coverage/joint prerequisites|
|---|---|---|---|---|
|B4−B1|mean≥.002andCI lower>.002|primaryp≤.05|everymean>0|≥12Final,allmainhistoryguardsbelow|
|B4−B2|mean≥.001andCI lower>.001|Holm5≤.05|everymean>0|samecoverage+primarypositive|
|B4−B3|mean≥.001andCI lower>.001|Holm5≤.05|everymean>0|samecoverage+primarypositive|
|D−B4|mean≥.001andCI lower>.001|Holm5≤.05|everymean>0|same+owndirectionguardsbelow|
|C−B4|mean≥.001andCI lower>.001|Holm5≤.05|everymean>0|same+owndirectionguardsbelow|
|D−S|mean≥.001andCI lower>.001|Holm5≤.05|everymean>0|same+own/N3guardbelow|

Mainhistory jointguards:mandatoryS01/S02/S04/S06/S07/S09available with≥12Final andmeanB4−B1>0;N1≥12andobservedmaingain>95threference-meanquantile. D/Cowncontrast mean>0 inthese samepanels;D−S additionallyobservedmean>95thN3reference-meanquantile≥12mice. Referencequantiles methodlinear,descriptive/approximate only;not exact conditional p. Optional pupil/strictQC/anatomy absence withholds respective robustness claim. Noforcedpositivecontrol.

Deterministic verdict precedence:mandatorysource/implementation/numericalfailure =>INCONCLUSIVE_REQUIRED_GATEandSTOP;Final6–11 =>FALLBACK_DESCRIPTIVE_COVERAGE_FAIL regardless of p,originalmain12gateFAIL retained;below6STOPbeforeD;otherwiseownmean≤0=>NEGATIVE_DIRECTION;otherwiseallown+jointconditions=>HELDOUT_DESCRIPTIVE_POSITIVE;otherwiseMIXED_UNSUPPORTED. NoVALIDATEDorphysicalstate/causal category. Nonsignificance is not equivalence or no biological effect.

FutureDevminimum14including≥3BO/≥10FC;Finalmain12. Floors and precision goals are design capacity/coverage limits,not empirical power. No post-result reroll,hypothesis/threshold change,extra model selection or second D. Allnegative/mixed/unavailable findings must remain in eventual manuscript.

The planning table also reports the hypothetical probability that a Gaussian-animal t-interval lower bound exceeds .002 or .001, using the same defining normal/chi-square integration. This directly illustrates the meaningful-effect interval criterion: at a true mean exactly equal to the target, that probability is .025. It is not the actual bootstrap acceptance probability and does not establish power for the entire conjunction of future gates.

Numerical tie handling uses math.fsum for each observed and signed mouse mean in the same numeric mouse order. No favorable tolerance or post-result p-value adjustment is introduced. Bootstrap arithmetic and quantile method remain as specified.
