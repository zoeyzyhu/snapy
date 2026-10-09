"""Numerical check of the symbolic gaps (moist_cov_sympy.py) by direct face quadrature.

Concrete ideal-moist EOS with two tracers (mass-weighted R and cv, so Pi = e R(y)/cv(y) is nonlinear in y):
    R(y) = Rd (1 - y1 - y2) + R1 y1 + R2 y2,  cv(y) likewise,  Pi = e R/cv,  ell = u01 y1 + u02 y2.
Smooth primitive profiles in x1 with non-zero velocities. For each dx1 = h, the exact face average <F(U)> is
computed by 40-point Gauss-Legendre in 50-digit arithmetic, F(Ubar) from the averaged conserved state (as the
scheme does), and compared with the predicted full gap (s2 = h^2/12):
    mass 0; tracer s2 rho u_n1 y_k1; transverse momentum s2 rho u_n1 u_t1;
    normal momentum s2 rho u_n1^2 + p_gap; energy s2 rho u_n1 (h_s + |v|^2/2)_1 + u_n p_gap,
    p_gap = rho J - (s2/2) rho Pi_e |v_1|^2,  J = (s2/2) psi_1^T Pi_psipsi psi_1, psi = (e, y1, y2),
with h_s = e + ell + Pi. The absolute residual must fall as h^4, i.e. the residual relative to the O(h^2)
gap must fall 4x per halving of h.
Run: python -I moist_cov_quadrature.py
"""
import mpmath as mp

mp.mp.dps = 50
Rd, R1, R2 = mp.mpf(3600), mp.mpf(461.5), mp.mpf(188.9)
cvd, cv1, cv2 = mp.mpf(9000), mp.mpf(1418), mp.mpf(1500)
u01, u02 = mp.mpf('2.5e6'), mp.mpf('-1.0e6')


def Pi(e, a, b):
    return e * (Rd * (1 - a - b) + R1 * a + R2 * b) / (cvd * (1 - a - b) + cv1 * a + cv2 * b)


# smooth primitive profiles around z0
z0 = mp.mpf('0.3')
prof = {
    'rho': lambda z: 1.2 * mp.exp(-0.7 * z),
    'un': lambda z: 3 + 2 * mp.sin(2 * z),
    'ut': lambda z: -1 + mp.cos(3 * z),
    'e': lambda z: 9000 * 300 * (1 - 0.3 * z) + 4000 * mp.sin(z),
    'y1': lambda z: 0.04 * mp.exp(-3 * z),
    'y2': lambda z: 0.01 + 0.02 * z ** 2,
}


def U_of(z):
    r, un, ut, e, a, b = (prof[k](z) for k in ('rho', 'un', 'ut', 'e', 'y1', 'y2'))
    ell = u01 * a + u02 * b
    return [r, r * un, r * ut, r * (e + ell) + r * (un ** 2 + ut ** 2) / 2, r * a, r * b]


def fluxes(U):
    r, mn, mt, En, Ya, Yb = U
    a, b = Ya / r, Yb / r
    e = En / r - (mn ** 2 + mt ** 2) / (2 * r ** 2) - (u01 * a + u02 * b)
    p = r * Pi(e, a, b)
    return {'mass': mn, 'mom_normal': mn ** 2 / r + p, 'mom_transverse': mn * mt / r,
            'energy': (En + p) * mn / r, 'tracer1': Ya * mn / r, 'tracer2': Yb * mn / r}


def predicted(h):
    s2 = h ** 2 / 12
    d = lambda k: mp.diff(prof[k], z0)
    v = {k: prof[k](z0) for k in prof}
    r = v['rho']
    psi = [v['e'], v['y1'], v['y2']]
    psi1 = [d('e'), d('y1'), d('y2')]
    f = lambda e, a, b: Pi(e, a, b)
    H = [[mp.diff(f, psi, tuple(1 if k in (i, j) and i != j else (2 if k == i == j else 0) for k in range(3)))
          for j in range(3)] for i in range(3)]
    J = s2 / 2 * sum(psi1[i] * H[i][j] * psi1[j] for i in range(3) for j in range(3))
    Pi_e = mp.diff(f, psi, (1, 0, 0))
    v1sq = d('un') ** 2 + d('ut') ** 2
    p_gap = r * J - s2 / 2 * r * Pi_e * v1sq
    hs = lambda z: prof['e'](z) + u01 * prof['y1'](z) + u02 * prof['y2'](z) + Pi(prof['e'](z), prof['y1'](z), prof['y2'](z))
    H1 = mp.diff(hs, z0) + v['un'] * d('un') + v['ut'] * d('ut')
    return {'mass': 0, 'tracer1': s2 * r * d('un') * d('y1'), 'tracer2': s2 * r * d('un') * d('y2'),
            'mom_transverse': s2 * r * d('un') * d('ut'), 'mom_normal': s2 * r * d('un') ** 2 + p_gap,
            'energy': s2 * r * d('un') * H1 + v['un'] * p_gap}


def measured(h):
    nodes = mp.gauss_quadrature(40, 'legendre') if hasattr(mp, 'gauss_quadrature') else None
    avg = lambda g: mp.quad(g, [z0 - h / 2, z0 + h / 2]) / h
    Ubar = [avg(lambda z, i=i: U_of(z)[i]) for i in range(6)]
    Fbar = fluxes(Ubar)
    out = {}
    for k in Fbar:
        Fav = avg(lambda z, k=k: fluxes(U_of(z))[k])
        out[k] = Fav - Fbar[k]
    return out


prev = None
print('h, then per flux: measured gap, (measured - predicted)/|measured|')
for h in (mp.mpf('0.04'), mp.mpf('0.02'), mp.mpf('0.01')):
    m, p = measured(h), predicted(h)
    row = {k: (m[k], (m[k] - p[k]) / (abs(m[k]) if m[k] != 0 else 1)) for k in m}
    print('h =', mp.nstr(h, 3))
    for k, (g, rel) in row.items():
        ratio = '' if prev is None or prev[k][1] == 0 or rel == 0 else f'  shrink x{mp.nstr(prev[k][1] / rel, 4)}'
        print(f'  {k:15s} gap {mp.nstr(g, 6):>14s}  rel.resid {mp.nstr(rel, 3):>10s}{ratio}')
    prev = row
