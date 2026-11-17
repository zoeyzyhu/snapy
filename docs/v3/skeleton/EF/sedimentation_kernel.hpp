// V3 lane EF skeleton -- declarations only, not built. Pin snapy 9e5de2d4. Rev 3.1.
#pragma once
#include <torch/torch.h>
#include "ef_register_use.hpp"

namespace snap {

//! Built once at SedHydro::reset() and again on to(device/dtype): persistent
//! device buffers in the compute dtype. Replaces the 23-argument signature
//! repeated across sed_hydro_dispatch.{hpp,cpp,cu} and sed_hydro_impl.h,
//! and the 8 per-call casts at sed_hydro.cpp:100-123.
struct SedKernelArgs {
  torch::Tensor radius, density, const_vsed;  // (nparticle,)
  torch::Tensor hydro_ids;                    // (nparticle,) int64
  torch::Tensor cosine_cell_kj;               // (nc3, nc2)
  torch::Tensor vsed;                         // (nparticle, nc3, nc2, nc1)
  int il = -1, iu = 0;      // sealed faces at physical x1 boundaries only
  double grav = 0.;         // signed grav1
  double gas_diameter = 0., gas_epsilon_lj = 0., gas_mass = 0.;
  double upper_limit = 0.;
};

//! The single sedimentation kernel (CPU, CUDA; MPS through OnHost).
//! Inputs from the EOS, so it serves ideal-moist and moist-mixture alike:
//!   temp = eos "W->T", energy = MoistEOS::species_energy(w) (rows hydro_ids)
//! Output: the settling increment, posted as P1 (x1) to the register. The
//! upwind/donor rule is the one in sed_hydro_impl.h:29-141.
void sedimentation_flux(torch::Tensor const& w, torch::Tensor const& temp,
                        torch::Tensor const& energy, SedKernelArgs& args,
                        torch::Tensor const& out_increment);

//! Compute into args' fixed buffer, then reg.add(1, EfPost::kSedimentation,
//! rows, buffer) in phase sweep (P1). The buffer is also R2.
void sedimentation_post(FluxRegister& reg, torch::Tensor const& w,
                        torch::Tensor const& temp, torch::Tensor const& energy,
                        SedKernelArgs& args);

}  // namespace snap
