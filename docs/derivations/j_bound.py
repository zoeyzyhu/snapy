"""Rough size of the J pieces vs the covariance piece in the x2 energy row, ideal-moist two-component gas.
Pi(e, y) = e * r(y), r = R(y)/cv(y) mass-weighted (H2-He dry: R 3600, cv 9000; H2O vapour: R 461.5, cv 1418),
so Pi_ee = 0 and J = (s2/2) [2 r'(y) e_1 y_1 + e r''(y) y_1^2]. For a mode with u_n1 = m u_n the ratio of
rho u_n J to s2 rho u_n1 h_1 is |(1/2)(2 r' e_1 y_1 + e r'' y_1^2)| / (m |h_1|), h = e + ell + Pi, ell = (u0v - u0d) y.
Assumed (not from the deck): T = 300 K, lapse 2 K/km, vapour y = 0.05 falling to 0 over 10 km
(y_1 = -5e-6 /m), column 50 km so m = pi/50 km, u0v - u0d = 2.5e6 J/kg (latent-heat-like offset) or 0.
Run: python -I j_bound.py"""
import math
Rd, Rv, cvd, cvv = 3600., 461.5, 9000., 1418.
y, T, dT = 0.05, 300., -2e-3
R = lambda y: Rd * (1 - y) + Rv * y
cv = lambda y: cvd * (1 - y) + cvv * y
r = lambda y: R(y) / cv(y)
hh = 1e-6
r1 = (r(y + hh) - r(y - hh)) / (2 * hh)
r2 = (r(y + hh) - 2 * r(y) + r(y - hh)) / hh**2
e = cv(y) * T
y1 = -0.05 / 10e3
e1 = cv(y) * dT + (cvv - cvd) * y1 * T
m = math.pi / 50e3
J_over_s2 = 0.5 * (2 * r1 * e1 * y1 + e * r2 * y1**2)
for dl in (2.5e6, 0.0):
    h1 = e1 * (1 + r(y)) + e * r1 * y1 + dl * y1
    print(f'offset gradient {dl:.1e}: J/s2 = {J_over_s2:.3e}  h_1 = {h1:.3e}  ratio rho u J / (s2 rho u_1 h_1) = {abs(J_over_s2) / (m * abs(h1)):.3e}')
