# 正文数字 → 数据源对照表（numbers.md）

> **唯一数据源规则**：正文/表/图中的每一个数值必须能在此表查到出处。优先级为 **JSON 字段 > 生成脚本中的显式公式 > summary.txt（仅冗余）**。若正文与 JSON 不一致，以 JSON 为准，重跑对应脚本后同步正文；不允许出现“只有正文、没有 JSON/公式”的数字（5608.5 的教训）。

## 0. 数据文件与生成脚本

| 数据文件 | 生成脚本 | 内容 |
|---|---|---|
| `第一题/results/q1_results.json` | `第一题/code/q1_solve.py` | Q1 全部数值（目标、弧、站点、敏感度） |
| `第一题/results/q1_area_estimators.json` | `第一题/code/area_estimators.py` | 0.25/0.1/0.05 m 中点与节点计数面积 |
| `第一题/results/q1_metric_compare.json` | `第一题/code/q1_metric_compare.py` | Q 与 Q₂ 的径向数值与最优解对照 |
| `第二题/results/q2a_results.json` | `第二题/code/q2a_core.py` | Q2(1) 精度模型、选站、MC、退化 |
| `第二题/results/q2b_results.json` | `第二题/code/q2b_core.py` | Q2(2) 调度、基线、敏感度、鲁棒变体 |
| `第二题/results/q2b_precision.json` | `第二题/code/q2b_gamma.py` | Q2(2) 交付方案与 γ 约束解的 γ/G/DRMS |
| `第三题/results/q3_results.json` | `第三题/code/q3_solve.py` | Q3 s_max、(a,b)、贡献分解、MC、精确求积 |
| `第四题/results/q4_results.json` | `第四题/code/q4_core.py` | Q4 74 场景全量结果 |
| `第四题/results/q4_robust.json` | `第四题/code/q4_robust.py` | Q4 鲁棒性与检验 |
| `第四题/results/q4_tlast_before_after.md/.csv` | `第四题/code/q4_tlast_diff.py` | 时间轴修复前后 t_last 对照 |
| `第四题/results/q4_scenario_list.md` | `第四题/code/q4_scenario_list.py` | 74 场景明细 |
| `params.csv` / `params_table.md` | `第一题/code/export_params.py` | B1–B5、V1–V5、T1–T3、全局常量 |

## 1. 题设参数（表 3-1 之前）

| 用途 | 取值 | 唯一来源 |
|---|---|---|
| 场地/调度中心 | 100 m × 100 m，O=(50,50) | `params_table.md`；`q2_lib.FIELD/O_POS` |
| 车辆半径/相机高/车速/云台 | 1.5 m / 2 m / 3 m·s⁻¹ / 30°·s⁻¹，ε∈[−10°,80°] | `params_table.md`；`q2_lib.py` 常量 |
| B1–B5 | [22,34]×[16,26]×20；[63,79]×[59,71]×28；[10,24]×[65,76]×12；[72,86]×[22,34]×24；[41,51]×[38,46]×32 | `params_table.md`；`params.csv` |
| V1–V5 | (15,14)/(88,10)/(14,86)/(88,68)/(50,93) | `params_table.md`；`params.csv` |
| T1/T2/T3 | (30°,40,45)/(150°,45,35)/(285°,38,55) | `params_table.md`；`q2_lib.ALERTS` |

## 2. 第一问

| 正文位置 | 数字/用途 | 取值 | 唯一来源 |
|---|---|---|---|
| 4.1.2 | T′ 水平投影 | (84.6410, 70.0000) | `q1_results.json → target.xy` |
| 4.1.2 | 闭式下界 r_min | 7.5821 m | `q1_results.json → r_min_closed_form`（=43/tan80°） |
| 4.1.3/4.1.4 | Q* | 0.1319（0.13189） m⁻¹ | `q1_results.json → q_star` |
| 4.1.4 | p* 与 φ | (88.8753, 76.2895)，φ=56.05° | `q1_results.json → optimal_station.x/y/phi_deg` |
| 4.1.3 | ε* | 80.00° | `q1_results.json → optimal_station.elevation_deg` |
| 4.1.4 | p* 自身裕度 | 9.6247 m | `q1_results.json → optimal_station.margin_m` |
| 4.1.4 | LOS 最小净空 | 7.41 m | `q1_results.json → optimal_station.los_clearance_m` |
| 表 4-1 | 最近车/行驶时间 | V4，2.78 s | `q1_results.json → optimal_station.nearest_vehicle/travel_time_s` |
| 4.1.4 | 弧上最大裕度 m* / φ* | 9.6746 m / 56.5038° | `q1_results.json → arc.m_star_margin_m/m_star_phi_deg` |
| 4.1.4 | 并列带下界 | 9.6246 m | `q1_results.json → arc.band_lower_m` |
| 4.1.4 | 被挡弧 | [160.75°, 236.89°]，长 76.15° | `q1_results.json → arc.blocked_runs_deg/blocked_total_deg` |
| 4.1.4 | 可行弧长/占比 | 283.85° / 78.85% | 派生：360−blocked_total；`arc.feasible_fraction` |
| 4.1.5 | 可观测面积（0.1 m 中点） | 5610.4 m² | `q1_results.json → grid.area_m2` |
| 4.1.5 | 节点计数面积（0.1 m） | 5628.7 m² | `q1_results.json → grid.area_node_count_m2` |
| 4.1.5 | 0.05 m 中点面积 | 5608.5 m² | `q1_area_estimators.json → estimators['h=0.05'].midpoint_area_m2` |
| 4.1.5/6.2 | 0.25 m 中点面积（扫描基准） | 5614.9 m² | `q1_area_estimators.json → estimators['h=0.25'].midpoint_area_m2` |
| 4.1.5 | 网格最小可行 r / 点 | 7.5828 m @ (92.2, 69.4) | `q1_results.json → grid.best_r/best_point` |
| 4.1.5 | 网格与解析差 | 0.0007 m | `q1_results.json → grid.r_diff_vs_analytic` |
| 6.2 | ∂r*/∂H | 0.1763 m/m | `q1_results.json → sensitivity.dr_dH` |
| 6.2 | ∂r*/∂ε_max | -0.7738 m/deg | `q1_results.json → sensitivity.dr_deps_deg` |
| 6.2 | E_H / E_εmax | 1.05 / −8.16 | 派生：(H/r*)∂r*/∂H；(ε_max/r*)∂r*/∂ε_max，基数见 `optimal_station` |
| 6.2 | 面积—B2 高度 / 车辆半径扫描 | 6300.4→3447.9 / 5821.9→5176.7 m² | `q1_results.json → sensitivity.area_vs_B2_height/area_vs_vehicle_radius` |
| 6.2 | Q₂ 径向扫描（表 6-1） | 0.08850→0.01146 m⁻¹ | `q1_metric_compare.json → radial_scan` |
| 6.2 | Q₂ 格点 argmax | (92.20, 69.40)，r=7.5828 m | `q1_metric_compare.json → Q2_grid_argmax` |

## 3. 第二问（1）

| 正文位置 | 数字/用途 | 取值 | 唯一来源 |
|---|---|---|---|
| 4.2.2 | T2 的 r_min | 5.8188 m | `q2a_results.json → r_min_geo_m` |
| 4.2.3 | G* / DRMS* | 5.8188 m / 0.1016 m | `q2a_results.json → certificate.G_star_m/DRMS_star_m` |
| 表 4-2 | 选中车/站点 | V3+V5；(5.2787,73.3912)/(11.9201,78.2501) | `q2a_results.json → chosen.vehicles/stations` |
| 表 4-2 | d / 基线 / γ | 5.8188 m / 8.2290 m / 90.0° | `q2a_results.json → chosen.d_m/baseline_m/gamma_deg` |
| 表 4-2 | 行驶时间/和 | 5.11/13.61 s，和 18.72 s | `q2a_results.json → chosen.travel_s/travel_sum_s` |
| 表 4-2 | DRMS / R95 | 0.1016 / 0.2486 m | `q2a_results.json → chosen.DRMS_m/ellipse95_radius_m` |
| 表 4-2 | MC 径向 RMSE / P95 | 0.1436 / 0.2486 m | `q2a_results.json → chosen.MC.rmse_m/p95_m` |
| 4.2.3 | T2 可行弧 | [59.66°, 244.24°] | `q2a_results.json → circle.feasible_runs_deg` |
| 4.2.3 | 90° 配对族 φ 区间 | [70.96°, 238.62°] | `q2a_results.json → certificate.phi_span_deg` |
| 4.2.3 | V2 组合 G | 8.9678 m | `q2a_results.json → pair_table[pair='V1+V2'].G_m` |
| 4.2.3 | 退化窗 / κ(30°) | [30.05°, 149.95°] / 2.0 | `q2a_results.json → degeneracy.gamma_window_G_le_2Gstar_deg/cond_number_at_30deg` |
| 4.2.3 | 78° 回退 r / DRMS | 7.0144 m / 0.1224 m（+20.5%） | `q2a_results.json → degeneracy.backoff_r_m/backoff_DRMS_m`；百分比派生 |
| 6.2 | ∂G*/∂H | 0.1763 m/m | `q2a_results.json → sensitivity.dG_dH_per_m` |
| 6.2 | G* 与 Ω₂ 随 H | 4.06→8.46 m；6272.7–6422.4 m² | `q2a_results.json → sensitivity.G_star_vs_H`（min/max 派生） |

## 4. 第二问（2）

| 正文位置 | 数字/用途 | 取值 | 唯一来源 |
|---|---|---|---|
| 4.2.5 | 优化开始时刻/目标 | 1.607/6.994/10.355 s，目标 10.355 s | `q2b_results.json → optimized.alert_starts/objective_s` |
| 4.2.5 | 指派/次序 | {'T1': [3, 5], 'T2': [1, 4], 'T3': [2, 3]}；{'V1': ['T2'], 'V2': ['T3'], 'V3': ['T1', 'T3'], 'V4': ['T2'], 'V5': ['T1']} | `q2b_results.json → optimized.assignment/orders` |
| 4.2.5 | 最近指派基线 | 1.607/11.140/20.968 s，目标 20.968 s | `q2b_results.json → heuristic.alert_starts/objective_s` |
| 4.2.5 | 差距/改善 | 10.613 s / +102.5% | `q2b_results.json → comparison.gap_s`；百分比派生 gap/obj_opt |
| 4.2.4 | 下界 LB | 3.414 s | `q2b_results.json → LB.global` |
| 5.2 | top-5 并列解 sum starts | 18.956 s | `q2b_results.json → top5_structures[0].sum_starts_s` |
| 4.2.6 | 鲁棒变体目标/开始 | 10.837 s；{'T1': 1.54, 'T3': 10.837, 'T2': 10.804} | `q2b_results.json → robust_05.obj_s/starts` |
| 6.2 | v×ω 敏感度表 | 见表 | `q2b_results.json → sensitivity_speed_omega` |
| 6.2 | ω/v 弹性 | −0.44 / −0.11 | 派生：对 `sensitivity_speed_omega` 做对数差分 |
| 4.2.6 | 刀锋净空 | 最小 0.0013 m | `q2b_results.json → knife_edge.min_station_clearance_m` |
| 4.2.1 | T1/T2/T3 区域面积 | 5610.4/6413.1/5459.8 m² | `q2b_results.json → region_areas` |
| 4.2.7/表 4-4 | 交付方案 γ/G/DRMS | T1 19.34°/176.67 m/3.084 m；T2 85.08°/67.93 m/1.186 m；T3 127.39°/81.32 m/1.419 m | `q2b_precision.json → delivered[]` |
| 4.2.7 | γ≥30° 约束解 | γ=30.12°，DRMS=2.036 m；t_last 12.983 s（+2.629 s，+25.38%） | `q2b_precision.json → constrained.*` |

## 5. 第三问

| 正文位置 | 数字/用途 | 取值 | 唯一来源 |
|---|---|---|---|
| 4.3.2 | 角误差斜率 k_loc | 1.432394 °/m | `q3_results.json → model.k_loc_deg_per_m` |
| 4.3.3 | σψ 上限 | 2.551067° | `q3_results.json → sigma_psi_max_deg` |
| 4.3.3 | s_max（闭式） | 66.92 m | `q3_results.json → s_max_m` |
| 4.3.3 | σ(s_max) | 1.6384 m | `q3_results.json → sigma_s_at_smax_m` |
| 4.3.3 | P(80) | 0.91538 | `q3_results.json → at_80.P` |
| 4.3.3 | a+80b / b_max / a_max | 1.6384 m / 0.0204806 / 1.6384 m | `q3_results.json → ab_region.*` |
| 4.3.3 | b 需降至 / a 需降至 | 0.0167306 m/m（−16.3%）/ 0.0384 m | 派生：(1.638446−0.3)/80；(1.638446−0.02×80) |
| 4.3.4 | 方差占比 s=0/40/80 | 15.6/54.0/30.4；71.3/18.4/10.3；88.1/7.6/4.3 % | `q3_results.json → contributions[].share_loc/share_zero/share_ctrl` |
| 4.3.4 | 交叉点 | 19.907 m | `q3_results.json → s_crossover_m` |
| 4.3.4 | 线性化残差 RMS | 0.1293°；方差占比 0.2% | `q3_results.json → monte_carlo.linearization_residual_rms_deg_at80`；占比派生 |
| 4.3.4 | 精确 s_max / P(66.92) / a+80b | 66.84 m / 0.94980 / 1.6367 m | `q3_results.json → exact_geometry.*` |
| 表 4-5 | MC 表 | 见表 | `q3_results.json → monte_carlo.points` |
| 6.2 | s_max 对 d | 46.44/56.68/66.92/77.16/87.40/107.88 m | `q3_results.json → sensitivity.s_max_vs_d` |
| 6.2 | ds_max/dd | 2.0481 m/m | `q3_results.json → sensitivity.ds_max_dd_m_per_m` |
| 6.2 | 置信度 0.90/0.95/0.98/0.99 | 85.20/66.92/51.41/43.07 m | `q3_results.json → ab_region.iso_levels` |
| 6.2 | 云台缩放 0.5–1.5 | 72.32/70.11/66.92/62.63/57.03 m | `q3_results.json → sensitivity.s_max_vs_gimbal_scale` |

## 6. 第四问

| 正文位置 | 数字/用途 | 取值 | 唯一来源 |
|---|---|---|---|
| 4.4.1 | 基线开始时刻 | {'T1': 1.607, 'T2': 6.994, 'T3': 10.355} | `q4_results.json → baseline.starts` |
| 4.4.4 | 场景计数 | {'A_new': 24, 'B_fail': 5, 'C_outage': 3, 'D_fail_out': 15, 'E_new_fail': 6, 'F_new_out': 9, 'G_triple': 12}，合计 74 | `q4_results.json → scenario_design.counts` |
| 4.4.4 | η 提升/持平/劣化 | 67/7/0 | 逐场景比较 `q4_results.json → scen_*[].keep.eta/resched.eta`；`q4_paper_numbers.py` |
| 4.4.4/表 4-7 | V4 故障代表 | η=1.000，t_last=11.17 s | `q4_results.json → representative.resched_failV4` |
| 4.4.4/表 4-7 | 三重代表 | η=1.000，t_last=25.01 s | `q4_results.json → representative.resched_triple` |
| 4.4.4 | 新告警 θ=0°,R=30 | η=1.000，t_last=16.77 s | `q4_results.json → scen_new[key='th0_R30'].resched` |
| 4.4.4 | V1 故障×中断 10/20/30 | 21.01/25.08/35.08 s | `q4_results.json → scen_fail_out[failed='V1'][t_rec].resched.t_last` |
| 6.2 | 新告警 t_last 范围 | 14.39–16.77 s | `scen_new[].resched.t_last` 的 min/max |
| 5.4 | 记账审计问题数 | 0 | `q4_robust.json → audit.issues` |
| 5.4 | 0.5 m 裕度/ε 容差/稳健基线/方位加密 | failV4 11.17 s；new_th135_R30 15.87 s；triple 25.01 s；ε 三档均 11.17 s；加密 14.57–16.45 s | `q4_robust.json → margin_05/eps_travel/baseline_robust/azimuth_densification` |
| 2（P2） | 修复前后 t_last 对照 | 见文件 | `q4_tlast_before_after.md/.csv` |
| 2（P5） | 74 场景明细 | 见文件 | `q4_scenario_list.md` |

## 7. 常用派生公式（正文出现但 JSON 未直接存的值）

| 派生量 | 公式 | 基数来源 |
|---|---|---|
| 改善百分比 | (obj_base−obj_opt)/obj_opt | `q2b_results.json → comparison` |
| 弹性 | Δln obj / Δln x | 对应 `sensitivity_*` 数组 |
| 方差占比 | var_i / var_total | `q3_results.json → contributions` |
| 线性化残差占比 | (resid/σψ)² | `monte_carlo.linearization_residual_rms_deg_at80` 与 `at_80.sigma_psi_deg` |
| 可行弧长 | 360° − blocked_total_deg | `q1_results.json → arc` |
| 0.1→0.05 m 面积收敛差 | (A0.1−A0.05)/A0.1 | `q1_area_estimators.json` |
| Q₂ 与 Q 的优劣 | Q₂(r)/Q₂(r_min) = (r_min/r)·cos²(ε−45)/cos²(35°) | `q1_metric_compare.json → radial_scan` |
| 67/74 计数 | 逐场景比较 resched.eta 与 keep.eta | `q4_results.json → scen_*`；`q4_paper_numbers.py` |

## 8. 核验规则（提交前）

1. 任一正文数字若不在本表，先补映射再写入正文；禁止“只存在于正文”的数字。
2. 重跑任一 `q*_core.py`/`q*_solve.py` 后，重新运行本脚本与本表引用的下游脚本，核对正文差异。
3. 面积三值必须分别标注口径：5610.4（0.1 m 中点，主估计）、5608.5（0.05 m 中点，收敛）、5614.9（0.25 m 中点，敏感性扫描基准），节点计数 5628.7 仅作参考。
4. 图表中的数字同样适用本表；图注中的极值与代表值必须能追到对应 JSON 字段。
