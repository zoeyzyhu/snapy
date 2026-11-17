// V3 lane EF skeleton -- declarations only, not built. Pin snapy 9e5de2d4. Rev 3.1.
#pragma once
#include <string>
#include <torch/torch.h>
#include "ef_register_use.hpp"
#include "ef_status.hpp"

namespace snap {

class MeshBlockImpl;

//! What one limiter call needs. Views only; nothing is owned.
struct PositivityInputs {
  torch::Tensor u;        // channel densities (nchan, nc3, nc2, nc1)
  torch::Tensor rho_dry;  // total dry density (1, nc3, nc2, nc1)
  torch::Tensor flux[3];  // R1: reg.total(d), channel rows, phase limit
  torch::Tensor mass[3];  // R1/R3: reg.total(d)[IDN]
  torch::Tensor fsed1;    // R2: EF's own P1 buffer (x1); undefined for scalars
  torch::Tensor hspec;    // energy per unit species mass; undefined: no carry
  torch::Tensor vel;      // donor momentum per unit mass; with hspec
  torch::Tensor vface[2]; // x2/x3 seam donor velocity per face (#370, merged
                          // after the pin); undefined: vel. Fixed storage.
  double dt = 0.;
};

//! One driver for hydro species (hydro_forward.cpp:1154-1252) and passive
//! scalars (scalar.cpp:219-240). Stateless; borrows the status and coord.
class PositivityLimiter {
 public:
  PositivityLimiter(MeshBlockImpl const* pmb, EfStatus* status,
                    EfStatus::Slot hits_slot);

  //! theta = min(1, avail/(dt*out)) with the 4096-ulp margin; td on the dry
  //! mass; phi = share (zero where settling drains, hydro_forward.cpp:1188-1191);
  //! theta = relax(theta, td, phi). Device ops only.
  torch::Tensor theta(PositivityInputs const& in) const;

  //! Census into the status: hits, severe (theta < 0.9 and withheld above
  //! positivity_roundoff of the cell gas mass), min theta. Interior cells,
  //! FP64 sums (FP32 on MPS).
  void census_(PositivityInputs const& in, torch::Tensor const& theta) const;

  //! Ghost fill of theta: raw exchange at seams, then the boundary functions
  //! (flux_positivity.cpp:177-193). A segment boundary (B1/B2, Q-S1).
  //! After #370, hspec and vface ride in the same batched exchange.
  void sync_(torch::Tensor const& theta, std::string const& key) const;

  //! In phase limit: reg.add(d, EfPost::kCarry, ...) when hspec is defined
  //! (x1: advected pair, then settling pair), then reg.scale(d, withhold_name,
  //! rows, factor). Both from one pre-scale read of reg.total(d).
  void post_(FluxRegister& reg, PositivityInputs const& in,
             torch::Tensor const& theta, char const* withhold_name) const;

  //! The whole sequence: theta, census_, sync_, post_.
  void apply(FluxRegister& reg, PositivityInputs const& in,
             std::string const& key, char const* withhold_name) const;

 private:
  MeshBlockImpl const* pmb_;
  EfStatus* status_;
  int hits_slot_;
};

//! Primitive kernels kept from flux_positivity.hpp (signatures unchanged):
//! flux_positivity_theta, _share, _relax, _scale_, _carry_, _sync_theta_.
//! Their per-dimension blocks become one loop over dims (D9).

}  // namespace snap
