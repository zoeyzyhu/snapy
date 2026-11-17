// V3 lane EF skeleton -- declarations only, not built. Pin snapy 9e5de2d4. Rev 3.3.
#pragma once
#include <torch/torch.h>

namespace snap {

//! Slots move to R's monitor (4c59162a :76-78) in R's R-1.
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
    kPosMin,             // min theta: FP64 (MPS: FP32)
    kLimCut,             // x1 face flux removed (lifetime sum)
    kLimFlux,            // x1 face flux offered (lifetime sum)
    kScalarPosHits,      // scalars, tracer and complement
    kNumSlots
  };

  //! Allocate once: int64 counts, FP64 sums/min (MPS: FP32), X.rst:235-239.
  void allocate(torch::Device device);

  //! Device view of one slot, for in-place writes inside a stage.
  torch::Tensor slot(Slot s) const;
  //! Zero per-step slots; census (kPosHits..) via StepReset "ef.census"
  //! commit/drop (X meshblock_parts.hpp:45) until R-1 moves it to R's monitor.
  void reset_step_();

  //! The values redo stacks into its single device-to-host copy
  //! (meshblock.cpp:1566). No host read here.
  torch::Tensor snapshot() const;

 private:
  torch::Tensor counts_, sums_;  // int64 / FP64 (MPS: FP32); fixed after allocate()
};

}  // namespace snap
