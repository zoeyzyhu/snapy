// V3 lane EF skeleton -- declarations only, not built. Pin snapy 9e5de2d4. Rev 3.3.
#pragma once
#include <torch/torch.h>

namespace snap {

class EfStatus;

//! One owner for the three floors and their encoding. The values and
//! defaults are unchanged (equation_of_state.hpp:52-55).
struct Floors {
  double density = 1.e-6;
  double pressure = 1.e-3;
  double temperature = 20.;

  //! Clamp `row` to `floor` in place. If `ref` is defined, `row` is an
  //! anomaly about `ref`. In FP32 the bound rounds up to a representable
  //! anomaly whose total is >= floor; inactive cells are left untouched.
  //! Replaces equation_of_state.cpp:244-251 and :281-288 (two copies).
  static void floor_row_(torch::Tensor const& row, torch::Tensor const& floor,
                         torch::Tensor const& ref);

  //! Finite, density > floor, pressure > floor, species >= 0 (limiter on).
  //! Shared by conv4 (hydro_forward.cpp:359-367) and redo
  //! (meshblock.cpp:1522-1525). No host read; returns a device bool tensor.
  torch::Tensor admissible(torch::Tensor const& a, bool primitive,
                           bool limiter) const;
};

//! Conserved limiter step order (unchanged; equation_of_state.cpp:213-391):
//! NaN -> 0 (mark kNan), density floor, energy floor through UT->I at
//! temperature_floor (mark kFloorPatch), then SpeciesRepair.
//! Primitive limiter (equation_of_state.cpp:394-418): NaN, density floor,
//! species clamp (mark if below -positivity_roundoff), pressure floor.

}  // namespace snap
