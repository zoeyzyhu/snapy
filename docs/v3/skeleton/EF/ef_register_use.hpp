// V3 lane EF skeleton -- declarations only, not built. Pin snapy 9e5de2d4. Rev 2.3.
// Register API = lane R's PROVISIONAL header, happysky19/snapy 543ff84f
// docs/v3/skeleton/R/flux_register.hpp (Tianhao). EF calls it directly.
#pragma once
#include <torch/torch.h>

namespace snap {

class FluxRegister;     // lane R: add, scale, total, cell_amount, enter
class RegisterMonitor;  // lane R: amounts, counters, retry_flags (read only)

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
// cell_amount(name, vol_du): floors and repairs, after the RK combine (Q-R-e)
constexpr char const* kFloor = "eos.floor";
constexpr char const* kBorrow = "eos.borrow";
constexpr char const* kFixVapor = "eos.fix_vapor";
}  // namespace EfPost

//! Reads: total(d) in phase limit (R1); R2 is EF's own P1 buffer, not a
//! register read; R3/R4 for scalars: Q-R-c. Order (header :25-28):
//!  x1 riemann < P1 < x1 seam replace < x2/x3 riemann, cov < [limit]
//!  theta sync (Q-R-d) < {P3, P2} < divergence

}  // namespace snap
