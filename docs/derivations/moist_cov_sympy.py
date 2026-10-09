"""Independent symbolic check of the O(dx1^2) face-average gaps of the x2 (transverse) fluxes for a
general EOS p = rho * Pi(e, y1, y2) with species energy offsets (W->I adds sum_n y_n u0_n).

Face of an x2 face spans one x1 cell, zeta in [-dx1/2, dx1/2]. The scheme evaluates F(Ubar), Ubar the x1
average of the conserved state U; the exact flux is <F(U)>. With <zeta^2> = dx1^2/12 =: s2 and the first-order
term vanishing exactly when expanding about Ubar,
    gap = <F(U)> - F(Ubar) = (s2/2) * U_1^T F_UU U_1 + O(dx1^4),
where U_1 = dU/dx1. Conserved U = (rho, m_n, m_t, E, Y1, Y2) with m = rho u, Y_k = rho y_k,
E = rho (e + ell(y)) + rho |v|^2 / 2, ell = u01 y1 + u02 y2 (the W->I offset), and the scheme recovers
e = E/rho - |m|^2/(2 rho^2) - ell(Y/rho), y = Y/rho. Fluxes along x2 (normal velocity u_n):
mass m_n; normal momentum m_n^2/rho + p; transverse momentum m_n m_t/rho; energy (E + p) m_n/rho;
tracer Y_k m_n/rho.
Everything is evaluated pointwise: P = primitive values, dP = their x1 derivatives (plain symbols).
Run: python -I moist_cov_sympy.py   (prints each gap, the comparison with the claims, and PASS/FAIL lines)
"""
import sympy as sp

rho, un, ut, e, y1, y2 = sp.symbols('rho u_n u_t e y1 y2', real=True)
drho, dun, dut, de, dy1, dy2 = sp.symbols('rho_1 u_n1 u_t1 e_1 y1_1 y2_1', real=True)
u01, u02, s2 = sp.symbols('u01 u02 s2', real=True)
R, Mn, Mt, E, Y1, Y2 = sp.symbols('R M_n M_t E Y1 Y2', real=True)
Pi = sp.Function('Pi')
P = [rho, un, ut, e, y1, y2]
dP = [drho, dun, dut, de, dy1, dy2]
Usym = [R, Mn, Mt, E, Y1, Y2]

ell = lambda a, b: u01 * a + u02 * b
# conserved state as a function of primitives
Uofp = {R: rho, Mn: rho * un, Mt: rho * ut, E: rho * (e + ell(y1, y2)) + rho * (un**2 + ut**2) / 2,
        Y1: rho * y1, Y2: rho * y2}
U1 = [sum(sp.diff(Uofp[u], p) * d for p, d in zip(P, dP)) for u in Usym]   # dU/dx1

# Pi derivatives at the point (e, y1, y2), as plain symbols: Pi, Pi_e, Pi_1, Pi_2, Pi_ee, Pi_e1, ...
names = {}
def Pd(*idx):
    key = tuple(sorted(idx))
    if key not in names:
        names[key] = sp.Symbol('Pi_' + ''.join('e12'[i] for i in key) if key else 'Pi')
    return names[key]

# The gap needs only second derivatives at the point, so Pi may be replaced EXACTLY (for this purpose) by its
# second-order Taylor polynomial about psi0 = (e, y1, y2); no undefined-function chain rule is involved.
psi0 = [e, y1, y2]
def Pi_T(psi):
    d = [psi[i] - psi0[i] for i in range(3)]
    return (Pd() + sum(Pd(i) * d[i] for i in range(3))
            + sp.Rational(1, 2) * sum(Pd(i, j) * d[i] * d[j] for i in range(3) for j in range(3)))

s = sp.Symbol('s')
Us = {u: Uofp[u] + s * du for u, du in zip(Usym, U1)}   # U(x1) along the face: U0 + s U_1

def scheme_p(U):
    """pressure the scheme rebuilds from a conserved state U (dict of expressions)"""
    r, mn, mt, En, Ya, Yb = (U[k] for k in Usym)
    eps_ = En / r - (mn**2 + mt**2) / (2 * r**2) - ell(Ya / r, Yb / r)
    return r * Pi_T([eps_, Ya / r, Yb / r])

def flux(name, U):
    r, mn, mt, En, Ya, Yb = (U[k] for k in Usym)
    p = scheme_p(U)
    return {'mass': mn, 'mom_normal': mn**2 / r + p, 'mom_transverse': mn * mt / r,
            'energy': (En + p) * mn / r, 'tracer1': Ya * mn / r, 'tracer2': Yb * mn / r}[name]

fluxes = ['mass', 'mom_normal', 'mom_transverse', 'energy', 'tracer1', 'tracer2']

def gap(name):
    F = flux(name, Us)
    d2 = sp.diff(F, s, 2).subs(s, 0)
    return sp.expand(sp.simplify(s2 / 2 * d2))

# the claims (Xi, thread ts 1791537083), written in this script's symbols
psi1 = [de, dy1, dy2]
Hpsi = [[Pd(0, 0), Pd(0, 1), Pd(0, 2)], [Pd(0, 1), Pd(1, 1), Pd(1, 2)], [Pd(0, 2), Pd(1, 2), Pd(2, 2)]]
J = s2 / 2 * sum(psi1[i] * Hpsi[i][j] * psi1[j] for i in range(3) for j in range(3))
h = e + ell(y1, y2) + Pd()            # h = (W->I + p)/rho = e + ell + Pi  (no kinetic energy)
dh = de + u01 * dy1 + u02 * dy2 + Pd(0) * de + Pd(1) * dy1 + Pd(2) * dy2
claims = {
    'mass': 0,
    'mom_normal': rho * J,
    'mom_transverse': 0,
    'energy': s2 * rho * dun * dh + rho * un * J,
    'tracer1': s2 * rho * dun * dy1,
    'tracer2': s2 * rho * dun * dy2,
}

eps_ = sp.Symbol('epsilon')   # velocity amplitude, for the linearisation about rest


def linear_part(expr):
    """terms of order <= 1 in the velocity (u_n, u_t and their derivatives scaled by eps_)"""
    sub = {un: eps_ * un, ut: eps_ * ut, dun: eps_ * dun, dut: eps_ * dut}
    ex = sp.expand(expr.subs(sub, simultaneous=True))
    return sp.expand(ex.coeff(eps_, 0) + ex.coeff(eps_, 1))


results = {}
for k in fluxes:
    g = gap(k)
    res_full = sp.simplify(g - claims[k])
    res_lin = sp.simplify(linear_part(g) - linear_part(sp.expand(claims[k])))
    results[k] = (g, res_full, res_lin)
    print(f'=== {k}')
    print('  gap            =', sp.factor_terms(g))
    print('  gap - claim    =', sp.factor_terms(res_full))
    print('  linear in |v|: gap - claim =', res_lin, '->', 'PASS' if res_lin == 0 else 'FAIL')

# exact energy gap in a compact form: s2 rho u_n1 H_1 + u_n * (p gap), H = h + |v|^2/2
H1 = dh + un * dun + ut * dut
p_gap = results['mom_normal'][0] - s2 * rho * dun**2
chk = sp.simplify(results['energy'][0] - (s2 * rho * dun * H1 + un * p_gap))
print('=== energy exact identity: gap = s2 rho u_n1 (h + |v|^2/2)_1 + u_n * [p gap]  ->', 'PASS' if chk == 0 else f'FAIL {chk}')
chk = sp.simplify(results['mom_normal'][0] - (s2 * rho * dun**2 + p_gap))
print('=== p gap (full, incl. kinetic part of e) =', sp.factor_terms(sp.expand(p_gap)))
print('    p gap - rho J =', sp.factor_terms(sp.simplify(p_gap - rho * J)))

# ---- prefactor claim for the e7f9904 form (I+p) d1 ln(p/rho) d1 u_n, ideal moist Pi = e / kappa(y) ----
kap = sp.Function('kappa')(y1, y2)
Pi_id = e / kap
dk = sp.diff(kap, y1) * dy1 + sp.diff(kap, y2) * dy2
dPi_id = sp.diff(Pi_id, e) * de + sp.diff(Pi_id, y1) * dy1 + sp.diff(Pi_id, y2) * dy2
h_id = e + ell(y1, y2) + Pi_id
dh_id = de + u01 * dy1 + u02 * dy2 + dPi_id
I_plus_p = rho * h_id
e7 = I_plus_p * dPi_id / Pi_id            # (I+p) d1 ln(p/rho), p/rho = Pi
exact = rho * dh_id
ellv = ell(y1, y2)
dell = u01 * dy1 + u02 * dy2
p_id = rho * Pi_id
claim_diff = rho * ellv * dPi_id / Pi_id - p_id * dk - rho * dell
d = sp.simplify(e7 - exact - claim_diff)
print('=== prefactor: (I+p) d ln(p/rho) - rho d h  ==  rho ell d ln(p/rho) - p d kappa - rho d ell  ->', 'PASS' if d == 0 else f'FAIL {d}')
# dry, uniform column: kappa, y constant (d kappa = d ell = 0), ell != 0
ratio = sp.simplify((e7 / exact).subs({dy1: 0, dy2: 0}))
claimed = 1 + ellv / ((kap + 1) * Pi_id)
print('=== dry uniform ratio e7/exact =', sp.factor(ratio), ' claim 1 + ell/((kappa+1) p/rho):',
      'PASS' if sp.simplify(ratio - claimed) == 0 else 'FAIL')
# zero offset, uniform composition: e7 term equals the exact one
z = sp.simplify((e7 - exact).subs({u01: 0, u02: 0, dy1: 0, dy2: 0}))
print('=== dry, uniform, zero-offset limit e7 - exact =', z, '->', 'PASS' if z == 0 else 'FAIL')

# ---- offset invariance: u0 -> u0 + c shifts E by rho c.y; energy row must shift by c.(tracer rows) ----
c1, c2 = sp.symbols('c1 c2', real=True)
def energy_corr_h(o1, o2):
    return s2 * rho * dun * (de + o1 * dy1 + o2 * dy2 + Pd(0) * de + Pd(1) * dy1 + Pd(2) * dy2)
shift_h = sp.simplify(energy_corr_h(u01 + c1, u02 + c2) - energy_corr_h(u01, u02))
tr = c1 * claims['tracer1'] + c2 * claims['tracer2']
print('=== offset shift of the h-differenced energy row == c . (tracer rows) ->', 'PASS' if sp.simplify(shift_h - tr) == 0 else 'FAIL')
def energy_corr_e7(o1, o2):
    hh = e + o1 * y1 + o2 * y2 + Pi_id
    return rho * hh * dPi_id / Pi_id * dun * s2
shift_e7 = sp.simplify(energy_corr_e7(u01 + c1, u02 + c2) - energy_corr_e7(u01, u02))
print('=== offset shift of the e7f9904 energy row =', sp.factor(shift_e7), '; equals c.(tracer rows)?',
      'yes' if sp.simplify(shift_e7 - tr) == 0 else 'no')
