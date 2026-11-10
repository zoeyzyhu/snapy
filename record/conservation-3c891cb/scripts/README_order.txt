Order of execution (all from the run directory, venv with snapy built from 3c891cb):
 1. python scripts/make_decks.py <snapy@3c891cb>/examples/bryan.yaml decks
 2. for each of ic_{uni,str}_{bubble,rest}.yaml: <build>/bin/bryan.release -i decks/<deck>  (in ic/<grid>_<kind>/)
 3. python scripts/make_twin_uniform.py ic/<g>_rest/ic_<g>_rest.00000.restart ic/<g>_rest_uniform.pt
 4. scripts/run_all.sh     (bubble runs of the 8 float64 + 4 float32 arms; its twins are superseded by step 5)
 5. scripts/run_twins.sh   (rest twins from the horizontally uniform balance_column rest state)
 6. python scripts/analyze.py runs > table.md
 7. scripts/run_checks.sh  (rk2 attribution, SNAP_WB_REF4=1);  scripts/check_pe.py, scripts/check_fp32.py
