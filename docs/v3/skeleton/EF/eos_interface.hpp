// V3 lane EF skeleton -- declarations only, not built. Pin snapy 9e5de2d4. Rev 3.2.
// Q5 (EF decides): typed EOS methods + capabilities; the register never calls
// the EOS. Replaces compute("W->A") etc. and the 16 type-string branches.
#pragma once
#include <cstdint>
#include <torch/torch.h>
namespace snap {
enum EosCap : uint32_t {
  kHasTemperature = 1u << 0,   // false: shallow-water
  kHasSpecies = 1u << 1,       // moist types
  kAnomalyStorage = 1u << 2,   // ideal-moist today (hydro.cpp:192)
  kFloat32Implicit = 1u << 3,  // ideal-moist today (hydro.cpp:505)
  kClosedFormMoist = 1u << 4,  // Roe moist path (roe.cpp:20)
};
//! Every type (ideal-gas, ideal-moist, moist-mixture, aneos, shallow-water).
struct EosInterface {
  virtual uint32_t caps() const = 0;
  virtual void prim_from_cons_(torch::Tensor u, torch::Tensor w) = 0;  // U->W
  virtual void cons_from_prim_(torch::Tensor w, torch::Tensor u) = 0;  // W->U
  virtual torch::Tensor internal_energy(torch::Tensor w) = 0;          // W->I
  virtual torch::Tensor temperature(torch::Tensor w) = 0;              // W->T
  virtual torch::Tensor internal_energy_at(torch::Tensor u, torch::Tensor t) = 0;
  //! W->A + WA->L, or ANEOS's W->L + WL->A: one contract for all solvers
  virtual void gamma_sound_(torch::Tensor w, torch::Tensor gamma, torch::Tensor cs) = 0;
};
}  // namespace snap
