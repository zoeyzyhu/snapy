// V3 lane EF skeleton -- declarations only, not built. Pin snapy 9e5de2d4.
// Register names are PROVISIONAL until lane R posts its interface (EF.rst s4).
#pragma once
#include <torch/torch.h>

namespace snap::v3 {

class FluxRegister;  // owned by lane R; EF only posts and reads

//! What EF posts. Each post is a named contribution or correction.
enum class EfPostKind {
  kSedimentation,        // P1: x1; species, IVX..IVZ, IPR (sed_hydro.cpp:36-40)
  kPositivityWithhold,   // P2: species rows, all dims (flux_positivity.cpp:92-122)
  kPositivityCarry,      // P3: IPR, IVX..IVZ (flux_positivity.cpp:124-167)
  kScalarUpperBound,     // P4: scalar rows (scalar.cpp:212-214)
  kScalarPositivity,     // P5: scalar rows (scalar.cpp:239)
};

//! What EF reads (R1-R4, EF.rst s4). Each returns a view; the caller never
//! writes through it.
//!  R1 total(dim) species + IDN rows  -> theta, td
//!  R2 part(x1, kSedimentation) species rows -> carry split, phi mask
//!  R3 total(dim)[IDN] of the hydro register -> scalar upwind mass flux
//!  R4 total(dim)[IDN] without the covariance post -> scalar laterals
//! Ordering (EF.rst s4):
//!  riemann(x1) < P1 < seam-avg(x1) < riemann(x2,x3), cov < R1,R2
//!  < theta sync < {P2,P3} < divergence, AAM, gravity work
//!  scalar register: riemann_s, cov_s < P4 < P5 < divergence_s

//! Post a correction that scales rows by `factor` (Q-R2). Needed for P2 and
//! P5 to stay bitwise against `F *= theta`.
void ef_post_scale(FluxRegister& reg, int dim, EfPostKind kind,
                   torch::Tensor const& rows, torch::Tensor const& factor);

//! Post an additive increment.
void ef_post_add(FluxRegister& reg, int dim, EfPostKind kind,
                 torch::Tensor const& rows, torch::Tensor const& increment);

}  // namespace snap::v3
