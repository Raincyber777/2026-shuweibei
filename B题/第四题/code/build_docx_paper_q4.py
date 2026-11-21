# -*- coding: utf-8 -*-
"""生成《第四题_论文素材文档.docx》（英文可粘贴段落 + 数字总表 + 图注映射）。"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _docx_common import (new_doc, title, h1, h2, para, bullet, table,
                          load_results)

R4 = load_results("q4_results.json")
cnt = R4["scenario_design"]["counts"]
BL = R4["baseline"]
reps = R4["scenario_design"]["reps"]


def gains(scen):
    ge = sum(1 for s in scen if s["resched"]["eta"] > s["keep"]["eta"])
    gt = sum(1 for s in scen if s["resched"]["eta"] == s["keep"]["eta"]
             and s["resched"]["t_last"] < s["keep"]["t_last"] - 1e-9)
    return ge, gt


doc = new_doc()
title(doc, "第四题论文素材（英文可粘贴段落 + 数字总表 + 图注映射）",
      "图内无文字，图注由论文手在 PPT 备注页取用；罗马数字分节")

h1(doc, "I. 可粘贴段落（Rescheduling model）")
para(doc, "The baseline schedule is the optimized plan of Problem 2(2) (observation "
          f"starts T1 = {BL['starts']['T1']:.2f} s, T2 = {BL['starts']['T2']:.2f} s, "
          f"T3 = {BL['starts']['T3']:.2f} s). A disturbance occurs at t = 5 s. Our "
          "rescheduling model is event-triggered and one-shot: at the planning time "
          "t_p (= 5 s, or t_rec after a communication outage) a snapshot of every "
          "vehicle is taken from a replay of the baseline timeline - (available "
          "time, position, gimbal attitude) - where vehicles already observing are "
          "locked until their reset completes (their alert counts as completed and "
          "cannot be rescheduled), while dispatched-but-not-started vehicles are "
          "freely reassignable from their current position. Because the gimbal is "
          "forced back to the due-east attitude during any travel (problem rule), "
          "every reassignment that involves moving re-slews from (0 deg, 0 deg); "
          "only a same-station reassignment rotates directly from the frozen "
          "attitude. Pending alerts are re-paired by an exhaustive enumeration of "
          "assignment structures (C(|A|,2)^|pending| times reuse orders) with "
          "greedy initialization, Gauss-Seidel coordinate descent over the doubled "
          "vehicles, and a final Nelder-Mead polish of every station against the "
          "global objective; mutual-waiting deadlocks are detected by the "
          "fixed-point simulation and discarded. The objective is lexicographic: "
          "maximize the number of alerts that start within the 60 s window first, "
          "then minimize the latest observation start time t_last.", indent=False)

h1(doc, "II. 可粘贴段落（Keep-original policy and metrics）")
para(doc, "The keep-original policy issues no new commands. Under a vehicle failure, "
          "any pending alert that lost one of its two vehicles can never start "
          "(its surviving partner keeps waiting), so k drops by one and t_last = 60 "
          "s; under a new alert, T4 is never assigned and likewise cannot start; a "
          "communication outage alone changes nothing because the baseline tasks "
          "were already commanded at t = 0. Metrics follow the problem statement: "
          "eta = k/N with N = 3 + 1{new alert}, and t_last = max observation start "
          "over alerts that start, set to 60 s whenever any pending alert cannot "
          "start inside the window.", indent=False)

h1(doc, "III. 可粘贴段落（Scenario set, justified）")
sd = R4["scenario_design"]
para(doc, f"The uncertainty is covered by a designed scenario set: the new alert's "
          f"azimuth is sampled every 45 deg (8 directions covering the full circle, "
          f"since the vehicle distribution is asymmetric) crossed with R = 30/40/50 m "
          f"(endpoints and midpoint of the given interval), H = 50 m fixed - "
          f"{cnt['A_new']} scenarios; all five equally-likely single-vehicle failures; "
          f"outage recovery times t_rec = 10/20/30 s (representative quantiles of the "
          f"uniform span (5, 30]); and combination scenarios built from three "
          f"representative new-alert positions (best/median/worst of the "
          f"single-disturbance sweep: {list(reps.values())}) crossed with the two "
          f"impact-different failures (V2 orphans T3, V4 orphans T2; V1 and V4 "
          f"impact T2 symmetrically, and a V5 failure is immaterial because its "
          f"only task, T1, has already completed by t = 5 s) and the early/late "
          f"recovery times - "
          f"{sum(cnt.values())} scenarios in total. All scenarios are evaluated "
          f"under both policies with identical simulation rules.", indent=False)

h1(doc, "IV. 可粘贴段落（Results）")
blocks = (("new-alert", "scen_new"), ("single-failure", "scen_fail"),
          ("outage", "scen_out"), ("failure x outage", "scen_fail_out"),
          ("new x failure", "scen_new_fail"), ("new x outage", "scen_new_out"),
          ("triple", "scen_triple"))
para(doc, "Across the scenario set the rescheduling policy never performs worse than "
          "keep-original and strictly improves every structurally damaged case; "
          "keep-original retains eta = 1 only in scenarios without a new alert and "
          "without an impacted failure. Per block (rescheduling gains in eta / in "
          "t_last among equal-eta cases):", indent=False)
rows = [["Block", "Scenarios", "Resched gains eta", "Resched gains t_last",
         "keep-original keeps eta = 1"]]
for label, key in blocks:
    sc = R4[key]
    ge, gt = gains(sc)
    nk = sum(1 for s in sc if s["keep"]["eta"] == 1.0)
    rows.append([label, str(len(sc)), str(ge), str(gt), f"{nk}/{len(sc)}"])
table(doc, rows[0], rows[1:])
rep = R4["representative"]
r4s = rep["resched_failV4"]
k4 = rep["keep_failV4"]
r2 = rep["resched_triple"]
k2 = rep["keep_triple"]
para(doc, f"Representative cases. (i) Failure of V4 (orphaning T2): keep-original "
          f"eta = {k4['eta']:.3f}, t_last = {k4['t_last']:.0f} s; rescheduling re-pairs "
          f"T2 and restores eta = {r4s['eta']:.3f} with t_last = {r4s['t_last']:.2f} s "
          f"(assignment { {a: tuple(v) for a, v in r4s['assignment'].items()} }, starts "
          f"{r4s['starts']}). (ii) Triple disturbance (median new-alert position, V4 "
          f"failure, outage until t_rec = 10 s): keep-original eta = {k2['eta']:.3f}; "
          f"rescheduling at t = 10 s restores eta = {r2['eta']:.3f} with "
          f"t_last = {r2['t_last']:.2f} s.", indent=False)

h1(doc, "V. 可粘贴段落（When rescheduling helps, when it fails, and why）")
para(doc, "Rescheduling converts structural losses (an unassigned alert, an orphaned "
          "alert) into temporal losses (a later observation start), which is strictly "
          "preferable under the eta-first metric. Its value is bounded by three "
          "factors: the azimuthal distribution of the idle or reassignable vehicles "
          "(a new alert appearing near idle vehicles is recovered almost "
          "immediately, whereas a far-side alert forces a cross-field repositioning), "
          "the recovery delay (slew plus travel), and the communication blackout - "
          "during the outage no command can be issued, so a failure occurring at "
          "t = 5 s is only repaired at t_rec and t_last grows roughly linearly with "
          "t_rec. Rescheduling never underperforms keep-original in our scenario set "
          "(the baseline plan itself belongs to the searched feasible set), and the "
          "two policies coincide for a pure communication outage and for the failure "
          "of a vehicle whose only task was the already-completed T1.", indent=False)

h1(doc, "VI. 英文数字总表（全部取自 JSON）")
rows2 = [["Baseline starts (s)", f"T1 {BL['starts']['T1']:.2f} / T2 "
                                 f"{BL['starts']['T2']:.2f} / T3 {BL['starts']['T3']:.2f}"],
         ["Disturbance time / window", "t = 5 s; [0, 60] s"],
         ["Scenario counts", f"A {cnt['A_new']} / B {cnt['B_fail']} / C {cnt['C_outage']} / "
                             f"D {cnt['D_fail_out']} / E {cnt['E_new_fail']} / "
                             f"F {cnt['F_new_out']} / G {cnt['G_triple']}"],
         ["New-alert keep-original", "eta = 0.75, t_last = 60 s (all 24 positions)"],
         ["Impacted-failure keep-original", "eta = 0.67, t_last = 60 s"],
         ["Representative V4 failure", f"keep ({k4['eta']:.2f}, {k4['t_last']:.0f}) -> "
                                       f"resched ({r4s['eta']:.2f}, {r4s['t_last']:.2f})"],
         ["Representative triple", f"keep ({k2['eta']:.2f}, {k2['t_last']:.0f}) -> "
                                   f"resched ({r2['eta']:.2f}, {r2['t_last']:.2f})"]]
table(doc, ["Item", "Value"], rows2)

h1(doc, "VII. 图注建议（图内无文字）")
table(doc, ["Label", "File", "Caption (suggest)"], [
    ["Fig. 1", "fig1_map_new_alerts",
     "24 new-alert positions coloured by rescheduled t_last (s)."],
    ["Fig. 2", "fig2_tlast_vs_theta",
     "t_last vs azimuth for R = 30/40/50 m; keep-original level 60 s."],
    ["Fig. 3", "fig3_failures",
     "Single-failure scenarios: eta and t_last, keep vs reschedule."],
    ["Fig. 4", "fig4_fail_outage",
     "Failure x outage: t_last vs t_rec per failed vehicle."],
    ["Fig. 5", "fig5_gantt_failV4",
     "Representative timelines for the V4 failure: keep vs reschedule."],
    ["Fig. 6", "fig6_global_scatter",
     "All scenarios in the (t_last, eta) plane, both policies."],
])

h1(doc, "VIII. 格式红线提醒")
bullet(doc, "全文英文、12 号 Times New Roman；正文 ≤ 25 页；图注在下、表注在上；图形图表无中文。")
bullet(doc, "题面四处点名对应：重调度模型、与保持原方案对比、(θ,R,H) 场景集设计与论证、受益/失效分析及原因——均已在素材中给段。")
bullet(doc, "代码进附录或支撑材料；数字源 results/q4_results.json 与 q4_summary.txt。")

doc.save(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                      "第四题_论文素材文档.docx"))
print("saved 第四题_论文素材文档.docx")
