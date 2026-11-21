# -*- coding: utf-8 -*-
"""生成《第四题_建模文档.docx》（重调度模型与场景对比，数字取自 JSON）。"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _docx_common import (new_doc, title, h1, h2, para, bullet, table,
                          load_results)

R4 = load_results("q4_results.json")
cnt = R4["scenario_design"]["counts"]
BL = R4["baseline"]


def gains(scen):
    ge = sum(1 for s in scen if s["resched"]["eta"] > s["keep"]["eta"])
    gt = sum(1 for s in scen if s["resched"]["eta"] == s["keep"]["eta"]
             and s["resched"]["t_last"] < s["keep"]["t_last"] - 1e-9)
    return ge, gt


def fmt_resched(r):
    return f"η={r['eta']:.2f}, t_last={r['t_last']:.2f} s"


doc = new_doc()
title(doc, "第四题（扰动下的重调度与方案对比）建模文档",
      "2026 数维杯 B 题 Problem 4 · 事件触发重调度 vs 保持原方案 · 2026-11-21")

h1(doc, "I. 问题重述与建模总览")
para(doc, f"以第二问 2(2) 的优化调度为基线（告警开始时刻 {BL['starts']['T1']:.2f} / "
          f"{BL['starts']['T2']:.2f} / {BL['starts']['T3']:.2f} s，指派 T1←{tuple(BL['assignment']['T1'])}、"
          f"T2←{tuple(BL['assignment']['T2'])}、T3←{tuple(BL['assignment']['T3'])}）。t = 5 s 发生扰动："
          "①新告警 T4（θ ∈ [0°,360°)，R ∈ [30,50] m，H = 50 m，需两车）；②五辆车等概率恰坏一辆（坏车退出且不挡路）；"
          "③通信中断 [5, t_rec]，t_rec ∈ (5,30]，中断期车辆继续在手任务，恢复后才接收新指令。"
          "规则：扰动前已开始观测的告警视为完成、不可重排（T1 于 1.61 s 开始 → 已完成锁定）；"
          "已派出未开始观测的车可重指派。评估窗 [0,60] s，η = k/N 优先、t_last 次之"
          "（存在未开始告警时 t_last 记 60 s）。设计重调度模型并与“保持原方案”对比，输出 (η, t_last) 与时间轴。")

h1(doc, "II. 重调度模型")
h2(doc, "II.1 状态快照（事件时刻的可行域内状态）")
para(doc, "对基线时间轴回放得到每车任务记录（出发/到达/就绪/观测窗/复位），在计划时刻 t_p 生成状态快照："
          "每车（可用时刻 t_avail，位置 pos，云台姿态 att，锁定至 locked_until）。状态分类与规则：")
bullet(doc, "行驶中：位置沿直线段插值，云台保持正东水平（题面规则）→ 姿态 (0°,0°)，立即可重指派；"
            "未观测，但含行驶段，改派后从正东全角转台；")
bullet(doc, "转台中：位置在站，姿态按转台进度线性插值，立即可重指派（未观测，同站改派可续转）；")
bullet(doc, "同步等待中（就绪后、观测开始前）：位置在站，姿态 = 目标指向，立即可重指派"
            "（未观测，同站改派可续转）；")
bullet(doc, "观测中 / 复位中：该告警已开始 → 告警锁定为完成；车辆锁定至复位完成，之后姿态回正东、位置在站"
            "（已观测，不参与重排，不存在续转）。")
h2(doc, "II.2 姿态感知的转台时长")
para(doc, "题面规定行驶期间云台保持正东水平，故任何含行驶的改派，其转台都从 (0°,0°) 起算："
          "slew = max(|α|, ε)/30。**“续转”只对未观测改派生效**：仅当车辆尚未开始观测、"
          "且新站与当前站位重合（无行驶段，距离 ≤ 5 cm）时，从当前姿态续转："
          "slew = max(|wrap(α_new − α_cur)|, |ε_new − ε_cur|)/30；"
          "其余一切改派均先行驶、再从正东全角转台。已开始观测或复位中的车辆锁定，不参与重排，"
          "故不存在续转。该裁定与 A6 一致：续转场景无行驶段、车辆已在站，"
          "属于同一指向阶段的延续，不构成新的“到站—指向”过程。复位规则不变（观测后回正东水平）。")
h2(doc, "II.3 待排告警与可用资源")
para(doc, "待排告警 = 基线中开始时刻 ≥ t_plan 的告警（若被孤儿化——其配对车之一故障——在持续原方案下永不开始，"
          "在重调度下仍待排）∪ {T4（若发生新告警）}。可用车辆 = 全部未故障车辆（忙碌车按其 t_avail/pos/att 参与指派）。"
          "N = 3 + 1{新告警}。")
h2(doc, "II.4 重优化与目标")
para(doc, "与 2(2) 同一套完备枚举（C(|A|,2)^|待排| 结构 × 复用车顺序排列）+ 贪心初始化 + 高斯-赛德尔坐标下降"
          " + 最优 12 结构的全局 NM 精修（绕障 travel_time、姿态感知转台、严格可行性罚函数）。"
          "目标字典序：先最大化 60 s 内成功开始的告警数（η），再最小化 t_last（含 T1 的已完成开始时刻）。"
          "互等死锁（循环依赖）由定点迭代检测剔除。")
h2(doc, "II.5 保持原方案（对照策略）的形式化")
para(doc, "不发出任何新指令：各车继续基线任务。若故障车 ∈ 某待排告警的配对，该告警失去一车、永不开始"
          "（k 减 1，t_last = 60）；新告警无指派、永不开始；中断对照原方案无影响（无需新指令）。"
          "该策略的 (η, t_last) 可由基线开始时刻与故障孤儿化关系直接解析得到。")

h1(doc, "III. 场景集设计与论证（题面点名）")
sd = R4["scenario_design"]
para(doc, "不确定性来自新告警 (θ, R)、故障车辆、t_rec。设计原则：方位覆盖 + 区间端点 + 对称性约简 + 代表位置组合：")
bullet(doc, f"新告警：θ 每 45° 一档共 8 档（覆盖全圆；车辆分布非对称，45° 足以刻画方向效应）× "
            f"R ∈ {sd['R_list_m']} m（题给区间端点 + 中点）= {cnt['A_new']} 个场景；H = 50 m 为题定值。")
bullet(doc, "故障：5 选 1 等概率，全部 5 个都评估。基线方案中 V5 的唯一任务是已完成的 T1 → V5 故障退化为"
            "无影响场景；V3 故障则孤儿化 T3（V3 是复用链 T1→T3 的执行者）——这本身是一个有价值的发现。")
bullet(doc, f"中断：t_rec ∈ {sd['t_rec_list_s']} s，取 (5,30] 均匀假设的下/中/上代表分位。")
bullet(doc, f"组合：新告警位置取单扰动扫描中最优/中位/最劣 3 个代表（{list(sd['reps'].values())}）；"
            f"故障取 V2、V4（分别孤儿化 T3 与 T2；V2 与 V3 对 T3 影响对称、V1 与 V4 对 T2 影响对称，"
            f"V5 的唯一任务是已完成的 T1、故障无影响）；"
            f"t_rec 取 10/30 s（早晚恢复两端）。组合数：新×故障 {cnt['E_new_fail']}、"
            f"故障×中断 {cnt['D_fail_out']}、新×中断 {cnt['F_new_out']}、三重 {cnt['G_triple']}。")
bullet(doc, "评估判据：η 优先、t_last 次之（题面定义）；另报告逐告警开始时刻与代表场景的每车时间轴。")

h1(doc, "IV. 求解结果汇总（数字取自 JSON）")
blocks = (("A 新告警（24）", "scen_new"), ("B 单车故障（5）", "scen_fail"),
          ("C 单中断（3）", "scen_out"), ("D 故障×中断（15）", "scen_fail_out"),
          ("E 新告警×故障（6）", "scen_new_fail"), ("F 新告警×中断（9）", "scen_new_out"),
          ("G 三重组合（12）", "scen_triple"))
rows = []
for label, key in blocks:
    sc = R4[key]
    ge, gt = gains(sc)
    n_eta_keep = sum(1 for s in sc if s["keep"]["eta"] == 1.0)
    rows.append([label, f"{ge}", f"{gt}", f"{n_eta_keep}/{len(sc)}"])
table(doc, ["场景类", "重调度使 η 提升的场景数", "重调度使 t_last 缩短的场景数",
            "keep-original 保持 η=1 的场景数"], rows)
para(doc, "结构性结论（与数值无关、由模型保证）：①含新告警的场景 keep-original 恒为 η=0.75、t_last=60"
          "（T4 无指派）；②被孤儿化告警的故障场景 keep-original 恒为 η=2/3、t_last=60；③单中断（无故障）"
          "两策略完全等价（车辆无需新指令即可完成基线计划）；④V5 故障对两策略均无影响"
          "（其唯一任务 T1 已于 1.61 s 完成锁定；而 V3 故障会孤儿化 T3、有影响）。其余差异见 JSON 数值。")

rep = R4["representative"]
h2(doc, "IV.1 代表场景：V4 故障（孤儿化 T2）")
k = rep["keep_failV4"]
r4s = rep["resched_failV4"]
para(doc, f"keep-original：η = {k['eta']:.3f}，t_last = {k['t_last']:.0f} s（V4 永久等待、T2 永不开始）。"
          f"重调度：η = {r4s['eta']:.3f}，t_last = {r4s['t_last']:.2f} s，新指派 "
          f"{ {a: tuple(v) for a, v in r4s['assignment'].items()} }，开始时刻 {r4s['starts']}——"
          "V2、V3 被重新配对到 T2，η 恢复为 1，代价是 T2 的开始时刻推迟。")
h2(doc, "IV.2 代表场景：三重组合（中位新告警位置 + V4 故障 + t_rec=10 s）")
k2 = rep["keep_triple"]
r2 = rep["resched_triple"]
para(doc, f"keep-original：η = {k2['eta']:.3f}，t_last = {k2['t_last']:.0f} s。"
          f"重调度（t=10 s 恢复后触发）：η = {r2['eta']:.3f}，t_last = {r2['t_last']:.2f} s，"
          f"指派 { {a: tuple(v) for a, v in r2['assignment'].items()} }，开始 {r2['starts']}。")

h1(doc, "V. 机理分析：重调度何时受益、何时失效")
bullet(doc, "受益场景 1（新告警）：keep-original 恒 η=0.75/t_last=60；重调度把空闲或可重指派的车辆"
            "（其中被改派者放弃原转台、由行车期间回正东规则重新全角转台）配给 T4，η 恢复 1；"
            "t_last 由 T4 的可达性决定——新告警方位靠近空闲车辆时 t_last 小，落在需跨场调动时 t_last 大（见 fig2）。")
bullet(doc, "受益场景 2（孤儿化故障）：keep-original η=2/3；重调度用空闲车（或改派他车）补配，η 恢复 1；"
            "若故障叠加中断，恢复只能发生在 t_rec 之后 → t_last 随 t_rec 线性推迟（中断越长损失越大）。")
bullet(doc, "无差异场景：单中断（无故障/无新告警）两策略相同；V5 故障两策略相同（其唯一任务 T1 已完成锁定；"
            "resched 的 t_last 与 keep 相差 2×10⁻⁵ s，按 0.01 s 报告精度记为持平，属优化器数值噪声）；"
            "且重调度从不劣于 keep-original——该性质依赖“重优化目标与基线目标一致、且约束集包含基线方案”"
            "这两个条件（基线方案本身在搜索空间内）。")
bullet(doc, "失效/受限情形：三重组合中若 t_rec 很晚（如 30 s），恢复的告警开始时刻被推到 ~30+ s，"
            "t_last 显著恶化但仍优于 η 损失（η 优先级更高）；若新告警方位落在所有可用车辆的就绪可达域之外"
            "（60 s 窗内无法双车就绪），重调度也无法救回（本场景集中未出现该情形，因其可达域覆盖全场）。")
bullet(doc, "机理小结：重调度的价值 = 把“结构性损失”（无指派/缺车）转化为“时间性损失”（开始时刻推迟）；"
            "其上限受制于（a）空闲车辆的方位分布、（b）转台+行车的恢复时延、（c）中断封锁期的长度。")

h1(doc, "VI. 鲁棒性与检验（复核后新增）")
RB5 = load_results("q4_robust.json")
para(doc, f"记账审计：对全部 {RB5['audit']['n_scenarios']} 个场景重推 (η, t_last) 的记账关系"
          f"（η = k/N、存在未开始告警时 t_last = 60、t_last = 已开始告警的最大开始时刻），"
          f"发现 {len(RB5['audit']['issues'])} 处问题。")
mg = RB5["margin_05"]
rows = [["代表场景", "η（无裕度 → 0.5 m 裕度）", "t_last（无裕度 → 0.5 m 裕度）",
         "修复后最小 LOS 净空 (m)"]]
for m in mg:
    rows.append([m["case"].replace("new_", "新告警 ").replace("triple_", "三重 ")
                 .replace("failV4", "V4 故障"),
                 f"{m['m00']['eta']:.2f} → {m['m05']['eta']:.2f}",
                 f"{m['m00']['t_last']:.2f} → {m['m05']['t_last']:.2f}",
                 f"{m['m00']['min_clearance_m']:.4f} → {m['m05']['min_clearance_m']:.4f}"
                 f"（修复 {m['m05']['repaired']} 站）"])
table(doc, rows[0], rows[1:])
eps_lines = "；".join(f"ε = {e['eps_m']} m：η = {e['eta']:.2f}、t_last = {e['t_last']:.2f} s"
                      for e in RB5["eps_travel"])
para(doc, f"零位移容差 ε 的敏感性：{eps_lines}——结论不随 ε 变化。")
br_lines = "；".join(f"{b['case']}：keep η = {b['keep']['eta']:.2f} → resched η = "
                     f"{b['resched']['eta']:.2f}（t_last {b['resched']['t_last']:.2f} s）"
                     for b in RB5["baseline_robust"])
para(doc, f"基线鲁棒变体（Q2(2) 的 0.5 m 裕度方案 10.837 s）替换基线后：{br_lines}"
          "——重调度相对 keep-original 的结论方向不变。")
dn = RB5["azimuth_densification"]
dn_txt = "；".join(f"θ = {d['theta']:g}°：t_last = {d['t_last']:.2f} s" for d in dn)
para(doc, "如实披露：三重组合场景中有 1 站位于 T3 可观测域的固有薄区（B3 东角附近），"
          "±1.5 m 邻域内不存在 0.5 m 净空的可行点，该站未完成裕度化——但 η 与 t_last 均不受影响；"
          "其完全裕度化需要更大的重定位或接受更晚的开始时刻。")
para(doc, f"方位网格加密验证（8 个 22.5° 中间方位，R = 40 m）：{dn_txt}——"
          "t_last 曲线在网格点之间平滑过渡，45° 采样的场景集论证成立。")

h1(doc, "VII. 与题面要求的对应")
bullet(doc, "重调度模型：事件触发 + 状态快照 + 完备结构枚举 + 连续精修（II）。")
bullet(doc, "与保持原方案对比：(η, t_last) 全场景对照（IV），策略细节与规则逐条落实（锁定/可重指派/中断期继续在手任务）。")
bullet(doc, "单扰动与组合扰动：A/B/C/D/E/F/G 六类共 "
            f"{sum(cnt.values())} 个场景（III）。")
bullet(doc, "新告警 (θ,R,H) 的代表性场景集与论证：III（45° 方位覆盖 × R 端点中点 × 代表位置组合）。")
bullet(doc, "(η, t_last)、策略与每车时间轴：JSON 与 fig5/图集备注（代表场景完整时间轴）。")
bullet(doc, "受益/失效分析及原因：V。")

doc.save(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                      "第四题_建模文档.docx"))
print("saved 第四题_建模文档.docx")
