# Synthetic test repair before real fitting

C_PRODUCTION_SYNTHETIC_TEST_1.log is preserved: 37 tests, 2 errors. No real fit was attempted.

TEST_BUG: Final thinning fixture used C, but one independently constructed expected RNG still used denied historical role A. Current owner explicitly authorizes C/D role-local thinning and forbids Development reruns. Correct that expected stream to the frozen M1 C seed string; retain every equality/count/order/assertion. This changes no scientific RNG definition and weakens no test.

LOCAL_ENV_BROKEN: Windows sandbox temporary directory creation succeeded but its file/cleanup ACL denied access. Use an explicitly resolved scratch directory inside the writable package work root. All fit, hash and duplicate-attempt assertions remain unchanged. No environment escalation or scientific change is used to mask a fit failure.
