// V3 lane EF skeleton -- declarations only, not built. Pin snapy 9e5de2d4. Rev 3.7.
// Register API = lane R's FROZEN header rev 4.2, happysky19/snapy 4c59162a
// docs/v3/skeleton/R/flux_register.hpp (Tianhao). EF calls it directly.
#pragma once
#include <torch/torch.h>

namespace snap {
class FluxRegister;     // lane R: add, scale, total, cell_amount, enter
class RegisterMonitor;  // lane R: amounts, counters, minima, retry_flags

//! EF's post names (the header leaves names to the poster; Q-R-h).
namespace EfPost {
// P1 sweep:  add(1, kSedimentation, {species hydro_ids, IVX..IVZ, IPR}, sed)
constexpr char const* kSedimentation = "sedimentation";
// P3 limit:  add(d, kCarry, {IPR}, -c_E); add(d, kCarry, {IVX,IVY,IVZ}, -c_m)
//            x1: advected pair first, then settling pair (in post order)
constexpr char const* kCarry = "positivity.carry";
// P2 limit:  scale(d, kWithhold, species, where(F > 0, th_lo, th_hi))
constexpr char const* kWithhold = "positivity.withhold";
// P4/P5 on the scalar register (Q-R-b): add, then scale
constexpr char const* kScalarUpper = "scalar.upper_bound";
constexpr char const* kScalarWithhold = "scalar.positivity.withhold";
// cell_amount(name, vol_du[nvar,..], 1.0, AmountKind::floor), after_combine
// after each stage's combine (R :22, :67-70)
constexpr char const* kFloor = "eos.floor";
constexpr char const* kBorrow = "eos.borrow";
constexpr char const* kFixVapor = "eos.fix_vapor";
// count (R :76): ef.floor_patch ef.nan ef.vapor_fail ef.heat_capacity
// ef.pos_hits ef.pos_severe ef.scalar_pos_hits; record_min (:77): ef.pos_min;
// flag_retry (:78): ef.floor_patch ef.nan ef.vapor_fail ef.heat_capacity
}  // namespace EfPost
//! Reads: total(d) in limit (R1); R2 = EF's P1 buffer; R3 =
//! mass.dry.limited@d; R4 = R3 - covariance.dry@d (R.rst Q-R-c). Order: sweep
//! (x1 riemann < P1 < x2/x3 riemann, cov) < reconcile (replace,
//! apply_prescribed) < limit (theta sync Q-R-d < P3 adds < P2 scale)

}  // namespace snap
