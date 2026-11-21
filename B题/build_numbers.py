# -*- coding: utf-8 -*-
"""Build numbers.md: one-to-one map from every headline number in the paper
to its JSON field or generating script.

Run from anywhere:  python build_numbers.py
"""
import json
import os

ROOT = os.path.dirname(os.path.abspath(__file__))
R1 = json.load(open(os.path.join(ROOT, "第一题", "results", "q1_results.json"),
                    encoding="utf-8"))
R1A = json.load(open(os.path.join(ROOT, "第一题", "results",
                                  "q1_area_estimators.json"), encoding="utf-8"))
R1M = json.load(open(os.path.join(ROOT, "第一题", "results",
                                  "q1_metric_compare.json"), encoding="utf-8"))
R2A = json.load(open(os.path.join(ROOT, "第二题", "results", "q2a_results.json"),
                     encoding="utf-8"))
R2B = json.load(open(os.path.join(ROOT, "第二题", "results", "q2b_results.json"),
                     encoding="utf-8"))
R2P = json.load(open(os.path.join(ROOT, "第二题", "results",
                                  "q2b_precision.json"), encoding="utf-8"))
R3 = json.load(open(os.path.join(ROOT, "第三题", "results", "q3_results.json"),
                    encoding="utf-8"))
R4 = json.load(open(os.path.join(ROOT, "第四题", "results", "q4_results.json"),
                    encoding="utf-8"))
R4R = json.load(open(os.path.join(ROOT, "第四题", "results", "q4_robust.json"),
                     encoding="utf-8"))

L = []
A = L.append


def f(x, n=4):
    return f"{x:.{n}f}"


A("# 正文数字 → 数据源对照表（numbers.md）")
A("")
A("> **唯一数据源规则**：正文/表/图中的每一个数值必须能在此表查到出处。"
  "优先级为 **JSON 字段 > 生成脚本中的显式公式 > summary.txt（仅冗余）**。"
  "若正文与 JSON 不一致，以 JSON 为准，重跑对应脚本后同步正文；"
  "不允许出现“只有正文、没有 JSON/公式”的数字（5608.5 的教训）。")
A("")
A("## 0. 数据文件与生成脚本")
A("")
A("| 数据文件 | 生成脚本 | 内容 |")
A("|---|---|---|")
A("| `第一题/results/q1_results.json` | `第一题/code/q1_solve.py` | Q1 全部数值（目标、弧、站点、敏感度） |")
A("| `第一题/results/q1_area_estimators.json` | `第一题/code/area_estimators.py` | 0.25/0.1/0.05 m 中点与节点计数面积 |")
A("| `第一题/results/q1_metric_compare.json` | `第一题/code/q1_metric_compare.py` | Q 与 Q₂ 的径向数值与最优解对照 |")
A("| `第二题/results/q2a_results.json` | `第二题/code/q2a_core.py` | Q2(1) 精度模型、选站、MC、退化 |")
A("| `第二题/results/q2b_results.json` | `第二题/code/q2b_core.py` | Q2(2) 调度、基线、敏感度、鲁棒变体 |")
A("| `第二题/results/q2b_precision.json` | `第二题/code/q2b_gamma.py` | Q2(2) 交付方案与 γ 约束解的 γ/G/DRMS |")
A("| `第三题/results/q3_results.json` | `第三题/code/q3_solve.py` | Q3 s_max、(a,b)、贡献分解、MC、精确求积 |")
A("| `第四题/results/q4_results.json` | `第四题/code/q4_core.py` | Q4 74 场景全量结果 |")
A("| `第四题/results/q4_robust.json` | `第四题/code/q4_robust.py` | Q4 鲁棒性与检验 |")
A("| `第四题/results/q4_tlast_before_after.md/.csv` | `第四题/code/q4_tlast_diff.py` | 时间轴修复前后 t_last 对照 |")
A("| `第四题/results/q4_scenario_list.md` | `第四题/code/q4_scenario_list.py` | 74 场景明细 |")
A("| `params.csv` / `params_table.md` | `第一题/code/export_params.py` | B1–B5、V1–V5、T1–T3、全局常量 |")
A("")
A("## 1. 题设参数（表 3-1 之前）")
A("")
A("| 用途 | 取值 | 唯一来源 |")
A("|---|---|---|")
A("| 场地/调度中心 | 100 m × 100 m，O=(50,50) | `params_table.md`；`q2_lib.FIELD/O_POS` |")
A("| 车辆半径/相机高/车速/云台 | 1.5 m / 2 m / 3 m·s⁻¹ / 30°·s⁻¹，ε∈[−10°,80°] | `params_table.md`；`q2_lib.py` 常量 |")
A("| B1–B5 | [22,34]×[16,26]×20；[63,79]×[59,71]×28；[10,24]×[65,76]×12；[72,86]×[22,34]×24；[41,51]×[38,46]×32 | `params_table.md`；`params.csv` |")
A("| V1–V5 | (15,14)/(88,10)/(14,86)/(88,68)/(50,93) | `params_table.md`；`params.csv` |")
A("| T1/T2/T3 | (30°,40,45)/(150°,45,35)/(285°,38,55) | `params_table.md`；`q2_lib.ALERTS` |")
A("")
A("## 2. 第一问")
A("")
A("| 正文位置 | 数字/用途 | 取值 | 唯一来源 |")
A("|---|---|---|---|")
A(f"| 4.1.2 | T′ 水平投影 | ({f(R1['target']['xy'][0])}, {f(R1['target']['xy'][1])}) | `q1_results.json → target.xy` |")
A(f"| 4.1.2 | 闭式下界 r_min | {f(R1['r_min_closed_form'])} m | `q1_results.json → r_min_closed_form`（=43/tan80°） |")
A(f"| 4.1.3/4.1.4 | Q* | 0.1319（{f(R1['q_star'],5)}） m⁻¹ | `q1_results.json → q_star` |")
A(f"| 4.1.4 | p* 与 φ | ({f(R1['optimal_station']['x'])}, {f(R1['optimal_station']['y'])})，φ={f(R1['optimal_station']['phi_deg'],2)}° | `q1_results.json → optimal_station.x/y/phi_deg` |")
A(f"| 4.1.3 | ε* | {f(R1['optimal_station']['elevation_deg'],2)}° | `q1_results.json → optimal_station.elevation_deg` |")
A(f"| 4.1.4 | p* 自身裕度 | {f(R1['optimal_station']['margin_m'])} m | `q1_results.json → optimal_station.margin_m` |")
A(f"| 4.1.4 | LOS 最小净空 | {f(R1['optimal_station']['los_clearance_m'],2)} m | `q1_results.json → optimal_station.los_clearance_m` |")
A(f"| 表 4-1 | 最近车/行驶时间 | {R1['optimal_station']['nearest_vehicle']}，{f(R1['optimal_station']['travel_time_s'],2)} s | `q1_results.json → optimal_station.nearest_vehicle/travel_time_s` |")
A(f"| 4.1.4 | 弧上最大裕度 m* / φ* | {f(R1['arc']['m_star_margin_m'])} m / {f(R1['arc']['m_star_phi_deg'],4)}° | `q1_results.json → arc.m_star_margin_m/m_star_phi_deg` |")
A(f"| 4.1.4 | 并列带下界 | {f(R1['arc']['band_lower_m'])} m | `q1_results.json → arc.band_lower_m` |")
A(f"| 4.1.4 | 被挡弧 | [{f(R1['arc']['blocked_runs_deg'][0][0],2)}°, {f(R1['arc']['blocked_runs_deg'][0][1],2)}°]，长 {f(R1['arc']['blocked_total_deg'],2)}° | `q1_results.json → arc.blocked_runs_deg/blocked_total_deg` |")
A(f"| 4.1.4 | 可行弧长/占比 | {f(360 - R1['arc']['blocked_total_deg'],2)}° / {f(100*R1['arc']['feasible_fraction'],2)}% | 派生：360−blocked_total；`arc.feasible_fraction` |")
A(f"| 4.1.5 | 可观测面积（0.1 m 中点） | {f(R1['grid']['area_m2'],1)} m² | `q1_results.json → grid.area_m2` |")
A(f"| 4.1.5 | 节点计数面积（0.1 m） | {f(R1['grid']['area_node_count_m2'],1)} m² | `q1_results.json → grid.area_node_count_m2` |")
A(f"| 4.1.5 | 0.05 m 中点面积 | {f(R1A['estimators']['h=0.05']['midpoint_area_m2'],1)} m² | `q1_area_estimators.json → estimators['h=0.05'].midpoint_area_m2` |")
A(f"| 4.1.5/6.2 | 0.25 m 中点面积（扫描基准） | {f(R1A['estimators']['h=0.25']['midpoint_area_m2'],1)} m² | `q1_area_estimators.json → estimators['h=0.25'].midpoint_area_m2` |")
A(f"| 4.1.5 | 网格最小可行 r / 点 | {f(R1['grid']['best_r'])} m @ ({f(R1['grid']['best_point'][0],1)}, {f(R1['grid']['best_point'][1],1)}) | `q1_results.json → grid.best_r/best_point` |")
A(f"| 4.1.5 | 网格与解析差 | {f(R1['grid']['r_diff_vs_analytic'],4)} m | `q1_results.json → grid.r_diff_vs_analytic` |")
A(f"| 6.2 | ∂r*/∂H | {f(R1['sensitivity']['dr_dH'])} m/m | `q1_results.json → sensitivity.dr_dH` |")
A(f"| 6.2 | ∂r*/∂ε_max | {f(R1['sensitivity']['dr_deps_deg'])} m/deg | `q1_results.json → sensitivity.dr_deps_deg` |")
A(f"| 6.2 | E_H / E_εmax | 1.05 / −8.16 | 派生：(H/r*)∂r*/∂H；(ε_max/r*)∂r*/∂ε_max，基数见 `optimal_station` |")
A("| 6.2 | 面积—B2 高度 / 车辆半径扫描 | 6300.4→3447.9 / 5821.9→5176.7 m² | `q1_results.json → sensitivity.area_vs_B2_height/area_vs_vehicle_radius` |")
A("| 6.2 | Q₂ 径向扫描（表 6-1） | 0.08850→0.01146 m⁻¹ | `q1_metric_compare.json → radial_scan` |")
A(f"| 6.2 | Q₂ 格点 argmax | ({f(R1M['Q2_grid_argmax']['station'][0],2)}, {f(R1M['Q2_grid_argmax']['station'][1],2)})，r={f(R1M['Q2_grid_argmax']['r_m'])} m | `q1_metric_compare.json → Q2_grid_argmax` |")
A("")
A("## 3. 第二问（1）")
A("")
A("| 正文位置 | 数字/用途 | 取值 | 唯一来源 |")
A("|---|---|---|---|")
A(f"| 4.2.2 | T2 的 r_min | {f(R2A['r_min_geo_m'])} m | `q2a_results.json → r_min_geo_m` |")
A(f"| 4.2.3 | G* / DRMS* | {f(R2A['certificate']['G_star_m'])} m / {f(R2A['certificate']['DRMS_star_m'])} m | `q2a_results.json → certificate.G_star_m/DRMS_star_m` |")
A(f"| 表 4-2 | 选中车/站点 | {R2A['chosen']['vehicles']}；({f(R2A['chosen']['stations'][0][0])},{f(R2A['chosen']['stations'][0][1])})/({f(R2A['chosen']['stations'][1][0])},{f(R2A['chosen']['stations'][1][1])}) | `q2a_results.json → chosen.vehicles/stations` |")
A(f"| 表 4-2 | d / 基线 / γ | {f(R2A['chosen']['d_m'][0])} m / {f(R2A['chosen']['baseline_m'])} m / {f(R2A['chosen']['gamma_deg'],1)}° | `q2a_results.json → chosen.d_m/baseline_m/gamma_deg` |")
A(f"| 表 4-2 | 行驶时间/和 | {f(R2A['chosen']['travel_s'][0],2)}/{f(R2A['chosen']['travel_s'][1],2)} s，和 {f(R2A['chosen']['travel_sum_s'],2)} s | `q2a_results.json → chosen.travel_s/travel_sum_s` |")
A(f"| 表 4-2 | DRMS / R95 | {f(R2A['chosen']['DRMS_m'])} / {f(R2A['chosen']['ellipse95_radius_m'])} m | `q2a_results.json → chosen.DRMS_m/ellipse95_radius_m` |")
A(f"| 表 4-2 | MC 径向 RMSE / P95 | {f(R2A['chosen']['MC']['rmse_m'])} / {f(R2A['chosen']['MC']['p95_m'])} m | `q2a_results.json → chosen.MC.rmse_m/p95_m` |")
A(f"| 4.2.3 | T2 可行弧 | [{f(R2A['circle']['feasible_runs_deg'][0][0],2)}°, {f(R2A['circle']['feasible_runs_deg'][0][1],2)}°] | `q2a_results.json → circle.feasible_runs_deg` |")
A(f"| 4.2.3 | 90° 配对族 φ 区间 | [{f(R2A['certificate']['phi_span_deg'][0],2)}°, {f(R2A['certificate']['phi_span_deg'][1],2)}°] | `q2a_results.json → certificate.phi_span_deg` |")
A(f"| 4.2.3 | V2 组合 G | {f([p for p in R2A['pair_table'] if p['pair']=='V1+V2'][0]['G_m'])} m | `q2a_results.json → pair_table[pair='V1+V2'].G_m` |")
A(f"| 4.2.3 | 退化窗 / κ(30°) | [{f(R2A['degeneracy']['gamma_window_G_le_2Gstar_deg'][0],2)}°, {f(R2A['degeneracy']['gamma_window_G_le_2Gstar_deg'][1],2)}°] / 2.0 | `q2a_results.json → degeneracy.gamma_window_G_le_2Gstar_deg/cond_number_at_30deg` |")
A(f"| 4.2.3 | 78° 回退 r / DRMS | {f(R2A['degeneracy']['backoff_r_m'])} m / {f(R2A['degeneracy']['backoff_DRMS_m'])} m（+20.5%） | `q2a_results.json → degeneracy.backoff_r_m/backoff_DRMS_m`；百分比派生 |")
A(f"| 6.2 | ∂G*/∂H | {f(R2A['sensitivity']['dG_dH_per_m'])} m/m | `q2a_results.json → sensitivity.dG_dH_per_m` |")
A("| 6.2 | G* 与 Ω₂ 随 H | 4.06→8.46 m；6272.7–6422.4 m² | `q2a_results.json → sensitivity.G_star_vs_H`（min/max 派生） |")
A("")
A("## 4. 第二问（2）")
A("")
A("| 正文位置 | 数字/用途 | 取值 | 唯一来源 |")
A("|---|---|---|---|")
A(f"| 4.2.5 | 优化开始时刻/目标 | {f(R2B['optimized']['alert_starts']['T1'],3)}/{f(R2B['optimized']['alert_starts']['T2'],3)}/{f(R2B['optimized']['alert_starts']['T3'],3)} s，目标 {f(R2B['optimized']['objective_s'],3)} s | `q2b_results.json → optimized.alert_starts/objective_s` |")
A(f"| 4.2.5 | 指派/次序 | {R2B['optimized']['assignment']}；{R2B['optimized']['orders']} | `q2b_results.json → optimized.assignment/orders` |")
A(f"| 4.2.5 | 最近指派基线 | {f(R2B['heuristic']['alert_starts']['T1'],3)}/{f(R2B['heuristic']['alert_starts']['T2'],3)}/{f(R2B['heuristic']['alert_starts']['T3'],3)} s，目标 {f(R2B['heuristic']['objective_s'],3)} s | `q2b_results.json → heuristic.alert_starts/objective_s` |")
A(f"| 4.2.5 | 差距/改善 | {f(R2B['comparison']['gap_s'],3)} s / +102.5% | `q2b_results.json → comparison.gap_s`；百分比派生 gap/obj_opt |")
A(f"| 4.2.4 | 下界 LB | {f(R2B['LB']['global'],3)} s | `q2b_results.json → LB.global` |")
A(f"| 5.2 | top-5 并列解 sum starts | {f(R2B['top5_structures'][0]['sum_starts_s'],3)} s | `q2b_results.json → top5_structures[0].sum_starts_s` |")
A(f"| 4.2.6 | 鲁棒变体目标/开始 | {f(R2B['robust_05']['obj_s'],3)} s；{R2B['robust_05']['starts']} | `q2b_results.json → robust_05.obj_s/starts` |")
A("| 6.2 | v×ω 敏感度表 | 见表 | `q2b_results.json → sensitivity_speed_omega` |")
A("| 6.2 | ω/v 弹性 | −0.44 / −0.11 | 派生：对 `sensitivity_speed_omega` 做对数差分 |")
A(f"| 4.2.6 | 刀锋净空 | 最小 {f(R2B['knife_edge']['min_station_clearance_m'],4)} m | `q2b_results.json → knife_edge.min_station_clearance_m` |")
A(f"| 4.2.1 | T1/T2/T3 区域面积 | {f(R2B['region_areas']['T1'],1)}/{f(R2B['region_areas']['T2'],1)}/{f(R2B['region_areas']['T3'],1)} m² | `q2b_results.json → region_areas` |")
_dv = {x["alert"]: x for x in R2P["delivered"]}
A(f"| 4.2.7/表 4-4 | 交付方案 γ/G/DRMS | T1 {_dv['T1']['gamma_deg']:.2f}°/{_dv['T1']['G_m']:.2f} m/{_dv['T1']['DRMS_m']:.3f} m；T2 {_dv['T2']['gamma_deg']:.2f}°/{_dv['T2']['G_m']:.2f} m/{_dv['T2']['DRMS_m']:.3f} m；T3 {_dv['T3']['gamma_deg']:.2f}°/{_dv['T3']['G_m']:.2f} m/{_dv['T3']['DRMS_m']:.3f} m | `q2b_precision.json → delivered[]` |")
A(f"| 4.2.7 | γ≥30° 约束解 | γ={f(R2P['constrained']['geometry']['T1']['gamma_deg'],2)}°，DRMS={f(R2P['constrained']['geometry']['T1']['DRMS_m'],3)} m；t_last {f(R2P['constrained']['objective_s'],3)} s（+{f(R2P['constrained']['delta_s'],3)} s，+{f(R2P['constrained']['delta_pct'],2)}%） | `q2b_precision.json → constrained.*` |")
A("")
A("## 5. 第三问")
A("")
A("| 正文位置 | 数字/用途 | 取值 | 唯一来源 |")
A("|---|---|---|---|")
A(f"| 4.3.2 | 角误差斜率 k_loc | {f(R3['model']['k_loc_deg_per_m'],6)} °/m | `q3_results.json → model.k_loc_deg_per_m` |")
A(f"| 4.3.3 | σψ 上限 | {f(R3['sigma_psi_max_deg'],6)}° | `q3_results.json → sigma_psi_max_deg` |")
A(f"| 4.3.3 | s_max（闭式） | {f(R3['s_max_m'],2)} m | `q3_results.json → s_max_m` |")
A(f"| 4.3.3 | σ(s_max) | {f(R3['sigma_s_at_smax_m'])} m | `q3_results.json → sigma_s_at_smax_m` |")
A(f"| 4.3.3 | P(80) | {f(R3['at_80']['P'],5)} | `q3_results.json → at_80.P` |")
A(f"| 4.3.3 | a+80b / b_max / a_max | {f(R3['ab_region']['a_plus_80b_max_m'])} m / {f(R3['ab_region']['b_max_m_per_m'],7)} / {f(R3['ab_region']['a_max_m'])} m | `q3_results.json → ab_region.*` |")
A(f"| 4.3.3 | b 需降至 / a 需降至 | 0.0167306 m/m（−16.3%）/ 0.0384 m | 派生：(1.638446−0.3)/80；(1.638446−0.02×80) |")
A(f"| 4.3.4 | 方差占比 s=0/40/80 | 15.6/54.0/30.4；71.3/18.4/10.3；88.1/7.6/4.3 % | `q3_results.json → contributions[].share_loc/share_zero/share_ctrl` |")
A(f"| 4.3.4 | 交叉点 | {f(R3['s_crossover_m'],3)} m | `q3_results.json → s_crossover_m` |")
A(f"| 4.3.4 | 线性化残差 RMS | {f(R3['monte_carlo']['linearization_residual_rms_deg_at80'],4)}°；方差占比 0.2% | `q3_results.json → monte_carlo.linearization_residual_rms_deg_at80`；占比派生 |")
A(f"| 4.3.4 | 精确 s_max / P(66.92) / a+80b | {f(R3['exact_geometry']['s_max_exact_m'],2)} m / {f(R3['exact_geometry']['P_at_linear_smax'],5)} / {f(R3['exact_geometry']['ab_max_exact_m'])} m | `q3_results.json → exact_geometry.*` |")
A("| 表 4-5 | MC 表 | 见表 | `q3_results.json → monte_carlo.points` |")
A("| 6.2 | s_max 对 d | 46.44/56.68/66.92/77.16/87.40/107.88 m | `q3_results.json → sensitivity.s_max_vs_d` |")
A(f"| 6.2 | ds_max/dd | {f(R3['sensitivity']['ds_max_dd_m_per_m'])} m/m | `q3_results.json → sensitivity.ds_max_dd_m_per_m` |")
A("| 6.2 | 置信度 0.90/0.95/0.98/0.99 | 85.20/66.92/51.41/43.07 m | `q3_results.json → ab_region.iso_levels` |")
A("| 6.2 | 云台缩放 0.5–1.5 | 72.32/70.11/66.92/62.63/57.03 m | `q3_results.json → sensitivity.s_max_vs_gimbal_scale` |")
A("")
A("## 6. 第四问")
A("")
A("| 正文位置 | 数字/用途 | 取值 | 唯一来源 |")
A("|---|---|---|---|")
_blocks = ("scen_new", "scen_fail", "scen_out", "scen_fail_out",
           "scen_new_fail", "scen_new_out", "scen_triple")
_n_eta = sum(1 for b in _blocks for x in R4[b]
             if x["resched"]["eta"] > x["keep"]["eta"] + 1e-9)
_n_worse = sum(1 for b in _blocks for x in R4[b]
               if x["resched"]["eta"] < x["keep"]["eta"] - 1e-9)
_n_tie = 74 - _n_eta - _n_worse
A(f"| 4.4.1 | 基线开始时刻 | {R4['baseline']['starts']} | `q4_results.json → baseline.starts` |")
A(f"| 4.4.4 | 场景计数 | {R4['scenario_design']['counts']}，合计 74 | `q4_results.json → scenario_design.counts` |")
A(f"| 4.4.4 | η 提升/持平/劣化 | {_n_eta}/{_n_tie}/{_n_worse} | 逐场景比较 `q4_results.json → scen_*[].keep.eta/resched.eta`；`q4_paper_numbers.py` |")
_v4 = R4["representative"]["resched_failV4"]
_tri = R4["representative"]["resched_triple"]
_th0 = [x for x in R4["scen_new"] if x["key"] == "th0_R30"][0]["resched"]
_fo1 = {(x["failed"], x["t_rec"]): x for x in R4["scen_fail_out"]}
_tls = [x["resched"]["t_last"] for x in R4["scen_new"]]
A(f"| 4.4.4/表 4-7 | V4 故障代表 | η={_v4['eta']:.3f}，t_last={_v4['t_last']:.2f} s | `q4_results.json → representative.resched_failV4` |")
A(f"| 4.4.4/表 4-7 | 三重代表 | η={_tri['eta']:.3f}，t_last={_tri['t_last']:.2f} s | `q4_results.json → representative.resched_triple` |")
A(f"| 4.4.4 | 新告警 θ=0°,R=30 | η={_th0['eta']:.3f}，t_last={_th0['t_last']:.2f} s | `q4_results.json → scen_new[key='th0_R30'].resched` |")
A(f"| 4.4.4 | V1 故障×中断 10/20/30 | " + "/".join(f"{_fo1[('V1', t)]['resched']['t_last']:.2f}" for t in (10.0, 20.0, 30.0)) + " s | `q4_results.json → scen_fail_out[failed='V1'][t_rec].resched.t_last` |")
A(f"| 6.2 | 新告警 t_last 范围 | {min(_tls):.2f}–{max(_tls):.2f} s | `scen_new[].resched.t_last` 的 min/max |")
A(f"| 5.4 | 记账审计问题数 | {len(R4R['audit']['issues'])} | `q4_robust.json → audit.issues` |")
_mg = {x["case"]: x for x in R4R["margin_05"]}
_dens = [x["t_last"] for x in R4R["azimuth_densification"]]
A(f"| 5.4 | 0.5 m 裕度/ε 容差/稳健基线/方位加密 | failV4 {_mg['failV4']['m00']['t_last']:.2f} s；new_th135_R30 {_mg['new_th135_R30']['m00']['t_last']:.2f} s；triple {_mg['triple_th135_R30']['m00']['t_last']:.2f} s；ε 三档均 {R4R['eps_travel'][0]['t_last']:.2f} s；加密 {min(_dens):.2f}–{max(_dens):.2f} s | `q4_robust.json → margin_05/eps_travel/baseline_robust/azimuth_densification` |")
A("| 2（P2） | 修复前后 t_last 对照 | 见文件 | `q4_tlast_before_after.md/.csv` |")
A("| 2（P5） | 74 场景明细 | 见文件 | `q4_scenario_list.md` |")
A("")
A("## 7. 常用派生公式（正文出现但 JSON 未直接存的值）")
A("")
A("| 派生量 | 公式 | 基数来源 |")
A("|---|---|---|")
A("| 改善百分比 | (obj_base−obj_opt)/obj_opt | `q2b_results.json → comparison` |")
A("| 弹性 | Δln obj / Δln x | 对应 `sensitivity_*` 数组 |")
A("| 方差占比 | var_i / var_total | `q3_results.json → contributions` |")
A("| 线性化残差占比 | (resid/σψ)² | `monte_carlo.linearization_residual_rms_deg_at80` 与 `at_80.sigma_psi_deg` |")
A("| 可行弧长 | 360° − blocked_total_deg | `q1_results.json → arc` |")
A("| 0.1→0.05 m 面积收敛差 | (A0.1−A0.05)/A0.1 | `q1_area_estimators.json` |")
A("| Q₂ 与 Q 的优劣 | Q₂(r)/Q₂(r_min) = (r_min/r)·cos²(ε−45)/cos²(35°) | `q1_metric_compare.json → radial_scan` |")
A("| 67/74 计数 | 逐场景比较 resched.eta 与 keep.eta | `q4_results.json → scen_*`；`q4_paper_numbers.py` |")
A("")
A("## 8. 核验规则（提交前）")
A("")
A("1. 任一正文数字若不在本表，先补映射再写入正文；禁止“只存在于正文”的数字。")
A("2. 重跑任一 `q*_core.py`/`q*_solve.py` 后，重新运行本脚本与本表引用的下游脚本，"
  "核对正文差异。")
A("3. 面积三值必须分别标注口径：5610.4（0.1 m 中点，主估计）、5608.5（0.05 m 中点，收敛）、"
  "5614.9（0.25 m 中点，敏感性扫描基准），节点计数 5628.7 仅作参考。")
A("4. 图表中的数字同样适用本表；图注中的极值与代表值必须能追到对应 JSON 字段。")

out = os.path.join(ROOT, "numbers.md")
with open(out, "w", encoding="utf-8") as fh:
    fh.write("\n".join(L) + "\n")
print("written", out, "lines", len(L))
