# #289: the transverse-face covariance gaps for a general (moist) EOS — independent check

Verifier: Zoey Hu's agent. I derived everything below before reading Xi's post (Slack thread, ts 1791537083) and
compared only at the end (§6). Machine checks:
- `moist_cov_sympy.py`: symbolic, exact for the O(Δx₁²) term;
- `moist_cov_quadrature.py`: direct 50-digit face quadrature with a concrete moist EOS;
- `j_bound.py`: a size estimate for the J pieces.

Their outputs are `sympy_out.txt` and `quad_out.txt`; all of these files sit next to this one.

## 1. Setup

An x2 (or x3) face spans one x1 cell, $\zeta\in[-\Delta x_1/2,\Delta x_1/2]$. The scheme evaluates the face flux
from the x1-averaged conserved state, $F(\bar U)$. The finite-volume flux is the face average $\langle F(U)\rangle$.
The reconstruction in x2 is assumed to deliver $\bar U$ at the face; the x2 error is a separate matter.

Conserved state:
$$U=(\rho,\ m_n,\ m_t,\ E,\ Y_k),\quad m=\rho u,\quad Y_k=\rho y_k,\quad
E=\rho\,(e+\ell(y))+\tfrac12\rho|v|^2,\quad \ell=\textstyle\sum_k y_k u_{0k},$$

- $e$ is the specific thermal energy, the one the EOS sees: $p=\rho\,\Pi(e,y)$.
- $\ell$ is the offset that W→I adds (§5).

The scheme recovers $y=Y/\rho$ and $e=E/\rho-|m|^2/(2\rho^2)-\ell(Y/\rho)$ from $\bar U$. A constant dry offset is
included by writing $\ell=u_{0d}+\sum_n y_n(u_{0n}-u_{0d})$; a constant part of $\ell$ drops out of every
derivative below.

x2 fluxes ($u_n$ is the face-normal velocity, $u_t$ a transverse one; x3 faces are the same with roles swapped):
- mass: $m_n$
- normal momentum: $m_n^2/\rho+p$
- transverse momentum: $m_nm_t/\rho$
- energy: $(E+p)\,m_n/\rho$
- tracer: $Y_km_n/\rho$

## 2. The O(Δx₁²) gap

Expand $U(\zeta)=U_0+U_1\zeta+\tfrac12U_{11}\zeta^2+\dots$. Then $\bar U=U_0+\tfrac{\Delta x_1^2}{24}U_{11}+O(\Delta x_1^4)$, and
$\langle (U-\bar U)_a(U-\bar U)_b\rangle=s_2\,U_{1a}U_{1b}+O(\Delta x_1^4)$ with

$$s_2=\langle\zeta^2\rangle=\Delta x_1^2/12 .$$

Expanding $F$ about $\bar U$ (not $U_0$), the linear term averages to zero exactly, and the third moments vanish by
parity at this order. So

$$\boxed{\ \langle F(U)\rangle-F(\bar U)=\tfrac{s_2}{2}\,U_1^{\mathsf T}F_{UU}\,U_1+O(\Delta x_1^4)\ } $$

with $F_{UU}$ taken at the point. The scripts evaluate exactly this quadratic form. They replace $\Pi$ by its
second-order Taylor polynomial about $\psi_0=(e,y)$ (exact for second derivatives), set $U(s)=U_0+sU_1$, and
take $\tfrac{s_2}{2}\,d^2F/ds^2|_0$.

## 3. Results (exact at O(Δx₁²), all velocity orders)

Notation: subscript 1 means $\partial_{x_1}$, $\psi=(e,y_1,\dots)$, $h=e+\ell+\Pi=(\text{W→I}+p)/\rho$ (no KE), and

$$J=\tfrac{s_2}{2}\,\psi_1^{\mathsf T}\,\Pi_{\psi\psi}\,\psi_1 .$$

| flux | gap $\langle F\rangle-F(\bar U)$ |
|---|---|
| mass | $0$ |
| tracer $k$ | $s_2\,\rho\,u_{n,1}\,y_{k,1}$ |
| transverse momentum | $s_2\,\rho\,u_{n,1}\,u_{t,1}$ |
| normal momentum | $s_2\,\rho\,u_{n,1}^2+\delta p$ |
| energy | $s_2\,\rho\,u_{n,1}\,(h+\tfrac12|v|^2)_{,1}+u_n\,\delta p$ |
| pressure the scheme rebuilds, $\delta p$ | $\rho J-\tfrac{s_2}{2}\,\rho\,\Pi_e\,|v_1|^2$ |

Derivation of the structure, which the sympy run confirms term by term:
- A ratio $q=Q/\rho$ has quadratic form $-2\rho_1 q_1/\rho$, so a flux $Q\,m/\rho$ gives $s_2\,\rho\,u_1 q_1$.
  The $u\rho_1$ and $q\rho_1$ cross terms cancel identically, as in the dry case.
- $p=\rho\,\Pi(\psi(U))$ is homogeneous of degree 1 in $U$. Its quadratic form is
  $\rho\,\psi_1^{\mathsf T}\Pi_{\psi\psi}\psi_1+2\rho_1\Pi_\psi\psi_1+\rho\,\Pi_\psi\cdot\psi_{UU}[U_1,U_1]$.
  The last term is $-2\rho_1\Pi_\psi\psi_1$ plus the kinetic-energy part $-\rho\,\Pi_e|v_1|^2$, so it cancels
  the middle term and leaves $\delta p$.
- The energy flux $(E+p)\,u_n$ splits as $s_2\rho\,u_{n,1}H_1+u_n\,\delta p$, with $H=(E+p)/\rho$.

**Linearised about a resting state** (velocity a perturbation, background gradients $O(1)$), every term
quadratic in velocity drops:

- mass: $0$
- tracer $k$: $s_2\,\rho\,u_{n,1}\,y_{k,1}$
- normal momentum: $\rho J$
- transverse momentum: $0$
- energy: $s_2\,\rho\,u_{n,1}\,h_{,1}+\rho\,u_n\,J$

**Notes.**
- $J$ involves only the Hessian of $\Pi$ along $\psi_1$. It vanishes when $\Pi$ is linear along the gradient,
  e.g. a single ideal gas, where $\Pi=e/\kappa$ with constant $\kappa$.
- $J$ is invariant under any linear change of variables in $\psi$. It is therefore the same whether $e$ is taken
  with or without the (linear-in-$y$) offset.
- For an ideal moist gas, $\Pi_{ee}=0$, so $J=\tfrac{s_2}{2}(2\Pi_{ey}e_1y_1+\Pi_{yy}y_1^2)$.

**Numerical confirmation** (`quad_out.txt`): non-zero velocities, two tracers with composition gradients, and
latent-size offsets. Halving $\Delta x_1$ from 0.04 to 0.01, (measured − predicted)/|measured| falls 4.0× per
halving for every flux (normal momentum 3.99×). So the residual is $O(\Delta x_1^4)$ and the table above is the
complete $O(\Delta x_1^2)$ gap.

## 4. The e7f9904 prefactor

At e7f9904 (`e7f99040834c5be3e97ee9e952d28453dfd0b7d4`), `src/hydro/hydro_forward.cpp`:
```
60:  auto lnt = (p / wbar[IDN]).log();
61:  auto enth = peos->compute("W->I", {wbar}) + p;
101:      enth.narrow(-1, 1, n1 - 2) * s2.narrow(-1, 1, n1 - 2) * dlnt * dun -
102:      ds.narrow(-1, 1, n1 - 2) * dhflx;
```
So the energy covariance term is $(I+p)\,s_2\,\partial_1\ln(p/\rho)\,\partial_1u_n$ (plus the curved-grid centroid term,
not at issue here). `src/eos/ideal_moist.cpp`:
```
219:  // add the internal energy offset
220:  auto yd = 1. - yfrac.sum(0);
221:  ie += prim[IDN] * yd * u0[0];
222:  ie +=
223:      prim[IDN] * yfrac.unfold(0, ny, 1).matmul(u0.narrow(0, 1, ny)).squeeze(0);
```
So W→I $=\rho(e+\ell)$ with $\ell=y_du_{0d}+\sum_n y_nu_{0n}$, and $I+p=\rho h$.

For the ideal moist EOS, $\Pi=e/\kappa(y)$ with $\kappa=1/(\gamma_i-1)$ (`ideal_moist.cpp:202,217`), so
$h=(\kappa+1)\Pi+\ell$. Then

$$(I+p)\,\partial_1\ln\Pi-\rho\,\partial_1h=\rho\,\ell\,\partial_1\ln(p/\rho)-p\,\partial_1\kappa-\rho\,\partial_1\ell .$$

Sympy confirms this identically. In a dry, uniform column ($\kappa_1=\ell_1=0$, $\ell\ne0$):
$$\frac{(I+p)\,\partial_1\ln\Pi}{\rho\,\partial_1h}=1+\frac{\ell}{(\kappa+1)\,p/\rho},$$
which sympy confirms. With a non-zero dry offset $u_{0d}$, $\ell\neq0$ even in a single-species column, so the
e7f9904 coefficient is off by that factor there.

## 5. Offset invariance, and the dry limit

Shifting the offsets $u_{0k}\to u_{0k}+c_k$ redefines $E\to E+\rho\,c\cdot y$. The exact system maps to itself if
the energy equation gains $c\,\cdot$ (tracer equations). For the corrections:

- **h-differenced energy row** $s_2\rho\,u_{n,1}h_1$: it shifts by $s_2\rho\,u_{n,1}\,c\cdot y_1$, which is exactly
  $c\,\cdot$ (tracer rows $s_2\rho\,u_{n,1}y_{k,1}$). Invariant **only if** the tracer rows carry their
  correction. Without them, the shift of the energy row has no counterpart. A constant shift of $\ell$ changes
  nothing, since $h_1$ is unchanged.
- **e7f9904 row** $\rho h\,\partial_1\ln\Pi\,\partial_1u_n$: it shifts by
  $s_2\rho\,u_{n,1}(c\cdot y)\,\partial_1\ln\Pi$, which is **not** $c\,\cdot$ (tracer rows) even with tracer rows
  added. It is not offset-invariant, and a constant offset already changes it.
- **Dry, uniform, zero-offset limit** ($\ell=0$, $\kappa$ constant): $\rho h_1=\rho(\kappa+1)\Pi_1=(I+p)\,\partial_1\ln\Pi$
  exactly, so the h-differenced row reduces to e7f9904's term. Sympy gives 0.

## 6. Comparison with Xi's post (ts 1791537083), made after §§1–5

| claim | verdict | note |
|---|---|---|
| (a) energy $s_2\rho\,\partial_1u_n\partial_1h+\rho u_nJ$, $h=(\text{W→I}+p)/\rho$ without KE | **agree** at linear order about rest | the exact form adds $s_2\rho\,u_{n,1}\,(\tfrac12|v|^2)_{,1}-\tfrac{s_2}{2}\rho\,u_n\Pi_e|v_1|^2$, quadratic in velocity |
| (b) tracer $s_2\rho\,\partial_1u_n\partial_1y_n$ | **agree** exactly | |
| (c) momentum $\rho J$ | **agree** for the normal momentum at linear order | exact: $s_2\rho u_{n,1}^2+\rho J-\tfrac{s_2}{2}\rho\Pi_e|v_1|^2$; transverse momentum $s_2\rho u_{n,1}u_{t,1}$, zero at linear order |
| (d) mass 0 | **agree** exactly | |
| (e) $J=\tfrac{s_2}{2}\psi_1^{\mathsf T}\Pi_{\psi\psi}\psi_1$, $\psi=(e,y)$, zero unless $\Pi$ is nonlinear along the gradient | **agree** | invariant under linear changes of $\psi$, so offset convention does not matter |
| prefactor error $\rho\ell\,\partial_1\ln(p/\rho)-p\,\partial_1\kappa-\rho\,\partial_1\ell$ | **agree** (sign: e7f9904 minus exact) | |
| dry uniform factor $1+\ell/((\kappa+1)p/\rho)$ | **agree** | |
| h-differencing offset-invariant only with the tracer rows | **agree** | and e7f9904's form is not invariant with or without them |
| dry, uniform, zero-offset limit equals e7f9904's term | **agree** | |

**Size of J (optional; a rough estimate, not Xi's metric).** `j_bound.py` assumes an H2-He atmosphere with 5%
water vapour falling to 0 over 10 km, T = 300 K, a 2 K/km lapse rate and a 50 km column mode. Under those
assumptions, $|\rho u J|/|s_2\rho u_1h_1|$ is 0.9e-3 with a 2.5e6 J/kg offset gradient, and 2.2e-3 without one.
Xi's "6e-8 vs 1e-5" is a ratio of 6e-3. These are the same order and both say the J pieces are small next to the
covariance term. The metrics differ, so this is consistency, not confirmation.

**Hypotheses, not shown here:**
- Dropping the velocity-quadratic terms is harmless for turbulent (non-linear) flow. That is item 5's question.
- The discrete $D_1[h]$ form inherits the exactness above. I have derived the continuous gap only, not checked
  any implementation.
