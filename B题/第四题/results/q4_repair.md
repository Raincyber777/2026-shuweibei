# Problem 4 simple-repair baseline

n = 74 scenarios

| comparison | eta improve | eta tie | eta degrade | t_last improve (eta tie) | t_last worse (eta tie) |
|---|---|---|---|---|---|
| repair vs keep | 67 | 7 | 0 | 0 | 0 |
| resched vs keep | 67 | 7 | 0 | 0 | 0 |
| resched vs repair | 0 | 74 | 0 | 61 | 0 |

Mean t_last: keep 55.30 s, repair 23.15 s, resched 19.57 s

## Completion-rule sensitivity

T1 starts at 1.607 s and is interrupted at the 5 s failure after 3.393 s; a >= 4 s synchronized-observation criterion therefore fails T1 in 8 scenarios.

| policy | eta=1 count (main) | eta=1 count (strict) |
|---|---|---|
| keep | 7 | 3 |
| repair | 74 | 66 |
| resched | 74 | 66 |

Strict repair vs keep: {'eta_improve': 67, 'eta_tie': 7, 'eta_degrade': 0, 'tlast_improve_within_tie': 0, 'tlast_worse_within_tie': 0, 'tlast_equal_within_tie': 7}

Strict resched vs repair: {'eta_improve': 0, 'eta_tie': 74, 'eta_degrade': 0, 'tlast_improve_within_tie': 57, 'tlast_worse_within_tie': 0, 'tlast_equal_within_tie': 17}

- B_fail V3 t_rec=None: keep 0.333, repair 0.667, resched 0.667
- B_fail V5 t_rec=None: keep 0.667, repair 0.667, resched 0.667
- D_fail_out V3 t_rec=10.0: keep 0.333, repair 0.667, resched 0.667
- D_fail_out V3 t_rec=20.0: keep 0.333, repair 0.667, resched 0.667
- D_fail_out V3 t_rec=30.0: keep 0.333, repair 0.667, resched 0.667
- D_fail_out V5 t_rec=10.0: keep 0.667, repair 0.667, resched 0.667
- D_fail_out V5 t_rec=20.0: keep 0.667, repair 0.667, resched 0.667
- D_fail_out V5 t_rec=30.0: keep 0.667, repair 0.667, resched 0.667