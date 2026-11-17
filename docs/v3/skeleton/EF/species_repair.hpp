// V3 lane EF skeleton -- declarations only, not built. Pin snapy 9e5de2d4. Rev 3.7.
#pragma once
#include <utility>
#include <vector>
#include <torch/torch.h>

namespace snap {

class EfStatus;

//! Cloud -> parent-vapor borrow and the volume-weighted column repair.
//! Owned by the EOS module; the math is unchanged (fix_vapor_impl.h:8-90).
class SpeciesRepair {
 public:
  //! (parent vapor slot, normalized stoichiometric mass fraction) per cloud;
  //! built at reset from the thermo card's own species copy
  //! (equation_of_state.cpp:129-182, issue #234).
  using ParentTable = std::vector<std::vector<std::pair<int, double>>>;

  void build_parents(ParentTable table);

  //! Per-cell borrow of a negative condensate from its parents
  //! (equation_of_state.cpp:307-324). Conserves mass, energy, elements.
  void borrow_(torch::Tensor const& cons, int nvapor, int ncloud) const;

  //! Column repair of vapor (require_success) or parentless clouds.
  //! Failures are added on the device to status.slot(kVaporFail); no host
  //! read inside a stage. `whole_column`: gather x1 across ranks when pz > 1
  //! (segment boundary B3, Q-S3).
  void repair_columns_(torch::Tensor const& field, torch::Tensor const& major,
                       torch::Tensor const& vol, bool require_success,
                       bool whole_column, EfStatus& status) const;

  //! Mark a deficit above species_repair_mark(dtype) * rho_total
  //! (equation_of_state.cpp:385-390).
  void mark_deficit_(torch::Tensor const& before, torch::Tensor const& rho,
                     EfStatus& status) const;

 private:
  ParentTable parents_;
};

}  // namespace snap
