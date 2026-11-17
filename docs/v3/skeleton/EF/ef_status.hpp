// V3 lane EF skeleton -- declarations only, not built. Pin snapy 9e5de2d4. Rev 1.1.
#pragma once
#include <torch/torch.h>

namespace snap::v3 {

//! One persistent device tensor per MeshBlock. Every write is in place
//! (logical_or_, add_, minimum_out), so a CUDA-graph replay updates it the
//! same way eager does (roadmap G1, bullet 4). It replaces:
//!   EquationOfStateImpl::pending_marks_/limiter_marks_/vapor_failures_
//!     (equation_of_state.hpp:177-209)
//!   IdealMoistImpl::heat_capacity_failure_ (ideal_moist.cpp:136-152)
//!   HydroImpl::_positivity_* and _lim_* (hydro.hpp:472,476)
//!   ScalarImpl::_positivity_hits (scalar.hpp:111)
class EfStatus {
 public:
  enum Slot : int {
    kFloorPatch = 0,     // was limiter_marks_[0]
    kNan,                // was limiter_marks_[1]
    kVaporFail,          // was vapor_failures_ (int count)
    kHeatCapacity,       // was heat_capacity_failure_
    kFloorDMass,         // sum of vol * (rho after floor - before), FP64 (req 7)
    kFloorDEnergy,       // same for total energy; the monitor reads both
    kPosHits,            // cumulative (cell, species) with theta < 1
    kPosSevere,          // theta < 0.9 and withheld above round-off
    kPosMin,             // min theta (FP64 in every precision)
    kLimCut,             // x1 face flux removed (lifetime sum)
    kLimFlux,            // x1 face flux offered (lifetime sum)
    kScalarPosHits,      // scalars, tracer and complement
    kNumSlots
  };

  //! Allocate once on `device` (FP64 slots; counts are stored exactly).
  void allocate(torch::Device device);

  //! Device view of one slot, for in-place writes inside a stage.
  torch::Tensor slot(Slot s) const;

  //! Zero the per-step slots (kFloorPatch..kFloorDEnergy); keep lifetime ones.
  void reset_step_();

  //! The values redo stacks into its single device-to-host copy
  //! (meshblock.cpp:1566). No host read here.
  torch::Tensor snapshot() const;

 private:
  torch::Tensor data_;  // (kNumSlots,), never reallocated after allocate()
};

}  // namespace snap::v3
