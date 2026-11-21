# -*- coding: utf-8 -*-
"""Build 第二题_建模文档.docx (Chinese modeling document, Roman-numeral sections)."""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _docx_common import (new_doc, title, h1, h2, para, bullet, table, spacer,
                          load_results)

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "第二题_建模文档.docx")
RA = load_results("q2a_results.json")
RB = load_results("q2b_results.json")
ch = RA["chosen"]
DRMS_S = RA["certificate"]["DRMS_star_m"]
RSTAR = RA["r_min_geo_m"]
REACH_DESC = "B(Vᵢ, 90 m)（30 s 绕障可达域，路径时间 ≤ 30 s）"


def chain_facts(op):
    """Data-driven description of the reuse chain(s) from Gantt segments."""
    orders = op["orders"]
    segs = RB["gantt_opt"]
    out = []
    for v, tasks in sorted(orders.items()):
        if len(tasks) < 2:
            continue
        ss = segs[v]
        obs = [s for s in ss if s[0] == "obs"]
        facts = {"v": int(v[1:]) - 1, "tasks": tasks, "obs": obs, "legs": []}
        # legs between consecutive observations: reset -> travel -> slew
        cur = {"reset": None, "travel": 0.0, "slew": None}
        for s in ss:
            if s[0] == "obs":
                if cur["reset"] is not None:
                    facts["legs"].append(dict(cur))
                cur = {"reset": None, "travel": 0.0, "slew": None}
            elif s[0] == "reset" and cur["reset"] is None:
                cur["reset"] = float(s[2]) - float(s[1])
            elif s[0] == "travel" and cur["reset"] is not None:
                cur["travel"] += float(s[2]) - float(s[1])
            elif s[0] == "slew" and cur["reset"] is not None:
                cur["slew"] = float(s[2]) - float(s[1])
        out.append(facts)
    return out


def chain_zh(facts):
    parts = []
    for f in facts:
        legs = "；".join(
            f"复位 {g['reset']:.2f} s，行驶 {g['travel']:.2f} s，转云台 "
            f"{g['slew']:.2f} s" for g in f["legs"])
        parts.append(f"V{f['v']+1} 依次执行 {'→'.join(f['tasks'])}"
                     f"（{'；'.join('观测 [{:.2f}, {:.2f}]'.format(o[1], o[2]) for o in f['obs'])}；{legs}）")
    return "；".join(parts)


CH = chain_facts(RB["optimized"])
OP = RB["optimized"]
HP = RB["heuristic"]

doc = new_doc()
title(doc, "第二题（双站交会定位与多目标车辆复用调度）建模文档",
      "2026 第十二届数维杯秋季赛 B 题 · Problem 2(1) & 2(2) · 2026-11-20")

# ============================ I ============================
h1(doc, "I. 问题重述与建模总览")
para(doc, "第二问包含两个子问题。子问题 2(1)：建立双站方位角交会的定位精度模型（方位角测角误差独立服从 N(0,(1°)²)），"
          "给出精度指标并论证其与基线长、交会角、目标距离的关系；在每车行驶时间不超过 30 s 的约束下从 5 辆车中选 2 辆、"
          "并为告警 T2（150°, 45, 35，水平投影 T2′=(11.0289, 72.5000)，高度 35 m）选择最优双站，报告站坐标、基线长、交会角、"
          "行驶时间与精度指标；讨论交会角 γ→0°/180° 及站点位于可观测域边界时的模型退化与处理策略。")
para(doc, "子问题 2(2)：三告警 T1、T2、T3 在 t=0 同时释放，共 6 个任务槽而只有 5 辆车，必须复用；每告警的两辆车须同步观测，"
          "目标为最小化三告警观测开始时刻的最大值；输出每车完整时间轴；并独立定义“最近指派启发式”基线、对比分析差异来源。")
para(doc, "两个子问题共用第一问的三约束可观测域模型（车辆几何 C1、俯仰角 C2、视线遮挡 C3，相切即遮挡）与同一套车辆/云台参数。"
          "建模路线：先解析建模并推导可证明的下界，再做小规模精确枚举与连续精修，最后以蒙特卡洛与逐项手工核验双重验证。")

# ============================ II ============================
h1(doc, "II. 子问题 2(1)：交会精度模型与可证全局最优双站")
h2(doc, "II.1 误差传播模型推导")
para(doc, "设两站 p₁=(x₁,y₁)、p₂=(x₂,y₂)，到目标水平投影 T′ 的水平距离（站目距）为 d₁、d₂，"
          "视线方位角为 α₁、α₂（自正东逆时针）。测角误差 δαᵢ~N(0,σ²) 独立，σ=1°=π/180 rad。")
para(doc, "第 i 条视线为过 pᵢ、方向 uᵢ=(cosαᵢ, sinαᵢ) 的直线，其单位法向 nᵢ⊥uᵢ。视线横移误差为 δᵢ=dᵢ·δαᵢ，"
          "交会点是两条平移后直线的交点，满足线性方程组 A·Δp = δ，其中 A=[n₁ᵀ; n₂ᵀ]，δ=(δ₁,δ₂)ᵀ。")
para(doc, "于是交会点误差协方差为 Σ = A⁻¹ D A⁻ᵀ，D=diag(d₁²σ², d₂²σ²)。由于 det A = n₁×n₂ = ±sin γ"
          "（γ 为两视线方向夹角，即交会角），得闭式结果：")
para(doc, "    trace(Σ) = σ²(d₁²+d₂²)/sin²γ，  det(Σ) = σ⁴d₁²d₂²/sin²γ。", indent=False)
h2(doc, "II.2 精度指标及其合理性")
para(doc, "定义几何精度因子（无量纲化前）G(d₁,d₂,γ) = √((d₁²+d₂²)/2) / |sin γ|（单位 m），精度指标取 DRMS = σ·G，"
          "即交会点误差椭圆均方根半径（2 维均方根位置误差/√2）。其合理性：①G 只依赖站目几何（站目距与交会角），"
          "与坐标系的旋转平移无关；②G 与 1σ 误差椭圆面积 π·σ²·d₁d₂/|sinγ| 单调一致（等 d₁=d₂ 时相等），且对协方差各向同性/异性统一刻画；"
          "③G² 正比于克拉美-罗下界意义的参数估计方差，γ=90° 时最小。95% 圆半径取 DRMS·√χ²₂(0.95)=DRMS·2.4477（各向同性时精确）。")
h2(doc, "II.3 关键定理：可证明的全局下界与取等条件")
para(doc, f"引理（QM≥AM）：√((d₁²+d₂²)/2) ≥ (d₁+d₂)/2，等号当且仅当 d₁=d₂；又由第一问同类约束，"
          f"可观测域内任一站满足 dᵢ ≥ r_min = (H₂−h_cam)/tan80° = 33/tan80° = {RSTAR:.4f} m。故对一切可行双站：")
para(doc, f"    G ≥ (d₁+d₂)/2 ≥ r_min = {RSTAR:.4f} m，", indent=False)
para(doc, f"等号当且仅当 d₁=d₂=r_min 且 |sinγ|=1（γ=90°）。定理（全局最优）：只要 r_min 圆上存在两个可行点、"
          f"其极角差恰为 90°，且两站分别可达（30 s 路径可达），则全局最优几何因子 G*={RSTAR:.4f} m，"
          f"DRMS*=σ·G*={DRMS_S:.4f} m。数值验证：r_min 圆上可行弧 "
          f"[{RA['circle']['feasible_runs_deg'][0][0]:.2f}°, {RA['circle']['feasible_runs_deg'][-1][1]:.2f}°]，"
          "其中“鲁棒可行弧”（LOS 屋顶净空与几何裕度 ≥0.5 m）为 "
          f"[{RA['circle']['robust_runs_deg'][0][0]:.2f}°, {RA['circle']['robust_runs_deg'][-1][1]:.2f}°]，"
          f"存在 90° 配对族 φ∈({RA['certificate']['phi_span_deg'][0]:.2f}°, "
          f"{RA['certificate']['phi_span_deg'][1]:.2f}°)，证书成立——最优解集仍是一维连续族（与第一问结构一致），"
          "故需 tie-breaking 唯一化。")
h2(doc, "II.4 退化分析与处理策略（题面点名）")
bullet(doc, "γ→0°/180°：sinγ→0，G→∞；法方程矩阵 A 的条件数 κ=1/|sinγ|→∞，交会点对测角误差极端敏感，估计失效。"
            "处理：①运行侧约束交会窗 γ∈[30°,150°]（对称站型下 G≤2G(90°)；本模型给出 γ∈(30.05°,149.95°) 为 G≤2G* 的精确窗口）；"
            "②估计侧采用正则化：以两视线到初始粗解的加权最小二乘（TLS）+ 微小岭项求解，并放大报告置信椭圆；"
            "③任务侧触发重定位：指派车辆侧移以张开交会角后再观测。")
dg = RA["degeneracy"]
bullet(doc, "站点位于可观测域边界：最优解落在 d=r_min 圆（俯仰角=80° 主动）或遮挡/几何边界上时，约束主动、裕度为零，"
            "微小扰动即失可行（“刀锋解”）。处理：以裕度回退设计——例如要求俯仰 ≤78°"
            f"（r ≥ 33/tan78° = {dg['backoff_r_m']:.4f} m，DRMS 增至 {dg['backoff_DRMS_m']:.4f} m，"
            f"代价 +{(dg['backoff_DRMS_m']/DRMS_S-1)*100:.1f}%），并要求 LOS 屋顶净空 ≥0.5–0.75 m、"
            "几何裕度 ≥0.5–0.75 m；本问 tie-breaking 即在该鲁棒内域上执行（见 II.5）。")
h2(doc, "II.5 选车选站模型与三级 tie-breaking")
para(doc, f"决策变量：车辆对 (Vᵢ,Vⱼ)（C(5,2)=10 组合）与两站位置 p₁,p₂；约束：p₁∈Ω₂∩{REACH_DESC}、"
          f"p₂∈Ω₂∩{REACH_DESC}（Ω₂ 为 T2 三约束可观测域，0.1 m 单元中心栅格面积 "
          f"{RA['region']['area_m2']:.1f} m²）。目标：min G。行驶时间按绕障最短路径计"
          "（可视图+Dijkstra；直线距离只是下界——如 V2 到 T2 可观测域东缘的直线路径穿越 B4 缓冲区）。"
          "对含 V2 的组合：其直线路径 29.98 s 已近上限，绕障后超过 30 s，判不可行；其余组合可达 r_min 圆，"
          "G 达到下界 5.8188 m——对照表说明选车必要性。")
para(doc, "精度目标对最优族不敏感（一维连续族），需三级字典序 tie-breaking 唯一化：")
bullet(doc, "T1（总行驶时间最短）：在鲁棒内域（LOS 净空 ≥0.75 m、几何裕度 ≥0.75 m）且直线路径不入建筑缓冲的条件下，"
            "min(t₁+t₂)。理由：部署最快，且与 2(2) 的时效目标同向。")
bullet(doc, "T2（最大单车行驶时间最短）：min max(t₁,t₂)。")
bullet(doc, "T3（字典序兜底）：仍并列取 (φ₁,φ₂) 字典序最小。")
para(doc, f"结果：选 {ch['vehicles']}，站 p₁=({ch['stations'][0][0]:.4f}, {ch['stations'][0][1]:.4f})（V3）、"
          f"p₂=({ch['stations'][1][0]:.4f}, {ch['stations'][1][1]:.4f})（V5），d₁=d₂={RSTAR:.4f} m，"
          f"γ={ch['gamma_deg']:.3f}°，基线 B={ch['baseline_m']:.4f} m，行驶 "
          f"({ch['travel_s'][0]:.2f}, {ch['travel_s'][1]:.2f}) s、总和 {ch['travel_sum_s']:.2f} s；"
          f"两站 LOS 屋顶净空 ({ch['los_clearance_m'][0]:.2f}, {ch['los_clearance_m'][1]:.2f}) m，"
          "直线路径净空（绕障模型下行驶时间与直线一致）。")

# ============================ III ============================
h1(doc, "III. 子问题 2(2)：六槽五车复用调度模型")
h2(doc, "III.1 时序规则的形式化")
para(doc, "车辆 v 的一个任务（告警 a、站点 p）耗时链：行驶 t_tr=|pos−p|/3 → 转云台 t_sl=max(|α|,ε)/30（α 为站→目标方位角，"
          "ε 为仰角；水平/俯仰同时转取较长者）→ 与同伴同步（观测开始=两者就绪时刻的较大者）→ 同步观测 5 s → "
          "云台复位（时长仍为 max(|α|,ε)/30，回正东水平）→ 出发下一站。t=0 全部车辆位于初始位置、云台正东水平。")
h2(doc, "III.2 决策结构与目标")
para(doc, "决策 = (指派：每告警 2 辆互异车辆；每车任务顺序；每任务站点)。目标 min max_a(告警 a 观测开始时刻)。"
          "结构空间完备枚举：每告警从 10 个车辆对中选 1，共 10³=1000 种指派组合，再乘以复用车辆的任务排列（≤2 辆双任务车，各 ≤2 种序）。")
h2(doc, "III.3 站点选择的分解与耦合")
para(doc, "单车任务的就绪时刻 = 前站出发时刻 + 行驶 + 转云台，站点选择是 2 维连续优化；复用车的第二任务站点选择依赖第一任务的"
          "完成位置与时刻，而第一任务的观测开始又取决于同伴——形成链式耦合。处理：贪心初始化 + 高斯-赛德尔坐标下降"
          "（双任务车在候选集上做 p₁×p₂ 枚举）+ 对最优结构的全部站点做全局目标下的 Nelder-Mead 连续精修（严格可行性罚函数）。")
h2(doc, "III.4 下界与死锁判定")
para(doc, f"下界证书：r(v,a)=min_p[|V_v−p|/3 + max(|α|,ε)/30] 为车辆 v 对告警 a 的最早可就绪时刻；告警 a 需两辆互异车，"
          f"故 start(a) ≥ r(v,a) 的次小值，全局 LB = max_a 次小值 = {RB['LB']['global']:.3f} s（T2 列）。该界不计复用延迟，故偏松；"
          f"在全部 1000 结构 × 站点精修意义下搜索到的最优为 {RB['optimized']['objective_s']:.3f} s（见 IV）。")
para(doc, "死锁判定：若两辆复用车互相等待对方先完成的告警（如 v₁ 先 T2 后 T1、v₂ 先 T1 后 T2），链条形成循环依赖，"
          "物理上互等、无合法时刻表；仿真器以定点迭代检测，无进展即判该结构不可行并剔除。")
h2(doc, "III.5 最近指派启发式基线（题面点名，独立定义）")
para(doc, "定义：按告警索引序 T1→T2→T3 依次为每告警依次填两槽；每槽在未承担本告警的车辆中，选取“当前链末端到其本告警"
          "就绪最小站的行驶时间”最小者（即最近者，平局取车号小者），站点取该就绪最小站；复用车在其已承诺链之后追加任务。"
          "同一时序规则仿真。该基线只看“谁最近”，不考虑同步配对质量与链条次序效应。")

# ============================ IV ============================
h1(doc, "IV. 求解结果（数值自 results/*.json 单一数据源）")
h2(doc, "IV.1 各车最早就绪时刻表 r(v,a)（s）")
rows = []
rv = RB["r_va_table"]
for v in ["V1", "V2", "V3", "V4", "V5"]:
    rows.append([v] + [f"{rv[v][a]:.3f}" for a in ["T1", "T2", "T3"]])
table(doc, ["车辆", "T1", "T2", "T3"], rows)
para(doc, f"解读：就绪时刻由“行驶+转云台”共同决定——V1 对 T3 就绪 {rv['V1']['T3']:.3f} s 是因为 T3 位于 V1 正东"
          "（pan 转角≈0.9°，slew 由 49.8° 俯仰主导）；V2 对 T1 就绪 "
          f"{rv['V2']['T1']:.3f} s 由 93.2° 的 pan 转角主导。这解释了“最优站往往就在车辆原位附近”。")
h2(doc, "IV.2 优化方案与启发式基线对比")
op, hp = RB["optimized"], RB["heuristic"]
rows = [
    ["T1", f"{op['alert_starts']['T1']:.3f}", f"{hp['alert_starts']['T1']:.3f}"],
    ["T2", f"{op['alert_starts']['T2']:.3f}", f"{hp['alert_starts']['T2']:.3f}"],
    ["T3", f"{op['alert_starts']['T3']:.3f}", f"{hp['alert_starts']['T3']:.3f}"],
    ["最大观测开始时刻（目标）", f"{op['objective_s']:.3f}", f"{hp['objective_s']:.3f}"],
]
table(doc, ["告警", "优化方案 (s)", "最近指派基线 (s)"], rows)
oa = op["assignment"]
ha = hp["assignment"]
para(doc, f"优化指派：T1←({oa['T1'][0]+1},{oa['T1'][1]+1})，T2←({oa['T2'][0]+1},{oa['T2'][1]+1})，"
          f"T3←({oa['T3'][0]+1},{oa['T3'][1]+1})；复用链：{chain_zh(CH)}。"
          f"基线指派：T1←({ha['T1'][0]+1},{ha['T1'][1]+1})，T2←({ha['T2'][0]+1},{ha['T2'][1]+1})，"
          f"T3←({ha['T3'][0]+1},{ha['T3'][1]+1})，V1、V3 双任务。目标差距 "
          f"{RB['comparison']['gap_s']:.2f} s（基线劣化 "
          f"{(hp['objective_s']/op['objective_s']-1)*100:.0f}%）。")
h2(doc, "IV.3 差异来源分析")
bullet(doc, "同步配对损失：基线把“最近”的两辆车配给同一告警（如 V1+V3 给 T2），但告警开始取决于较慢者——快车被迫等待，"
            "而真正受限的 T2 反而由更慢的组合覆盖。优化方案把 V4（pan 转角 176.7° 导致就绪 6.99 s）配给 T2 时，"
            "让 V1 只承担 3.13 s 即就绪的一侧，避免双慢配对。")
bullet(doc, "复用链次序效应：基线让 V1 先 T2 后 T3、V3 先 T1 后 T2，两条链把慢任务串在快告警之后，阻塞了 T3 的早期窗口；"
            f"优化方案仅 {'、'.join('V%d' % (f['v']+1) for f in CH)} 一车复用，"
            f"链内复位+转位+转云台合计 "
            f"{sum(g['reset']+g['travel']+g['slew'] for f in CH for g in f['legs']):.2f} s，链代价最小。")
bullet(doc, "方位角驱动的站点选择：就绪时刻对 pan 转角高度敏感（30°/s），基线以行驶距离选站而忽略转角；"
            "优化模型的就绪时刻最小化天然偏向“小转角、近原位”的站。")
h2(doc, "IV.4 并列最优与 tie-breaking")
top5 = RB["top5_structures"]
n_tie = sum(1 for t in top5 if abs(t["obj_s"] - top5[0]["obj_s"]) < 1e-6)
para(doc, f"结构枚举+精修后有 {n_tie} 个结构并列达到最优 {top5[0]['obj_s']:.3f} s"
          f"（对应 T2 由 {'、'.join('(%d,%d)' % (t['assignment']['T2'][0], t['assignment']['T2'][1]) for t in top5[:n_tie])} 承担的变体），"
          f"二级 tie-breaking 取三告警开始时刻之和最小者（{top5[0]['sum_starts_s']:.2f} s），唯一确定最终方案。")

# ============================ V ============================
h2(doc, "IV.5 刀锋解披露与 0.5 m 裕度鲁棒变体（复核后新增）")
knife = RB["knife_edge"]
rob = RB["robust_05"]
para(doc, f"最优方案（数学最优 {op['objective_s']:.3f} s）的两处站位 LOS 净空处于刀锋量级："
          f"V3 的 T3 站 {knife['station_clearances_m']['V3']['T3']:.4g} m、V4 的 T2 站 "
          f"{knife['station_clearances_m']['V4']['T2']:.4g} m——数学上可行（非相切），物理上脆弱。"
          f"以 LOS 净空 ≥ {rob['margin_m']:.1f} m 为附加约束，对最优 8 个结构做裕度惩罚精修，"
          f"得鲁棒变体 obj = {rob['obj_s']:.3f} s（+{(rob['obj_s']-op['objective_s']):.3f} s），"
          f"开始时刻 {rob['starts']}——部署建议采用鲁棒变体；η/t_last 对比结论对两种口径均成立。"
          f"另注：“最优”指 1000 指派结构 × 站点精修意义下的最好解（结构穷举完备、站点精修为数值方法），非全局证书。")
para(doc, "路径模型口径说明：绕障路径用 1.5 m 方形外扩（矩形膨胀），站址判据用圆盘距离——方形外扩是圆盘外扩的"
          "包围盒，方形路径为保守上界；V2 相关组合的不可行结论在两种口径下均成立（方形 30.28 s > 30 s，"
          "圆盘网格上界 30.37 s），但裕度较薄。V2 的直线既穿 B4 也穿 B5 的缓冲。", indent=False)

h1(doc, "V. 模型检验与敏感性")
h2(doc, "V.1 蒙特卡洛验证（2(1)）")
mc = ch["MC"]
para(doc, f"在最优双站下注入 N(0,1°) 方位角误差 {mc['n']//10000} 万次并按视线精确求交："
          f"RMSE={mc['rmse_m']:.4f} m（解析 σ·√2={DRMS_S*np.sqrt(2):.4f}），"
          f"P95={mc['p95_m']:.4f} m（解析 {ch['ellipse95_radius_m']:.4f}）——闭式传播模型成立。")
h2(doc, "V.2 逐项核验（2(2)）")
chain0 = CH[0]
g0 = chain0["legs"][0]
para(doc, f"r(v,a) 表与手算一致；甘特图各环节时长与“行驶/转云台/同步等待/5 s/复位”逐项吻合；三告警开始时刻与链式推演一致"
          f"（复用链：就绪 {chain0['obs'][0][1]:.2f} → 观测 [{chain0['obs'][0][1]:.2f},{chain0['obs'][0][2]:.2f}] → "
          f"复位至 {chain0['obs'][0][2]+g0['reset']:.2f} → 行驶 {g0['travel']:.2f} s → 转云台 {g0['slew']:.2f} s → "
          f"就绪 {chain0['obs'][1][1]:.2f}）。")
h2(doc, "V.3 敏感性（参数扰动重仿真）")
sens = RB["sensitivity_speed_omega"]
rows = []
for s in sorted(sens, key=lambda t: (t["speed"], t["omega_deg_s"])):
    rows.append([f"{s['speed']}", f"{s['omega_deg_s']:.0f}",
                 f"{s['obj_s']:.2f}" if s["obj_s"] is not None else "—"])
table(doc, ["车速 (m/s)", "云台角速度 (°/s)", "目标值 (s)"], rows)
sens_map = {(s["speed"], s["omega_deg_s"]): s["obj_s"] for s in sens}
o_base = op["objective_s"]
sp_lo, sp_hi = sens_map[(2.5, 30.0)], sens_map[(3.5, 30.0)]
om_lo, om_hi = sens_map[(3.0, 24.0)], sens_map[(3.0, 36.0)]
para(doc, f"目标值对云台角速度最敏感（24→36 °/s 变化 "
          f"{(om_hi-om_lo)/o_base*100:.1f}%），对车速次之（±17% 车速变化 "
          f"{(sp_lo-o_base)/o_base*100:+.1f}% / {(sp_hi-o_base)/o_base*100:+.1f}%）——"
          "再次印证“转角主导、行程次要”的结构性结论；部署启示：优先小转角选站、提高云台转速收益大于提速。")
h2(doc, "V.4 2(1) 的闭式敏感性与佐证数值")
senA = RA["sensitivity"]
para(doc, f"∂G*/∂H = 1/tan80° = {senA['dG_dH_per_m']:.4f} m/m"
          f"（DRMS 对 H 的敏感度 {senA['dDRMS_dH_m_per_m']:.5f} m/m）；"
          f"γ 运行窗 [{dg['gamma_window_G_le_2Gstar_deg'][0]:.2f}°, "
          f"{dg['gamma_window_G_le_2Gstar_deg'][1]:.2f}°]；"
          f"裕度回退设计点 r={dg['backoff_r_m']:.4f} m 对应 DRMS={dg['backoff_DRMS_m']:.4f} m。")

doc.save(OUT)
print("saved", OUT)
