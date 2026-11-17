=====================================================================
V3 design, lane EF: EOS, floors, positivity, tracers, sedimentation
=====================================================================

:Lane: EF (owner Zoey Hu; alternate Linfeng Li)
:Revision: 2.3 (rev 1 ``16b8976a``, rev 1.1 ``de030195``, rev 2
           ``6adc7f74``, rev 2.1 ``7f70c735``, rev 2.2 ``8966a7f2``).
           Rev 2.3: lane R's provisional header ``543ff84f`` (Tianhao)
           replaces every guessed register name; namespace ``snap``.
           Rev 2.2: F6 status
           (proceeding, counted, recorded for Cheng). Rev 2.1: lane R's provisional answers (Linfeng's
           local header ``fd3d68a``) are recorded in section 4; EF's EOS
           interface decision (Q5) is in section 3 and the skeleton; the
           answer to R's bitwise question is in section 4. Rev 2: Cheng
           decided F1, so ANEOS stays. It keeps its place in the EOS class
           tree on the shared base, and section 9 gives one budget with
           ANEOS kept. F5 is a standalone proposal with a "what changes"
           table. F3 and F4 proceed on my proposals, still FOR CHENG.
           Rev 1.1: baseline 4,971 with ``src/turbulence``; the
           ``hydro_forward.cpp`` lines are lane R's; #370 absorption;
           section 11 against the ten register requirements.
:Pins: snapy ``9e5de2d4ce497d0b2d4da3295fc1fe969fe7e410``;
       kintera ``3f5ff938181351a84cb129a9e6314fb89b669b71``
:Status: design only. Nothing here is implemented or built.

Every ``file:line`` below is at the snapy pin and relative to the repository
root, unless it starts with ``kintera:``, which means the kintera pin. A
statement marked **(hypothesis)** has not been tested. Line counts come from
``wc -l`` at the pin. "Target" line counts are design estimates, not
measurements.

**Source gap.** Revision 1 was written from brief 3/3, CHANGE 1,
``V3_ROADMAP.md`` at the pin and the code. The ten register requirements and
the lane letters used here (sections 4 and 11) are those restated in the EF
lane thread. I have still not read briefs 1/3 and 2/3 verbatim. The register
names in section 4 and the skeleton stay **provisional** until lane R's
interface header is posted.

.. contents::
   :local:
   :depth: 1

1. Scope and pins
=================

**In scope (lane EF):**

* The EOS layer: ``src/eos/`` (23 files, 2,716 lines). This covers
  conversions, the conserved and primitive limiter, density, pressure and
  temperature floors, the cloud-to-parent borrow and the vapor column repair.
* The tracer flux positivity limiter and its withheld-mass carry:
  ``src/hydro/flux_positivity.{hpp,cpp}`` (346 lines), and the EF slices of
  ``src/hydro/hydro_forward.cpp`` (step 4.C, 1154-1252, and the
  sedimentation post, 858-866).
* Passive scalars where they touch EF: ``src/scalar/`` (3 files, 458 lines).
  This is their positivity, their upper bound and their flux rebuild.
* Sedimentation: ``src/sedimentation/`` (8 files, 1,049 lines).
* Turbulence: ``src/turbulence/`` (3 files, 402 lines; C24 in section 2).

The ``hydro_forward.cpp`` slices named above (step 4.C, 1154-1252, 99 lines;
the sedimentation post, 858-866, 9 lines; 108 in all) are **lane R's lines**.
Lane R counts their deletion. EF designs what replaces them and counts only
the new EF code that does it (in ``flux_positivity.*``).

**Read but owned elsewhere.** EF changes how these sites call EF, but other
lanes own them. Section 11 asks each owner.

* Redo plumbing: ``meshblock.cpp:688-695``, ``735-738``, ``907-909``,
  ``952``, ``1417-1430``, ``1438-1446`` and ``1506-1566``.
* Floor reads in reconstruction and boundaries: ``recon/reconstruct.cpp:150-158``,
  ``hydro_forward.cpp:594-614`` and ``bc/bc_func.cpp:96-97,198-199``.
* Gravity work, which reads the limited mass flux:
  ``hydro_forward.cpp:575-580,846-848,1412-1435``.
* VIC species transfer: ``implicit/vic_redistribute_impl.h:149-157``.

**Baselines (measured at the pin):**

* ``git ls-files src | grep -E '\.(cpp|hpp|h|c|cu|cuh)$' | xargs cat | wc -l``
  gives **42,677**, which matches the brief.
* EF lane: 39 whole files, **4,971 lines**, which matches the brief. Each
  directory was measured on its own with
  ``git ls-files <dir> | xargs cat | wc -l``:

  .. list-table::
     :header-rows: 1
     :widths: 50 10 10 30

     * - pathspec
       - files
       - lines
       - brief
     * - ``src/eos``
       - 23
       - 2,716
       - 2,716
     * - ``src/scalar``
       - 3
       - 458
       - 458
     * - ``src/sedimentation``
       - 8
       - 1,049
       - 1,049
     * - ``src/turbulence``
       - 3
       - 402
       - 402
     * - ``'src/hydro/flux_positivity.*'``
       - 2
       - 346
       - 346
     * - all five in one ``git ls-files`` call
       - 39
       - **4,971**
       - 4,971

  Revision 1 counted 4,677 lines. It left out ``src/turbulence`` (402) and
  included the 108 ``hydro_forward.cpp`` lines, which are lane R's.
  4,677 - 108 + 402 = 4,971. **Lane ceiling: 3,976** (4,971 x 0.8 = 3,976.8,
  rounded down).
* Main moved after the pin. #370 merged as ``730b35007d16389c64116e4bf9d2fe93707e29e9``,
  the pin's direct child. It adds 8 lines to the EF files
  (``flux_positivity.cpp`` 195 -> 198, ``.hpp`` 151 -> 156, measured with
  ``git show 730b3500:<f> | wc -l``). The baseline stays at the pin
  (section 10 says how the design absorbs #370).
* Inside the 36 non-turbulence EF files: 5 ``.item<>`` host reads, 16 hard
  FP64 dtype sites and 10 ``set_``/``set_data`` sites (section 7). The
  turbulence files are not compiled (C24), so none of their sites run.

2. Concepts and current sites
=============================

I updated the 919936da inventory (Zoey's eos/interface/forcing/mesh lane) to
the pin and extended it to positivity, scalars and sedimentation.

.. list-table:: EF concepts at the pin
   :header-rows: 1
   :widths: 6 30 40 24

   * - id
     - concept
     - sites (``file:line``)
     - note
   * - C1
     - EOS factory and types: ideal-gas, ideal-moist, moist-mixture, aneos,
       shallow-water
     - ``eos/equation_of_state.cpp:426-454``
     - Repository YAMLs by type (``grep -rlE "type:\s*\"?<t>" --include=*.yaml``):
       ideal-gas 23, ideal-moist 36, moist-mixture 4, **aneos 0**,
       shallow-water 9.
   * - C2
     - ANEOS: registered, but cannot be built. **Stays in V3** (Cheng,
       F1).
     - ``eos/aneos.{hpp,cpp}``, ``eos/aneos/aneos_thermo.hpp``,
       ``eos/aneos/aneos_thermo_dummy.cpp:14-17`` (a weak constructor that
       throws)
     - 281 lines. 0 decks use it. Measured at 919936da: building it raises
       "ANEOSThermoImpl constructor is not implemented". The code is the same
       at the pin; I did not re-run it.
   * - C3
     - Stored versus total state ("U'->W", "W->U'")
     - ``eos/equation_of_state.cpp:205-211``, ``eos/ideal_moist.cpp:163-187``
     - The FP32 anomaly storage of roadmap M2.
   * - C4
     - Conserved limiter: NaN to 0, density floor, energy floor from
       ``temperature_floor`` through "UT->I"
     - ``eos/equation_of_state.cpp:213-290``
     - Anomaly floors round toward a representable bound
       (``float_anomaly_floor``, ``:40-46``).
   * - C5
     - Primitive limiter: NaN, density floor, species clamp, pressure floor
     - ``eos/equation_of_state.cpp:394-418``
     - Species marks use ``positivity_roundoff`` (``:410-412``).
   * - C6
     - Floor values and defaults: 1e-6, 1e-3, 20 K; ``limiter`` defaults to
       false
     - ``eos/equation_of_state.hpp:52-55``, ``eos/equation_of_state.cpp:82-93``
     - The struct and YAML defaults now agree. They diverged at 919936da.
   * - C7
     - Floor reads outside EOS
     - ``recon/reconstruct.cpp:150,158``; ``hydro/hydro_forward.cpp:359-367``
       (conv4 admissibility), ``:602-612`` (FP32 face floors);
       ``bc/bc_func.cpp:96-97,198-199``; ``mesh/meshblock.cpp:1426-1428,1522-1525``
     - Six owners read two option fields.
   * - C8
     - Cloud-to-parent-vapor borrow (one cell)
     - ``eos/equation_of_state.cpp:129-182`` (parent table),
       ``:307-324`` (borrow)
     - Conserves mass, energy and elements in the same cell.
   * - C9
     - Vapor and parentless-cloud column repair (``fix_vapor``)
     - ``eos/equation_of_state.cpp:326-380``; kernel
       ``eos/fix_vapor_impl.h:8-90``; CPU ``eos/eos_dispatch.cpp:80-103``;
       CUDA ``eos/eos_dispatch.cu:52-79``; MPS through ``OnHost``
       (``eos/eos_dispatch.cpp:116-117``)
     - The repair is volume-weighted (#241). When the column spans ranks,
       ``layout->gather_x1`` gathers it (``:340-347``).
   * - C10
     - Limiter marks and vapor failures, read by redo
     - ``eos/equation_of_state.hpp:177-209``;
       ``eos/equation_of_state.cpp:233-237,290,385-390``;
       ``mesh/meshblock.cpp:735-738,1052-1056,1438-1446,1535-1556``
     - A host ``std::vector`` queue of 0-d tensors (``hpp:209``).
   * - C11
     - Tracer flux positivity: theta, share, relax, scale
     - ``hydro/flux_positivity.cpp:30-80`` (theta), ``:82-90`` (share),
       ``:92-122`` (scale), ``:169-175`` (relax)
     - Each face is scaled by its donor's single factor, so conservation is
       exact (``hpp:61-63``).
   * - C12
     - Withheld-mass carry: energy and momentum leave with the withheld
       species mass (#269, #236)
     - ``hydro/flux_positivity.cpp:124-167``; called at
       ``hydro/hydro_forward.cpp:1232-1236``
     - The x1 species flux is split into its advected part and its settling
       part (``fsed1``).
   * - C13
     - Step 4.C driver for hydro species: gate, theta on the species, td on
       the dry mass, phi share, relax, census, sync, carry, scale, cut meter
     - ``hydro/hydro_forward.cpp:1154-1252``. Gate at ``:1165``
       (``limiter || cov2 || cov3``).
     - #338 (uniform ratio) is at ``:1174-1193``. The census uses ``wide``
       (FP64; FP32 on MPS), ``:373,1196-1222``.
   * - C14
     - Ghost sync of theta
     - ``hydro/flux_positivity.cpp:177-193``; keys ``"hydro_theta"``
       (``hydro_forward.cpp:1227``) and ``"scalar_theta"`` (``scalar.cpp:179``)
     - An exchange (communication) inside every stage. The species enthalpy is
       not exchanged (``hydro_forward.cpp:1224-1226``, #238). #370 (merged after the pin, section 10) adds
       the hspec and donor-velocity seam sync and is not in the pin.
   * - C15
     - Sedimentation posted into the x1 flux, and its settling part kept for
       the carry
     - ``hydro/hydro_forward.cpp:861-866`` (``fadv`` clone, then
       ``fsed1 = F - fadv``)
     - Happens before the x1 seam averaging (``:868-``) and before 4.C.
   * - C16
     - Sedimentation flux: three copies of the Stokes velocity and upwind
       flux
     - (a) tensor path for non-ideal-moist EOS, ``sedimentation/sed_hydro.cpp:18-43``
       with ``sed_vel.cpp:34-71``; (b) fused kernel
       ``sedimentation/sed_hydro_impl.h:32-141``, CPU
       ``sed_hydro_dispatch.cpp:122-157``, CUDA ``sed_hydro_dispatch.cu``; (c) MPS
       tensor copy ``sed_hydro_dispatch.cpp:159-212``
     - Path (a) is live: ``examples/uranus.yaml`` uses moist-mixture with
       sedimentation. The kernel recomputes f_eps
       (``sed_hydro_impl.h:15-27``), a fourth copy after
       ``ideal_moist.cpp:342-357``, ``ideal_moist_impl.h:17-24`` and
       ``sed_hydro_dispatch.cpp:85-100``.
   * - C17
     - Gravity-work background flux F^R, taken before sedimentation and the
       limiter
     - ``hydro/hydro_forward.cpp:575-580,846-848,902-917,1412-1435``
     - A clone that exists only to recover "F minus the EF posts".
   * - C18
     - Passive scalar flux rebuild: upwind on the hydro mass flux, with the
       covariance row
     - ``scalar/scalar.cpp:96-100,155-171``
     - The lateral flux uses ``mass - flux_covariance_dry(dim)``
       (``:161``), which also recovers a pre-post value.
   * - C19
     - Scalar upper bound (positivity of the complement ``b*rho - s``)
     - ``scalar/scalar.cpp:190-215``
     - It adds the change ``h - g`` and never recomputes the flux
       (``:207-214``).
   * - C20
     - Scalar positivity: the same pipeline as C13, written again
     - ``scalar/scalar.cpp:219-240``
     - The theta, td, phi and relax sequence repeats
       ``hydro_forward.cpp:1172-1193``.
   * - C21
     - Species energy: ``"W->E"`` (sedimentation) and ``species_enthalpy``
       (carry)
     - ``eos/ideal_moist.cpp:270-292,294-315``; ``eos/moist_mixture.cpp:89-108,110-132``
     - Two moist types each carry both functions.
   * - C22
     - Code that never runs
     - ``eos/ideal_moist_impl.h:34-55`` (its callers are commented out at
       ``eos_dispatch.cpp:61-78`` and ``eos_dispatch.cu:32-50``);
       ``eos/shallow_water_impl.h:11-15`` (0 callers); MPS ideal-gas
       ``eos/eos_dispatch.cpp:42-59``, which throws with its caller's
       iterator (measured at 919936da)
     -
   * - C23
     - Heat-capacity failure latch (ideal-moist perturbations)
     - ``eos/ideal_moist.cpp:136-152``, read at ``mesh/meshblock.cpp:1557-1560``
     - Already a device flag when ``defer_check`` is set.
   * - C24
     - Turbulence: a k-epsilon two-equation model (``TurbulenceModel``,
       ``KEpsilonTurbulence``, ``TurbulenceFactory``) that sets an isotropic
       eddy viscosity ``mu_t = c_mu rho k^2/eps`` and ``kappa = nu``
     - ``turbulence/turbulence_model.{hpp,cpp}``,
       ``turbulence/k_epsilon_turbulence.cpp``. **Clamps:** the sink step
       halves ``eps`` or ``k`` instead of letting it go negative
       (``k_epsilon_turbulence.cpp:174-177,185-188``). It does not register
       what it changed and conserves nothing. There is **no floor** on
       ``k`` or ``eps`` before the divisions at ``:170,172,207-208``.
     - **Not compiled and not reachable.** It is legacy Athena++ code
       (``AthenaArray``, ``ParameterInput``, ``#include <athena/athena.hpp>``;
       no ``athena/`` header exists in the repository). ``src/turbulence`` is
       in neither glob in ``src/CMakeLists.txt:35-53,122-134``. No file outside
       it names ``TurbulenceModel``, ``NTURBULENCE`` or ``turbulence_model``
       (``grep -rn``, all sources, Python and YAML), and no deck sets it.
       It was added in ``0b60576`` (#24), and since then only docstrings
       have changed (#95). The only trace outside it is an output-name
       entry ``"mut"`` (``output/output_utils.cpp:55``, lane O).

3. Target design
================

Five types. Each concept from section 2 has exactly one owner.

``EfStatus`` (new; ``skeleton/EF/ef_status.hpp``)
  One persistent device tensor per block, allocated once at block setup, with
  named slots:

  * ``floor_patch`` and ``nan`` (today's ``limiter_marks_[0..1]``);
  * ``vapor_fail`` (today's ``vapor_failures_``);
  * ``heat_capacity`` (today's ``heat_capacity_failure_``);
  * ``pos_hits``, ``pos_severe``, ``pos_min``, ``lim_cut`` and ``lim_flux``
    (today in ``HydroImpl``, ``hydro.hpp:472,476``);
  * ``scalar_pos_hits`` (``scalar.hpp:111``);
  * **new in 1.1** ``floor_dm`` and ``floor_de``: the volume-weighted mass
    and total energy the conserved limiter added this step (FP64). Revision
    1 counted floor hits but not how much a floor added. Requirement 7 needs
    the amount, and the device monitor (requirement 6) adds these two slots
    to its mass and E+PE budgets. The cloud borrow and the column repair
    conserve mass by construction (I5, I6). They report a failure count,
    not an amount.

  Writes are in-place device ops (``logical_or_``, ``add_``,
  ``minimum_out``). There is one ``reset_step_()`` and one
  ``snapshot()``. Redo reads ``snapshot()`` in its single device-to-host copy
  (``meshblock.cpp:1566``). This replaces the host queue ``pending_marks_``
  (``equation_of_state.hpp:184-193,209``), which a CUDA-graph replay would not
  re-run.

``Floors`` (``skeleton/EF/eos_floors.hpp``)
  Holds the three floor values and one encoder, ``floor_row_(row, floor, ref,
  dtype)``, for total and anomaly rows. Today that encoder is written twice:
  ``equation_of_state.cpp:244-251`` (density) and ``:281-288`` (energy). It
  also provides ``admissible(w)``, used by conv4 (``hydro_forward.cpp:359-367``)
  and by redo (``meshblock.cpp:1522-1525``). The conserved and primitive
  limiters stay methods of ``EquationOfStateImpl``. They call ``Floors`` and
  write to ``EfStatus``.

``SpeciesRepair`` (``skeleton/EF/species_repair.hpp``)
  Holds the cloud-parent table (``equation_of_state.cpp:129-182``), the
  per-cell borrow (``:307-324``) and the column repair (``:326-380``), which
  keeps calling the one kernel ``fix_vapor_impl.h``. Failures go to
  ``EfStatus::vapor_fail`` through the CUDA atomic sink that already exists
  (``eos_dispatch.cu:52-79``). No host count is read while a stage is running.

``PositivityLimiter`` (``skeleton/EF/positivity_limiter.hpp``)
  One driver for hydro species and passive scalars. Its inputs are the
  channel state, the mass-flux rows, the dry density, dt and an optional
  settling part. It does the following, in order:

  1. theta, td and phi, then relax (today ``hydro_forward.cpp:1171-1193``
     and ``scalar.cpp:221-237``);
  2. the census into ``EfStatus``;
  3. the theta ghost sync;
  4. the carry, for hydro only;
  5. the scale.

  It **posts** its corrections to the flux register (section 4) instead of
  writing ``_flux1/2/3`` in place. The scalar upper bound (C19) stays a
  scalar-only pre-pass that calls the same theta and scale.

``Sedimentation`` (``skeleton/EF/sedimentation_kernel.hpp``)
  One kernel for CPU and CUDA, with MPS through ``OnHost``, the way
  ``fix_vapor`` already runs on MPS (``eos_dispatch.cpp:116-117``). It takes
  ``SedKernelArgs``, which ``reset()`` builds once with persistent device
  buffers. The kernel takes the temperature and the species energy as
  **inputs**, computed by the EOS (``"W->T"`` and ``"W->E"``). That removes
  the EOS algebra from ``sed_hydro_impl.h:44-55,98-100``, the f_eps copy
  (``:15-27``) and the EOS-type branch (``sed_hydro.cpp:85-88``). The same path
  then serves ideal-moist and moist-mixture. The kernel **posts** the settling
  increment to the register.

**Declarations.** ``Floors`` and ``SpeciesRepair`` are declared in
``eos/equation_of_state.hpp`` and implemented in ``equation_of_state.cpp``,
where their code lives today. The skeleton gives them their own headers so
they can be reviewed apart. ``EfStatus`` is the only new source file
(``eos/ef_status.hpp``, header-only).

**One conversion base (D12, new in 1.1).** ``EquationOfStateImpl::compute``
handles ``"W->U"`` and ``"U->W"`` once and calls the virtual
``_prim2cons``/``_cons2prim``. Today the two branches are written out in
``ideal_gas.cpp:32-41``, ``shallow_water.cpp:16-25``, ``moist_base.cpp:34-43``
and ``aneos.cpp:14-23``. One helper ``_mom_from_vel_(prim, cons)``
(``mul_out`` of the velocity rows by density, then ``coord_vec_lower_``)
replaces the copies at ``ideal_gas.cpp:74-78``, ``shallow_water.cpp:59-63``
and ``moist_base.cpp:74-78``. The density rows stay per type because
moist-base stores the dry density. The ops and their order are unchanged, so the
result is bitwise. This is the "single conserved/primitive conversion" that
#350 left to do.

**ANEOS in the class tree (F1 decided: it stays).** ``ANEOSImpl`` keeps
deriving from ``EquationOfStateImpl`` and uses the same base dispatch and
helper (``aneos.cpp:14-23,57-59``). It keeps its own thermodynamics
(``ANEOSThermo`` in ``eos/aneos/aneos_thermo.hpp``: ``DP->TUL``,
``DU->PTL``, ``DT->PUL``) behind
``_prim2intEng``, ``_prim2temp`` and ``_temp2intEng``, and it uses the same
``Floors`` and ``EfStatus``. Two findings, both **not tested**, because ANEOS
cannot be built at the pin (C2):

* ``aneos.cpp:57-59,77-79`` never calls ``coord_vec_lower_`` or
  ``coord_vec_raise_``. The other types do. With the shared helper ANEOS
  gets the metric on curved grids. This is a correction, not a rounding
  change, and no deck can see it.
* ANEOS answers ``"W->L"``/``"WL->A"``, while the other types answer
  ``"W->A"``/``"WA->L"`` (``ideal_gas.cpp:53-61``). The callers branch on
  the type string to cope (``riemann/lmars.cpp:38,47``,
  ``riemann/hllc.cpp:66,76``, ``hydro/hydro.cpp:389,519``). One finding,
  **(hypothesis, untested)**: ``gamma_for(state)`` at ``hydro.cpp:519-521``
  evaluates ANEOS on ``w`` rather than on ``state``.

**EOS interface: EF's decision on Q5.** Lane R's provisional answer
proposes typed EOS methods with queryable capabilities, leaves the choice
to EF, and states that the register never calls the EOS. EF decides:

1. **Typed methods replace the string keys at the public interface.**
   ``EosInterface`` (skeleton ``eos_interface.hpp``) declares
   ``prim_from_cons_``, ``cons_from_prim_``, ``internal_energy``,
   ``temperature``, ``internal_energy_at`` and ``gamma_sound_``. Every type
   implements them, ANEOS included, on the one base from D12. Outside
   ``src/eos`` there are 53 ``peos->compute("...")``/``eos->compute("...")``
   calls in 14 files (``git grep -n 'peos->compute("\|eos->compute("' -- src``,
   minus ``src/eos``). They move to the typed methods.
   ``compute(ab)`` stays only **inside** the moist types, where it forwards
   to kintera (``moist_mixture.cpp:35-36,64-66``).
2. **One sound-speed contract.** ``gamma_sound_(w, gamma, cs)`` returns
   both. Ideal types fill them from ``W->A`` and ``WA->L``, ANEOS from
   ``W->L`` and ``WL->A``. The six ANEOS branches in the solvers and
   ``hydro.cpp`` go. This answers Q-C3 from EF's side; lane C confirms.
3. **Capabilities, not type names.** ``caps()`` returns an ``EosCap``
   bitmask (has temperature, has species, anomaly storage, FP32 implicit,
   closed-form moist). It replaces the 16 type-string checks outside
   ``src/eos`` (``git grep -nE 'type\(\) == "(ideal-gas|ideal-moist|moist-mixture|aneos|shallow-water)"' -- src``,
   minus ``src/eos``), e.g. ``hydro.cpp:192,505`` and ``roe.cpp:20``. Adding
   a type, or keeping ANEOS, then changes no caller.
4. **The register never calls the EOS.** EF drivers evaluate
   ``species_enthalpy``, ``species_energy`` and the temperature, then post
   the results. Lane R only stores and sums.
5. **Budget.** No line credit is taken in section 9. Most call sites are
   in other lanes' files (C: riemann; R: hydro). The EOS files lose their
   ``if (ab == ...)`` chains but gain the method overrides. I count this
   as about neutral: a **target**, not measured.

**Turbulence (C24).** V3 deletes ``src/turbulence`` (D11). It is not built,
so this changes no result. It has one clamp (halving ``k`` or ``eps``) and no
floor, and its eddy viscosity has no consumer: the live diffusion is
``forcing/diffusion.cpp``. If V3 wants a turbulence closure, it would be a
new forcing on two passive-scalar channels. Its sink would then be a
registered correction (requirement 7), and ``k`` and ``eps`` would get
floors that go through ``Floors``. That would be new code with its own
budget. It is not a port of this code. F6 proceeds on EF's proposal
(recorded for Cheng).

**Species energy (C21).** ``MoistEOSImpl`` gets one ``species_energy(w)``.
It returns ``rho*y*(species_enthalpy - pressure share)``, which replaces the
two ``_prim2speciesEng`` (``ideal_moist.cpp:270-292``,
``moist_mixture.cpp:89-108``). **(hypothesis)** It equals today's ``"W->E"``
to round-off for both types. Gate G-EF-9 checks this. The 919936da inventory
measured ideal-moist and moist-mixture ``W->E`` agreeing to 5.4e-13.

**Ownership.** ``Floors`` and ``SpeciesRepair`` belong to the EOS module.
``PositivityLimiter`` is stateless; it holds nothing beyond a borrowed
``EfStatus&`` and the coordinate. ``EfStatus`` belongs to the MeshBlock, one
per block, and the hydro and scalar modules write to it. Sedimentation keeps
its options and ``SedKernelArgs``.

**Data flow in one stage.** The names are lane R's provisional header
``543ff84f`` (section 4). ``reg`` is the hydro ``snap::FluxRegister``.

.. code-block:: text

   hydro_u --EOS U'->W (Floors, SpeciesRepair -> EfStatus)--> w
   [sweep]      x1 riemann: reg.slot(1,"riemann") / post_slot   (lane C, :845)
                Sedimentation(W->T, W->E) -> EF buffer sed
                  reg.add(1,"sedimentation",rows,sed)          (P1, :861-866)
   [reconcile]  reg.replace(1, <seam post>, seam)              (R rule, S transport, :882)
   [sweep]      x2/x3 riemann, covariance                      (lane C, :1050-1152)
   [limit]      reg.total(d) -> theta, td; theta sync (exchange, Q-R-d)
                reg.add(d,"positivity.carry",{IPR,IVX..IVZ},-c) (P3, x1: adv then sed)
                reg.scale(d,"positivity.withhold",species,factor) (P2)
   [divergence] du reads reg.total(d)
   scalars: own register (Q-R-b): riemann on hydro total[IDN] (R3, R4)
            add(d,"scalar.upper_bound",...) (P4); scale(d,"scalar.positivity.withhold",...) (P5)
   after the RK combine: EOS conserved limiter -> reg.cell_amount("eos.floor", vol_du)
   check_redo: EfStatus.snapshot() inside X's one stacked read (meshblock.cpp:1566)

4. Flux-register contract
=========================

**Source.** Lane R's provisional header ``docs/v3/skeleton/R/flux_register.hpp``
(118 lines) at ``happysky19/snapy`` ``543ff84f4adb4b79c3f43fa7c2f0a5a6eb54fa48``,
written by Tianhao as lane R's backup owner. I verified the sha with
``git ls-remote`` and read the header in full. It replaces Linfeng's
``fd3d68a`` answers, which revision 2.1 used. All names below are the
header's (namespace ``snap``). Where the header does not cover something
EF needs, I list it as an open question (**Q-R-a** to **Q-R-i**, end of this
section) and do not invent a name. The *post names* (the ``name`` strings)
are EF's own choice, because the header leaves names to the poster.

**What EF uses from the header** (``flux_register.hpp:N`` is a line of the
header):

* ``FluxRegister::add(dim, name, rows, increment)``: in place, in post
  order (``:16``, ``:74-75``);
* ``FluxRegister::scale(dim, name, rows, factor)``: ``total[rows] *=
  factor``, bitwise ``F *= theta``; the amount ``(factor-1)*F`` goes to the
  monitor (``:16-18``, ``:76-78``);
* ``FluxRegister::total(dim)``: a view at the caller's phase (``:20``,
  ``:89``);
* ``FluxRegister::cell_amount(name, vol_du)``: a cell increment for fixers
  and floors, kept as a monitor amount with no field (``:83-84``);
* ``FluxRegister::enter(RegisterPhase)`` with phases ``sweep`` (riemann,
  sedimentation, covariance), ``reconcile`` (seam ``replace``) and
  ``limit`` (positivity: ``scale`` withholds, ``add`` carries)
  (``:42-51``);
* ``RegisterMonitor``, owned by R: per-post FP64 ``amounts(name)``,
  ``counters()`` and ``retry_flags()``, stacked into X's one step-end read
  (``:21-22``, ``:96-104``);
* ``class Fixer`` (``:106-116``), the fixer and floor base;
* the units (``:5-8``): a post is a flux density per unit face area and
  time, before stage weights, in global components after coord's rotation.
  EF's increments use the same units. The scale factors are
  dimensionless;
* the 108 ``hydro_forward.cpp`` lines are R's deletions (``:24``), and the
  register makes no EOS call (``:20``).

.. list-table:: EF posts on lane R's register (header names; post names are EF's)
   :header-rows: 1
   :widths: 6 26 14 16 38

   * - id
     - call
     - phase
     - rows / dims
     - today's site; notes
   * - P1
     - ``add(1, "sedimentation", rows, sed)``
     - ``sweep``
     - species ``hydro_ids``, IVX..IVZ, IPR; x1
     - ``sed_hydro.cpp:36-40`` adds into ``_flux1`` in place
       (``hydro_forward.cpp:864``). ``sed`` is EF's own fixed buffer
       (see "P1 buffer" below). It comes after the x1 riemann ``slot`` and
       before the x1 seam ``replace`` (header order, ``:25``).
   * - P3
     - ``add(d, "positivity.carry", {IPR}, -c_E)`` and
       ``add(d, "positivity.carry", {IVX,IVY,IVZ}, -c_m)``; on x1 one
       pair for the advected part, then one for the settling part
     - ``limit``
     - IPR, IVX..IVZ; x1, x2, x3
     - ``flux_positivity.cpp:124-167``. Computed from the pre-scale species
       rows of ``total(d)``.
   * - P2
     - ``scale(d, "positivity.withhold", species, factor)`` with
       ``factor = where(F > 0, theta_lo, theta_hi)``
     - ``limit``
     - species rows; x1, x2, x3
     - ``flux_positivity.cpp:99-121``. Bitwise by the header's definition.
   * - P4
     - ``add(d, "scalar.upper_bound", rows, g - g*factor)``
     - ``limit`` (scalar register, Q-R-b)
     - scalar rows
     - ``scalar.cpp:199-214``, which adds ``h - g``.
   * - P5
     - ``scale(d, "scalar.positivity.withhold", rows, factor)``
     - ``limit`` (scalar register)
     - scalar rows
     - ``scalar.cpp:239``.
   * - F1
     - ``cell_amount("eos.floor", vol_du)``
     - after the RK combine (Q-R-e)
     - IDN, IPR (the amounts ``floor_dm``, ``floor_de``)
     - ``equation_of_state.cpp:213-290``. It replaces EF's own
       ``floor_dm``/``floor_de`` slots once the monitor carries them.

**Kept parts.** EF requests none. The header keeps a part as a field only
if it is requested (``:9-12``), and ``replace()`` reconciles kept parts at
seams (``:18-19``, ``:79-80``). EF's reads are:

* R1: ``total(d)``, species and IDN rows, in phase ``limit``, for theta and
  td.
* R2: no register read. The settling part is EF's own P1 buffer.
* R3: ``total(d)[IDN]`` of the hydro register, read by the scalar module
  (``scalar.cpp:99,166,170``). Which phase's total it reads is **Q-R-c**.
* R4: the hydro IDN row without the dry covariance post, for scalar
  laterals (``scalar.cpp:161``). The header keeps ``riemann.central`` (one
  summed dry + species mass row, ``:10-12``). **(hypothesis)** That is not
  the same quantity as ``mass - flux_covariance_dry``. **Q-R-c.**

Gravity work is lane R's and I's matter. The header keeps ``bflux1``
unscaled (``:19``), so EF's earlier offer is withdrawn.

**Ordering** (the header's order, ``:25-28``, with EF's posts):
``x1 riemann (:845) < P1 (:861-866) < x1 seam replace (:882) < x2/x3
riemann, covariance (:1050-1152) < [limit] theta sync < {P3, P2} (:1154-1252)
< divergence (:1254)``. On the scalar register: ``riemann_s, covariance_s <
P4 < P5 < divergence_s``.

**P1 buffer: unchanged, and now required.** The header has no per-face
read of a non-kept part (``:12``) and only one in-place write: ``slot`` for
the first post of a stage (``:71-73``). Sedimentation is not first, so P1
must be an ``add()`` of an increment tensor. That tensor is EF's fixed
buffer, filled by the sedimentation kernel, and EF reuses it as the
settling part for the carry split and the phi mask. ``keep()`` would not
reproduce the pin: a kept ``sedimentation`` part is reconciled at the x1
seam (``:18-19``), while the pin's ``fsed1`` is formed **before** the seam
average (``hydro_forward.cpp:865`` then ``:868-``). **(hypothesis)** At an
internal x1 seam the pin's ``fsed1`` can differ between the two ranks, so
the carry posted at that face may not be single-valued. That is the same
at the pin, and it is **Q-R-i**.

**Lane C's ``(theta-1)F`` form.** The header lists a conflict: C posts
positivity as ``(theta-1)F``, while R scales (``:29``). EF follows R's
``scale()``. An additive ``(theta-1)F`` summed onto ``F`` is not the same
float as ``F*theta``, so the species rows would no longer be bitwise.

**Bitwise answer: carry plus scale; the conclusion is unchanged.** The
header settles two of my conditions:

* ``scale()`` is bitwise ``F *= theta`` (``:16-18``), so species rows stay
  bitwise;
* ``add()`` is in place and in post order (``:16``), so the carry's
  ``E = (E - c_adv) - c_sed`` order is kept when EF posts the advected pair
  before the settling pair. That reproduces ``flux_positivity.cpp:154-159``.
  **(hypothesis until G-EF-1 runs.)**

The remaining difference is unchanged from revision 2.1. The pin's
settling part is ``(F_adv + sed) - F_adv`` (``hydro_forward.cpp:862-865``),
and EF uses ``sed``. That is a rounding change in the energy and momentum
rows of sedimenting decks only. To be bitwise, EF would need the
pre-sedimentation x1 species rows, a per-stage copy that requirement 9
forbids. The order between P3 and P2 is free (disjoint rows, both from one
pre-scale read). Scalars need only ``scale()``, plus the ``add()`` for P4.
The census diagnostic ``lim_cut`` is computed from ``factor``. The header's
monitor amount ``(factor-1)*F`` is signed, not ``|F|`` minus ``|F*theta|``, so
it does not replace ``lim_cut``.

**Floors and fixers.** EF's floors and repairs are local: per cell (the
conserved limiter, the cloud borrow) or per column (``fix_vapor``). None
needs the global sums of ``Fixer::partial_sums``/``apply`` (``:112-115``).
So EF proposes that they post ``cell_amount`` directly and are not
``Fixer`` subclasses. Whether X's registry (X-2) requires every floor to be
a ``Fixer`` is **Q-R-f**. The borrow and ``fix_vapor`` conserve mass by
construction; they post their (round-off) amounts as ``"eos.borrow"`` and
``"eos.fix_vapor"`` so that the monitor names them.

**Monitor and EfStatus.** R owns the monitor (``:21-22``), which answers
the old Q-R8. The header can read ``counters()`` and ``retry_flags()``
(``:102-103``) but has **no call to write a counter or set a retry flag**.
EF's counts are floor hits, NaN, vapor failures, heat capacity, positivity
hits, severe hits, scalar hits, the minimum theta and ``lim_cut``/
``lim_flux``. Until R adds such a call, ``EfStatus`` stays an EF-owned
device tensor, stacked into X's one read. Then its slots move to the
monitor (**Q-R-a**). ``floor_dm``/``floor_de`` move to
``cell_amount`` (post F1) now.

**Open questions for lane R (Tianhao), from the header:**

* **Q-R-a.** How does a poster add to ``counters()`` and set
  ``retry_flags()``? There is no write call. EF also needs a minimum
  (``pos_min``), not only sums.
* **Q-R-b.** Are passive scalars a separate ``FluxRegister`` (nvar = the
  number of scalars), or rows of the hydro register? P4 and P5 depend on
  it.
* **Q-R-c.** Which phase's ``total(d)[IDN]`` do scalars read (R3)? The pin
  reads ``phydro->flux<d>()`` after the hydro forward. And how does EF
  get the IDN row without the dry covariance post (R4)? A kept part, under
  which name?
* **Q-R-d.** The theta ghost sync is an exchange in phase ``limit``,
  between the totals read and ``scale()``. Is an exchange allowed there, or
  only in ``reconcile``?
* **Q-R-e.** ``cell_amount`` outside a stage: the conserved limiter and
  ``fix_vapor`` run after the RK combine (``meshblock.cpp:907-909``). Which
  weight applies there, and what shape is ``vol_du`` (per row, or a field)?
* **Q-R-f.** Must local floors be ``Fixer`` subclasses for X's registry,
  or may they post ``cell_amount`` directly?
* **Q-R-g.** The ``factor`` shape for ``scale()``: per face and per row
  (theta differs by species). Is broadcasting over ``rows`` defined?
* **Q-R-h.** Post-name convention: EF proposes ``sedimentation``,
  ``positivity.carry``, ``positivity.withhold``, ``scalar.upper_bound``,
  ``scalar.positivity.withhold``, ``eos.floor``, ``eos.borrow`` and
  ``eos.fix_vapor``. Does that match yours?
* **Q-R-i.** The carry at internal x1 seams: the settling part is
  unreconciled, as at the pin. Should a second ``replace()`` follow the
  carry ``add()`` on IPR and IVX..IVZ, or do you accept the pin's
  behaviour? **(hypothesis: the carry may be two-valued there.)**

5. Invariants and gates
=======================

The tests named here exist at the pin (``ls tests``, ``tests/CMakeLists.txt``).
Names that start with ``G-EF`` are new gates this design adds.

.. list-table::
   :header-rows: 1
   :widths: 6 34 36 24

   * - id
     - identity
     - gate (existing test, or new)
     - kind
   * - I1
     - Species mass is conserved through the limiter: each face is scaled by
       one donor factor (``flux_positivity.hpp:61-64``).
     - ``test_conservation_budget`` (+ ``_cuda``, ``_mp``), ``test_flux_positivity``
     - tolerance (round-off of the budget sum)
   * - I2
     - Transport never drives a species negative in a stage
       (``flux_positivity.hpp:51-59``).
     - ``test_flux_positivity``, ``test_flux_positivity_cubedsphere{,_moist}{,_cuda}``
     - exact (``>= 0``)
   * - I3
     - The withheld mass keeps its energy and momentum (#269).
     - ``test_flux_positivity_carry``
     - tolerance
   * - I4
     - A uniform ratio stays uniform when the limiter fires (#338).
     - ``test_tracer_ratio``, ``test_scalar_stratified``
     - tolerance
   * - I5
     - The column vapor repair keeps ``sum(vapor*vol)`` (#241) and counts
       every failure.
     - ``test_fix_vapor_volume``, ``test_fix_vapor_deficit``,
       ``test_fix_vapor_counts_every_column``,
       ``test_fix_vapor_reports_failure{,_cuda}``, ``test_fix_vapor_stale_count{,_cuda}``,
       ``test_check_redo_vapor_deficit``, ``test_vapor_column_nb1``
     - tolerance (mass); exact (counts)
   * - I6
     - The cloud-to-parent borrow conserves mass and elements.
     - ``test_parentless_cloud{,_nb1,_nb1_mp}``, ``test_condensate_conservation``
     - tolerance
   * - I7
     - Floors hold in total and anomaly storage; an active FP32 anomaly floor
       reconstructs to at least the floor (``equation_of_state.cpp:37-46``).
     - ``test_face_floor``, ``test_check_redo_floor``, ``test_abnormal_exit_floor``,
       the ``fp32-foundations`` label
     - exact
   * - I8
     - Sedimentation upwinds, seals the walls and gives a single-valued seam
       flux.
     - ``test_gravity_sedimentation``, ``test_stokes_sedimentation``,
       ``test_sedimentation_guards``, ``test_sedimentation_cubed_seam{,_gloo}``
     - tolerance
   * - I9
     - Scalars: positivity, the upper bound, covariance rows.
     - ``test_scalar``, ``test_scalar_upper_bound_donor{,_cuda}``,
       ``test_scalar_source_bound``, ``test_scalar_flux_covariance{,_cuda}``,
       ``test_scalar_cov_x1_split``, ``test_tracer_dry_convention``
     - tolerance
   * - I10
     - EOS round trips: W->U->W, and UT->I(T(w)) == W->I.
     - ``test_eos``, ``test_eos_temp2inteng``, ``test_eos_species_registry``
     - tolerance
   * - I11
     - Theta is single-valued across ranks and panels.
     - ``test_flux_positivity_cubedsphere``, ``test_check_redo_parallel``
     - exact
   * - G-EF-1
     - **new**: the sum of the register posts equals the pin's in-place
       ``_flux1/2/3`` after step 4.C.
     - a C++ test comparing the register build against a main build on the
       moist carry deck (``tests/test_flux_positivity_carry.yaml``)
     - **bitwise** on species rows (scale post, Q3) and on decks without
       sedimentation; on sedimenting decks, the energy and momentum rows
       within a stated tolerance (section 4, "Bitwise answer")
   * - G-EF-2
     - **new**: ``EfStatus`` gives the same redo causes as today's marks.
     - replay ``test_check_redo_*`` and ``run_straka_redo``, comparing the
       cause bit vectors
     - exact
   * - G-EF-3
     - **new**: graph replay equals eager for the limiter, vapor repair and
       sedimentation.
     - a moist, sedimenting, limiter-on column: 2 captures, 10 replays,
       injected NaN and vapor deficit (G1/G2)
     - bitwise against eager on the same device
   * - G-EF-4
     - **new**: the shared ``PositivityLimiter`` equals today's scalar path.
     - ``test_scalar_*`` outputs, before and after EF-4
     - bitwise
   * - G-EF-9
     - **new**: the base ``species_energy`` equals ``"W->E"`` and the single
       sedimentation kernel equals both old paths.
     - ideal-moist and moist-mixture, CPU and CUDA, on
       ``tests/test_gravity_sedimentation.yaml`` and ``examples/uranus.yaml``
       (short)
     - tolerance: 1e-12 relative **(hypothesis; set from the measurement
       before EF-5 merges)**

6. FP32 contract
================

.. list-table::
   :header-rows: 1
   :widths: 26 16 16 42

   * - quantity
     - storage
     - compute
     - FP64 mandatory? why (site)
   * - species rows of ``hydro_u``
     - state dtype (FP32 under M4)
     - state dtype
     - no
   * - primitives ``w`` under ``fp32()``
     - **FP64**
     - FP64
     - Yes, as today. ``"U'->W"`` allocates ``w`` in FP64
       (``ideal_moist.cpp:176-180``) and the perturbation EOS is FP64
       (``:89``).
   * - anomaly floor bound
     - FP32 anomaly
     - FP64 bound, then ``nextafter``
     - Yes. A rounded bound can reconstruct below the floor
       (``equation_of_state.cpp:37-46,277``).
   * - limiter energy floor ``UT->I``
     - —
     - FP64 when storage is a float anomaly
     - Yes (``equation_of_state.cpp:277``).
   * - theta margin and round-off bounds
     - —
     - dtype-aware
     - The constants are per dtype (``flux_positivity.hpp:18-33``). The
       margin uses ``machine_epsilon(u.dtype)`` (``flux_positivity.cpp:73``).
       **FP32 hazard:** ``drain.clamp_min(1e-300)`` (``:78``) becomes 0 in
       FP32. Only the branch that ``where`` discards sees it today. The design
       uses ``finfo(dtype).tiny``, which is bitwise in FP64.
   * - positivity census
     - device counters
     - FP64 (``wide``); FP32 on MPS
     - Yes. Sums over the block (``hydro_forward.cpp:373,1196-1222``).
       Policy: "cast before reductions" (roadmap M4).
   * - fix_vapor column sums
     - state dtype
     - state dtype today (``fix_vapor_impl.h:32-39``)
     - **(hypothesis)** FP32 sums break ``test_fix_vapor_volume`` at its
       current tolerance. Proposal: accumulate in FP64 inside the kernel
       (``acc_t``) when ``T=float``. This is a rounding change in FP32 only.
   * - sedimentation
     - state dtype
     - FP32 when ``fp32()`` (``hydro_forward.cpp:864``)
     - No. Buffers ``radius``, ``density`` and ``const_vsed`` are FP64
       (``sed_vel.cpp:24-31``) and cast on every call
       (``sed_hydro.cpp:117-123``). The design casts them once at
       ``reset()``/``to()``.
   * - scalar flux buffers
     - registered FP64 (``scalar.cpp:62-72``), then rebound by ``set_data``
       (``:98,166,170,242``)
     - riemann output dtype
     - No. The design allocates them in the compute dtype, fixed storage.
   * - EOS constants ``inv_mu_ratio_m1``, ``cv_ratio_m1``, ``u0``
     - FP64 buffers (``ideal_moist.cpp:34-55``)
     - cast to the call dtype (``ideal_moist.cpp:256,354,369``)
     - The masters stay FP64. A per-dtype cache follows roadmap M1.
   * - ``EfStatus``
     - int64 / bool / FP64 slots
     - —
     - Counters and minima are FP64 or int64 in every precision.

7. CUDA-graph contract
======================

Counted in the 36 EF files with
``grep -n "\.item<\|\.item()"``, ``grep -n "kFloat64\|kDouble"`` and
``grep -n "\.set_(\|set_data("``: **5 host reads, 16 hard FP64 dtype sites,
10 set_/set_data sites.**

.. list-table:: Host reads (``.item``)
   :header-rows: 1
   :widths: 30 40 30

   * - site
     - when it runs
     - design / G stage
   * - ``eos/eos_dispatch.cu:78``
     - Only when vapor failures are not deferred. Inside a stage they are
       deferred (``meshblock.cpp:688-701``).
     - The sink becomes ``EfStatus::vapor_fail``. Callers outside a stage keep
       the read. G1/G2.
   * - ``eos/ideal_moist.cpp:149``
     - Only when ``defer_check`` is false. Hydro passes true
       (``hydro_forward.cpp:413-414``).
     - The flag moves to ``EfStatus::heat_capacity``. G1.
   * - ``eos/moist_base.cpp:19``
     - ``reset()`` (setup)
     - Allowed outside capture. Read ``thermo->mu()`` on the host instead, as
       ``ideal_moist.cpp:100-117`` already does.
   * - ``eos/moist_base.cpp:23,28``
     - At **run time**: ``IdealMoistImpl::specific_heat_cv``
       (``ideal_moist.cpp:61``) calls ``species_cv_ref()``, and forcings call
       that every stage (``forcing/diffusion.cpp:566``, ``body_heat.cpp:49``,
       ``relax_bot_temp.cpp:69``).
     - **(hypothesis)** On CUDA this is a device-to-host sync per call, if
       ``pthermo->inv_mu`` lives on the device after ``to(cuda)``. The design
       caches it on the host from ``thermo->mu()`` and ``cref_R()``. G2.

.. list-table:: Allocations, rebinding and host-state branches
   :header-rows: 1
   :widths: 30 40 30

   * - site
     - hazard
     - design / G stage
   * - ``eos/equation_of_state.hpp:184-193,209`` (``pending_marks_``)
     - A host vector is pushed during capture and not on replay, so the marks
       would be lost on replay.
     - ``EfStatus`` in-place writes. G1 (named in the roadmap, G1 bullet 4).
   * - ``eos/equation_of_state.cpp:358-360`` (lazy ``vapor_failures_``)
     - The first-use allocation inside a stage.
     - Preallocated in ``EfStatus``. G1.
   * - ``eos/moist_mixture.cpp:64-65,189-190`` (``ivol.set_``, ``temp.set_``)
     - Rebinds the buffers. ``_ensure_cache`` decides on the host from
       ``prim._version()`` (``:175-192``). **(hypothesis)** A graph captured
       on a cache hit would replay without recomputing ``ivol`` and ``temp``,
       so the values would be stale.
     - Fixed buffers, ``copy_``, and always recompute inside captured
       segments. G2.
   * - ``scalar/scalar.cpp:98,166,170,242`` (``set_data``)
     - Rebinds registered buffers every stage.
     - Fixed storage; the register owns the face arrays. G1.
   * - ``sedimentation/sed_hydro.cpp:35,93`` (``vsed.set_data``)
     - Allocates and rebinds every call. ``:100-123`` makes 8 dtype or device
       copies per call.
     - ``SedKernelArgs`` built at ``reset()``/``to()``. G2.
   * - ``hydro/hydro_forward.cpp:862-865`` (``fadv`` clone)
     - A full species-flux copy per stage.
     - Removed by read R2. G1.
   * - ``hydro/hydro_forward.cpp:1202-1216`` (cell-volume cache)
     - A host branch on ``_version()``.
     - Use the coordinate's cached volume (lane S, Q-S4). G1.

**Data-dependent branches.** None in EF code depends on device values today.
The branches at ``equation_of_state.cpp:262-266,307-317,340-341`` and
``hydro_forward.cpp:1165`` depend on options and layout only. They are fixed
for a graph's lifetime, and they belong in the graph key (configuration
generation, roadmap "Execution design").

**Segment boundaries EF causes:**

* B1: the theta sync for hydro (``hydro_forward.cpp:1227``);
* B2: the theta sync for scalars (``scalar.cpp:205,239``), up to two
  exchanges;
* B3: the whole-column vapor repair when ``pz > 1``, through ``gather_x1``
  (``equation_of_state.cpp:340-347``);
* B4: kintera's ``VU->T`` and ``PV->T`` iterations, which read on the host
  every iteration (``kintera:src/thermo/thermo_y.cpp:480,525``) and are used
  by moist-mixture (``moist_mixture.cpp:65,190``).

B1 and B2 are exchanges (G4 and G6). B3 is G4 with ``nb1 > 1``. B4 is lane K
(G2). The design asks lane S to batch B1 and B2 into one exchange (Q-S1).

**Mapping to G0-G7:**

* G0: this inventory.
* G1: ``EfStatus``, fixed scalar storage, no ``fadv`` clone.
* G2: vapor repair, sedimentation, species positivity, the moist-mixture
  cache, host-cached constants; kintera B4.
* G3: none in EF. VIC reads the positivity margin (Q-I1).
* G4: B1-B3.
* G5: FP32 cubed-sphere positivity and the FP32 fix_vapor accumulation.
* G6: the joint matrix with sedimentation and positivity.
* G7: no EF-specific item.

8. Cross-repository interface changes and their merge order
===========================================================

The provider merges first in every case.

1. **kintera (lane K provides)**:

   (a) capture-safe ``VU->T`` and ``PV->T`` without a host convergence read
       each iteration (``kintera:src/thermo/thermo_y.cpp:480,525``);
   (b) a device failure counter with reset, accumulate and consume. snapy
       today takes the counter by assigning ``pthermo->nfail_ = Tensor()``
       (``meshblock.cpp:1544-1547``) and through
       ``take_saturation_adjustment_failures`` (``kintera:src/thermo/thermo.hpp:166``,
       which reads at ``thermo_y.cpp:402``).

   EF consumes (b) through ``EfStatus`` only if lane K and the mesh lane agree
   that saturation failures join it. Otherwise EF does not need them. EF needs
   (a) for moist-mixture graph capture (G2). Ideal-moist does not call these
   keys on the U->W path (``ideal_moist.cpp:209-231``).
2. **pyharp, pydisort**: no EF change.
3. **snapy, internal provider order**: lane R's register PR merges before EF-3
   (section 10). The coordinate's cached cell volume merges before EF-4, if
   lane C or R adds one.

No EF change edits kintera's public API. The EOS keeps calling ``ThermoY``
through ``compute("DY->V" | "VU->T" | "PV->T" | "VT->P" | "VT->U")``
(``moist_mixture.cpp:35-36,64-66,81,189-190``).

9. Line budget
==============

**One budget, ANEOS kept** (Cheng's decision on F1). "Now" is ``wc -l``
at pin ``9e5de2d4``. Each value was checked against
``git show 9e5de2d4:src/<file> | wc -l`` by the script that builds this
table. **Every "after" number is a target**, a design estimate, not a
measurement. The baseline is 4,971 lines, with ``src/turbulence``; the 108
``hydro_forward.cpp`` lines are lane R's. The ceiling is 3,976
(floor(0.8 x 4,971)).

Deletion ids:

* *D1 (ANEOS removal) is withdrawn.* ANEOS stays in the class tree and
  shares the base (D12).
* **D2**: the MPS ideal-gas copy.
* **D3**: code that never runs (commented out, or no callers).
* **D4**: ``EfStatus`` (its new header is counted).
* **D5**: the single floor encoder.
* **D6**: the single species energy.
* **D7**: the single ``PositivityLimiter``.
* **D8**: the single sedimentation kernel.
* **D9**: dimension loops in the positivity primitives.
* **D10**: register reads (R2) replace clones and caches.
* **D11**: ``src/turbulence``, not compiled (C24; F6, proceeding on EF's
  proposal, deletion counted, recorded for Cheng).
* **D12**: one ``W->U``/``U->W`` dispatch and momentum helper in the base,
  used by ideal-gas, shallow-water, the moist base and ANEOS.
* **D13**: one YAML reader for the three per-particle sedimentation keys.
* **D14**: ``SedVel`` folded into ``SedHydro``. No caller outside
  ``src/sedimentation`` names it (``grep -rn``).

.. list-table:: EF budget, revision 2, ANEOS kept (after = **target**, not measured)
   :header-rows: 1
   :widths: 32 8 10 8 42

   * - file (``src/``)
     - now
     - after (target)
     - delta
     - deletions named
   * - ``eos/aneos/aneos_thermo_dummy.cpp``
     - 34
     - 34
     - +0
     - kept (F1 decided: ANEOS stays)
   * - ``eos/aneos/aneos_thermo.hpp``
     - 50
     - 50
     - +0
     - kept (F1 decided: ANEOS stays)
   * - ``eos/aneos.cpp``
     - 111
     - 98
     - -13
     - kept (F1 decided); D12 dispatch :14-23 and momentum :57-59 -> base (-13)
   * - ``eos/aneos.hpp``
     - 86
     - 86
     - +0
     - kept (F1 decided: ANEOS stays)
   * - ``eos/eos_dispatch.cpp``
     - 119
     - 83
     - -36
     - D2 MPS ideal-gas copy :42-59; D3 commented moist kernel :61-78
   * - ``eos/eos_dispatch.cu``
     - 89
     - 69
     - -20
     - D3 commented :32-50, :87
   * - ``eos/eos_dispatch.hpp``
     - 19
     - 19
     - +0
     - unchanged
   * - ``eos/equation_of_state.cpp``
     - 456
     - 423
     - -33
     - D4 mark queues -> EfStatus; D5 one anomaly/total floor helper (:244-251, :281-288); commented :200-203, :253-257; D12 base W->U/U->W dispatch and _mom_from_vel_ (+15); floor_dm/de tally (+6) (ANEOS factory lines :447-448 kept)
   * - ``eos/equation_of_state.hpp``
     - 221
     - 208
     - -13
     - D4 ``pending_marks_``, ``limiter_marks_``, ``vapor_failures_`` (:177-209) -> ``EfStatus``; Floors struct (+20); D12 decls (+3)
   * - ``eos/fix_vapor_impl.h``
     - 92
     - 92
     - +0
     - unchanged
   * - ``eos/ideal_gas.cpp``
     - 120
     - 105
     - -15
     - unchanged; D12 dispatch :32-41 and momentum :74-78 -> base
   * - ``eos/ideal_gas.hpp``
     - 68
     - 68
     - +0
     - unchanged
   * - ``eos/ideal_gas_impl.h``
     - 40
     - 40
     - +0
     - unchanged
   * - ``eos/ideal_moist.cpp``
     - 372
     - 345
     - -27
     - D6 _prim2speciesEng :270-292 -> base; gammad expr x3
   * - ``eos/ideal_moist.hpp``
     - 126
     - 122
     - -4
     - D6
   * - ``eos/ideal_moist_impl.h``
     - 63
     - 30
     - -33
     - D3 never-instantiated cons2prim :34-55 + macros
   * - ``eos/moist_base.cpp``
     - 125
     - 125
     - +0
     - + base species energy; host-cached weights (no .item); D12 dispatch :34-43 -> base
   * - ``eos/moist_base.hpp``
     - 76
     - 80
     - +4
     - + decls
   * - ``eos/moist_mixture.cpp``
     - 194
     - 172
     - -22
     - D6 _prim2speciesEng :89-108
   * - ``eos/moist_mixture.hpp``
     - 116
     - 114
     - -2
     - D6
   * - ``eos/shallow_water.cpp``
     - 68
     - 53
     - -15
     - unchanged; D12 dispatch :16-25 and momentum :59-63 -> base
   * - ``eos/shallow_water.hpp``
     - 49
     - 49
     - +0
     - unchanged
   * - ``eos/shallow_water_impl.h``
     - 22
     - 16
     - -6
     - D3 side_quantities :11-15 (0 callers)
   * - ``hydro/flux_positivity.cpp``
     - 195
     - 235
     - +40
     - + limiter driver; D9 per-dim blocks -> one loop (:45-67, :98-121)
   * - ``hydro/flux_positivity.hpp``
     - 151
     - 175
     - +24
     - + PositivityLimiter decl
   * - ``scalar/scalar.cpp``
     - 258
     - 195
     - -63
     - D7 positivity pipeline :173-240 -> PositivityLimiter
   * - ``scalar/scalar.hpp``
     - 135
     - 128
     - -7
     - D7 _positivity_hits -> EfStatus
   * - ``scalar/scalar_options.cpp``
     - 65
     - 65
     - +0
     - unchanged
   * - ``sedimentation/sed_hydro.cpp``
     - 139
     - 87
     - -52
     - D8 generic tensor path :18-43; per-call arg assembly :85-126 -> SedKernelArgs at reset; D14 +12 for the folded buffers
   * - ``sedimentation/sed_hydro_dispatch.cpp``
     - 224
     - 60
     - -164
     - D8 MPS copy :159-212, feps copy :85-100, arg checks :23-83 -> struct
   * - ``sedimentation/sed_hydro_dispatch.cu``
     - 75
     - 45
     - -30
     - D8 23-arg signature -> struct
   * - ``sedimentation/sed_hydro_dispatch.hpp``
     - 50
     - 30
     - -20
     - D8 tensor upwind :12-24; typedef
   * - ``sedimentation/sed_hydro_impl.h``
     - 143
     - 80
     - -63
     - D8 feps copy :15-27; EOS math (temp, ke, species energy) -> inputs
   * - ``sedimentation/sedimentation.hpp``
     - 193
     - 150
     - -43
     - D8 SedVel::forward decl, vsed cache; D14 SedVelImpl class :107-151 folded into SedHydroImpl (3 buffers kept)
   * - ``sedimentation/sed_options.cpp``
     - 144
     - 120
     - -24
     - unchanged; D13 three name loops :55-68 and three value loops :87-109 -> one helper over the three keys
   * - ``sedimentation/sed_vel.cpp``
     - 81
     - 0
     - -81
     - D8 tensor Stokes forward :34-71 (kernel is the one copy); D14 file removed; reset() buffers move to sed_hydro.cpp
   * - ``eos/ef_status.hpp (new)``
     - 0
     - 45
     - +45
     - D4 EfStatus, header-only (skeleton 50 lines with comments); missing from rev 1
   * - ``turbulence/k_epsilon_turbulence.cpp``
     - 218
     - 0
     - -218
     - D11 not compiled, no caller (C24); F6 proceeding, recorded for Cheng
   * - ``turbulence/turbulence_model.cpp``
     - 68
     - 0
     - -68
     - D11 not compiled, no caller (C24); F6 proceeding, recorded for Cheng
   * - ``turbulence/turbulence_model.hpp``
     - 116
     - 0
     - -116
     - D11 not compiled, no caller (C24); F6 proceeding, recorded for Cheng
   * - **EF lane total (40 rows)**
     - **4971**
     - **3896**
     - **-1075**
     - **21.6% reduction; ceiling 3976, 80 lines under**

**Where the cut comes from (by directory, targets):**

.. list-table::
   :header-rows: 1
   :widths: 34 12 12 12 30

   * - directory
     - now
     - after
     - delta
     - main ids
   * - ``src/sedimentation``
     - 1,049
     - 572
     - -477
     - D8, D13, D14
   * - ``src/turbulence``
     - 402
     - 0
     - -402
     - D11
   * - ``src/eos`` (incl. new ``ef_status.hpp`` +45)
     - 2,716
     - 2,526
     - -190
     - D2-D6, D12
   * - ``src/scalar``
     - 458
     - 388
     - -70
     - D7
   * - ``src/hydro/flux_positivity.*``
     - 346
     - 410
     - +64
     - takes the step 4.C body from lane R's lines
   * - **total**
     - **4,971**
     - **3,896**
     - **-1,075 (21.6%)**
     - 80 under the ceiling

**Honesty notes.**

* The lane reaches 20% with ANEOS kept **only with D11** (deleting
  ``src/turbulence``, F6, proceeding on EF's proposal). With turbulence kept, "after" is 4,298
  (13.5%), **322 lines over** the ceiling. I know of no other dead or
  duplicated EF code that large. The candidates would be F5 (a standalone
  proposal, below) and typed EOS methods (section 3, Q5). Neither is
  counted, and neither would close 322 lines.
* The margin is 80 lines. The largest estimate is D8 (-400 across seven
  sedimentation files). If D8 delivers 81 or more lines (20%) less than its
  target, the lane misses. I will replace the D8 target with a measured
  count when EF-6 is prototyped.
* ``flux_positivity.*`` grows by 64 because it takes over the step 4.C
  logic. The 99 + 9 lines it replaces are deleted in lane R's count.
* The 108 lines and #370's later +8 in EF files are not in this table
  (section 10).

Lines touched outside EF that the design deletes are not counted here:

* the ``bflux1`` clone and its seam row, ``hydro_forward.cpp:846-848,902-917``
  (gravity work, lane I);
* the ``HydroImpl`` positivity buffers, ``hydro.hpp:265-271,472,476`` and
  ``hydro.cpp:276-286`` (lane R);
* the ``limiter_hits`` and ``floor_hit`` duplicates, ``meshblock.cpp:1417-1446``
  (lane X);
* the ``"mut"`` output name, ``output/output_utils.cpp:55`` (lane O).

10. Migration
=============

Each PR is small and has one owner. "Bitwise" means bitwise against main on
CPU and CUDA at the same dtype, on the gates of section 5.

.. list-table::
   :header-rows: 1
   :widths: 7 37 14 42

   * - PR
     - content
     - vs main
     - removed; reason for any rounding change
   * - EF-1
     - D3 and D2: code that never runs, and the MPS ideal-gas copy
       (``eos_dispatch.cpp:42-78``, ``eos_dispatch.cu:32-50``,
       ``ideal_moist_impl.h:34-55``, ``shallow_water_impl.h:11-15``). MPS
       ideal-gas goes through ``OnHost``, as ``fix_vapor`` does.
     - bitwise (CPU/CUDA)
     - On MPS the ideal-gas path changes from a path that throws (measured at
       919936da) to a host round-trip.
   * - EF-2
     - D4: ``EfStatus`` replaces the mark queues, ``vapor_failures_``, the
       heat-capacity latch and the positivity counters.
     - bitwise
     - Gate G-EF-2. Removes ``pending_marks_``. Needs the mesh owner's review
       (``meshblock.cpp:1506-1566``).
   * - EF-3
     - P1, P2, P3 and reads R1 and R2 on lane R's register (D10). Removes the
       ``fadv`` clone.
     - species rows bitwise (scale post); E and momentum rows bitwise
       without sedimentation, rounding with it
     - Section 4, "Bitwise answer": the carry is an in-place additive
       post (adv, then sed). The settling part is the kernel's increment,
       not ``(F_adv + sed) - F_adv``, so the ``fadv`` copy goes.
   * - EF-4
     - D7 and D9: one ``PositivityLimiter`` for species and scalars (P4, P5,
       R3, R4).
     - bitwise **(hypothesis)**, gate G-EF-4
     - Removes ``scalar.cpp:219-240`` and ``hydro_forward.cpp:1171-1252``
       body. Same op order kept.
   * - EF-5
     - D5: the single floor encoder; ``Floors::admissible`` shared by conv4
       and redo.
     - bitwise
     - Same expressions, factored.
   * - EF-6
     - D8: one sedimentation kernel; temperature and species energy taken
       from the EOS; ``SedKernelArgs`` at reset; MPS through ``OnHost``.
     - **rounding**
     - The op order changes for ideal-moist (EOS ``W->T``/``W->E`` against
       the kernel's inline algebra), and moist-mixture moves from tensor
       Stokes to the kernel. Gate G-EF-9. If the measurement shows a change
       beyond round-off, this becomes **FOR CHENG F3**.
   * - EF-7
     - D6: the base ``species_energy``.
     - **rounding**
     - Gate G-EF-9.
   * - EF-8
     - Graph preparation: fixed buffers in moist-mixture, scalar and
       sedimentation; host-cached weights (``moist_base.cpp:19-28``); FP32
       tiny (``flux_positivity.cpp:78``).
     - bitwise FP64; FP32 rounding only in FP32 fix_vapor (FP64 accumulator)
     - G1/G2. The moist-mixture capture needs kintera's capture-safe
       ``VU->T``/``PV->T`` (section 8) first.
   * - EF-10
     - D11: remove ``src/turbulence``.
     - bitwise (not compiled)
     - F6 (proceeding; recorded for Cheng). No build, test or deck changes.
   * - EF-11
     - D12: the base ``W->U``/``U->W`` dispatch and ``_mom_from_vel_``.
     - bitwise
     - The same ops in the same order, factored.
   * - EF-12
     - D13 and D14: the single sedimentation YAML reader, and ``SedVel``
       folded into ``SedHydro``.
     - bitwise
     - Module buffer names change (``sedvel.radius`` -> ``radius``). They are
       rebuilt from YAML at ``reset()`` (requirement 10). **Not checked**:
       whether any restart or ``state_dict`` reader keys on the old names.

**Order:** EF-1, EF-2, EF-5, EF-11 (independent) → [lane R register] →
EF-3 → EF-4 → EF-6 → EF-12 → EF-7 → [kintera K] → EF-8. EF-10 merges
on its own (F6 proceeds; nothing waits on it). (There is no EF-9 any more: it was the ANEOS
removal.)

**Absorbing #370.** #370 ("sync positivity-carry enthalpy and donor velocity
across cubed-sphere seams") is not in the baseline. It merged after the pin
as ``730b35007d16389c64116e4bf9d2fe93707e29e9``, the pin's direct child
(``git rev-list --count 9e5de2d4..730b3500`` = 1). I have read its diff. I
have not built it or run its tests. It does two things at step 4.C:

(a) it ghost-syncs ``hspec`` with theta's raw seam copy (key
    ``"hydro_hspec"``);
(b) on the cubed sphere only, it exchanges each lateral donor's velocity as
    a face state (``hydro_vlo:+``/``hydro_vhi:-``), rotates it to the
    face's flux basis and passes ``vface2``/``vface3`` to
    ``flux_positivity_carry_``.

The design takes both in as follows:

1. **Inputs, not code paths.** ``PositivityInputs`` gets ``vface[2]``
   (skeleton). P3 uses ``vface`` where it is defined and the cell velocity
   otherwise, as #370's ``carry`` lambda does. The hspec ghost layer is
   simply valid on input.
2. **One exchange.** The ``hydro_hspec`` sync and the two face-velocity
   exchanges join the batched theta exchange (B1, Q-S1). #370 opens one
   extra exchange per lateral dimension inside the stage. With the batch,
   the stage keeps one segment boundary for EF.
3. **Requirement 9.** #370 allocates two ``zeros_like(w)`` full fields per
   lateral dimension per stage (four on the cubed sphere). The design
   replaces them with fixed buffers of only the three velocity rows,
   allocated at setup, or with the seam face states lane S already
   exchanges for the Riemann solver, if they carry the donor velocity
   **(hypothesis; Q-S2)**.
4. **Requirement 5.** For the carry, the donor side's ``hspec`` and
   velocity are authoritative. Both copies of a seam face withhold the
   same energy and momentum, because they read the same donor values.
   This is the reconciliation rule EF asks lane S to state once for every
   donor-valued correction.
5. **Gates and lines.** G-EF-1 and G-EF-4 take the reference "main at the
   time EF-3 branches". If that main includes #370, they compare against
   it. #370 adds 8 lines to EF files (195 -> 198, 151 -> 156). Those lines
   go in the EF "after" column of the revision that follows the rebase. Its
   +49 net lines in ``hydro_forward.cpp`` are lane R's. Under the design,
   about 40 of them (the exchange block) move into the batched sync. That
   is a **target**, not counted here.

**Options and code paths removed:**

* the ``src/turbulence`` directory (EF-10). It had no snapy YAML key; its
  ``hydro/turbulence`` key belonged to Athena++'s ``ParameterInput``.
* the MPS tensor copies of ideal-gas and sedimentation;
* the generic tensor sedimentation path (moist-mixture moves to the kernel);
* ``SedVelImpl::forward``.

No YAML key is removed. No default changes.

FOR CHENG
---------

**Decided.** *F1 (remove ANEOS): no, ANEOS stays* (Cheng, in the EF lane
thread, 2026-11-17). It is off the kill list. It stays in the class tree on
the shared base, and section 9 counts its 281 lines as kept (``aneos.cpp``
111 -> 98, a target, from D12). *F2 is withdrawn*: #370 is not in the
baseline, and section 10, "Absorbing #370", covers it.

**F3. Sedimentation results** (open; I am proceeding on this proposal).

.. list-table::
   :header-rows: 1
   :widths: 22 78

   * - item
     - proposal
   * - what changes
     - EF-6: one sedimentation kernel takes T and the species energy from
       the EOS (``"W->T"``, ``"W->E"``). Moist-mixture moves from the tensor
       Stokes path to the kernel. EF-7: one base ``species_energy``.
   * - decks touched
     - Every deck with a ``sedimentation`` block. Moist-mixture decks change
       path (``examples/uranus.yaml``).
   * - expected result change
     - Round-off, from the new op order **(hypothesis)**.
   * - gate
     - G-EF-9: 1e-12 relative on ``tests/test_gravity_sedimentation.yaml`` and
       a short ``examples/uranus.yaml``, CPU and CUDA. The tolerance is set
       from the measurement before EF-6 merges.
   * - if the gate fails
     - EF-6 keeps the kernel's inline algebra for ideal-moist and I bring
       the measured difference back to you. The ``sed_hydro_impl.h`` target
       (80) would then rise, by an amount not yet estimated, which eats into
       the 80-line margin.

**F4. MPS support level** (open; I am proceeding on this proposal).

.. list-table::
   :header-rows: 1
   :widths: 26 24 50

   * - path on MPS
     - today
     - proposal
   * - ideal-gas ``U->W``
     - a tensor copy (``eos_dispatch.cpp:42-59``) that threw at 919936da
     - the one kernel through ``OnHost``, as ``fix_vapor`` already does
       (``eos_dispatch.cpp:116-117``). Same math; a host round-trip per
       call.
   * - sedimentation flux
     - a tensor copy (``sed_hydro_dispatch.cpp:159-212``)
     - the one kernel through ``OnHost``. Same math, slower on MPS **(not
       measured)**.
   * - CPU, CUDA
     - unchanged
     - unchanged

**F5. One moist EOS** (standalone proposal; undecided, not counted in
section 9). Fold ``moist-mixture`` into ``ideal-moist`` (or the reverse).
What changes:

.. list-table::
   :header-rows: 1
   :widths: 26 74

   * - item
     - change (grep at the pin)
   * - decks that set ``type: moist-mixture``
     - 4 of the repository's YAMLs: ``examples/uranus.yaml``,
       ``tests/test_eos.yaml``, ``tests/test_uranus_cycle1_abort.yaml``,
       ``tests/test_uranus_late_abort.yaml``
       (``git grep -lE 'type:\s*"?moist-mixture' -- '*.yaml'``). Each sets
       constant ``cv_R`` for every species.
   * - decks that set ``type: ideal-moist``
     - 36 (7 in ``examples``, 29 in ``tests``). Unchanged if ideal-moist is
       the survivor.
   * - the default type
     - ``moist-mixture`` is the default when ``type`` is absent
       (``equation_of_state.cpp:74``, ``equation_of_state.hpp:45``). No
       repository deck relies on it (every ``equation-of-state`` block sets
       ``type``). User decks without ``type`` would change meaning.
   * - options
     - The ``moist-mixture`` value of ``type`` becomes an alias, or an
       error. ``max-iter``, ``ftol`` and ``uv-solver`` are forwarded to
       kintera for every type (``equation_of_state.cpp:66-70``) and are not
       removed. Which kintera calls they govern in each type is **not
       checked**.
   * - code
     - ``moist_mixture.{hpp,cpp}`` (310 lines now, 286 after the targets in
       section 9) would go, up to about 286 lines. That is **not counted**.
       Type branches gain moist-mixture decks: anomaly storage
       (``hydro.cpp:192``), FP32 implicit (``hydro.cpp:505``) and the Roe
       moist path (``roe.cpp:20``).
   * - tests
     - ``test_eos.cpp:125`` (the moist-mixture case) and
       ``test_uranus_cycle1_abort.cpp``. Both uranus decks run there
       (``:117``), and their abort signatures involve kintera iterations,
       so they would need re-deriving.
   * - results beyond round-off?
     - **Hypothesis: yes for the uranus decks.** Moist-mixture gets T from
       kintera's iterative ``VU->T`` (``moist_mixture.cpp:65``). The uranus
       decks set ``ftol: 1.e-6``, while ideal-moist uses a closed form. So
       the two would differ at the solver tolerance, not at round-off. The
       919936da inventory measured agreement within 3.3e-12, but I did not
       re-check which deck and tolerance that used. **Not tested at the
       pin.**
   * - capability lost
     - Temperature-dependent heat capacity through kintera
       (``VT->cv``, ``moist_mixture.cpp:36``). No repository deck uses it
       today (all use constant ``cv_R``), but it is a physics option.

My recommendation: do not do F5 in V3. Section 9 meets the ceiling without
it, and its result change is likely beyond round-off.

**F6. Remove ``src/turbulence``** (D11, 402 lines). **Status: proceeding on
EF's proposal. The deletion is counted in section 9, the rows are kept, and
it is recorded for Cheng; nothing waits on it** (PM, EF lane thread).
Evidence at pin ``9e5de2d4``:

* the build glob ``src/CMakeLists.txt:35-53`` lists ``bc``, ``coord``,
  ``eos``, ``eos/aneos``, ``hydro``, ``riemann``, ``recon``, ``mesh``,
  ``output``, ``scalar``, ``utils``, ``forcing``, ``implicit``, ``input``,
  ``sedimentation`` and ``layout``. It has no ``turbulence/`` entry, and
  ``git show 9e5de2d4:src/CMakeLists.txt | grep -c turbulence`` gives 0
  (the CUDA glob at ``:122-134`` has none either);
* ``git grep -lE 'turbulence|TurbulenceModel|NTURBULENCE|KEpsilon' 9e5de2d4 -- . ':!src/turbulence'``
  finds only ``docs/doxygen/SUMMARY.md:33-34``, a documentation listing
  that goes with the deletion. No source, test, Python file or deck refers
  to it.

It is a k-epsilon model in Athena++ form (C24). Removing it changes no
result. This is the same case as uncompiled ``src/diagnostics`` in lane
O. If a turbulence closure is wanted in V3, I propose writing a new one on
the register (section 3, "Turbulence") rather than porting this. With ANEOS
kept, the lane reaches 20% only with F6 (section 9: 3,896 with it, 4,298
without).

11. Open questions to other lanes
=================================

Lanes and owners, as given in the EF lane thread: R register and stage
pipeline (Tianhao, backup owner; Linfeng did not claim it), I implicit
and gravity work (Xinyue), C reconstruction and Riemann (Tianhao), S
seams, coord, layout (Xinyue; Jiheng did not claim it), A rotation, AAM,
sources (Jiachen), K kintera (chen sihe), X execution, mesh, pyharp (Xi),
O output, input, utils, diagnostics (Jiachen). Revision 1 guessed several
letters wrongly. It read S as immersed solid and X as exchange/layout. The
questions below are re-addressed, and their ids have changed.

Check against the ten register requirements
-------------------------------------------

.. list-table::
   :header-rows: 1
   :widths: 5 30 40 25

   * - req
     - requirement (as restated in the thread)
     - EF design
     - gap / question
   * - 1
     - One owner of every conservative face flux; one documented frame and
       area weighting.
     - EF owns no face flux of its own. It posts increments (P1-P5) onto
       lane R's register, in the frame of the row it corrects.
     - Settled by the header's units (``flux_register.hpp:5-8``): flux
       density per unit face area and time, global components after
       rotation. P1 and P3 use them. #370's face-basis velocity is rotated
       to global (``flux2global2_``/``3_``) before P3.
   * - 2
     - Named increments in a declared order.
     - P1-P5 and F1, header calls and phases (section 4).
     - Post names: Q-R-h.
   * - 3
     - Stage fluxes accumulated with the stage weights into the step
       transfer.
     - EF posts are per stage. ``end_stage`` adds ``c_s*dt*total`` with all
       posts in it (``flux_register.hpp:13-15``).
     - Settled. ``cell_amount`` outside stages: Q-R-e.
   * - 4
     - The divergence and every flux-derived term read the register.
     - AAM, gravity work and the scalar mass flux read the register (R3,
       R4; Q-A1, Q-I3). The ``fadv`` clone goes (R2).
     - VIC species transfer (``vic_redistribute_impl.h:149-157``): Q-I2.
   * - 5
     - A shared face has two entries and one reconciliation rule.
     - Theta is single-valued (I11). For #370's carry, the donor side's
       values are authoritative (section 10).
     - **Gap.** Today's reconciliation is an exchange of theta, not a
       register rule. Q-S1, Q-S2.
   * - 6
     - One device-side monitor (mass, species, E+PE, AAM, scalars); no host
       read inside a segment.
     - ``EfStatus`` is device-only. The 5 host reads are removed or moved
       out of stages (section 7).
     - **Gap.** R owns the monitor (header ``:21-22``), but it has no write
       call for counters or retry flags, so ``EfStatus`` stays separate for
       now. Q-R-a, Q-O1.
   * - 7
     - Every fixer and floor registers what it added.
     - Positivity: P2-P5. Conserved floors: ``floor_dm``/``floor_de``
       (new in 1.1). Borrow and column repair: conservative, failure count.
     - **Gap.** The face floors (``reconstruct.cpp:150-158``,
       ``hydro_forward.cpp:594-614``) add nothing conserved directly, but
       their hits are not counted anywhere. Q-C1. The turbulence clamp is
       deleted (D11).
   * - 8
     - Stated dtype under FP32; fixed storage a CUDA graph can capture.
     - Section 6 (dtypes), section 7 (fixed buffers, G1/G2).
     - kintera ``VU->T``/``PV->T`` host reads: Q-K1.
   * - 9
     - No added full-field copy per stage.
     - Removes ``fadv`` (D10) and ``bflux1`` (offered to lane I).
     - P2/P3 need no snapshot: both read the pre-scale ``total(d)`` in phase
       ``limit`` before ``scale()``. The P1 buffer is fixed storage. **Gap:**
       #370's ``zeros_like(w)`` pairs (section 10).
   * - 10
     - Rebuilt, never written to restart.
     - ``EfStatus`` is reset each step. Floors, ``SedKernelArgs`` and the
       sedimentation buffers are rebuilt from options at ``reset()``.
     - **Not checked:** whether restart serializes module buffers (D14
       renames them). Q-O2.

Questions by lane (ready to post)
---------------------------------

**Lane R (Tianhao, backup owner; provisional header ``543ff84f``):** the
header answers the old Q-R1 (kept parts only), Q-R2 (``scale()``), Q-R3
(``replace()`` on the total and kept parts), Q-R4/Q5 (no EOS call), Q-R6
(units), Q-R7 (``end_stage`` weights) and Q-R8 (R owns the monitor). Open:
**Q-R-a** to **Q-R-i** (section 4, end). The split is agreed: the 108
``hydro_forward.cpp`` lines (858-866, 1154-1252) are R's deletion
(header ``:24``).

**Lane I (Xinyue):**

* **Q-I1.** VIC keeps a 4096-ulp margin (``vic_redistribute_impl.h:155``),
  while the FP32 positivity round-off bound is 64 ulp
  (``flux_positivity.hpp:22``). Should VIC read one shared constant, and
  which value applies in FP32?
* **Q-I2.** The relax step assumes the implicit x1 refill returns a drained
  species (``hydro_forward.cpp:1175-1179``). Does V3 VIC keep that, and will
  its species transfer read the register total (requirement 4)?
* **Q-I3.** Gravity work: the header keeps ``bflux1`` as an unscaled
  kept part and reads the explicit x1 total in ``pre_implicit``
  (``flux_register.hpp:19,48``). EF no longer offers a replacement; the
  lines are yours and R's to book.

**Lane C (Tianhao):**

* **Q-C1.** The face floors (``recon/reconstruct.cpp:150-158``, FP32 face
  floors ``hydro_forward.cpp:594-614``) are yours. Will they use EF's
  ``Floors`` values and count their hits in an ``EfStatus`` slot
  (requirement 7)?
* **Q-C2.** The conv4 admissibility check (``hydro_forward.cpp:359-367``)
  would call ``Floors::admissible``, shared with redo. Agree?
* **Q-C3.** EF decided Q5 (section 3): the solvers call
  ``gamma_sound_(w, gamma, cs)`` and ``caps()``, and the ANEOS branches in
  ``lmars.cpp:38,47`` and ``hllc.cpp:66,76`` go. Do you accept that
  contract for V3's solvers?

**Lane S (Xinyue):**

* **Q-S1.** Can the theta syncs (``"hydro_theta"``, up to two
  ``"scalar_theta"``) and #370's ``"hydro_hspec"`` and donor-velocity face
  exchanges go out as one batched exchange, one segment boundary per stage?
* **Q-S2.** Do your seam face states already carry the donor velocity in the
  face basis, so #370's two ``zeros_like(w)`` per lateral dimension
  (requirement 9) can go? And will you state one rule for donor-valued
  corrections at a shared face (requirement 5)?
* **Q-S3.** The column vapor repair gathers x1 columns when ``pz > 1``
  (``equation_of_state.cpp:340-347``). Does V3 keep ``gather_x1``?
* **Q-S4.** EF wants a coordinate-owned cached cell volume in place of the
  ``_version()`` cache at ``hydro_forward.cpp:1202-1216``. Will coord
  provide it?

**Lane A (Jiachen):**

* **Q-A1.** ``conserve_axial_momentum_`` (``hydro_forward.cpp:1288-1297``)
  reads the fluxes after the carry has changed the momentum rows. Will you
  read ``total(d)`` in phase ``divergence``, which includes P3?
* **Q-A2.** Forcings call ``species_cv_ref()`` every stage
  (``forcing/diffusion.cpp:566``, ``body_heat.cpp:49``,
  ``relax_bot_temp.cpp:69``), which reads a device tensor
  (``moist_base.cpp:23,28``). EF will cache it on the host. Any objection?

**Lane K (chen sihe):**

* **Q-K1.** When will kintera have capture-safe ``VU->T``/``PV->T`` (no host
  read per iteration, ``thermo_y.cpp:480,525``) and a device failure counter
  with reset/accumulate/consume, and in which version?
* **Q-K2.** Should kintera's saturation failures join ``EfStatus`` (or the
  monitor), or stay kintera-owned?

**Lane X (Xi):**

* **Q-X1.** Redo would read ``EfStatus.snapshot()`` inside the single
  device-to-host copy (``meshblock.cpp:1566``). The ``limiter_hits`` and
  ``floor_hit`` duplicates (``:1417-1446``) would go. Do you book those
  lines and accept the cause mapping (gate G-EF-2)?
* **Q-X2.** Solid cells: primitives are marked (``hydro_forward.cpp:521-522``)
  and conserved values filled after the RK combine (``meshblock.cpp:937``),
  after the whole-column limiter (``:907-909``). Should they be excluded from
  theta and the repair columns?
* **Q-X3.** EF's option branches (limiter gate ``hydro_forward.cpp:1165``,
  vapor repair layout) are fixed for a graph's life. Will they be in your
  graph key?

**Lane O (Jiachen):**

* **Q-O1.** Will diagnostics output the ``EfStatus`` counters and the floor
  amounts, and will you drop the dead ``"mut"`` output name
  (``output/output_utils.cpp:55``)?
* **Q-O2.** Does restart write module buffers? D14 renames the
  sedimentation buffers, which must stay rebuilt-only (requirement 10).

12. Skeleton index
==================

``docs/v3/skeleton/EF/`` holds declarations and comments only. It has no
function bodies, and is not added to any build. Its register names are lane
R's provisional header ``543ff84f`` (namespace ``snap``; section 4). Revision 1.1 adds the ``floor_dm``/``floor_de``
slots to ``EfStatus`` and the #370 ``vface`` input to ``PositivityInputs``.

.. list-table::
   :header-rows: 1
   :widths: 34 66

   * - file
     - declares
   * - ``ef_register_use.hpp``
     - EF's post names (``EfPost``) and its calls on lane R's
       ``snap::FluxRegister`` (header ``543ff84f``): ``add``, ``scale``,
       ``total``, ``cell_amount``, with phases. No EF wrapper functions.
   * - ``ef_status.hpp``
     - ``EfStatus``: slot enum, allocate, reset, snapshot.
   * - ``eos_floors.hpp``
     - ``Floors``: values, ``floor_row_``, ``admissible``.
   * - ``species_repair.hpp``
     - ``SpeciesRepair``: parent table, borrow, column repair.
   * - ``eos_interface.hpp``
     - ``EosCap`` and ``EosInterface``: the typed EOS methods of Q5.
   * - ``positivity_limiter.hpp``
     - ``PositivityInputs`` and ``PositivityLimiter``.
   * - ``sedimentation_kernel.hpp``
     - ``SedKernelArgs`` and the single dispatch signature.
