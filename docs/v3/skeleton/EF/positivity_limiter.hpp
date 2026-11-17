// V3 lane EF skeleton -- declarations only, not built. Pin snapy 9e5de2d4. Rev 1.1.
#pragma once
#include <string>
#include <torch/torch.h>
#include "ef_register_use.hpp"
#include "ef_status.hpp"

namespace snap::v3 {

class MeshBlockImpl;

//! What one limiter call needs. Views only; nothing is owned.
struct PositivityInputs {
  torch::Tensor u;        // channel densities (nchan, nc3, nc2, nc1)
  torch::Tensor rho_dry;  // total dry density (1, nc3, nc2, nc1)
  torch::Tensor flux[3];  // R1: register totals of the channel rows
  torch::Tensor mass[3];  // R1/R3: register totals of the IDN row
  torch::Tensor fsed1;    // R2: settling part (x1); undefined for scalars
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

  //! Post P3 (carry; when hspec is defined), then P2 or P5 (withhold, as a
  //! scale post, Q-R2). Both are computed from the same pre-limit read, so
  //! the posting order does not change the result.
  void post_(FluxRegister& reg, PositivityInputs const& in,
             torch::Tensor const& theta, EfPostKind withhold_kind) const;

  //! The whole sequence: theta, census_, sync_, post_.
  void apply(FluxRegister& reg, PositivityInputs const& in,
             std::string const& key, EfPostKind withhold_kind) const;

 private:
  MeshBlockImpl const* pmb_;
  EfStatus* status_;
  int hits_slot_;
};

//! Primitive kernels kept from flux_positivity.hpp (signatures unchanged):
//! flux_positivity_theta, _share, _relax, _scale_, _carry_, _sync_theta_.
//! Their per-dimension blocks become one loop over dims (D9).

}  // namespace snap::v3
