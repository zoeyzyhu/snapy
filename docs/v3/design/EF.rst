=====================================================================
V3 design, lane EF: EOS, floors, positivity, tracers, sedimentation
=====================================================================

:Lane: EF (owner Zoey Hu; alternate Linfeng Li)
:Revision: 3.1 (rev 1 ``16b8976a``, rev 1.1 ``de030195``, rev 2
           ``6adc7f74``, rev 2.1 ``7f70c735``, rev 2.2 ``8966a7f2``, rev 2.3
           ``d874dd2b``). Rev 3: re-cited to lane R ``3490d7e1`` and lane S
           rev 1.1 ``d03e4888``; ``bflux1`` removed (N13); answers to
           Xinyue's round-2 notes (section 11); 17 FP64 sites (N15).
           Rev 3.1: N1-N16 answered by number from Xinyue's round-2 text;
           re-cited to lane R rev 2 FROZEN ``175af2fc`` (``1bc247f9`` and
           ``3490d7e1`` are its ancestors); ``has_bf`` read at the pin.
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
* Inside the 36 non-turbulence EF files: 5 ``.item<>`` host reads, 17 hard
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
``175af2fc`` (rev 2, frozen; section 4). ``reg`` is the hydro ``snap::FluxRegister``; each
Scalar module has its own.

.. code-block:: text

   hydro_u --EOS U'->W (Floors, SpeciesRepair)--> w
   [sweep]      x1 riemann: reg.slot(1,...) / post_slot          (lane C, :845)
                Sedimentation(W->T, W->E) -> EF buffer sed
                  reg.add(1,"sedimentation",rows,sed)             (P1, :861-866)
                x2/x3 riemann, covariance                         (lane C, :1050-1152)
   [reconcile]  reg.replace(d, faces, peer, SeamRule::mean|owner_copy)
                reg.apply_prescribed(d)        (boundary.prescribed, S mask)
   [limit]      reg.total(d) -> theta, td; theta sync (exchange, Q-R-d)
                reg.add(d,"positivity.carry",{IPR},...), {IVX..IVZ}  (P3; x1 adv then sed)
                reg.scale(d,"positivity.withhold",species,factor)   (P2)
                reg.count("ef.pos_hits", ...) etc.
   [divergence] du reads reg.total(d)
   scalars (own register): add "scalar.upper_bound" (P4); scale (P5)
   [after_combine] EOS conserved limiter, borrow, fix_vapor
                -> reg.cell_amount("eos.floor"|"eos.borrow"|"eos.fix_vapor", vol_du)
   step end: monitor counters, amounts, retry_flags in X's one read (meshblock.cpp:1566)

4. Flux-register contract
=========================

**Source: lane R rev 2, FROZEN.** ``docs/v3/skeleton/R/flux_register.hpp``
(header rev 4, 118 lines) and ``R.rst`` rev 2 at ``happysky19/snapy``
``175af2fca68f5ae615b2b169a2d79f433df0b719``, by Tianhao. ``git ls-remote``
showed it as the head of ``v3-design/R`` while rev 3.1 was written. It is a
child of ``3490d7e1``, which rev 3 cited (``git merge-base --is-ancestor``).
``1bc247f92f64cb445609bb38e3299b54dc401e96``, the sha in the round-2 notes,
was also checked: it is an ancestor of both (R rev 1 → ``e0e9ade`` →
``3490d7e1`` → ``175af2fc``). Bare ``:N`` below is a line of that header;
``R.rst:N`` is a line of R.rst at ``175af2fc``. R's answers to EF's
Q-R-a..i are at ``R.rst:496-544``.

**What EF uses from the header:**

* ``add(dim, name, rows, increment)`` (``:57-59``): in call order, never
  fused or pre-summed, which keeps ``E = (E - c_adv) - c_sed``
  (``R.rst:318-320``);
* ``scale(dim, name, rows, factor)`` (``:60-62``) multiplies in place, as
  ``f.mul_(where(f > 0, th_lo, th_hi))`` does (``R.rst:320-321``,
  ``flux_positivity.cpp:99-121``). ``factor`` is ``[faces...]`` or
  ``[rows, faces...]`` (``:60``; Q-R-g);
* ``total(dim)`` (``:83``), ``enter`` (``:52``), and the phases ``sweep``,
  ``reconcile``, ``limit`` ("EF: total read, theta sync (an exchange),
  carry, scale", ``:19``) and ``after_combine`` ("fixers, EF floors",
  ``:24``) (``:16-25``);
* ``cell_amount(name, vol_du, stage_weight, kind)`` (``:68-71``) with
  ``AmountKind::floor`` for local floors and repairs (``:28-33``). In
  ``after_combine`` ``stage_weight = 1.0`` (``R.rst``, Q-R-e);
* ``count`` (``:77``), ``record_min`` (``:78``) and ``flag_retry``
  (``:79``), with names in ``RegisterRequest::counters`` and ``retry``
  (``:38-39``), read through ``RegisterMonitor`` ``counters()``,
  ``minima()`` and ``retry_flags()`` (``:100-103``);
* ``replace(dim, faces, peer, SeamRule)`` (``:63-65``), ``SeamRule``
  ``{mean, owner_copy}`` (``:26``), ``set_prescribed``/``apply_prescribed``
  (``:48-49``, ``:66``);
* the units and frame (``:5-6``): a flux density per unit face area and
  time before stage weights, in coord's ``flux2global<d>_`` frame. EF's
  carry increments use that frame;
* one register for hydro and one per Scalar module (``:43``);
* no EOS call (``R.rst:393``); the 108 ``hydro_forward.cpp`` lines are R's
  (``R.rst:673``, D2).

.. list-table:: EF posts on lane R's frozen register (``175af2fc``)
   :header-rows: 1
   :widths: 6 30 14 16 34

   * - id
     - call
     - phase
     - rows / dims
     - today's site; notes
   * - P1
     - ``add(1, "sedimentation", rows, sed)``
     - ``sweep``
     - species ``hydro_ids``, IVX..IVZ, IPR; x1
     - ``sed_hydro.cpp:36-40``; ``sed`` is EF's fixed buffer (see "P1
       buffer")
   * - P3
     - ``add(d, "positivity.carry", {IPR}, -c_E)``,
       ``add(d, "positivity.carry", {IVX,IVY,IVZ}, -c_m)``; on x1 the
       advected pair, then the settling pair
     - ``limit``
     - IPR, IVX..IVZ; x1-x3
     - ``flux_positivity.cpp:124-167``. Kind ``flux_correction``
       (``R.rst``, Q-R-h).
   * - P2
     - ``scale(d, "positivity.withhold", species, factor)``, with ``factor``
       ``[species, faces...]``
     - ``limit``
     - species; x1-x3
     - ``flux_positivity.cpp:99-121``; ``flux_correction``
   * - P4
     - ``add(d, "scalar.upper_bound", rows, g - g*factor)``
     - ``limit`` (Scalar's register)
     - scalar rows
     - ``scalar.cpp:199-214``
   * - P5
     - ``scale(d, "scalar.positivity.withhold", rows, factor)``
     - ``limit`` (Scalar's register)
     - scalar rows
     - ``scalar.cpp:239``
   * - F1
     - ``cell_amount("eos.floor" | "eos.borrow" | "eos.fix_vapor", vol_du,
       1.0, AmountKind::floor)``
     - ``after_combine``
     - IDN, IPR; species
     - ``equation_of_state.cpp:213-290,307-380``. Not ``Fixer`` subclasses
       (``R.rst``, Q-R-f).
   * - C1
     - ``count``/``record_min``/``flag_retry`` for EF's names (below)
     - where each event happens
     - n/a
     - today's ``EfStatus`` slots

**EfStatus becomes monitor entries** (Q-R-a answered). The counts are
``count`` names: ``ef.floor_patch``, ``ef.nan``, ``ef.vapor_fail``,
``ef.heat_capacity``, ``ef.pos_hits``, ``ef.pos_severe`` and
``ef.scalar_pos_hits``. The minimum is ``record_min("ef.pos_min")``.
``ef.lim_cut``/``ef.lim_flux`` (FP64 sums) and the floor amounts are
``cell_amount`` amounts, not int64 counters. The redo causes are
``flag_retry`` causes: ``ef.floor_patch``, ``ef.nan``, ``ef.vapor_fail``
and ``ef.heat_capacity``. ``R.rst:496-506`` moves the slots in R's PR R-1;
until then ``EfStatus`` stays EF's tensor in X's stacked read. The +45
lines stay counted (N7). R asks EF to name the vapor-repair retry cause
(``R.rst:1339``): it is ``ef.vapor_fail``.

**Solid cells and faces (lane S rev 1.1,** ``XinyueWang05/snapy``
``v3-design/S`` ``d03e48880dc28b33eca6c62ff6ad8ad162bdcdb2``, ``S.rst:935-1000``):

* S's ``bc.solid_face`` maps onto R's ``boundary.prescribed``. R calls
  ``apply_prescribed(d)`` in ``reconcile`` after ``replace``, and again
  after ``post_implicit``. S supplies ``set_prescribed(d, mask, value)``
  when the solid field changes. The mask zeroes **mass, species, energy
  and scalars** on wall and solid faces. **Normal momentum keeps the
  mirror-Riemann flux**; no momentum row is prescribed.
* Tangential momentum is **free-slip**, as at the pin (mirror state;
  ``bc/internal_boundary.cpp:78-91``, ``bc/bc_func.cpp:10-34``). No
  momentum row is prescribed; EF agreed this in the lane S thread. Whether
  the tangential flux is zero to round-off is R's G-R9 **(hypothesis)**.
* For EF (``S.rst:75-79,1013-1015``): a solid cell is a **column break**
  in ``fix_vapor``, never a donor or receiver. Solid cells are excluded
  from theta, the hit census and the neighbour minimum (``phi``). Because
  ``boundary.prescribed`` acts in ``reconcile``, before ``limit``, theta
  already sees zero species flux on solid faces.

**Reads.**

* R1: ``total(d)`` in ``limit``, species and IDN rows.
* R2: EF's own P1 buffer, not a register read.
* R3: the Scalar module requests the one-row part
  ``mass.dry.limited@1/@2/@3``, which the hydro register fills with
  ``total(d)[IDN]`` as ``limit`` ends (``R.rst``, Q-R-c).
* R4: ``mass.dry.limited@d - covariance.dry@d``, the same operation as
  ``scalar.cpp:161`` (**hypothesis**: bitwise; ``R.rst``, Q-R-c).

**Gravity work.** EF depends on nothing here. There is no x1 Riemann-only
row: ``bflux1`` belongs to ``gravity-work: cell``, which Cheng removed
(``R.rst:171``; at ``3490d7e1`` it was ``flux_register.hpp:13``). The pin's
``has_bf`` lines (``hydro_forward.cpp:902,907,917``) carry only
``bflux1``'s seam row. They are in R's deletion D5 (``R.rst:1213``).

**Ordering** (``:16-25``): ``sweep: x1 riemann (:845) < P1 (:861-866) <
x2/x3 riemann, covariance`` < ``reconcile: replace, apply_prescribed`` <
``limit: total read < theta sync < P3 adds < P2 scale`` < ``divergence``;
``after_combine: F1``. On the Scalar's register: ``P4 < P5`` in ``limit``.

**P1 buffer: unchanged** (Xinyue's N5/N6: resolved). Only the first post
of a stage or a requested part is written in place (``slot``/``part_slot``,
``:54-55``). So P1 is an ``add`` of EF's fixed buffer, reused as the
settling part. A kept part would be reconciled (``:63-65``), while the
pin's ``fsed1`` precedes the seam average (``hydro_forward.cpp:865`` then
``:868-``).

**Bitwise answer: unchanged.** R states both conditions (``R.rst:318-321``):
the carry's ``add`` calls run in call order and are never pre-summed, and
``scale`` is the pin's in-place multiply. Species rows are bitwise. The one
difference is that EF uses ``sed`` rather than ``(F_adv + sed) - F_adv``
(``hydro_forward.cpp:862-865``). That is a rounding change in the energy
and momentum rows of sedimenting decks, made because a bitwise match would
need a per-stage copy (requirement 9). R records it too: "bitwise (EF
settling part excepted)" (``R.rst:1044``). **Hypothesis until G-EF-1.**
Lane C's ``(theta-1)F`` form is withdrawn (``1bc247f9``
``flux_register.hpp:19``; ``R.rst`` "``scale()`` over ``(theta-1)F``"), and
EF does not rely on it.

**Lateral seams (N9): no replace after ``limit``.** ``replace(...,
owner_copy)`` in ``reconcile`` makes the pre-limit totals identical. EF's
``limit`` posts are functions of inputs that are then also identical:
theta (synced raw, ``flux_positivity.cpp:177-193``), ``hspec`` and the
donor velocities (#370; S rows 17p, 16r), with the same op order and
dtype. So species and IPR totals stay bit-identical without a second
``replace`` **(hypothesis)**. Panel-seam momentum agrees only to S's 16r
tolerance. R keeps the pin's behaviour (no second ``replace``) and extends
G-R2 to the end of ``limit``. If that fails, S's second ``owner_copy`` in
``limit`` is the fix, and EF accepts it (``R.rst``, Q-R-i).

**Lane R questions, status at** ``175af2fc`` (``R.rst:496-544``):
**a**–**h** are answered (write calls; one register per Scalar module;
``mass.dry.limited``; exchange in ``limit``; ``stage_weight = 1.0`` and the
``vol_du`` shape; floors are not ``Fixer`` subclasses; the ``factor``
shape; names adopted). **i** is open, with R and EF agreeing on the path:
G-R2 extended to the end of ``limit``, and S's second ``replace`` if it
fails.

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
``grep -n "\.set_(\|set_data("``: **5 host reads, 17 hard FP64 dtype sites,
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

**D8 sedimentation target (recorded for Cheng).** D8's -400-line target
(seven sedimentation files) carries the 80-line margin. It is a target and
not measured, and it stays FOR CHENG until EF-6 is prototyped.

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
     - Settled by R ``175af2fc`` ``flux_register.hpp:5-6``: flux density
       per unit face area and time; frame = ``flux2global<d>_`` output
       (x2/x3 momentum in the panel face basis). P1 and P3 use it.
   * - 2
     - Named increments in a declared order.
     - P1-P5 and F1, header calls and phases (section 4).
     - Post names: Q-R-h.
   * - 3
     - Stage fluxes accumulated with the stage weights into the step
       transfer.
     - EF posts are per stage. ``end_stage`` adds ``c_s*dt*total`` with all
       posts in it (``175af2fc`` ``R.rst`` 3.4; ``end_stage``, ``:86``).
     - Settled. Floors post in ``after_combine`` (``:24``) with
       ``stage_weight = 1.0`` (Q-R-e).
   * - 4
     - The divergence and every flux-derived term read the register.
     - AAM and the scalar mass flux read the register (R3, R4; Q-A1). The
       ``fadv`` clone goes (R2). The gravity-work cell form is removed
       (``R.rst:171``).
     - VIC species transfer (``vic_redistribute_impl.h:149-157``): Q-I2.
   * - 5
     - A shared face has two entries and one reconciliation rule.
     - The rule is R's ``replace`` (``SeamRule::mean`` x1, ``owner_copy``
       panels) in ``reconcile``, before EF posts. EF's ``limit`` posts are
       functions of identical inputs (synced theta; #370's ``hspec`` and
       donor velocities), so no ``replace`` after ``limit`` (section 4,
       "Lateral seams").
     - Open: panel-seam momentum rows agree only to the 16r tolerance
       (S, **hypothesis**), with fallback ``owner_copy`` in ``limit``; x1
       seams Q-R-i.
   * - 6
     - One device-side monitor (mass, species, E+PE, AAM, scalars); no host
       read inside a segment.
     - ``EfStatus`` is device-only. The 5 host reads are removed or moved
       out of stages (section 7).
     - Settled: ``count``/``record_min``/``flag_retry`` (``:77-79``);
       ``EfStatus`` moves to the monitor in R's R-1 (Q-R-a answered).
       Output of the counters: Q-O1.
   * - 7
     - Every fixer and floor registers what it added.
     - Positivity: P2-P5 (``scale`` books ``(factor-1)*F``; the carry
       ``add`` is named). Conserved floors, borrow and column repair:
       ``cell_amount("eos.floor" | "eos.borrow" | "eos.fix_vapor")`` in
       ``after_combine``, with counts via ``count()``. Solid faces:
       ``boundary.prescribed`` (R, S).
     - Face floors (``reconstruct.cpp:150-158``,
       ``hydro_forward.cpp:594-614``) count through ``count()`` (header
       ``:38``, "C's five" counters); C posts them (Q-C1). The turbulence
       clamp is deleted (D11).
   * - 8
     - Stated dtype under FP32; fixed storage a CUDA graph can capture.
     - Section 6 (dtypes), section 7 (fixed buffers, G1/G2).
     - kintera ``VU->T``/``PV->T`` host reads: Q-K1.
   * - 9
     - No added full-field copy per stage.
     - Removes ``fadv`` (D10). The P1 buffer is fixed storage.
     - P2/P3 need no snapshot: both read the pre-scale ``total(d)`` in
       ``limit``. Not added versus the pin: the per-stage ``factor``
       (``where``) temporary, as at ``flux_positivity.cpp:104``. **Gap:**
       #370's ``zeros_like(w)`` pairs, replaced by fixed buffers (section
       10). Cost is measured, not here, as R's requirement-9 count.
   * - 10
     - Rebuilt, never written to restart.
     - EF's counters and amounts live in R's monitor, reset at
       ``begin_step()`` and rolled back on retry (``:50``, ``:87``); nothing
       to restart. Floors, ``SedKernelArgs`` and the sedimentation buffers
       are rebuilt from options at ``reset()``.
     - **Not checked:** whether restart serializes module buffers (D14
       renames them). Q-O2.

Round-2 notes from Xinyue (against ``b58e12bb``; lane I side her rev 2 ``c6f9d957``)
------------------------------------------------------------------------------------

Her summary: the budget 4,971 -> 3,896 (-21.63%) reproduces at the pin
across all 40 rows (``wc -l``), and passes 20% only with F6. The skeleton
was 296 lines (299 at rev 3). She did not check rev 1's 3,680 or #370's +8.
Her status is quoted first; EF's answer follows.

.. list-table::
   :header-rows: 1
   :widths: 6 20 74

   * - N
     - reviewer / EF
     - answer
   * - N1
     - agree / agreed
     - No change.
   * - N2
     - agree / agreed
     - No change.
   * - N3
     - request / open (Cheng)
     - F6 (``src/turbulence``, -402, counted) and D8 (-400 target) stay FOR
       CHENG (section 10). Without F6 the cut is 13.5%, and that is stated
       in section 9.
   * - N4
     - request / changed
     - Re-cited to R rev 2 FROZEN ``175af2fc``, R's head at rev 3.1.
       ``1bc247f9`` was checked: it is an ancestor of ``3490d7e1`` and
       ``175af2fc``. Every R line in section 4 is read at ``175af2fc``. C's
       ``(theta-1)F`` is withdrawn, and EF does not rely on it.
   * - N5
     - resolved / agreed
     - EF's own P1 buffer (section 4, "P1 buffer").
   * - N6
     - resolved / agreed
     - As N5.
   * - N7
     - agree / agreed
     - The +45 lines for ``ef_status.hpp`` stay in section 9. R
       ``175af2fc`` has ``count``/``record_min``/``flag_retry``
       (``:77-79``), and the slots move in R-1, so the header may
       shrink to a list of names. No line credit is taken until it is
       written.
   * - N8
     - agree / agreed
     - As N7.
   * - N9
     - request / changed (EF half)
     - Section 4, "Lateral seams": no ``replace`` after ``limit``. Species
       and IPR totals are bit-identical **(hypothesis)**. Panel-seam
       momentum is held to S's 16r tolerance, with an ``owner_copy``
       fallback. The lane S half is Xinyue's.
   * - N10
     - partly resolved / open
     - Her round-2 text does not say which part remains. EF owns asking:
       Xinyue, please name the remaining part, and it gets answered in rev
       4.
   * - N11
     - none / agreed
     - No round-2 comment from the reviewer; treated as agreed at rev 2.3.
   * - N12
     - none / agreed
     - No round-2 comment from the reviewer; treated as agreed at rev 2.3.
   * - N13
     - conflict / changed
     - Accepted. Rev 2.3 misread R ``543ff84f:19``, which only notes that
       ``bflux1`` is unscaled at the pin. Under ruling (a)
       (``gravity-work: cell`` refused) ``bflux1`` goes, and rev 3 removed
       the sentence and its dependents. The ``has_bf`` hypothesis is checked
       by reading the pin: ``hydro_forward.cpp:902`` sets
       ``has_bf = bflux1.defined()``, and its only uses are packing
       (``:907``) and unpacking (``:917``) the ``bflux1`` row of the x1
       seam-average payload. Those lines go with ``bflux1`` in **R's** seam
       rewrite. They are R's lines, not EF's.
   * - N14
     - unchanged / unchanged
     - EF keeps its rev 2.3 position.
   * - N15
     - request / changed
     - 17 FP64 dtype sites (section 7), recounted at the pin. No budget
       change.
   * - N16
     - request / changed
     - Requirements 5, 7, 9 and 10 are rewritten in the check above
       (rev 3).
   * - Q-I1
     - answer / adopted
     - One constant: VIC's keep is ``kPositivityRoundoffUlp`` (4096) times
       the eps of VIC's dtype. The 64 at ``flux_positivity.hpp:23`` is the
       FP32 census bound only. VIC books its keep as
       ``cell_amount("vic.mass_clamped")``. **(Hypothesis, not run:** FP32
       VIC keeps about 4.9e-4, against 9.1e-13 for FP64 theta.)
   * - Q-I2
     - answer / adopted
     - VIC keeps the refill. It posts ``vic.mass_species`` in
       ``implicit``, reading w, gamma, the solid mask and du.
       ``post_implicit`` reads ``total(1)``, ``vic.momentum_t`` and
       ``vic.mass_dry``. So P2 and P3 stay before the divergence. The relax
       assumption (``hydro_forward.cpp:1175-1179``) stands.
   * - Q-I3
     - conflict / withdrawn
     - As N13.
   * - F6, D8
     - open (Cheng)
     - As N3.

Questions by lane (ready to post)
---------------------------------

**Lane R (Tianhao, backup owner; rev 2 FROZEN ``175af2fc``):** R.rst
answers Q-R-a to Q-R-h (``R.rst:496-544``). Q-R-i stays open on an agreed
path (G-R2 to the end of ``limit``; S's second ``replace`` if it fails).
R's asks of EF (``R.rst:1339``): the vapor-repair retry cause is
``ef.vapor_fail``, and the tangential-momentum option is free-slip (S
rev 1.1). The 108 ``hydro_forward.cpp`` lines (858-866, 1154-1252) are
R's deletion (``R.rst:673``, D2).

**Lane I (Xinyue):**

* **Q-I1.** *EF adopts:* VIC's donor margin ``T(4096) * epsilon<T>``
  (``vic_redistribute_impl.h:150-155``) and theta's margin
  (``kPositivityRoundoffUlp * machine_epsilon``, ``flux_positivity.cpp:73``)
  are the same 4096 ulp in both precisions. VIC reads the one constant
  ``kPositivityRoundoffUlp`` times the eps of its dtype. The FP32 64-ulp
  ``kPositivityRoundoffUlpFloat`` (``flux_positivity.hpp:22-23``) is only
  the census/severe threshold, not a margin. Bitwise **(hypothesis: same
  expression, a named constant)**. Confirmed by Xinyue (I rev 2
  ``c6f9d957``). The keep is booked as ``cell_amount("vic.mass_clamped")``.
* **Q-I2.** *EF adopts:* the relax keeps its refill assumption
  (``hydro_forward.cpp:1175-1179``) as a modelling assumption, **not
  tested**. VIC's species transfer is an ``add`` of ``vic.mass_species`` on
  x1 in ``implicit`` (``R.rst``, I section; header ``:41``), so it is a
  register post (requirement 4). Confirmed by Xinyue: VIC keeps the
  refill. ``post_implicit`` reads ``total(1)``, ``vic.momentum_t`` and
  ``vic.mass_dry``, so P2 and P3 stay before the divergence.
* **Q-I3.** *Withdrawn.* The gravity-work cell form and ``bflux1`` are
  removed (lane R ``175af2fc`` ``R.rst:171``; Cheng). EF
  depends on no Riemann-only x1 row.

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
R's frozen header ``175af2fc`` (rev 2; namespace ``snap``; section 4). Revision 1.1 adds the ``floor_dm``/``floor_de``
slots to ``EfStatus`` and the #370 ``vface`` input to ``PositivityInputs``.

.. list-table::
   :header-rows: 1
   :widths: 34 66

   * - file
     - declares
   * - ``ef_register_use.hpp``
     - EF's post names (``EfPost``) and its calls on lane R's
       ``snap::FluxRegister`` (header ``175af2fc``): ``add``, ``scale``,
       ``total``, ``cell_amount`` (``AmountKind::floor``), ``count``,
       ``record_min``, ``flag_retry``, with phases; EF's names. No EF wrapper functions.
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
