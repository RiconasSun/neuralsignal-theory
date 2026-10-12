# Supplementary Methods and Results

This supplement belongs to P11-MANUSCRIPT-CLOSEOUT-1, not original R3. All results are copied from exposed development evidence; independent validation was not executed.

## S1. Full Configuration Grid

All 57 configurations are retained below. F = family, K/d = number of states/dimension, L = extra history lags, P = patient-weighted mean nominal coefficients INCLUDING shared offsets. Scores are development nats/unit-bin. Baseline names identify their distinct covariate sets. Full precision and training-objective seed policy remain in all57configurations.csv.

| Family | Ridge | K/d | L | P total | Development score |
| --- | --- | --- | --- | --- | --- |
| stationary | 0.0 | - | - | 23.389 | -0.541291238 |
| history | 0.001 | - | - | 140.333 | -0.541148902 |
| history | 0.01 | - | - | 140.333 | -0.625239693 |
| history | 0.1 | - | - | 140.333 | -0.863300484 |
| history | 1.0 | - | - | 140.333 | -1.036731430 |
| event | 0.001 | - | - | 163.722 | -0.545506185 |
| event | 0.01 | - | - | 163.722 | -0.602585421 |
| event | 0.1 | - | - | 163.722 | -0.813795828 |
| event | 1.0 | - | - | 163.722 | -1.021970414 |
| drift | 0.001 | - | - | 46.778 | -0.541583493 |
| drift | 0.01 | - | - | 46.778 | -0.579602241 |
| drift | 0.1 | - | - | 46.778 | -0.802580248 |
| drift | 1.0 | - | - | 46.778 | -1.023682681 |
| combined | 0.001 | - | - | 304.056 | -0.534921315 |
| combined | 0.01 | - | - | 304.056 | -0.568088596 |
| combined | 0.1 | - | - | 304.056 | -0.760691587 |
| combined | 1.0 | - | - | 304.056 | -0.995955080 |
| population | 0.001 | - | - | 3841.370 | -0.541962913 |
| population | 0.01 | - | - | 3841.370 | -0.554542315 |
| population | 0.1 | - | - | 3841.370 | -0.662697017 |
| population | 1.0 | - | - | 3841.370 | -0.910859720 |
| discrete | 0.001 | 2 | 0 | 353.833 | -0.518112435 |
| discrete | 0.01 | 2 | 0 | 353.833 | -0.547175973 |
| discrete | 0.1 | 2 | 0 | 353.833 | -0.565546349 |
| discrete | 1.0 | 2 | 0 | 353.833 | -0.567812260 |
| discrete | 0.001 | 4 | 0 | 412.611 | -0.515393923 |
| discrete | 0.01 | 4 | 0 | 412.611 | -0.554497068 |
| discrete | 0.1 | 4 | 0 | 412.611 | -0.566760152 |
| discrete | 1.0 | 4 | 0 | 412.611 | -0.567949724 |
| continuous | 0.001 | 1 | 0 | 357.833 | -0.550125007 |
| continuous | 0.01 | 1 | 0 | 357.833 | -0.551795924 |
| continuous | 0.1 | 1 | 0 | 357.833 | -0.568088507 |
| continuous | 1.0 | 1 | 0 | 357.833 | -0.568088596 |
| continuous | 0.001 | 2 | 0 | 413.611 | -0.540875774 |
| continuous | 0.01 | 2 | 0 | 413.611 | -0.546674737 |
| continuous | 0.1 | 2 | 0 | 413.611 | -0.568087082 |
| continuous | 1.0 | 2 | 0 | 413.611 | -0.568088596 |
| continuous | 0.001 | 4 | 0 | 531.167 | -0.537378019 |
| continuous | 0.01 | 4 | 0 | 531.167 | -0.543501399 |
| continuous | 0.1 | 4 | 0 | 531.167 | -0.568087527 |
| continuous | 1.0 | 4 | 0 | 531.167 | -0.568088596 |
| hybrid | 0.001 | 2 | 1 | 400.611 | -0.516518920 |
| hybrid | 0.01 | 2 | 1 | 400.611 | -0.546237251 |
| hybrid | 0.1 | 2 | 1 | 400.611 | -0.565489020 |
| hybrid | 1.0 | 2 | 1 | 400.611 | -0.567808203 |
| hybrid | 0.001 | 2 | 5 | 587.722 | -0.515997654 |
| hybrid | 0.01 | 2 | 5 | 587.722 | -0.545279771 |
| hybrid | 0.1 | 2 | 5 | 587.722 | -0.565413767 |
| hybrid | 1.0 | 2 | 5 | 587.722 | -0.567805368 |
| hybrid | 0.001 | 4 | 1 | 506.167 | -0.514453621 |
| hybrid | 0.01 | 4 | 1 | 506.167 | -0.553912039 |
| hybrid | 0.1 | 4 | 1 | 506.167 | -0.566732507 |
| hybrid | 1.0 | 4 | 1 | 506.167 | -0.567948134 |
| hybrid | 0.001 | 4 | 5 | 880.389 | -0.514053175 |
| hybrid | 0.01 | 4 | 5 | 880.389 | -0.552932337 |
| hybrid | 0.1 | 4 | 5 | 880.389 | -0.566703689 |
| hybrid | 1.0 | 4 | 5 | 880.389 | -0.567947120 |

## S2. Complete Patient Scores

The four columns reproduce the original selected/reference means. Baseline is combined ridge0.001, not the stationary one-SEbaseline. No model selection is repeated.

| Patient | Baseline | Discrete | Continuous | Hybrid |
| --- | --- | --- | --- | --- |
| sub-01 | -0.440993096 | -0.459340501 | -0.483732157 | -0.457733319 |
| sub-02 | -0.577737752 | -0.589624930 | -0.601118745 | -0.587867109 |
| sub-03 | -0.674959645 | -0.680181759 | -0.689338536 | -0.679404843 |
| sub-04 | -0.663997952 | -0.688733226 | -0.714915792 | -0.688245846 |
| sub-05 | -0.368052066 | -0.362101626 | -0.373153888 | -0.361910558 |
| sub-06 | -0.464314056 | -0.486346416 | -0.522423518 | -0.485862444 |
| sub-07 | -0.434149053 | -0.446110056 | -0.459398996 | -0.446095589 |
| sub-08 | -0.526356200 | -0.541865905 | -0.587442574 | -0.540726125 |
| sub-09 | -0.663732013 | -0.670279340 | -0.681273162 | -0.668289428 |

## S3. Full Patient Paired Effects

| Patient | D-C | D-H | C-H | D-B | C-B | H-B |
| --- | --- | --- | --- | --- | --- | --- |
| sub-01 | +0.024392 | -0.001607 | -0.025999 | -0.018347 | -0.042739 | -0.016740 |
| sub-02 | +0.011494 | -0.001758 | -0.013252 | -0.011887 | -0.023381 | -0.010129 |
| sub-03 | +0.009157 | -0.000777 | -0.009934 | -0.005222 | -0.014379 | -0.004445 |
| sub-04 | +0.026183 | -0.000487 | -0.026670 | -0.024735 | -0.050918 | -0.024248 |
| sub-05 | +0.011052 | -0.000191 | -0.011243 | +0.005950 | -0.005102 | +0.006142 |
| sub-06 | +0.036077 | -0.000484 | -0.036561 | -0.022032 | -0.058109 | -0.021548 |
| sub-07 | +0.013289 | -0.000014 | -0.013303 | -0.011961 | -0.025250 | -0.011947 |
| sub-08 | +0.045577 | -0.001140 | -0.046716 | -0.015510 | -0.061086 | -0.014370 |
| sub-09 | +0.010994 | -0.001990 | -0.012984 | -0.006547 | -0.017541 | -0.004557 |

## S4. Saved Population Intervals and Tests

| Contrast | Mean effect | 95% exploratory CI | Raw sign-flip p | Holm-six p | Patients |
| --- | --- | --- | --- | --- | --- |
| discrete minus continuous | +0.020913 | [+0.013508, +0.029372] | 0.00390625 | 0.02343750 | 9 |
| discrete minus hybrid | -0.000939 | [-0.001374, -0.000497] | 0.00390625 | 0.02343750 | 9 |
| continuous minus hybrid | -0.021851 | [-0.030288, -0.014437] | 0.00390625 | 0.02343750 | 9 |
| discrete minus baseline | -0.012255 | [-0.017749, -0.006137] | 0.01171875 | 0.02343750 | 9 |
| continuous minus baseline | -0.033167 | [-0.045727, -0.020913] | 0.00390625 | 0.02343750 | 9 |
| hybrid minus baseline | -0.011316 | [-0.016862, -0.005293] | 0.01562500 | 0.02343750 | 9 |

All six contrasts use n=9patients;10000paired patient bootstrap replicas and512exact sign flips. Holm-six was applied once to the saved contrast set. These intervals condition on the selected configurations and do not repeat selection; they are not selection-adjusted confirmatory inference.

## S5. Conditional Patient Intervals

36descriptive intervals resample whole trials within each retained session and average sessions equally. They condition on the patient and are not independent-population CIs. No new resampling is performed.

| Family | Patient | Mean | Saved 95% CI |
| --- | --- | --- | --- |
| baseline | sub-01 | -0.440993096 | [-0.476683, -0.405906] |
| baseline | sub-02 | -0.577737752 | [-0.596863, -0.557963] |
| baseline | sub-03 | -0.674959645 | [-0.691574, -0.659626] |
| baseline | sub-04 | -0.663997952 | [-0.677649, -0.651370] |
| baseline | sub-05 | -0.368052066 | [-0.436361, -0.313315] |
| baseline | sub-06 | -0.464314056 | [-0.484248, -0.445650] |
| baseline | sub-07 | -0.434149053 | [-0.449913, -0.418161] |
| baseline | sub-08 | -0.526356200 | [-0.568811, -0.487928] |
| baseline | sub-09 | -0.663732013 | [-0.679164, -0.647392] |
| continuous | sub-01 | -0.483732157 | [-0.512114, -0.456172] |
| continuous | sub-02 | -0.601118745 | [-0.620371, -0.581538] |
| continuous | sub-03 | -0.689338536 | [-0.703979, -0.676375] |
| continuous | sub-04 | -0.714915792 | [-0.724262, -0.705987] |
| continuous | sub-05 | -0.373153888 | [-0.433328, -0.323755] |
| continuous | sub-06 | -0.522423518 | [-0.536285, -0.509524] |
| continuous | sub-07 | -0.459398996 | [-0.472387, -0.446283] |
| continuous | sub-08 | -0.587442574 | [-0.618408, -0.560329] |
| continuous | sub-09 | -0.681273162 | [-0.695793, -0.665585] |
| discrete | sub-01 | -0.459340501 | [-0.489906, -0.429578] |
| discrete | sub-02 | -0.589624930 | [-0.610321, -0.568663] |
| discrete | sub-03 | -0.680181759 | [-0.695051, -0.666530] |
| discrete | sub-04 | -0.688733226 | [-0.698742, -0.679140] |
| discrete | sub-05 | -0.362101626 | [-0.427541, -0.309541] |
| discrete | sub-06 | -0.486346416 | [-0.501101, -0.472646] |
| discrete | sub-07 | -0.446110056 | [-0.460011, -0.432108] |
| discrete | sub-08 | -0.541865905 | [-0.573074, -0.514457] |
| discrete | sub-09 | -0.670279340 | [-0.685641, -0.654020] |
| hybrid | sub-01 | -0.457733319 | [-0.488066, -0.428214] |
| hybrid | sub-02 | -0.587867109 | [-0.608198, -0.567178] |
| hybrid | sub-03 | -0.679404843 | [-0.694309, -0.665742] |
| hybrid | sub-04 | -0.688245846 | [-0.698261, -0.678690] |
| hybrid | sub-05 | -0.361910558 | [-0.427441, -0.309321] |
| hybrid | sub-06 | -0.485862444 | [-0.500577, -0.472199] |
| hybrid | sub-07 | -0.446095589 | [-0.459994, -0.432101] |
| hybrid | sub-08 | -0.540726125 | [-0.571339, -0.513724] |
| hybrid | sub-09 | -0.668289428 | [-0.683343, -0.652305] |

## S6. Conditional Session Intervals

92descriptive whole-trial intervals below;23sessions per each of four selected/reference models. Trials, sessions and neurons are not independent patients.

| Family | Session | Mean | Saved 95% CI |
| --- | --- | --- | --- |
| baseline | sub-01/ses-01 | -0.541013497 | [-0.583420, -0.492624] |
| baseline | sub-01/ses-02 | -0.340972695 | [-0.396956, -0.288446] |
| baseline | sub-02/ses-01 | -0.592942966 | [-0.633432, -0.554199] |
| baseline | sub-02/ses-02 | -0.492263428 | [-0.514302, -0.472599] |
| baseline | sub-02/ses-03 | -0.547654632 | [-0.562741, -0.536419] |
| baseline | sub-02/ses-04 | -0.678089983 | [-0.736117, -0.616202] |
| baseline | sub-03/ses-01 | -0.612153341 | [-0.627020, -0.595624] |
| baseline | sub-03/ses-02 | -0.733023695 | [-0.778830, -0.694984] |
| baseline | sub-03/ses-03 | -0.679701898 | [-0.697448, -0.662140] |
| baseline | sub-04/ses-01 | -0.677185977 | [-0.698957, -0.657411] |
| baseline | sub-04/ses-02 | -0.650809926 | [-0.667773, -0.635656] |
| baseline | sub-05/ses-01 | -0.368052066 | [-0.436361, -0.313315] |
| baseline | sub-06/ses-01 | -0.484599992 | [-0.512796, -0.455967] |
| baseline | sub-06/ses-02 | -0.462582698 | [-0.494020, -0.436226] |
| baseline | sub-06/ses-03 | -0.445759477 | [-0.489582, -0.408748] |
| baseline | sub-07/ses-02 | -0.522817580 | [-0.542060, -0.501638] |
| baseline | sub-07/ses-03 | -0.345480527 | [-0.369596, -0.320330] |
| baseline | sub-08/ses-02 | -0.458177576 | [-0.616394, -0.317641] |
| baseline | sub-08/ses-03 | -0.531856766 | [-0.564862, -0.497467] |
| baseline | sub-08/ses-04 | -0.502423399 | [-0.527969, -0.476558] |
| baseline | sub-08/ses-05 | -0.612967059 | [-0.662256, -0.563678] |
| baseline | sub-09/ses-01 | -0.680480461 | [-0.702302, -0.655734] |
| baseline | sub-09/ses-02 | -0.646983566 | [-0.667242, -0.625653] |
| continuous | sub-01/ses-01 | -0.578898598 | [-0.611526, -0.541512] |
| continuous | sub-01/ses-02 | -0.388565717 | [-0.433376, -0.346277] |
| continuous | sub-02/ses-01 | -0.611755865 | [-0.647986, -0.577410] |
| continuous | sub-02/ses-02 | -0.529628792 | [-0.546929, -0.514999] |
| continuous | sub-02/ses-03 | -0.573200002 | [-0.588584, -0.563312] |
| continuous | sub-02/ses-04 | -0.689890319 | [-0.751147, -0.624251] |
| continuous | sub-03/ses-01 | -0.621186218 | [-0.632888, -0.607756] |
| continuous | sub-03/ses-02 | -0.748974527 | [-0.789665, -0.717323] |
| continuous | sub-03/ses-03 | -0.697854862 | [-0.714014, -0.682445] |
| continuous | sub-04/ses-01 | -0.724936266 | [-0.738931, -0.711603] |
| continuous | sub-04/ses-02 | -0.704895318 | [-0.717724, -0.693539] |
| continuous | sub-05/ses-01 | -0.373153888 | [-0.433328, -0.323755] |
| continuous | sub-06/ses-01 | -0.535883909 | [-0.555643, -0.516041] |
| continuous | sub-06/ses-02 | -0.525411686 | [-0.546610, -0.506791] |
| continuous | sub-06/ses-03 | -0.505974958 | [-0.535793, -0.479953] |
| continuous | sub-07/ses-02 | -0.557571169 | [-0.574323, -0.540823] |
| continuous | sub-07/ses-03 | -0.361226824 | [-0.380957, -0.341005] |
| continuous | sub-08/ses-02 | -0.500998873 | [-0.617986, -0.399601] |
| continuous | sub-08/ses-03 | -0.580904004 | [-0.602333, -0.557817] |
| continuous | sub-08/ses-04 | -0.585944582 | [-0.602735, -0.569014] |
| continuous | sub-08/ses-05 | -0.681922838 | [-0.713763, -0.650638] |
| continuous | sub-09/ses-01 | -0.693230365 | [-0.714540, -0.669619] |
| continuous | sub-09/ses-02 | -0.669315958 | [-0.688043, -0.649390] |
| discrete | sub-01/ses-01 | -0.555756859 | [-0.591329, -0.514791] |
| discrete | sub-01/ses-02 | -0.362924144 | [-0.411315, -0.317763] |
| discrete | sub-02/ses-01 | -0.600462536 | [-0.638088, -0.564662] |
| discrete | sub-02/ses-02 | -0.503937003 | [-0.522998, -0.487268] |
| discrete | sub-02/ses-03 | -0.560153144 | [-0.576618, -0.549365] |
| discrete | sub-02/ses-04 | -0.693947038 | [-0.760284, -0.623122] |
| discrete | sub-03/ses-01 | -0.615714977 | [-0.628512, -0.601165] |
| discrete | sub-03/ses-02 | -0.736715690 | [-0.777103, -0.703433] |
| discrete | sub-03/ses-03 | -0.688114611 | [-0.705067, -0.671732] |
| discrete | sub-04/ses-01 | -0.699375097 | [-0.715147, -0.684437] |
| discrete | sub-04/ses-02 | -0.678091356 | [-0.691291, -0.666387] |
| discrete | sub-05/ses-01 | -0.362101626 | [-0.427541, -0.309541] |
| discrete | sub-06/ses-01 | -0.499967286 | [-0.521142, -0.478647] |
| discrete | sub-06/ses-02 | -0.489014248 | [-0.510776, -0.469881] |
| discrete | sub-06/ses-03 | -0.470057713 | [-0.502578, -0.441645] |
| discrete | sub-07/ses-02 | -0.540346851 | [-0.557678, -0.522319] |
| discrete | sub-07/ses-03 | -0.351873260 | [-0.373134, -0.329858] |
| discrete | sub-08/ses-02 | -0.441827745 | [-0.557882, -0.341781] |
| discrete | sub-08/ses-03 | -0.548614077 | [-0.572235, -0.523410] |
| discrete | sub-08/ses-04 | -0.539610343 | [-0.558073, -0.520988] |
| discrete | sub-08/ses-05 | -0.637411454 | [-0.672027, -0.603171] |
| discrete | sub-09/ses-01 | -0.684412478 | [-0.706903, -0.659539] |
| discrete | sub-09/ses-02 | -0.656146201 | [-0.675635, -0.635311] |
| hybrid | sub-01/ses-01 | -0.553268632 | [-0.588683, -0.512798] |
| hybrid | sub-01/ses-02 | -0.362198005 | [-0.410356, -0.317264] |
| hybrid | sub-02/ses-01 | -0.599107057 | [-0.636735, -0.563309] |
| hybrid | sub-02/ses-02 | -0.503762973 | [-0.522916, -0.487010] |
| hybrid | sub-02/ses-03 | -0.558294882 | [-0.573978, -0.547896] |
| hybrid | sub-02/ses-04 | -0.690303526 | [-0.755297, -0.621373] |
| hybrid | sub-03/ses-01 | -0.615574033 | [-0.628355, -0.601048] |
| hybrid | sub-03/ses-02 | -0.735487616 | [-0.775919, -0.702279] |
| hybrid | sub-03/ses-03 | -0.687152879 | [-0.703954, -0.670803] |
| hybrid | sub-04/ses-01 | -0.699010213 | [-0.714660, -0.684146] |
| hybrid | sub-04/ses-02 | -0.677481479 | [-0.690655, -0.665778] |
| hybrid | sub-05/ses-01 | -0.361910558 | [-0.427441, -0.309321] |
| hybrid | sub-06/ses-01 | -0.499444488 | [-0.520638, -0.478253] |
| hybrid | sub-06/ses-02 | -0.488467315 | [-0.510104, -0.469404] |
| hybrid | sub-06/ses-03 | -0.469675527 | [-0.502054, -0.441308] |
| hybrid | sub-07/ses-02 | -0.540320781 | [-0.557641, -0.522344] |
| hybrid | sub-07/ses-03 | -0.351870397 | [-0.373125, -0.329866] |
| hybrid | sub-08/ses-02 | -0.439543137 | [-0.553273, -0.341692] |
| hybrid | sub-08/ses-03 | -0.547714650 | [-0.571158, -0.522684] |
| hybrid | sub-08/ses-04 | -0.539218376 | [-0.557597, -0.520642] |
| hybrid | sub-08/ses-05 | -0.636428337 | [-0.670797, -0.602416] |
| hybrid | sub-09/ses-01 | -0.682392476 | [-0.704400, -0.657995] |
| hybrid | sub-09/ses-02 | -0.654186381 | [-0.673403, -0.633676] |

## S7. Complete Session Coverage

| Session | Units | Train | Development |
| --- | --- | --- | --- |
| sub-01/ses-01 | 25 | 28 | 9 |
| sub-01/ses-02 | 18 | 28 | 9 |
| sub-02/ses-01 | 17 | 28 | 9 |
| sub-02/ses-02 | 23 | 25 | 8 |
| sub-02/ses-03 | 19 | 25 | 8 |
| sub-02/ses-04 | 7 | 27 | 9 |
| sub-03/ses-01 | 15 | 26 | 8 |
| sub-03/ses-02 | 16 | 24 | 8 |
| sub-03/ses-03 | 16 | 30 | 10 |
| sub-04/ses-01 | 38 | 28 | 9 |
| sub-04/ses-02 | 37 | 28 | 9 |
| sub-05/ses-01 | 6 | 25 | 8 |
| sub-06/ses-01 | 31 | 29 | 9 |
| sub-06/ses-02 | 34 | 30 | 10 |
| sub-06/ses-03 | 35 | 28 | 9 |
| sub-07/ses-02 | 19 | 24 | 8 |
| sub-07/ses-03 | 6 | 29 | 9 |
| sub-08/ses-02 | 34 | 25 | 8 |
| sub-08/ses-03 | 40 | 27 | 9 |
| sub-08/ses-04 | 51 | 27 | 9 |
| sub-08/ses-05 | 65 | 29 | 9 |
| sub-09/ses-01 | 20 | 27 | 9 |
| sub-09/ses-02 | 20 | 25 | 8 |

## S8. Optimizer Diagnostics and Computational Cost

All 3887records remain in optimizer_diagnostics.csv, including all seeds. One-iteration records:117; largest recorded gradient infinity norm:0.0565088103506. First-unit design rank is not joint rank. Convergence does not mean small gradients or global optima.

| Termination message | Recorded fits |
| --- | --- |
| CONVERGENCE: RELATIVE REDUCTION OF F <= FACTR*EPSMCH | 3319 |
| CONVERGENCE: NORM OF PROJECTED GRADIENT <= PGTOL | 545 |
| Exact constant-rate maximum likelihood | 23 |

The recorded fit_seconds=805.5225947985891 is cumulative training timing in the original environment. It is not a new speed benchmark. Penalization, bounds[-8,8],500iterations,ftol/gtol1e-5 are mathematical parts of the compared pipelines. Nominal coefficient budgets are unequal; the frontier reports that inequality rather than asserting exact complexity matching.

## S9. Numerical, Null and External Failures

OriginalM4/NUM1/NUM2/NUM3 failures are immutable. NUM2 failed a controlled proposal oracle before real data. NUM3 independent quadrature consistency is empirical; registered worst-replica-plus1.96SD-and-reference-sensitivity criterion failed at131072particles. None establishes that all numerical evaluators must fail. These are controlled algorithmic observations, not hippocampal experiments.

The null plan required200replicas each of3types. Eight full count-permutation cohort replicas and2896savednullfits (including partial work) were preserved. No partial-null pvalue or completed full-null claim appears. Circular/task-event suites and external final validation were not executed. DANDI5unknown-support sessions were not deleted to pass. Subsequent OSF/Figshare admission audits were inconclusive.

## S10. Evidence Traceability and Scope

Each of the seven figure sidecars lists source paths andSHA256 plus render-code hash. build_inputs.json and claim_map.json bind the document to frozen sources. Saved-only reproduction regenerates tables/figures/document formatting; it neither refits models nor reproduces unexecuted controls/external evaluation. Author contributions/funding/competing-interest/submission declarations remain unprovided, explicitly disclosed in the main paper.

## Supplementary References

1. Boran E, Fedele T, Steiner A, Hilfiker P, Stieglitz L, Grunwald T, Sarnthein J. (2020). Dataset of human medial temporal lobe neurons, scalp and intracranial EEG during a verbal working memory task. Scientific Data 7, 30. [https://doi.org/10.1038/s41597-020-0364-3](https://doi.org/10.1038/s41597-020-0364-3)

2. Boran E et al. (2019). Persistent hippocampal neural firing and hippocampal-cortical coupling predict verbal working memory load. Science Advances 5(3), eaav3687. [https://doi.org/10.1126/sciadv.aav3687](https://doi.org/10.1126/sciadv.aav3687)

3. Dimakopoulos V, Megevand P, Stieglitz LH, Imbach L, Sarnthein J. (2022). Information flows from hippocampus to auditory cortex during replay of verbal working memory items. eLife 11, e78677. [https://doi.org/10.7554/eLife.78677](https://doi.org/10.7554/eLife.78677)

4. Niediek J, Bostrom J, Elger CE, Mormann F. (2016). Reliable Analysis of Single-Unit Recordings from the Human Brain under Noisy Conditions: Tracking Neurons over Hours. PLoS ONE 11, e0166598. [https://doi.org/10.1371/journal.pone.0166598](https://doi.org/10.1371/journal.pone.0166598)

5. Chandravadia N et al. (2020). A NWB-based dataset and processing pipeline of human single-neuron activity during a declarative memory task. Scientific Data. [https://doi.org/10.1038/s41597-020-0415-9](https://doi.org/10.1038/s41597-020-0415-9)

6. Cao R, Brunner P, Brandmeir NJ, Willie JT, Wang S. (2025). A human single-neuron dataset for object recognition. Scientific Data 12, 79. [https://doi.org/10.1038/s41597-024-04265-1](https://doi.org/10.1038/s41597-024-04265-1)

7. Kolibius LD et al. (2023). Hippocampal neurons code individual episodic memories in humans. Nature Human Behaviour 7, 1968-1979. [https://doi.org/10.1038/s41562-023-01706-6](https://doi.org/10.1038/s41562-023-01706-6)

8. NEURALSIGNAL INSTITUTE. (2026). P11-v2 frozen predictive implementations and exploratory evidence. Repository snapshot 33dc10db016d69b656dd2491be041b1f6d15826c. Internal code/evidence record, not a peer-reviewed validation. [https://github.com/RiconasSun/neuralsignal-theory/tree/33dc10db016d69b656dd2491be041b1f6d15826c/paper11_v2](https://github.com/RiconasSun/neuralsignal-theory/tree/33dc10db016d69b656dd2491be041b1f6d15826c/paper11_v2)
