## Abstract

Low-altitude small UAVs provide only azimuth, horizontal range and altitude alerts and cannot be localized directly. Following the chain "geometric feasibility—intersection accuracy—error propagation—disturbance response", this paper builds four models—observable-region determination, two-station intersection accuracy, pointing-error propagation and event-triggered rescheduling—and follows the route of certifying the optimal value in closed form, enumerating the optimal solution deterministically, and using numerical experiments only for verification.

For Problem 1 (observable region and optimal station for one target), the three constraints—vehicle geometry, gimbal pitch and line-of-sight (LOS) occlusion—are intersected, and the reciprocal of the horizontal distance is used as the quality measure, giving an observable-region model and a quality-optimization model. The minimum horizontal distance is about 7.58 m with the elevation at the 80° pitch limit, so the optimum is attained with the pitch constraint active and is independent of the building layout, and the optimal set is a continuous arc of 283.85°. A representative station (88.88, 76.29) m is then selected by the three-level rule (maximum safety-margin band, shortest reachable point within the band, coordinate lexicographic order). The observable area is 5610 m² (56.1% of the site), and the grid recomputation differs from the closed-form bound by only 0.0007 m.

For Problem 2 (two-station intersection accuracy and multi-alert scheduling), the error propagation relation is derived from the LOS equations, the geometric dilution of precision G characterizes the accuracy, and the mean inequality proves the lower bound, giving a two-station accuracy model and a six-slot five-vehicle scheduling model. The accuracy bound is 5.8188 m, attained when the two stations are equidistant and the lines of sight are orthogonal, with DRMS 0.1016 m and a 95% radius of 0.2486 m. The latest observation start is 10.355 s, 50.6% shorter than the nearest-assignment baseline of 20.968 s, and the robust plan gives 10.837 s. Substituting the plan back into the accuracy model shows that the first alert has an intersection angle of only 19.34° and degraded accuracy; requiring γ ≥ 30° raises the latest start to 12.983 s, so timeliness and accuracy are not interchangeable.

For Problem 3 (localization and pointing errors versus horizontal azimuth accuracy), the localization error is projected onto the cross-range direction and linearized for small angles, and the three error sources are combined into a normal distribution, giving a pointing-error propagation model. The maximum reliable observation distance is 66.92 m (a conservative 66.84 m from high-accuracy quadrature), and the dominant error source switches at a vehicle–target distance of about 19.9 m. At 80 m the probability of meeting the criterion falls to 0.915, so the distance-error coefficient must be reduced by about 16.3%; localization then contributes 88.1% of the variance.

For Problem 4 (plan failure under vehicle failure, communication outage and new alerts), event-triggered snapshots are combined with rescheduling, giving a rescheduling model under disturbance. Among 74 scenarios the completion rate improves in 67, ties in 7 and never degrades, and for a single vehicle failure the latest observation start drops from 60 s to 11.17 s. The mechanism is that structural loss is converted into temporal loss.

Sensitivity analysis shows that the pitch limit, the angular rate, the vehicle–target distance and the communication recovery time are the core parameters of the four problems: a 1 m rise in target height increases the minimum horizontal distance by 0.176 m, a 1° relaxation of the pitch limit reduces it by 0.774 m, and the elasticity of the angular rate is about four times that of the travel speed; no qualitative conclusion changes under reasonable perturbations. The paper thus gives provable results for station selection and accuracy bounds, and reliable plans for scheduling and disturbances in the sense of structural exactness and station-wise local optimality, providing a quantitative basis for station placement and cooperative scheduling in low-altitude surveillance.

**Keywords:** UAV localization; two-station intersection; geometric dilution of precision; observable region; vehicle scheduling; event-triggered rescheduling

## Contents

# 1. Introduction

## 1.1 Background

When a low-altitude small UAV enters the surveillance airspace, the reconnaissance system reports only the target's azimuth, horizontal range, and altitude, not its position. A single vehicle yields only one bearing line; two vehicles observing synchronously from different directions intersect two bearing lines to determine the horizontal position. The target altitude is given by the alert and does not enter the intersection, but it affects feasibility and accuracy through elevation constraints, building occlusion, and pointing errors. A baseline that is too short, or an intersection angle that is too small or too large, amplifies the error; station geometry is therefore the key to accuracy.

## 1.2 Problems to Be Solved

**(1) Single-target observable region and optimal station.** For T1, determine and plot the observable region under the three constraints of vehicle geometry, LOS occlusion, and gimbal pitch. Using Q = 1/r as the quality measure, find the optimal station, horizontal distance, and elevation angle, and specify the optimality criterion and tie-breaking rules.

**(2) Two-station intersection accuracy and multi-target assignment.** Under independent azimuth errors N(0,(1°)²), establish the analytical relation between accuracy and baseline, intersection angle, and station–target distance, and define an accuracy index. Under a per-vehicle travel limit of 30 s, select two of five vehicles for T2 and analyze the degeneracy as γ→0°/180° and at boundary stations. With three alerts released simultaneously and six slots shared by five vehicles, minimize the latest observation start time; give the assignment, stations, and complete timeline for each vehicle, and independently define a nearest-assignment baseline for comparison.

**(3) Localization and pointing error propagation.** The localization error is σ(s) = 0.3 + 0.02s m (independent and identically distributed in x and y), the gimbal bias is 0.8°, and the control error is 0.6°, independent; the target position is exact and the vehicle–target distance is 40 m. Build the propagation model for Δψ and find the maximum travel distance satisfying P(|Δψ| ≤ 5°) ≥ 0.95. Derive the constraints on a,b ≥ 0 in σ(s) = a + bs required to still satisfy the criterion at 80 m; justify the approximation, compare the contributions of the three error sources, and give deployment implications.

**(4) Rescheduling under disturbances.** Taking the 2(2) plan as the baseline, at t = 5 s consider a new alert (θ ∈ [0°,360°), ρ ∈ [30,50] m, H = 50 m), exactly one vehicle failure, a communication outage [5,t<sub>rec</sub>] (t<sub>rec</sub> ∈ (5,30]), and their combinations. Build a rescheduling model and compare it with keeping the original plan; lock observations that have started and allow redispatch of dispatched-but-unobserved vehicles; design a representative scenario set; report results within [0,60] s with η as the primary and t<sub>last</sub> as the secondary index, and analyze the mechanism.

# 2. Problem Analysis

The four problems progress along the chain "geometric feasibility—intersection accuracy—error propagation—disturbance response": Q1 answers where observation is possible and where it is best; Q2 extends single-station geometry to two-station intersection and multi-alert scheduling; Q3 advances deterministic geometry to error probability; Q4 advances static scheduling to disturbance response. The feasible region, accuracy conclusions, and timeline of earlier problems form the input baselines of later ones. Figure 2-1 shows the input–output relations and the modeling chain.

[[FIG:论文图表/fig0_framework.png|Figure 2-1 Framework of the four problems and the overall modeling chain]]

## 2.1 Geometry and Parameters

The site is a flat 100 m × 100 m square with the southwest corner as the origin, the x-axis east and the y-axis north; the dispatch center is O = (50,50). The site contains five axis-aligned cuboid buildings and five standby observation vehicles; their geometry and initial positions are listed in Table 2-1. A vehicle is modeled as a disk of radius 1.5 m, travels at a constant 3 m/s, carries a camera 2 m above the ground, and has a gimbal pitch range of [−10°,80°] with horizontal and pitch angular rates of 30°/s; the slew time is set by the slower axis. During travel the gimbal remains level facing east, and it may turn toward the target only after arrival. A task consists of travel, slew, synchronized 5 s observation by two vehicles, and reset; all phases are counted on the timeline. A line of sight that merely touches a building counts as occluded. An alert is given as (θ,ρ,H), and the target's horizontal position is (50+ρ cos θ, 50+ρ sin θ); the baseline alerts are T1(30°,40 m,45 m), T2(150°,45 m,35 m), and T3(285°,38 m,55 m) (see [1]); Problem 4 adds T4(θ ∈ [0°,360°), ρ ∈ [30,50] m, H = 50 m).

**Table 2-1 Building geometry and initial positions of the observation vehicles**

| Category | ID | Footprint (m) | Initial position (x, y) (m) | Height (m) |
|---|---|---|---|---|
| Building | B1 | [22, 34] × [16, 26] | — | 20 |
| Building | B2 | [63, 79] × [59, 71] | — | 28 |
| Building | B3 | [10, 24] × [65, 76] | — | 12 |
| Building | B4 | [72, 86] × [22, 34] | — | 24 |
| Building | B5 | [41, 51] × [38, 46] | — | 32 |
| Vehicle | V1 | — | (15, 14) | — |
| Vehicle | V2 | — | (88, 10) | — |
| Vehicle | V3 | — | (14, 86) | — |
| Vehicle | V4 | — | (88, 68) | — |
| Vehicle | V5 | — | (50, 93) | — |

Note: All buildings are axis-aligned cuboids standing on z = 0; a vehicle is an equivalent disk of radius 1.5 m, and the tabulated position is the initial coordinate of its center (the ground projection of the camera). The three baseline alerts are given in Section 2.1; the complete parameter table is provided in `params_table.md` in the supporting materials.

## 2.2 Analysis of Problem 1

Problem 1 asks where observation is possible, where it is best, what "best" means, and how to break ties: the observable region gives the feasible set, the optimal station is the optimizer within it, and the criterion and tie-breaking rule guarantee uniqueness. The difficulty is that the three constraint types are heterogeneous and the optimal solution may be a one-dimensional continuum; this paper therefore adopts an "analytics first, numerics as evidence" route.

## 2.3 Analysis of Problem 2

Part 2(1) requires a two-station intersection accuracy model, an accuracy index, selection of vehicles and stations for T2 under the 30 s limit, and a discussion of degeneracy. Part 2(2) requires minimizing the latest observation start time with three alerts, six slots, and five vehicles, outputting the complete timeline and comparing with a nearest-assignment baseline. The two parts share geometry and the timeline but have different objectives: 2(1) targets accuracy and 2(2) targets timeliness, so the stations in 2(2) are independently re-optimized for timeliness and cannot simply reuse the accuracy-optimal stations of 2(1).

## 2.4 Analysis of Problem 3

Problem 3 requires a propagation model for Δψ, the value of s<sub>max</sub>, the (a,b) constraints at 80 m, justification of the approximation, comparison of three error sources, and deployment implications. The difficulties are that the three error sources have different dimensions, atan2 is nonlinear, the criterion is two-sided, and the (a,b) constraints rely on the monotonicity of σ(s).

## 2.5 Analysis of Problem 4

Problem 4 uses the 10.355 s plan of Problem 2(2) as the baseline and considers, at t = 5 s, new alerts, a single vehicle failure, communication outages, and their combinations. The difficulty is that disturbances occur mid-execution: a state snapshot must decide what is locked and what can be redispatched; no new commands can be received during an outage, so rescheduling should be triggered at t<sub>rec</sub>; new-alert parameters are continuous, so a representative scenario set must be designed; and the evaluation index is the lexicographic pair (η,t<sub>last</sub>).

## 2.6 Algorithm Routes and Selection

The algorithms for the four problems follow three criteria—provable, reproducible, and scale-matched: a closed-form certificate is used for the optimal value whenever possible instead of iterative search; deterministic complete enumeration is used instead of randomized heuristics when the scale permits; and numerical experiments serve only as verification. Table 2-2 gives an overview; details are in Sections 4.2.5, 4.3.7, 4.4.4, and 4.5.4.

**Table 2-2 Algorithm routes and selection rationale for the four problems**

| Problem | Algorithm (key steps) | Rationale | Scale / complexity | Comparison with alternatives |
|---|---|---|---|---|
| Q1 | Closed-form lower bound (C2 ⇒ r ≥ r<sub>min</sub>); 200,000-point sampling on the r<sub>min</sub> circle; 3-D slab intersection; visibility graph + Dijkstra; three-level lexicographic rule | Q = 1/r is strictly monotone, so the optimal value is fixed in closed form by the active constraint; the optimal set is a one-dimensional arc, and sampling only describes the set, not a 2-D search | Closed form O(1); arc sampling O(2×10⁵); one grid verification O(10⁶) | A 0.1 m grid only gives the best grid value 7.5828 m; the closed form also gives the global certificate 7.5821 m |
| Q2(1) | Covariance propagation Σ = A<sup>−1</sup>DA<sup>−T</sup>; QM–AM lower-bound certificate; enumeration of C(5,2) = 10 pairs; polar candidate stations + Nelder–Mead | The equality condition reduces optimality verification to a one-dimensional 90° pairing test on the r<sub>min</sub> circle; with only five vehicles, pairs can be exhaustively enumerated | 10 pairs; 4-D NM ≤ 300 iterations per pair | Direct 4-D search has no optimality proof and easily falls into local optima; the certificate gives G* = 5.8188 m |
| Q2(2) | 1,000 assignment structures expanded through reuse-chain orderings into 5,880 combinations; fixed-point timeline simulation for each; greedy initialization → Gauss–Seidel coordinate descent → Nelder–Mead; top-12 re-refinement; deadlock detection | With only 5 vehicles and 6 slots, complete enumeration exhausts the structures and is deterministic and reproducible; continuous station positions are handled by local refinement | 5,880 simulations; at most 2 tasks per vehicle; ≤160 NM iterations per call | 10.355 s vs. 20.968 s for nearest assignment (−50.6%); randomized searches such as GA cannot guarantee the same solution |
| Q3 | Closed-form first-order propagation; two-sided quantile criterion; bisection; 256×256 Gauss–Hermite quadrature; 10<sup>6</sup> MC verification | σ<sub>ψ</sub>(s) is monotone, so the P criterion can be inverted in closed form; Hermite quadrature has no sampling error and uses 1/15 of the MC nodes | Closed form O(1); 65,536 quadrature nodes; 10<sup>6</sup> MC for verification only | Closed form 66.92 m vs. exact 66.84 m (0.13%); direct MC root search requires multiple rounds of 10<sup>6</sup> samples |
| Q4 | Event-triggered snapshot; reuse of the Q2(2) solver; deterministic enumeration of 74 scenarios; analytical keep-original evaluation | After a disturbance, available resources and pending alerts are of the same order as Q2(2); reusing the solver keeps the conventions consistent; the scenario set is small, so no online stochastic optimization is needed | 74 scenarios × one re-optimization each; timeline audit finds 0 negative durations/overlaps | η improved in 67/74, tied in 7, degraded in 0; scenario-by-scenario comparison with keep-original |

# 3. Symbols and Assumptions

## 3.1 Symbols

Table 3-1 lists the main symbols used throughout the paper.

**Table 3-1 Main symbols**

| Symbol | Meaning | Unit / value |
|---|---|---|
| O | Dispatch center | (50,50) m |
| B<sub>i</sub> | Building i (i = 1,…,5), planar range [x<sub>i</sub><sup>0</sup>,x<sub>i</sub><sup>1</sup>]×[y<sub>i</sub><sup>0</sup>,y<sub>i</sub><sup>1</sup>], height h<sub>i</sub> | m |
| T<sub>a</sub>; θ<sub>a</sub>,ρ<sub>a</sub>,H<sub>a</sub>; T′<sub>a</sub> | Alert a and its target; azimuth (counterclockwise from east), horizontal distance, height; horizontal projection | °, m, m; m |
| h<sub>cam</sub>; Δz<sub>a</sub> | Camera height above ground; camera–target height difference Δz<sub>a</sub> = H<sub>a</sub> − h<sub>cam</sub> | 2 m; m |
| p = (x,y); r(p); ε(p) | Center of the observation station; horizontal distance from camera to target projection; LOS elevation arctan(Δz<sub>a</sub>/r) | m; m; ° |
| [ε<sub>min</sub>,ε<sub>max</sub>] | Feasible gimbal pitch range | [−10°,80°] |
| C1,C2,C3; Ω<sub>a</sub> | Vehicle geometry, gimbal pitch, and LOS occlusion constraints; observable region Ω<sub>a</sub> = C1∩C2∩C3 | —; m² |
| Q(p); p*,r*,ε*,Q* | Observation quality 1/r; optimal station, horizontal distance, elevation, and quality in Problem 1 | m<sup>−1</sup>; m,m,°,m<sup>−1</sup> |
| m(p); φ | Geometric safety margin; polar angle parameter of the optimal arc | m; ° |
| V<sub>j</sub>; V<sub>j</sub><sup>0</sup> | Observation vehicle j and its initial position (j = 1,…,5) | m |
| R<sub>veh</sub>; v; ω | Equivalent vehicle disk radius; travel speed; maximum gimbal single-axis angular rate | 1.5 m; 3 m/s; 30°/s |
| α | Azimuth from station to target (pan command angle) | ° |
| t<sub>tr</sub>,t<sub>sl</sub>,t<sub>obs</sub>,t<sub>rs</sub> | Travel, slew, synchronized observation, and reset times | s (t<sub>obs</sub> = 5) |
| d<sub>i</sub>; d | Horizontal distance from station i to target; single-station shorthand in Problem 3 (nominal 40 m) | m |
| σ<sub>α</sub>; γ; β | Single-station azimuth standard deviation; intersection angle of the two LOS; two-station baseline length | 1° (rad in computation); °; m |
| Σ; G | Covariance of the intersection-point position error; geometric dilution of precision √((d<sub>1</sub>²+d<sub>2</sub>²)/2)/\|sin γ\| | m²; m |
| DRMS; R95 | Root-mean-square position error σ<sub>α</sub>G; 95% error-circle radius 2.4477DRMS | m; m |
| π<sub>j</sub>; p<sub>j,a</sub>; M<sub>a</sub> | Task order of vehicle j; station of vehicle j for alert a; vehicle pair observing alert a | —; m; — |
| t<sup>rd</sup><sub>v,k</sub>; t<sub>a</sub><sup>start</sup> | Ready time of the k-th task of vehicle v; observation start time of alert a | s |
| P,P̂,δ; s; σ(s) = a + bs | True position, estimated position, and localization error; cumulative travel distance; single-axis localization standard deviation (a,b ≥ 0) | m; m; m,m/m |
| ε<sub>0</sub>,ε<sub>c</sub>; Δψ; σ<sub>ψ</sub>; s<sub>max</sub> | Gimbal bias/control error; signed pointing offset ψ<sub>cmd</sub>−ψ<sub>true</sub> (wrap180); combined standard deviation of Δψ; maximum travel distance satisfying P(\|Δψ\| ≤ 5°) ≥ 0.95 | 0.8°/0.6°; °; °; m |
| t<sub>p</sub>,t<sub>rec</sub>; N,k,η; t<sub>last</sub> | Rescheduling trigger/communication recovery time; total alerts, successful starts, η = k/N; latest observation start time (60 s if not started) | s; —; s |

## 3.2 Assumptions

(A1) **Site and building geometry.** The site is level; the five buildings are axis-aligned cuboids standing on the ground, with the given planar outlines and heights. The coordinate system and building geometry are collected in Section 4.1. Terrain, vegetation, and other obstacles are ignored.

(A2) **Vehicle geometry and motion.** An observation vehicle is a disk of radius 1.5 m; its center must lie at least 1.5 m from the site boundary and at least 1.5 m from each building footprint (Minkowski expansion, Section 4.1). Vehicles travel at a constant 3 m/s; acceleration, braking, turning, and collision avoidance are ignored. Paths are shortest obstacle-avoiding paths, and straight-line distance is only a lower bound.

(A3) **Gimbal kinematics.** The pitch range [−10°,80°] is closed. Both axes rotate at 30°/s and can rotate simultaneously; the slew time is the longer axis, and start/stop transients and control delay are ignored. During travel the gimbal remains level facing east; it may turn toward the target only after the vehicle stops.

(A4) **Line of sight and occlusion.** The LOS is the straight segment from the camera to the target; buildings are opaque. Tangency or contact counts as occlusion; the 3-D slab test is given in Section 4.1. Atmospheric refraction and rain/fog are ignored.

(A5) **Targets and alerts.** Targets are stationary during deployment. An alert (θ,R,H) is treated as the true horizontal position and height, without measurement error. Height is used only for elevation and occlusion tests; it does not enter the intersection solution.

(A6) **Observation timing and information.** Two vehicles begin a 5 s synchronized observation after arriving and completing the slew; they then reset and travel to the next station, with all phases counted on the timeline. During travel the gimbal remains east; after arrival it performs a full-angle slew. Only when a dispatched-but-unobserved vehicle is redispatched and the new station coincides with its current position (no travel segment) does the first post-snapshot task continue from the current attitude; all later tasks start from east. Except during a communication outage, commands, feedback, and computation have no delay.

(A7) **Error statistics.** In Problem 2, the two stations' azimuth errors are independent N(0,(1°)²). In Problem 3, the vehicle's horizontal coordinate errors are independent, identically distributed normal in x and y; the gimbal bias 0.8° and control error 0.6° are independent of each other and of the localization error. All sources have zero mean.

(A8) **Decision information and disturbances.** At t = 0, when the baseline plan is made, no disturbance is known in advance; rescheduling is triggered only after a disturbance occurs, using real-time information. No random events other than the specified disturbances are considered. A failed vehicle exits immediately and does not block traffic.

# 4. Model Establishment and Solution

## 4.1 Geometric Preprocessing and Conventions

All four problems share the same site geometry and observation model. This section collects the three conventions used repeatedly below; they are not repeated in each problem.

(a) **Coordinate system and site.** The southwest corner is the origin, the x-axis points east, and the y-axis points north; the site is [0,100]², and the dispatch center is O = (50,50). A building is the axis-aligned cuboid [x<sub>i</sub><sup>0</sup>,x<sub>i</sub><sup>1</sup>]×[y<sub>i</sub><sup>0</sup>,y<sub>i</sub><sup>1</sup>]×[0,h<sub>i</sub>] standing on z = 0; the camera height is h<sub>cam</sub> = 2 m. The horizontal projection of an alert (θ,ρ,H) is T′ = (50+ρ cos θ, 50+ρ sin θ), and its height is H.

(b) **Vehicle geometry and Minkowski expansion.** A vehicle is a disk of radius R<sub>veh</sub> = 1.5 m centered at p = (x,y). The vehicle geometry constraint is

$$ C1 = {p : 1.5 ≤ x ≤ 98.5, 1.5 ≤ y ≤ 98.5, d(p,B<sub>i</sub>) ≥ 1.5, i = 1,…,5}, $$ (1)

where d(p,B) = √{[max(x<sub>0</sub>−x,0,x−x<sub>1</sub>)]² + [max(y<sub>0</sub>−y,0,y−y<sub>1</sub>)]²}; this is equivalent to expanding each building footprint by 1.5 m (Minkowski dilation).

(c) **Slab test for LOS occlusion.** The LOS is the 3-D segment from the camera (p,2) to the target T = (T′,H). For the k-th axis interval [lo<sub>k</sub>,hi<sub>k</sub>], compute the parameter interval [t<sub>k</sub><sup>−</sup>,t<sub>k</sub><sup>+</sup>] and set t<sub>enter</sub> = max<sub>k</sub> t<sub>k</sub><sup>−</sup>, t<sub>exit</sub> = min<sub>k</sub> t<sub>k</sub><sup>+</sup>. The segment intersects the cuboid (including tangency) if and only if max(t<sub>enter</sub>,0) ≤ min(t<sub>exit</sub>,1). Tangency counts as occlusion, and numerical intersection tests use a tolerance of 1e−9 [2]. The LOS occlusion constraint is

$$ C3 = ∩<sub>i=1</sub><sup>5</sup>{p : L(p) ∩ B<sub>i</sub> = ∅}. $$ (2)

The observable region is Ω = C1∩C2∩C3, where the gimbal pitch constraint C2 is given by ε(p) = arctan(Δz/r(p)) ∈ [−10°,80°]; for a given target, Δz = H − h<sub>cam</sub>, which is equivalent to r ≥ Δz/tan 80°, with Δz evaluated per problem. The gimbal timing and the rule "return to east during travel, turn after arrival" follow A3/A6 and are not repeated below.

## 4.2 Problem 1: Observable Region and Optimal Station

### 4.2.1 Constraint Formalization and Optimization Model

The horizontal projection and 3-D position of T1 are

$$ T′ = (50+40cos30°, 50+40sin30°) = (84.6410,70.0000) m, $$ (3)

$$ T = (84.6410,70.0000,45) m,  Δz = 45−2 = 43 m. $$ (4)

From C1/C3 in Section 4.1, the gimbal pitch constraint for T1 (Δz = 43 m) is equivalent to

$$ C2 = {p : r(p) ≥ r<sub>min</sub>},  r<sub>min</sub> = Δz/tan80° = 43/5.6712818 = 7.5821 m. $$ (5)

The observable region is Ω = C1∩C2∩C3. With Q(p) = 1/r(p) as the observation quality, the optimal station is

$$ p* = argmax<sub>p∈Ω</sub> Q(p) = argmin<sub>p∈Ω</sub> r(p). $$ (6)

The criterion is chosen for four reasons. (i) A single-station angle error δα translates into a lateral position error r·δα at the target, so 1/r has the same direction as single-station accuracy. (ii) C2 itself is r ≥ r<sub>min</sub>, so Q is aligned with the active constraint, and maximizing Q is equivalent to pushing the pitch to its upper bound. (iii) In the two-station accuracy model of 2(1), DRMS increases monotonically with the station–target distances d<sub>i</sub> (Section 4.3.1), so a smaller r is desirable for two-station accuracy. (iv) Q is coordinate-independent, dimensionally simple, and strictly monotone, which facilitates tie-breaking. Q is not the only admissible criterion; the alternative Q<sub>2</sub> = (1/r)cos²(ε−45°) was also tested, and both criteria have the same optimal set.

### 4.2.2 Global Lower Bound and Optimality Theorem

**Lemma 1.** For any p ∈ Ω, r(p) ≥ r<sub>min</sub>.

Proof. By C2, ε(p) ≤ 80°. Since arctan is strictly increasing on (0,∞) and Δz > 0, r(p) ≥ Δz/tan80° = r<sub>min</sub>. ∎

**Theorem 1.** If Ω∩{p : r(p) = r<sub>min</sub>} is nonempty, then r* = r<sub>min</sub>, ε* = 80°, Q* = 1/r<sub>min</sub> = 0.1319 m<sup>−1</sup>, and the optimal set is the arc(s) of the r<sub>min</sub> circle that lie in Ω.

Proof. By Lemma 1, r* ≥ r<sub>min</sub>. If some p<sub>0</sub> satisfies r(p<sub>0</sub>) = r<sub>min</sub>, then r* ≤ r<sub>min</sub>, hence r* = r<sub>min</sub>. Then ε* = arctan(Δz/r<sub>min</sub>) = 80° and Q* = 1/r<sub>min</sub>. Every optimizer must satisfy r = r<sub>min</sub>, so the optimal set is the intersection of Ω with the circle, i.e., a union of arcs. ∎

The theorem also shows that r* is independent of the building layout; the environment changes only the position and length of the optimal arc. This is the origin of the principle "the optimal value is robust, the optimal location is sensitive."

### 4.2.3 Optimal Arc and Tie-Breaking

The distance from T′ to the east face x = 79 of B2 is only 5.6410 m, less than r<sub>min</sub>, so the r<sub>min</sub> circle intrudes westward into the 1.5 m buffer of B2. Substituting points on the circle into the two inequalities of the expanded rectangle [61.5,80.5]×[57.5,72.5] gives the blocked arc φ ∈ [160.75°,236.89°] (76.15°); the feasible arc crosses 0° continuously and has length 283.85° (78.85% of the circle). The derivation is in Appendix A.1. The distances from the other buildings to T′ exceed r<sub>min</sub>, and LOS on the feasible arc passes east of or above B2, so C3 does not shorten the feasible arc further (proof in A.1); 200,000-point arc sampling agrees with the analytics. In addition, the explicit feasible point p<sub>c</sub> = (84.641,77.582) has LOS with x ≡ 84.641 > 79 throughout, does not intersect any building, and satisfies C1; thus both steps—"lower bound" and "attainability"—are verified by explicit construction.

The optimal arc is made unique by a three-level lexicographic tie-break:

(R1) Maximum-safety-margin band: m(p) = min{min<sub>i</sub>[d(p,B<sub>i</sub>)−1.5], x−1.5, 98.5−x, y−1.5, 98.5−y}; keep the tie band m(p) ≥ m*−0.05 m, where m* = 9.6746 m is the maximum margin on the feasible arc, attained at φ = 56.5038°.

(R2) Shortest reachable within the band: choose the point with the shortest obstacle-avoiding travel time from the nearest standby vehicle.

(R3) Coordinate lexicographic order: if still tied, choose the smallest (x,y) in lexicographic order.

The result is p* = (88.8753,76.2895) m, φ = 56.05°, r* = 7.5821 m, ε* = 80°, Q* = 0.1319 m<sup>−1</sup>. The margin of p* itself is 9.6247 m, entering the tie band with a 0.0001 m surplus; the travel time to the nearest vehicle V4 is 2.78 s, and the minimum LOS clearance is 7.41 m. It should be emphasized that p* is "the fastest station within the near-maximum-margin band," not the maximum-margin point itself.

### 4.2.4 Results

A 0.1 m midpoint grid gives an observable area of 5610.4 m² (56.1% of the site); a 0.05 m recomputation gives 5608.5 m² (0.033% lower, converged). The 0.25 m benchmark 5614.9 m² and the node-count value 5628.7 m² are kept only for same-convention comparisons and reference. The grid minimum r = 7.5828 m at (92.2,69.4) lies 0.0007 m above the closed-form bound, as expected from quantization. C1, C2 and C3 remove 1685.7, 157.9 and 2547.7 m², leaving 5610.4 m² (sum 4391.3 m²; the 1.7 m² gap to 10 000−5610.4 is quantization). The LOS passes north of B2 with a minimum clearance of 7.41 m (A.1(b)). Figure 4-1 shows the region, Figure 4-2 the optimal arc, and Figure 4-3 the sensitivity to H, ε<sub>max</sub>, B2 height and vehicle radius.

[[FIG:论文图表/fig4-1_region.png|Figure 4-1 Observable region for T1 and building occlusion shadows (including the r<sub>min</sub> exclusion zone)]]

In Figure 4-1, the black circle is the r<sub>min</sub> = 7.5821 m exclusion zone; the blue shaded area outside the circle and not shadowed by buildings is Ω, with color depth corresponding to r from small to large. The dark-blue narrow band immediately northeast of T1′ is the candidate-station region with the largest Q = 1/r.

[[FIG:论文图表/fig4-2_arc_margin.png|Figure 4-2 Optimal arc and margin–azimuth curve ((a) feasible and blocked arcs; (b) m(p)−m*)]]

In Figure 4-2(a), green is the feasible arc on the r<sub>min</sub> circle, red is the arc [160.75°,236.89°] blocked by B2, and p* is on the northeast side at φ = 56.05°; in (b), the margin curve has two sharp peaks near m* at φ ≈ 56° and ≈310°, and tie-breaking selects the nearest reachable station within the left peak.

[[FIG:论文图表/fig4-3_sensitivity.png|Figure 4-3 Sensitivity of Problem 1 ((a) r*–H; (b) r*–ε<sub>max</sub>; (c) area–B2 height; (d) area–vehicle radius)]]

Figure 4-3(a)(b) shows that r* increases linearly with target height H and decreases nonlinearly as the pitch limit ε<sub>max</sub> rises; (c)(d) shows that the observable area shrinks first quickly and then slowly as B2 grows taller, and decreases almost linearly with the vehicle radius. Together, the four panels show that the pitch limit is the most sensitive geometric parameter for r*, and Table 4-1 collects the main results.

**Table 4-1 Main results of Problem 1**

| Item | Result |
|---|---|
| Target horizontal projection T′ | (84.6410,70.0000) m |
| Closed-form lower bound r* | 7.5821 m (43/tan 80°) |
| Optimal elevation ε* | 80.000° (active constraint) |
| Optimal quality Q* | 0.1319 m<sup>−1</sup> |
| Optimal station p* | (88.8753,76.2895) m, φ = 56.05° |
| Observable area | 5610.4 m² (about 56.1%) |
| Optimal arc | feasible 283.85°, blocked [160.75°,236.89°] |
| Grid verification | 7.5828 m @ (92.2,69.4), +0.0007 m |
| Minimum LOS clearance / nearest vehicle | 7.41 m / V4, 2.78 s |

### 4.2.5 Algorithm and Efficiency

This problem uses "closed-form lower bound + arc parameterization + three-level lexicographic rule" rather than 2-D continuous optimization over (x,y). The steps are: (i) solve C2 for r<sub>min</sub> = Δz/tan80°; (ii) sample 200,000 points uniformly on the r = r<sub>min</sub> circle (about 0.0018° spacing) and mark the feasible arc by 3-D slab intersection; (iii) make the choice unique on the feasible arc by "maximum-safety-margin band—shortest obstacle-avoiding path within the band—coordinate lexicographic order"; (iv) independently recompute the area and minimum r on a 0.1 m grid (about 10<sup>6</sup> points). The reason for this algorithm is that Q = 1/r is strictly monotone, so the optimal value must be attained on the active constraint C2 and the closed form provides a global optimality certificate. A 2-D grid search would only give the best grid value, without an optimality proof, at a cost of 10<sup>6</sup> points, whereas the closed-form part is O(1). The grid is used only for independent verification: arc sampling is O(2×10<sup>5</sup>), and the grid verification is one O(10<sup>6</sup>) pass. The closed-form 7.5821 m and the grid 7.5828 m differ by only 0.0007 m, confirming that the certificate and the numerical recomputation agree.

## 4.3 Problem 2: Two-Station Intersection and Multi-Target Scheduling

### 4.3.1 Two-Station Intersection Accuracy Model

Let the two stations be p<sub>i</sub>, with station–target distances d<sub>i</sub>, LOS azimuths α<sub>i</sub>, unit directions u<sub>i</sub> = (cos α<sub>i</sub>, sin α<sub>i</sub>), and unit normals n<sub>i</sub> = (−sin α<sub>i</sub>, cos α<sub>i</sub>). The azimuth errors δα<sub>i</sub> ~ N(0,σ²) are independent. The intersection-point error satisfies Eq. (7) (first-order propagation [3,4]), and its covariance is Eq. (8).

$$ A Δp = δ,  A = [n<sub>1</sub><sup>T</sup>; n<sub>2</sub><sup>T</sup>],  δ = (d<sub>1</sub>δα<sub>1</sub>, d<sub>2</sub>δα<sub>2</sub>)<sup>T</sup>, $$ (7)

$$ Σ = A<sup>−1</sup>DA<sup>−T</sup>,  D = diag(d<sub>1</sub>²σ², d<sub>2</sub>²σ²). $$ (8)

Hence traceΣ = σ²(d<sub>1</sub>²+d<sub>2</sub>²)/sin²γ and detΣ = σ⁴d<sub>1</sub>²d<sub>2</sub>²/sin²γ (full algebra in Appendix A.2).

Define G = √((d<sub>1</sub>²+d<sub>2</sub>²)/2)/|sin γ|, DRMS = σG = √(traceΣ/2); the 2-D radial RMSE is √2 DRMS, and the 95% circle radius is R95 = 2.4477DRMS (exact when isotropic).

### 4.3.2 Global Lower Bound and Vehicle/Station Selection

From |sin γ| ≤ 1, the QM–AM (quadratic-mean–arithmetic-mean) inequality, and d<sub>i</sub> ≥ r<sub>min</sub> from C2,

$$ G ≥ √((d<sub>1</sub>²+d<sub>2</sub>²)/2) ≥ (d<sub>1</sub>+d<sub>2</sub>)/2 ≥ r<sub>min</sub> = (35−2)/tan80° = 5.8188 m. $$ (9)

Equality requires γ = 90° and d<sub>1</sub> = d<sub>2</sub> = r<sub>min</sub>. For T2, the geometrically feasible arc on the r<sub>min</sub> circle is [59.66°,244.24°]; with a 0.5 m LOS/geometric margin, the robust feasible arc is [70.95°,238.63°], of length 167.68° > 90°, so a 90° pair exists. The 30 s limit is applied to each vehicle's ready time (travel plus slew). All ten pairs are listed in Table D-1: the four V2 pairs share the same candidate station, so they all give G = 8.9678 m, while the V2-side travel alone is 30.29 s (V1+V2) or 34.75 s (V2+V3, V2+V4, V2+V5), which already exceeds 30 s, so all four are infeasible (V1+V2 is the thinnest, 30.29 s, against a straight-line lower bound of 30.00 s). Paths are computed on the visibility graph with Dijkstra [5]. Within the same 0.5 m robust domain, V3+V5 is selected by "minimum total travel time—minimum maximum single-vehicle time—lexicographic order": p<sub>1</sub> = (5.2787,73.3912) m, p<sub>2</sub> = (11.9201,78.2501) m, d<sub>1</sub> = d<sub>2</sub> = 5.8188 m, γ = 90.000°, β = 8.2290 m, travel times 5.11/13.61 s (sum 18.72 s), DRMS = 0.1016 m, R95 = 0.2486 m (Table 4-2).

**Table 4-2 Two-station intersection accuracy and station-selection results**

| Item | Result |
|---|---|
| Selected vehicles | V3+V5 |
| Stations p<sub>1</sub> / p<sub>2</sub> | (5.2787,73.3912) / (11.9201,78.2501) m |
| Station–target distances d<sub>1</sub> = d<sub>2</sub> | 5.8188 m |
| Intersection angle γ / baseline β | 90.000° / 8.2290 m |
| Travel times | 5.11 / 13.61 s (sum 18.72 s) |
| DRMS / R95 | 0.1016 / 0.2486 m |
| MC radial RMSE / P95 | 0.1436 / 0.2486 m |
| Robust fallback (78°) | r ≥ 7.0144 m, DRMS = 0.1224 m (+20.5%) |

[[FIG:论文图表/fig4-4_t2_region_reach.png|Figure 4-4 Observable region of T2 and the 30 s reachable domains ((a) full domain; (b) zoom at the selected stations)]]

Figure 4-4(a) shows the observable region of T2 and the 30 s reachable domains of the five vehicles (dashed circles of radius 90 m). The target T2′ lies above B3, and the feasible stations are mainly on the west side of the building. The zoom in (b) shows the selected stations p<sub>1</sub> = (5.2787,73.3912) m and p<sub>2</sub> = (11.9201,78.2501) m; both are 5.8188 m from the target, the intersection angle is γ = 90.000°, and the baseline is 8.2290 m. The travel times are 5.11 s and 13.61 s, both within the 30 s limit.

[[FIG:论文图表/fig4-5_accuracy_params.png|Figure 4-5 Two-station accuracy versus parameters ((a) DRMS–γ; (b) DRMS–d; (c) DRMS–baseline)]]

Figure 4-5(a) shows that DRMS is U-shaped in the intersection angle γ, minimized at γ = 90° and diverging rapidly as γ→0°/180° (the shaded region is degenerate); the selected point (γ = 90°, d = 5.8 m) has DRMS = 0.1016 m. (b) shows that DRMS grows almost linearly with the station–target distance d, with the smallest slope at γ = 90°; when d increases from 5.8 m to 30 m, DRMS rises to about 0.75 m. (c) shows that, at a fixed intersection angle, DRMS increases linearly with the baseline β, with the steepest slope at γ = 60°.

[[FIG:论文图表/fig4-6_error_ellipses.png|Figure 4-6 Intersection error ellipses and 95% circle (with a local zoom)]]

The zoom in Figure 4-6 shows the geometry of the selected stations p<sub>1</sub>, p<sub>2</sub>, and T2′; the local inset gives the 1σ, 2σ, and 95% position-error circles at the target. Because the two stations are equidistant and orthogonal, the error distribution is nearly isotropic with R95 = 0.2486 m. The error-circle radii are much smaller than the station–target distances, indicating that the intersection geometry of this station pair is close to ideal.

Degeneracy analysis: as γ→0°/180°, G→∞ and the condition number is κ = 1/|sin γ|; at γ = 30°, G = 2G*, so [30°,150°] is used as the operating window, and a ridge-regularized least-squares estimator is used on the estimation side. The optimal station lies on the C2 boundary (ε = 80°); if a pitch margin is required, one may fall back to ε ≤ 78°, giving r ≥ 7.0144 m and DRMS = 0.1224 m (+20.5%).

### 4.3.3 Six-Slot, Five-Vehicle Scheduling Model

Let the alert set be A = {T1,T2,T3} (distinct from the coefficient matrix A of Section 4.3.1) and the vehicle set be V = {V1,…,V5}. Each alert a is assigned two distinct vehicles M<sub>a</sub>; the task sequence of vehicle v is π<sub>v</sub>, and the station of task k is p<sub>v,k</sub> ∈ Ω<sub>a</sub>. For task k, let D<sub>v,k−1</sub> be the previous task's departure time and pos<sub>v,k−1</sub> the previous position. Then

$$ τ<sub>tr</sub> = dist<sub>path</sub>(pos,p)/3,  τ<sub>sl</sub> = max(|α|,|ε|)/30, $$ (10)

$$ t<sup>rd</sup><sub>v,k</sub> = D<sub>v,k−1</sub> + τ<sub>tr</sub> + τ<sub>sl</sub>, $$ (11)

$$ S<sub>a</sub> = max(t<sup>rd</sup><sub>v,k</sub>, t<sup>rd</sup><sub>v′,k′</sub>)  (the later of the two vehicles' ready times), $$ (12)

$$ D<sub>v,k</sub> = S<sub>a</sub> + 5 + τ<sub>rs</sub>,  τ<sub>rs</sub> = max(|α|,|ε|)/30. $$ (13)

The objective is min max<sub>a</sub> S<sub>a</sub>, with the timeline propagated by Eqs. (10)–(13). Each alert has 10 vehicle pairs, so the three alerts give 10³ = 1000 assignment structures. For each structure, reuse orders are enumerated; stations are initialized greedily, refined by Gauss–Seidel coordinate descent and Nelder–Mead [6]; if two reused vehicles wait for each other and the fixed-point iteration makes no progress, the structure is declared deadlocked and removed.

Lower bound: LB(v,a) = min<sub>p</sub>[dist<sub>path</sub>(V<sub>v</sub><sup>0</sup>,p)/3 + max(|α|,|ε|)/30], S<sub>a</sub> ≥ the second-smallest LB(v,a), and the global LB = max<sub>a</sub> second-smallest = 3.414 s. This bound ignores reuse and synchronization, so it is loose.

### 4.3.4 Nearest-Assignment Baseline and Comparison

Note that the T2 pair of 2(1) is accuracy-optimal, whereas 2(2) re-optimizes the stations for timeliness; Section 4.3.6 verifies the accuracy that this costs.

In the order T1→T2→T3, fill two slots for each alert. For each slot, among vehicles not already serving this alert, choose the one with the smallest "travel time from the current chain end to its minimum-ready station for this alert" (ties: smaller vehicle number), and use that minimum-ready station; if the vehicle already has tasks, append to its chain. The same timeline simulation computes the start times. This baseline considers only "who is nearest" and ignores synchronized pairing, reuse-chain order, and slew angle.

Optimized plan: T1←(V3,V5), T2←(V1,V4), T3←(V2,V3), with the V3 reuse chain T1→T3; the start times are 1.607/6.994/10.355 s and the objective is 10.355 s. Baseline: T1←(V3,V5), T2←(V1,V3), T3←(V1,V5), with reuse chains for V1, V3, and V5; the start times are 1.607/11.140/20.968 s and the objective is 20.968 s. The latest start is reduced by 10.613 s (−50.6%).

The difference has three sources. (i) Synchronized-pairing loss: the baseline places T2 as the second task in V3's reuse chain, so V3 must first finish T1 and reset, forcing V1 on the other side of T2 to wait; the optimized plan instead pairs V1 with the dedicated V4. (ii) Reuse-chain order: the baseline's three two-task chains serialize slow tasks after fast alerts and block T3's early window; the optimized plan has only one T1→T3 chain. (iii) Azimuth-driven station selection: ready time is highly sensitive to the pan angle (30°/s), while the baseline selects stations by distance and ignores the turn angle; the optimization model minimizes ready time.

### 4.3.5 Results and Robust Deployment

The 10.355 s optimum has knife-edge station clearances of only 1.3×10<sup>−3</sup> m (V3 at T3) and 6.7×10<sup>−2</sup> m (V4 at T2); the full stations and timings are listed in Table D-2. Re-optimizing with 0.5 m clearance yields a robust variant of 10.837 s (+4.7%), with assignment T1←(V3,V5), T2←(V1,V3), T3←(V4,V5) and start times 1.54/10.804/10.837 s; the robust variant is recommended for deployment. The sensitivities to speed and angular rate are given in Section 6.2; the elasticity of ω is about four times that of v.

**Table 4-3 Scheduling plan versus the nearest-assignment baseline**

| Item | Optimized plan | Nearest-assignment baseline |
|---|---|---|
| T1 start | 1.607 s | 1.607 s |
| T2 start | 6.994 s | 11.140 s |
| T3 start | 10.355 s | 20.968 s |
| Objective max | 10.355 s | 20.968 s |
| Assignment | T1(V3,V5), T2(V1,V4), T3(V2,V3) | T1(V3,V5), T2(V1,V3), T3(V1,V5) |
| Reuse chains | V3: T1→T3 | V1: T2→T3; V3: T1→T2; V5: T1→T3 |

The baseline Gantt chart is structurally the same as the optimized plan and is omitted (its times are listed in Table 4-3).

[[FIG:论文图表/fig4-7_gantt_inset.png|Figure 4-7 Vehicle Gantt chart and deployment routes of the optimized plan ((a) Gantt chart; (b) routes and stations)]]

Figure 4-7(a) gives the complete task chain of the optimized plan on the time axis: T1, T2, and T3 begin synchronized two-vehicle observation at 1.607, 6.994, and 10.355 s, respectively; V3 completes T1 and, after reset and slew, continues to T3, forming the only reuse chain. The orange slew segments and gray synchronized-waiting segments explain the composition of each alert's start time. (b) shows the post-arrival deployment positions of the five vehicles and the three alert bearings: T1 is observed by V3 and V5 from the same northwest side (γ only 19.34°), T2 is bracketed by V1 and V4 from the south and east (γ = 85.08°), and T3 is bracketed by V2 and V3 from the southeast and northwest (γ = 127.39°), providing the geometric basis for the accuracy check in Section 4.3.6.

### 4.3.6 Accuracy Check of the Timeliness Plan

The stations of the 10.355 s plan are re-optimized independently for timeliness and must be substituted back into the accuracy model of 2(1) to check the intersection geometry. Using G and DRMS from Section 4.3.1, the three station pairs are evaluated in Table 4-4. T2 and T3 have γ = 85.08° and 127.39°, inside the [30°,150°] operating window; T1 has γ = 19.34° (κ = 3.02) and DRMS = 3.084 m, approaching degeneracy—the two lines of sight are nearly parallel on the same side of the target. If T1 must also satisfy γ ≥ 30°, fixing the assignment and order and reselecting T1's two stations gives (14.90,85.60)/(53.90,98.40), γ = 30.12°, G = 116.68 m, DRMS = 2.036 m; T1's start is delayed from 1.607 s to 3.746 s, and the maximum start over the three alerts rises from 10.355 s to 12.983 s (+2.629 s, +25.38%). This shows that timeliness and accuracy are not interchangeable: if deployment requires T1 to satisfy γ ≥ 30°, an intersection-angle constraint must be added to the scheduling model.

**Table 4-4 Intersection geometry and accuracy of the timeliness plan**

| Alert | Pair | γ (°) | G (m) | DRMS (m) |
|---|---|---|---|---|
| T1 | V3+V5 | 19.34 | 176.67 | 3.084 |
| T2 | V1+V4 | 85.08 | 67.93 | 1.186 |
| T3 | V2+V3 | 127.39 | 81.32 | 1.419 |
| T1* | V3+V5 | 30.12 | 116.68 | 2.036 |

Note: DRMS = σG, σ = 1° = 0.017453 rad; T1* is the constrained re-solution with γ<sub>T1</sub> ≥ 30° under the same assignment/order and does not constitute a global optimality claim. The error covariance of none of the four pairs is isotropic (the eigenvalue ratio for T1 is about 46:1); exact 95% coverage should use the ellipse semi-axes √(5.991λ<sub>i</sub>), which are (10.56,1.55)/(3.27,2.48)/(4.77,1.19)/(6.87,1.58) m for T1/T2/T3/T1*, respectively.

### 4.3.7 Algorithm and Efficiency

2(1) uses "covariance propagation + analytical lower-bound certificate + pair enumeration." First, G is derived from Σ = A<sup>−1</sup>DA<sup>−T</sup>; the QM–AM inequality and C2 then prove G ≥ r<sub>min</sub>, and the equality condition is reduced to a one-dimensional test: whether a feasible pair with a 90° intersection angle exists on the r<sub>min</sub> circle. Then candidate stations are enumerated and refined by Nelder–Mead for all C(5,2) = 10 vehicle pairs (4-D NM, ≤300 iterations per call). The analytical certificate reduces the global optimality check to a one-dimensional feasibility test, avoiding local optima while keeping the computation at the scale of 10 pairs; a direct 4-D search has neither an optimality proof nor protection against local optima.

2(2) uses "complete structural enumeration + fixed-point timeline simulation + coordinate descent/Nelder–Mead." The three alerts each have C(5,2) = 10 vehicle pairs, giving 10³ = 1000 assignment structures; each structure enumerates reuse-chain orders, for a total of 5,880 (structure, order) combinations, each simulated deterministically and checked for deadlock. Stations are initialized greedily, refined by Gauss–Seidel coordinate descent and Nelder–Mead, and the top 12 structures are re-refined. With only 5 vehicles and 6 slots, all 5,880 deterministic simulations complete in one run, exhaust the assignment structures, and guarantee reproducibility; a randomized search such as a genetic algorithm would neither guarantee the same solution nor explain why the plan is optimal. In terms of efficiency, 10.355 s is 50.6% lower than the nearest-assignment baseline of 20.968 s, at a cost of only a few thousand simulations, at most 2 tasks per vehicle, and at most 160 NM iterations per call.

## 4.4 Problem 3: Localization and Pointing Error Propagation

### 4.4.1 Error Propagation Model

Take the true position P as the origin and the true LOS as the x′ axis, with the target at (d,0), d = 40 m. Decompose the localization error into cross-range δ<sub>⊥</sub> and along-range δ<sub>∥</sub>; under isotropy, δ<sub>⊥</sub> ~ N(0,σ(s)²). The exact deviation from the estimated position to the target is Δα = atan2(−δ<sub>⊥</sub>, d−δ<sub>∥</sub>) ≈ −δ<sub>⊥</sub>/d (residual analysis in A.3). Adding the gimbal bias ε<sub>0</sub> ~ N(0,0.8²) and control error ε<sub>c</sub> ~ N(0,0.6²),

$$ Δψ = wrap180(Δα·180/π + ε<sub>0</sub> + ε<sub>c</sub>), $$ (14)

where wrap180(·) folds angles into (−180°,180°]. The three terms are independent zero-mean normals, and wrap180 is not triggered at this problem's scale, so

$$ Δψ ~ N(0,σ<sub>ψ</sub>²(s)),  σ<sub>ψ</sub>²(s) = (σ(s)/40·180/π)² + 0.8² + 0.6² = (1.432394σ(s))² + 1.0. $$ (15)

### 4.4.2 s<sub>max</sub> and (a,b) Constraints

From P(|Δψ| ≤ 5°) = 2Φ(5/σ<sub>ψ</sub>) − 1 ≥ 0.95, we obtain σ<sub>ψ</sub> ≤ 5/z<sub>0.975</sub> = 2.551067°. Substituting into the expression above,

$$ σ(s) ≤ √(2.551067²−1.0)/1.432394 = 1.638446 m, $$ (16)

$$ s<sub>max</sub> = (1.638446−0.3)/0.02 = 66.9223 m ≈ 66.92 m. $$ (17)

At s = 80 m, σ(80) = 1.9 m, σ<sub>ψ</sub> = 2.89945°, and P = 0.91538 < 0.95. If the criterion must still hold at 80 m, then a + 80b ≤ 1.638446 m, which together with a,b ≥ 0 forms a triangular feasible region (b = 0 gives a ≤ 1.6384 m; a = 0 gives b ≤ 0.0204806 m/m). The nominal point (0.3,0.02) lies outside; one must reduce b to 0.0167306 m/m (−16.3%) or reduce a to 0.0384 m.

### 4.4.3 Contribution Decomposition and Exact Verification

Let var<sub>loc</sub> = (1.432394σ(s))², var<sub>bias</sub> = 0.64, and var<sub>ctrl</sub> = 0.36. At s = 0 the three shares are 15.6%/54.0%/30.4%; at s = 40 they are 71.3%/18.4%/10.3%; at s = 80 they are 88.1%/7.6%/4.3%; the bias:control ratio is always 64:36. The dominant-factor switch point is obtained from var<sub>loc</sub> = var<sub>bias</sub> + var<sub>ctrl</sub> as s = 19.907 m (shares 50.0%/32.0%/18.0%), after which localization becomes the first source. The linearization residual RMS is σ(s)²/d², which at s = 80 m is 0.1293°, only 4.46% of σ<sub>ψ</sub> and about 0.2% of the variance. A 256×256 Hermite quadrature gives the reference value s<sub>max</sub> = 66.84 m, P(66.92) = 0.94980, and a + 80b ≤ 1.6367 m; the recommended practice is to use 66.84 m as the conservative design value and 66.92 m as the closed-form primary answer. The P deviation of 10<sup>6</sup> Monte Carlo runs [7] is ≤ 3×10<sup>−4</sup>, validating the linearization and the normal composition.

**Deployment implications.** (i) The travel budget should be capped near the conservative 66.84 m rather than 66.92 m, because the closed form slightly understates the risk at the boundary. (ii) If the sensing budget is limited, reducing the slope b of the localization error is far more effective than reducing the offset a: at 80 m one unit of b saves 80 units of σ, whereas a enters one-to-one. (iii) Improving the gimbal (bias plus control, 1.0° combined) helps mainly at short travel; beyond about 100 m the localization term dominates and gimbal upgrades saturate (Section 6.2).

**Table 4-5 Monte Carlo verification for Problem 3 (10<sup>6</sup> samples)**

| s (m) | σ(s) (m) | P empirical | P analytical | σ empirical (°) | σ analytical (°) |
|---|---|---|---|---|---|
| 0 | 0.30 | 0.999996 | 0.999996 | 1.0875 | 1.0884 |
| 20 | 0.70 | 0.999584 | 0.999586 | 1.4163 | 1.4161 |
| 40 | 1.10 | 0.992694 | 0.992622 | 1.8651 | 1.8662 |
| 66.92 | 1.6384 | 0.949730 | 0.950000 | 2.5528 | 2.5511 |
| 80 | 1.90 | 0.915229 | 0.915376 | 2.9006 | 2.8995 |

[[FIG:论文图表/fig4-8_variance.png|Figure 4-8 Variance components and shares of σ<sub>ψ</sub> ((a) component curves; (b) stacked shares)]]

In Figure 4-8(a), the localization term rises linearly with s, and its intersection with the allowable line 2.551° is s<sub>max</sub> = 66.92 m; (b) shows that after s ≈ 19.9 m the localization share exceeds the sum of the gimbal bias and control shares, reaching 88.1% at s = 80 m.

[[FIG:论文图表/fig4-9_probability_ab.png|Figure 4-9 P(|Δψ| ≤ 5°) curve and the (a,b) feasible region ((a) P–s; (b) (a,b) region)]]

Figure 4-9(a) gives the decreasing curve of P(|Δψ| ≤ 5°) versus s; its intersection with the 0.95 line is s<sub>max</sub> = 66.92 m (exact 66.84 m), and the Monte Carlo points coincide with the analytical curve. In (b), the shaded area is the (a,b) feasible region where P ≥ 0.95 at 80 m; the nominal point (0.3,0.02) lies outside.

### 4.4.4 Algorithm and Efficiency

This problem uses "closed-form first-order propagation + monotone criterion + exact quadrature verification." The steps are: (i) linearize the lateral projection to obtain Δψ ~ N(0,(1.432394σ(s))²+1.0); (ii) from the two-sided criterion P(|Δψ| ≤ 5°) ≥ 0.95, obtain σ<sub>ψ</sub> ≤ 2.5511° and invert for σ(s) and s<sub>max</sub>; (iii) evaluate the exact atan2 geometry by a 256×256 Gauss–Hermite quadrature over the two-dimensional expectation and find s<sub>max</sub> by bisection; (iv) independently verify with 10<sup>6</sup> Monte Carlo runs. The closed form is chosen because σ<sub>ψ</sub>(s) is monotone in s, so the criterion can be inverted directly and gives the primary answer in O(1); Hermite quadrature is chosen because 65,536 nodes already reach 10<sup>−3</sup> accuracy, at about 1/15 of the cost of 10<sup>6</sup> MC runs and without sampling error. The results are 66.92 m in closed form and 66.84 m exact (0.13% difference), with an MC P deviation no larger than 3×10<sup>−4</sup>.

## 4.5 Problem 4: Rescheduling under Disturbances

### 4.5.1 State Snapshot and Locking Rules

At t<sub>p</sub> (5 s without an outage, t<sub>rec</sub> with an outage), record (t<sub>avail</sub>,pos,att,locked<sub>until</sub>) for each vehicle. Traveling: position is interpolated linearly, attitude is east, and the vehicle can be redispatched immediately. Slewing: the vehicle is at its station, attitude is interpolated, and it can be redispatched. Synchronized waiting: the vehicle is at its station, attitude points at the target, and it can be redispatched. Observing/resetting: the alert is locked and counted as served—it is not rescheduled even though its 5 s observation may still be in progress—and the vehicle remains locked until its reset finishes.

Rules: alerts that started before t<sub>p</sub> cannot be rescheduled; dispatched-but-unobserved vehicles can be redispatched; a failed vehicle is removed and its pending alerts become orphans; no new commands are received during an outage, and rescheduling is triggered after t<sub>rec</sub>. **"Continue-slew" applies only to the first task of an unobserved redispatch**: only if the vehicle has not started observing and the new station coincides with its current position (distance ≤ 5 cm), the first post-snapshot task continues from the current attitude, with slew = max(|wrap180(α<sub>new</sub>−α<sub>cur</sub>)|,|ε<sub>new</sub>−ε<sub>cur</sub>|)/30; after that task resets, all subsequent tasks perform a full-angle slew from east. Other redispatches (new station more than 5 cm from the current position) follow A3/A6: return to east during travel and perform a full slew after arrival. For example, in the (θ = 0°, ρ = 30 m) scenario (internal id `th0_R30`), V1's redispatch chain is T2→T3: T2 has a 0 s continue-slew; after T2 observation and reset, T3 slews from east for 1.655 s, so T3 starts at 16.772 s. Continue-slew is the continuation of the same pointing phase, not a new "arrival–pointing" process.

### 4.5.2 Rescheduling Model and Benchmark Strategy

The pending alert set A<sub>p</sub> is the union of alerts whose baseline start is ≥ t<sub>p</sub>, orphan alerts, and the new alert T4; the available vehicle set V<sub>p</sub> contains all non-failed vehicles. The decisions are M<sub>a</sub>, π<sub>v</sub>, and p<sub>v,k</sub>; the objective is lexicographic: maximize k, then minimize t<sub>last</sub>; the constraints are two distinct available vehicles per pending alert, stations in the corresponding Ω<sub>a</sub>, timeline propagation from the snapshot state, and exclusion of locked alerts and vehicles. The solution reuses the structural enumeration, coordinate descent, Nelder–Mead, and deadlock detection of Problem 2(2), changing only the initial conditions.

Keep-original: no new commands are issued. If a failed vehicle belongs to the pair of a pending alert, that alert never starts, so k decreases by 1 and t<sub>last</sub> = 60; the new alert has no assignment, so N increases by 1 while k is unchanged; with an outage only, the two strategies are equivalent.

### 4.5.3 Scenario Set and Results

The scenario set has 74 scenarios: A, new alert, 8 azimuths × 3 distances = 24; B, single vehicle failure, 5; C, single outage, 3; D, failure × outage, 15; E, new alert × failure, 6; F, new alert × outage, 9; G, triple combination, 12. New alerts use 8 azimuths at 45° and ρ ∈ {30,40,50} m, covering the shadow directions of all buildings and both ends of the distance range; a subsequent 22.5° refinement moves t<sub>last</sub> smoothly within 14.57–16.45 s, which confirms that 45° sampling suffices. The failure class runs all 5 vehicles; the combination class uses V2 and V4 as representatives, because V1 and V4 are the two members of T2's pair and V2, V3 are the two members of T3's pair, so a failure within a pair leaves an isomorphic orphan structure (V3's only other task, T1, is locked at t<sub>p</sub>), while V5's only task T1 is already locked and loses nothing. Failure × outage covers all three t<sub>rec</sub>, while the triple class uses only t<sub>rec</sub> = 10/30 s: t<sub>last</sub> responds in two stages (chain-limited, then unit slope), the middle value 20 s is already covered by D, and the secant slope (≈0.6) makes the missing points predictable. The set covers azimuth, distance, failure role, outage length and combination, and its representativeness is supported by the 22.5° refinement and the 0.5 m margin/tolerance/robust-baseline checks.

Results: rescheduling strictly improves η in 67 of 74 scenarios, ties in 7, and degrades none (reported at 0.01 s precision); Table 4-6 summarizes the outcome by scenario class and Table 4-7 lists three representative scenarios. Representative values: V4 failure, keep (0.667,60)→resched (1.000,11.17); new alert θ = 0°, ρ = 30 m, keep (0.750,60)→(1.000,16.77); triple combination (median new alert + V4 failure + t<sub>rec</sub> = 10 s), keep (0.500,60)→(1.000,25.01). By failed vehicle, the rescheduled t<sub>last</sub> for V1/V4, V2/V3, and V5 is 11.17, 10.90, and 10.35 s, respectively, all with η = 1. For a V1 failure, failure × outage with t<sub>rec</sub> = 10/20/30 gives t<sub>last</sub> = 21.01/25.08/35.08 s (increments 4.07/10.00 s), showing the two-stage behavior. The mechanism is "structural loss → temporal loss"; its upper limit is jointly constrained by the azimuth of idle vehicles, the slew + travel recovery delay, and the outage duration.

**Table 4-6 Summary by scenario class**

| Scenario class | Scenarios | η improved | Tied |
|---|---|---|---|
| A New alert | 24 | 24 | 0 |
| B Single vehicle failure | 5 | 4 | 1 |
| C Single outage | 3 | 0 | 3 |
| D Failure × outage | 15 | 12 | 3 |
| E New alert × failure | 6 | 6 | 0 |
| F New alert × outage | 9 | 9 | 0 |
| G Triple combination | 12 | 12 | 0 |
| Total | 74 | 67 | 7 |

Note: G uses 3 representatives × 2 failed vehicles × 2 recovery times (t<sub>rec</sub> = 10/30 s only); the intermediate value t<sub>rec</sub> = 20 s is covered by D.

**Table 4-7 Comparison of representative scenarios**

| Scenario | Keep original (η,t<sub>last</sub>) | Reschedule (η,t<sub>last</sub>) |
|---|---|---|
| V4 failure | (0.667,60) | (1.000,11.17) |
| New alert θ = 0°, ρ = 30 m | (0.750,60) | (1.000,16.77) |
| Triple (median + V4 + t<sub>rec</sub> = 10 s) | (0.500,60) | (1.000,25.01) |

[[FIG:论文图表/fig4-10_tlast_response.png|Figure 4-10 Two-stage response of t<sub>last</sub> to t<sub>rec</sub> ((a) t<sub>last</sub>–θ; (b) t<sub>last</sub>–t<sub>rec</sub>)]]

Figure 4-10(a) shows that the new alert's azimuth has little effect on t<sub>last</sub> (about 14.6–16.5 s), far below the 60 s of keeping the original plan; (b) shows that t<sub>last</sub> rises piecewise with the recovery time t<sub>rec</sub>, that V5 stays at 10.36 s because T1 is already under way and locked, and that the other failed vehicles exhibit the "chain-limited—unit-slope" two-stage behavior.

[[FIG:论文图表/fig4-11_resched_compare.png|Figure 4-11 Rescheduling Gantt chart and 74-scenario comparison ((a) V4 failure Gantt chart; (b) keep/resched scatter)]]

Figure 4-11(a) shows that after V4 fails at t = 5 s, rescheduling still starts T2 and T3 at about 7 s and 10 s and keeps η = 1.00; in (b), among the 74 scenarios, all green hollow points lie at η = 1.00, the red crosses are distributed between 0.50 and 1.00, and the arrows show that rescheduling trades a larger t<sub>last</sub> for a restored completion rate.

### 4.5.4 Algorithm and Efficiency

This problem uses "event-triggered snapshot + reuse of the 2(2) solver + deterministic scenario enumeration." The steps are: (i) at t<sub>p</sub>, record (t<sub>avail</sub>,pos,att,locked<sub>until</sub>) for each vehicle and classify states as redispatchable or locked; (ii) using the snapshot as the initial condition, re-optimize the pending alerts with the structural enumeration, fixed-point simulation, coordinate descent, and Nelder–Mead of 2(2); (iii) compute (η,t<sub>last</sub>) for keep-original and reschedule in each of the 74 representative scenarios. This approach is chosen because the post-disturbance scale is the same order as 2(2) and reusing the same solver keeps the conventions consistent; with only 74 scenarios, deterministic enumeration completes in one run without online stochastic optimization. Keep-original is evaluated analytically and serves as a comparison with per-scenario simulation. The result is a strict η improvement in 67/74 scenarios, 7 ties, and 0 degradations.

# 5. Model Validation and Result Analysis

Table 5-1 summarizes the validation evidence for the four problems.

**Table 5-1 Summary of validation for the four problems**

| Object | Method | Deviation | Details |
|---|---|---|---|
| Q1 global optimum | Closed-form r* vs. 0.1 m grid | 7.5821 vs. 7.5828 m (+0.0007 m, 0.009%) | 4.2.4 |
| Q2 accuracy and scheduling | Covariance vs. 200,000 MC; structural enumeration + top-5 + 0.5 m variant | RMSE 0.1436 m = √2DRMS; P95 0.2486 m; optimum 10.355 s, robust 10.837 s | 4.3.2/4.3.5 |
| Q3 error propagation | Linearization vs. 256×256 Hermite; 10<sup>6</sup> MC | s<sub>max</sub> 66.92 vs. 66.84 m (0.13%); P deviation ≤ 3×10<sup>−4</sup> | 4.4.3 |
| Q4 rescheduling | 74-scenario accounting audit; 0.5 m margin/tolerance/22.5° densification | 0 anomalies; η/t<sub>last</sub> conclusions unchanged | 4.5.3 |

## 5.1 Validation of Problem 1

The closed-form lower bound r* = 7.5821 m differs from the 0.1 m grid minimum 7.5828 m by only 0.0007 m (0.009%); the observable area is stable at 5610.4 and 5608.5 m² for the 0.1 m and 0.05 m midpoint grids (0.03% apart).

## 5.2 Validation of Problem 2

The covariance model gives DRMS = 0.1016 m; 200,000 MC runs give a radial RMSE of 0.1436 m = √2DRMS and P95 = 0.2486 m. The robust variant (10.837 s, +4.7%) is consistent with the unconstrained optimum (10.355 s).

## 5.3 Validation of Problem 3

The P deviation of 10<sup>6</sup> MC runs is ≤ 3×10<sup>−4</sup>, and the linearization residual is 0.1293° (about 0.2% of the variance); the exact Hermite s<sub>max</sub> = 66.84 m differs from the closed form 66.92 m by 0.13%.

## 5.4 Validation of Problem 4

The 74-scenario accounting audit finds no anomalies; the 0.5 m margin, the 5 cm coincidence threshold and its 2/5/10 cm variants, replacement with the 10.837 s robust baseline, and the 22.5° densification all leave the η/t<sub>last</sub> conclusions unchanged.

# 6. Sensitivity Analysis

## 6.1 Parameter Selection and Perturbation Design

Parameters are chosen for their relevance, order of magnitude, influence on the model, and interpretability: geometric parameters H, ε<sub>max</sub>, R<sub>veh</sub>, and B2 height; accuracy parameters σ<sub>α</sub>, d, and γ; timeliness parameters v, ω, and the 30 s limit; disturbance parameters t<sub>rec</sub>, failed vehicle, new-alert θ/ρ, and safety margin. Continuous parameters use one-factor perturbations, v×ω uses a 3×3 full factorial, discrete disturbances use the 74-scenario enumeration, and all other parameters stay at nominal values.

## 6.2 Main Results

Table 6-1 gives the objective under the v×ω full factorial.

**Table 6-1 Objective time under the v×ω full factorial (unit: s)**

| v \ ω | 24°/s | 30°/s | 36°/s |
|---|---|---|---|
| 2.5 m/s | 11.655 | 10.611 | 9.932 |
| 3.0 m/s | 11.499 | 10.355 | 9.676 |
| 3.5 m/s | 11.387 | 10.243 | 9.493 |

**Problem 1 elasticities.** The closed-form partial derivatives of r* are ∂r*/∂H = 0.1763 m/m, ∂r*/∂ε<sub>max</sub> = −0.7738 m/deg, and ∂r*/∂h<sub>cam</sub> = −0.1763 m/m; at the nominal point (H,ε<sub>max</sub>) = (45 m,80°), the elasticities are E<sub>H</sub> = 1.05 and E<sub>εmax</sub> = (−0.7738×80)/7.5821 ≈ −8.16. As H increases from 30 to 60 m, r* increases linearly from 4.94 to 10.23 m; as ε<sub>max</sub> increases from 70° to 85°, r* decreases nonlinearly from 15.65 to 3.76 m. Replacing Q with Q<sub>2</sub> = (1/r)cos²(ε−45°) leaves the optimal set unchanged: on the r<sub>min</sub> circle Q<sub>2</sub> is constant at 0.0885 m<sup>−1</sup>, so every point of the feasible arc is again optimal and the choice is still fixed by the tie-break rules (the 0.1 m mesh reports (92.2,69.4), r = 7.5828 m). The criterion therefore preserves the optimal set without adding discrimination.

**Problem 2 elasticities.** The elasticity of ω is about −0.44 and that of v about −0.11, so the former is about four times the latter; a 0.5 m margin raises the objective from 10.355 to 10.837 s (+4.7%) and increases the clearance from 1.3 mm/6.7 cm to more than 0.5 m. The sensitivity of G* to H has the same origin as in Problem 1 (0.1763 m/m); σ<sub>α</sub> and DRMS are strictly linear, and G doubles at γ = 30°.

**Slope in d for Problem 3.** d = 30/35/40/45/50/60 m corresponds to s<sub>max</sub> = 46.44/56.68/66.92/77.16/87.40/107.88 m, with a slope of 2.0481 m/m; confidence levels 0.90/0.95/0.98/0.99 correspond to 85.20/66.92/51.41/43.07 m; gimbal-error scalings 0.5/0.75/1.0/1.25/1.5 correspond to 72.32/70.11/66.92/62.63/57.03 m. d is the strongest continuous lever, the confidence level acts nonlinearly, and gimbal improvements saturate over long travels.

## 6.3 Stability Conclusions

Within reasonable perturbation ranges, no qualitative conclusion changes sign: the optimum lies on the boundary, G* = r<sub>min</sub>, localization dominates over long travel, and rescheduling converts structural loss into temporal loss all remain valid. The model is insensitive to numerical/engineering parameters such as the grid step, 0.5 m margin, zero-displacement tolerance, and 45° azimuth sampling; the two-stage response of t<sub>last</sub> to t<sub>rec</sub> in Problem 4 is shown in Section 4.5.3. Remodeling is needed only under extreme conditions (the r<sub>min</sub> circle is completely occluded, t<sub>rec</sub> approaches 30 s with triple disturbances, or errors are strongly correlated).

# 7. Strengths and Weaknesses

## 7.1 Strengths

(1) **Analytical certificates instead of numerical search.** Problem 1 derives r* = 7.5821 m from C2 and proves attainability on the feasible arc; Problem 2(1) proves G* = r<sub>min</sub> with the QM–AM inequality and C2; Problem 3 solves s<sub>max</sub> in closed form from the monotonicity of σ<sub>ψ</sub>(s) and verifies it by exact quadrature. All three give a complete "lower bound + attainability/equality" proof rather than a best grid value.

(2) **Integrated geometry—accuracy—timing—disturbance modeling with cross-validation.** The four problems share the same site geometry, observable region, and observation timing: Ω is used for station selection, the 2(2) timeline becomes the Problem 4 baseline, and the Problem 4 snapshot reuses the same slew/reset rules. Closed form—grid—sampling, covariance—MC—path simulation, linearization—Hermite—10<sup>6</sup> MC, and analytical benchmark—74 scenarios—robust re-solution all have residuals at the discretization/linearization level.

(3) **Robustness and deployability built in.** Problem 2(2) discloses the 1.3 mm/6.7 cm knife-edge clearance and gives a 10.837 s robust variant; Problem 1 gives a 78° fallback design with a 20.5% cost; Problem 3 gives the conservative 66.84 m value; Problem 4 uses 74 scenarios and 22.5° densification for validation. All reported numbers are generated from a single JSON data source by the accompanying scripts, so the results can be reproduced.

## 7.2 Weaknesses

(1) **The global optimality of Problem 2(2) is not certified.** The assignment structures are exhaustively enumerated at the 10³ level, but station optimization relies on coordinate descent and Nelder–Mead; 10.355 s is the best solution in the sense of "structural exhaustion + station refinement," and the lower bound 3.414 s is loose because it ignores reuse delays.

(2) **The independent normal error assumption is strong.** Problem 2 assumes independent N(0,(1°)²) azimuth errors at the two stations, and Problem 3 assumes three independent zero-mean normal sources; MC validates the nominal parameters but does not cover correlated, nonzero-mean, or heavy-tailed cases.

(3) **The scenario set is a discrete representative set, and the kinematics are simplified.** The 74 scenarios cover 8 azimuths, 3 distances, 5 failure types, and 3 recovery times, but not continuous arrivals, secondary disturbances, or adversarial choices; vehicles travel at constant speed with no acceleration/turning/collision avoidance, the gimbal rotates ideally, and the vehicle–target distance in Problem 3 is fixed at 40 m. These simplifications are consistent with the problem statement but would change the timeline and error propagation of a more realistic system. The lock rule of Section 4.5.1 is also optimistic: an observation that has started is counted as served even if the vehicle fails during it, so the reported rescheduling gain for mid-observation failures is an upper bound.

## 7.3 Model Extensions

(1) **Multi-station/multi-target.** The two-station covariance Σ = A<sup>−1</sup>DA<sup>−T</sup> can be extended to multi-station intersection by stacking the rows of A; for multiple targets, each target has its own Σ and shares the same vehicle and timeline constraints.

(2) **Arbitrary monotone Q(r).** The "closed-form lower bound + attainability" certificate of Problem 1 depends only on the monotonicity of Q in r; the Q<sub>2</sub> comparison in Section 6.2 shows that switching to another monotone criterion in the same family leaves the optimal set unchanged, so the certificate transfers to other monotone quality measures.

(3) **Continuous arrivals/secondary disturbances.** The event-triggered snapshot and re-optimization framework can directly accept continuously arriving new alerts and secondary disturbances; it suffices to refresh A<sub>p</sub>/V<sub>p</sub> at the trigger time and reuse the same solver.

# 8. Conclusion

First, the single-target observable region is determined by the intersection of the vehicle geometry, gimbal pitch, and LOS occlusion constraints; the optimal distance is fixed by the closed-form bound r* = 7.5821 m (Q* = 0.1319 m<sup>−1</sup>), and the optimal set is a continuous arc that must be made unique by tie-breaking.

Second, two-station accuracy is characterized by the geometric dilution of precision G, whose lower bound is attained at d<sub>1</sub> = d<sub>2</sub> = r<sub>min</sub> and γ = 90°; under the 30 s limit, V3+V5 is selected, and the maximum scheduling start is 10.355 s, 50.6% lower than the nearest-assignment baseline of 20.968 s; timeliness and accuracy are not interchangeable.

Third, the pointing deviation is composed of localization, bias, and control sources; the maximum travel distance satisfying P(|Δψ| ≤ 5°) ≥ 0.95 is 66.92 m (with the exact-geometry conservative value 66.84 m), and localization dominates over long travel.

Fourth, event-triggered rescheduling improves the completion rate in 67 of 74 scenarios, ties in 7, and degrades none; its value lies in converting structural loss into temporal loss.

Overall, geometry determines feasibility, accuracy determines station placement, scheduling determines timeliness, and rescheduling preserves the completion rate.

# References

[1] 2026 12th ShuWei Cup National College Mathematical Modeling Challenge (Autumn), Problem B: Rapid UAV Localization via Coordinated Mobile Vehicles.

[2] Preparata F P, Shamos M I. Computational Geometry: An Introduction. New York: Springer, 1985.

[3] Torrieri D J. Statistical theory of passive location systems. IEEE Transactions on Aerospace and Electronic Systems, 1984, AES-20(2): 183–198.

[4] Foy W H. Position-location solutions by Taylor-series estimation. IEEE Transactions on Aerospace and Electronic Systems, 1976, AES-12(2): 187–194.

[5] Dijkstra E W. A note on two problems in connexion with graphs. Numerische Mathematik, 1959, 1: 269–271.

[6] Nelder J A, Mead R. A simplex method for function minimization. The Computer Journal, 1965, 7(4): 308–313.

[7] Hammersley J M, Handscomb D C. Monte Carlo Methods. London: Methuen, 1964.

# Appendix

## Appendix A: Proofs and Supplementary Derivations

### A.1 Problem 1: Intersection of the Optimal Arc and the Proof That C3 Adds No Occlusion

**(a) Derivation of the blocked arc.** Let T′ = (84.6410,70.0000) and r<sub>min</sub> = 7.5821 m. The 1.5 m expanded rectangle of B2 is [61.5,80.5]×[57.5,72.5]; a point on the circle, (84.6410+7.5821cos φ, 70+7.5821sin φ), falls inside this rectangle if and only if

$$ cos φ ≤ (80.5−84.6410)/7.5821 = −0.54616  and  sin φ ≤ (72.5−70)/7.5821 = 0.32972. $$

The first inequality gives φ ∈ [123.11°,236.89°], and the second gives φ ∈ [0°,19.25°]∪[160.75°,360°] (x ≥ 61.5 and y ≥ 57.5 hold automatically on the circle because x ≥ 77.06 and y ≥ 62.42 there). Their intersection is φ ∈ [160.75°,236.89°], i.e., a blocked arc of 76.15°. Hence C1 leaves the continuous arc [236.89°,360°)∪(0°,160.75°] on the circle, of total length 283.85°.

**(b) C3 adds no occlusion on the feasible arc.** Basis: the segment pT′ is contained in the disk centered at T′ with radius r<sub>min</sub> (convexity of the disk); the distances from the other buildings to T′ are 67.09, 60.64, 36.00, and 41.32 m, all greater than r<sub>min</sub>+1.5 = 9.0821 m (see Section 4.2.3), so only B2 needs to be excluded. For p on the feasible arc, consider two cases.

(i) x(p) ≥ 79: the x-coordinate of the horizontal projection of the LOS lies between x(p) and 84.6410, hence is always ≥ 79 and outside the east face of B2.

(ii) x(p) < 79: by the C1 test in (a), p must satisfy y(p) > 72.5. Let p = (x<sub>0</sub>,y<sub>0</sub>), t = y<sub>0</sub>−70 ∈ (2.5,7.5821], and x<sub>0</sub> = 84.6410−√(r<sub>min</sub>²−t²). The ordinate of the intersection of pT′ with the line x = 79 reduces to

$$ y(79) = 70 + 5.6410·t/√(r<sub>min</sub>²−t²). $$

This expression is strictly increasing on t ∈ (2.5,7.5821], so y(79) ≥ y(79)|<sub>t=2.5</sub> = 71.97 > 71; that is, the LOS passes north of the north face of B2 (y = 71) and does not enter the B2 footprint. Therefore C3 produces no additional occlusion on the feasible arc.

### A.2 Problem 2(1): Algebraic Expansion of Σ = A<sup>−1</sup>DA<sup>−T</sup>

Let the LOS azimuths of stations p<sub>1</sub> and p<sub>2</sub> be α<sub>i</sub>, with unit directions u<sub>i</sub> = (cos α<sub>i</sub>,sin α<sub>i</sub>) and unit normals n<sub>i</sub> = (−sin α<sub>i</sub>,cos α<sub>i</sub>) (n<sub>i</sub><sup>T</sup>u<sub>i</sub> = 0). A first-order azimuth error δα<sub>i</sub> makes the signed distance from the true target to the perturbed bearing line approximately d<sub>i</sub>δα<sub>i</sub>, so

$$ n<sub>i</sub><sup>T</sup>Δp = d<sub>i</sub>δα<sub>i</sub>,  i = 1,2, $$

which in matrix form is AΔp = δ with

$$ A = [n<sub>1</sub><sup>T</sup>;n<sub>2</sub><sup>T</sup>] = [[n<sub>1x</sub>,n<sub>1y</sub>],[n<sub>2x</sub>,n<sub>2y</sub>]],  δ = (d<sub>1</sub>δα<sub>1</sub>,d<sub>2</sub>δα<sub>2</sub>)<sup>T</sup>. $$

Since δα<sub>1</sub> and δα<sub>2</sub> are independent and identically distributed N(0,σ²), E[δδ<sup>T</sup>] = D = diag(d<sub>1</sub>²σ²,d<sub>2</sub>²σ²), and

$$ Σ = E[ΔpΔp<sup>T</sup>] = A<sup>−1</sup>E[δδ<sup>T</sup>]A<sup>−T</sup> = A<sup>−1</sup>DA<sup>−T</sup>. $$

**(a) Inverse and columns.** det A = n<sub>1x</sub>n<sub>2y</sub>−n<sub>1y</sub>n<sub>2x</sub> = n<sub>1</sub>×n<sub>2</sub> = sin γ (γ is the angle between the two LOS; the signed area is ±sin γ, and its absolute value enters the variance). The 2×2 adjugate is adj A = [[n<sub>2y</sub>,−n<sub>1y</sub>],[−n<sub>2x</sub>,n<sub>1x</sub>]], so

$$ A<sup>−1</sup> = (1/det A)[[n<sub>2y</sub>,−n<sub>1y</sub>],[−n<sub>2x</sub>,n<sub>1x</sub>]]. $$

Its two columns are

$$ col<sub>1</sub>(A<sup>−1</sup>) = (1/det A)(n<sub>2y</sub>,−n<sub>2x</sub>)<sup>T</sup> = (1/det A)u<sub>2</sub>, $$

$$ col<sub>2</sub>(A<sup>−1</sup>) = (1/det A)(−n<sub>1y</sub>,n<sub>1x</sub>)<sup>T</sup> = −(1/det A)u<sub>1</sub>, $$

using the 90° rotation relation between u<sub>i</sub> = (cos α<sub>i</sub>,sin α<sub>i</sub>) and n<sub>i</sub> = (−sin α<sub>i</sub>,cos α<sub>i</sub>).

**(b) Outer-product expansion.**

$$ Σ = A<sup>−1</sup>DA<sup>−T</sup> = Σ<sub>i=1</sub><sup>2</sup> D<sub>ii</sub> col<sub>i</sub>(A<sup>−1</sup>) col<sub>i</sub>(A<sup>−1</sup>)<sup>T</sup> = (σ²/det²A)[d<sub>1</sub>²u<sub>2</sub>u<sub>2</sub><sup>T</sup> + d<sub>2</sub>²u<sub>1</sub>u<sub>1</sub><sup>T</sup>]. $$

No cross term appears because D is diagonal; if u<sub>i</sub> were mistakenly written as the normal n<sub>i</sub>, the expression would be rotated by 90° (trace and det unchanged, but the matrix itself different). The main text consistently uses the LOS direction u<sub>i</sub>.

**(c) Trace and determinant.**

$$ traceΣ = (σ²/det²A)[d<sub>1</sub>²‖u<sub>2</sub>‖² + d<sub>2</sub>²‖u<sub>1</sub>‖²] = σ²(d<sub>1</sub>²+d<sub>2</sub>²)/sin²γ, $$

$$ detΣ = det(D)/det²A = σ⁴d<sub>1</sub>²d<sub>2</sub>²/sin²γ. $$

These correspond respectively to

$$ DRMS² = traceΣ/2 = σ²(d<sub>1</sub>²+d<sub>2</sub>²)/(2sin²γ) ⇒ DRMS = σ√((d<sub>1</sub>²+d<sub>2</sub>²)/2)/|sin γ| = σG. $$

**(d) 1σ ellipse and 95% radius.** From detΣ, the area of the 1σ error ellipse is

$$ S<sub>1σ</sub> = π√(detΣ) = πσ²d<sub>1</sub>d<sub>2</sub>/|sin γ|. $$

When d<sub>1</sub> = d<sub>2</sub> = d, S<sub>1σ</sub> = πσ²dG, so the two are of the same order; in general, both G and S<sub>1σ</sub> vary monotonically and inversely with |sin γ|, so G is a monotone representative of "area-type" accuracy indices. The 95% confidence ellipse is

$$ (Δp)<sup>T</sup>Σ<sup>−1</sup>(Δp) ≤ χ²<sub>2</sub>(0.95) = 5.991, $$

with semi-axes √(5.991λ<sub>i</sub>), where λ<sub>i</sub> are the eigenvalues of Σ. When Σ is isotropic (λ<sub>1</sub> = λ<sub>2</sub> = DRMS²), the ellipse degenerates to a circle of radius 2.4477DRMS; in general, 2.4477DRMS is the nominal circle radius, and exact 95% coverage should use the ellipse semi-axes. The main text reports R95 = 2.4477DRMS and notes "exact when isotropic."

**(e) Degeneracy and condition number.** As γ→0° or 180°, det A = ±sin γ→0, A becomes singular, and the entries of A<sup>−1</sup> diverge as 1/|sin γ|; by (c), traceΣ and detΣ both diverge as 1/sin²γ. det A = n<sub>1</sub>×n<sub>2</sub> = ±sin γ measures the singularity of A; using 1/|det A| = 1/|sin γ| as the condition-number indicator (same order as the 2-norm condition number cot(γ/2), both diverging as 1/γ as γ→0) gives the quantitative basis for the operating window [30°,150°]: at γ = 30°, G = 2G(90°), i.e., the accuracy cost doubles.

### A.3 Problem 3: Linearization Residual RMS = σ(s)²/d² and Hermite Quadrature

**(a) Exact angle and first-order approximation.** Take the true position as the origin and the true LOS as the x′ axis, with the target at (d,0), d = 40 m. Decompose the localization error into along-range δ<sub>∥</sub> and cross-range δ<sub>⊥</sub>, isotropic and independent, δ<sub>∥</sub>,δ<sub>⊥</sub> ~ N(0,σ(s)²). The exact azimuth deviation from the estimated position to the target is

$$ Δα = atan2(−δ<sub>⊥</sub>, d−δ<sub>∥</sub>). $$

Let u = δ<sub>∥</sub>/d and v = δ<sub>⊥</sub>/d; then d−δ<sub>∥</sub> = d(1−u), and

$$ Δα = −arctan(v/(1−u)). $$

Expanding v/(1−u) = v(1+u+u²+O(u³)) for |u| < 1 and using arctan z = z−z³/3+O(z⁵),

$$ Δα = −[v + uv + u²v − v³/3 + O(‖(u,v)‖⁴)]. $$

The first-order (linearized) model takes Δα ≈ −v = −δ<sub>⊥</sub>/d.

**(b) Residual and RMS.** The residual is

$$ R = Δα−(−v) = −uv − u²v + v³/3 + O(‖(u,v)‖⁴). $$

The leading term is −uv. Since δ<sub>∥</sub> and δ<sub>⊥</sub> are independent, zero-mean, and have variance σ²,

$$ E[R²] = E[u²v²] + O(σ⁶/d⁶) = E[δ<sub>∥</sub>²]E[δ<sub>⊥</sub>²]/d⁴ + O(σ⁶/d⁶) = σ⁴/d⁴ + O(σ⁶/d⁶). $$

Hence the residual RMS (in radians) is

$$ RMS<sub>R</sub> = √(E[R²]) = σ(s)²/d² + O(σ(s)³/d³). $$

Note that σ²/d² is dimensionless; under the small-angle approximation its numerical value is the RMS in radians, and conversion to degrees multiplies by 180/π. At s = 80 m, σ = 1.9 m, and d = 40 m:

$$ RMS<sub>R</sub> = (1.9/40)² = 2.256×10<sup>−3</sup> rad = 0.1293°. $$

Relative to σ<sub>ψ</sub>(80) = 2.8995° at the same point, the standard-deviation share is 0.1293/2.8995 = 4.46%, and the variance share is (0.1293/2.8995)² = 0.199% ≈ 0.2%. Higher-order terms are O(σ³/d³), and at σ/d ≤ 1.9/40 = 0.0475 they are at most about 5% of the leading term, so the first-order residual estimate is consistent within the parameter range of this paper.

**(c) Normal composition and the P criterion.** The gimbal bias ε<sub>0</sub> ~ N(0,0.8²), the control error ε<sub>c</sub> ~ N(0,0.6²), and the localization error are independent, so S = ε<sub>0</sub>+ε<sub>c</sub> ~ N(0,1.0²) (in degrees). Given (δ<sub>∥</sub>,δ<sub>⊥</sub>), Δα is deterministic, and the conditional probability is

$$ P(|Δα+S| ≤ 5° | δ<sub>∥</sub>,δ<sub>⊥</sub>) = Φ((5°−Δα)/1°) − Φ((−5°−Δα)/1°), $$

where Φ is the standard normal CDF. Therefore

$$ P(s) = E<sub>δ∥,δ⊥</sub>[Φ((5°−Δα(δ<sub>∥</sub>,δ<sub>⊥</sub>))/1°) − Φ((−5°−Δα(δ<sub>∥</sub>,δ<sub>⊥</sub>))/1°)]. $$

Since δ<sub>∥</sub> and δ<sub>⊥</sub> are independent and have equal variance, the two-dimensional expectation can be evaluated by tensor-product Gauss–Hermite quadrature:

$$ P(s) ≈ (1/π)Σ<sub>i=1</sub><sup>256</sup>Σ<sub>j=1</sub><sup>256</sup> w<sub>i</sub>w<sub>j</sub>[Φ((5°−Δα(√2σ(s)x<sub>i</sub>,√2σ(s)x<sub>j</sub>))/1°) − Φ((−5°−Δα(·))/1°)], $$

where x<sub>i</sub> and w<sub>i</sub> are the 256-point probabilistic Hermite nodes and weights (∫e<sup>−x²</sup>f(x)dx ≈ Σw<sub>i</sub>f(x<sub>i</sub>), Σw<sub>i</sub> = √π). P(s) decreases monotonically with s (σ(s) = a+bs is increasing, and the distribution of Δα widens with σ); bisection/root finding on P(s) = 0.95 gives s<sub>max</sub> = 66.84 m. The closed-form linearization gives 66.92 m, a 0.13% difference consistent with the Monte Carlo results in Table 4-5.

## Appendix B: Main Program List

- **Problem 1** (`Q1/`): `q1_solve.py` (domain gridding, arc sampling, tie-breaking, sensitivity); `area_estimators.py`, `q1_metric_compare.py`, `export_params.py` (three-convention area recomputation, Q/Q<sub>2</sub> comparison, export of the B1–B5/V1–V5/T1–T3 parameters).
- **Problem 2** (`Q2/`): `q2a_core.py`, `q2b_core.py`, `q2b_gamma.py` (two-station accuracy, vehicle and station selection, six-slot five-vehicle scheduling and baseline, 2(2) intersection-geometry check).
- **Problem 3** (`Q3/`): `q3_solve.py` (error propagation, s<sub>max</sub>, the (a,b) region, Monte Carlo, quadrature).
- **Problem 4** (`Q4/`): `q4_core.py`, `q4_robust.py`, `q4_tlast_diff.py`, `q4_scenario_list.py` (state snapshot, rescheduling, 74 scenarios, robustness checks, timeline comparison, scenario details).
- **Build scripts**: `build_numbers.py` → `numbers.md` (single data-source mapping from body numbers to JSON fields and scripts); `params.csv` / `params_table.md` (parameter specification exported by `export_params.py` and cross-checked with `q1_solve.py` and `q2_lib.py`).

The directory names `Q1/`–`Q4/` stand for the Chinese original directories in the submitted supporting materials. The correspondence between body numbers and data files is as follows:

- Section 4.2.4, three area conventions → `Q1/results/q1_area_estimators.json` (`area_estimators.py`)
- Table 4-4, 95% ellipse semi-axes → `Q2/results/q2b_precision.json` (`q2b_gamma.py`)
- Section 4.4.3 and Table 4-5 → `Q3/results/q3_summary.txt` (`q3_solve.py`)
- Section 4.5.3 and Table 4-6, scenario details → `Q4/results/q4_scenario_list.md` (`q4_scenario_list.py`)
- Section 6.2, Q/Q<sub>2</sub> comparison → `Q1/results/q1_metric_compare.json` (`q1_metric_compare.py`)
- Tables D-1 and D-2, all ten pairs and the 2(2) timeline → `Q2/results/q2a_results.json`, `Q2/results/q2b_results.json`

The complete source programs, run scripts, and result JSON files are provided in the supporting materials.

## Appendix C: Figure and Table Inventory

The four problem figure sets contain 11 multi-panel combined figures (3 for Q1, 4 for Q2, 2 for Q3, and 2 for Q4), plus one framework figure in Chapter 2 (Figure 2-1); each is delivered as an SVG vector with a PNG fallback.

**Table C-1 Figure inventory**

| Figure | Content | Section |
|---|---|---|
| Figure 2-1 | Framework of the four problems and the modeling chain | 2 |
| Figure 4-1 | Observable region of T1 and building occlusion shadows | 4.2.4 |
| Figure 4-2 | Optimal arc and margin–azimuth curve | 4.2.3 |
| Figure 4-3 | Sensitivity of r* and the observable area | 4.2.4 |
| Figure 4-4 | Observable region of T2 and 30 s reachable domains | 4.3.2 |
| Figure 4-5 | Two-station accuracy versus γ, d, and baseline | 4.3.2 |
| Figure 4-6 | Intersection error ellipses and the 95% circle | 4.3.2 |
| Figure 4-7 | Gantt chart and deployment routes of the optimized plan | 4.3.5 |
| Figure 4-8 | Variance components and shares of σ<sub>ψ</sub> | 4.4.3 |
| Figure 4-9 | Probability curve P(\|Δψ\| ≤ 5°) and the (a,b) region | 4.4.3 |
| Figure 4-10 | Two-stage response of t<sub>last</sub> to t<sub>rec</sub> | 4.5.3 |
| Figure 4-11 | Rescheduling Gantt chart and the 74-scenario comparison | 4.5.3 |

**Table C-2 Table inventory**

| Table | Content | Section |
|---|---|---|
| Table 2-1 | Building geometry and initial vehicle positions | 2.1 |
| Table 2-2 | Algorithm routes and selection rationale | 2.6 |
| Table 3-1 | Main symbols | 3.1 |
| Table 4-1 | Main results of Problem 1 | 4.2.4 |
| Table 4-2 | Two-station accuracy and station selection | 4.3.2 |
| Table 4-3 | Scheduling plan versus the nearest-assignment baseline | 4.3.4 |
| Table 4-4 | Intersection geometry of the timeliness plan | 4.3.6 |
| Table 4-5 | Monte Carlo verification for Problem 3 | 4.4.3 |
| Table 4-6 | Summary by scenario class for Problem 4 | 4.5.3 |
| Table 4-7 | Comparison of representative scenarios | 4.5.3 |
| Table 5-1 | Summary of validation for the four problems | 5 |
| Table 6-1 | Objective time under the v×ω full factorial | 6.2 |
| Table D-1 | All ten vehicle pairs for T2 | Appendix D |
| Table D-2 | Stations and per-task timeline of the 10.355 s plan | Appendix D |

## Appendix D: Supplementary Tables

**Table D-1 All ten vehicle pairs for T2 in 2(1)**

| Pair | d<sub>1</sub> / d<sub>2</sub> (m) | γ (°) | G (m) | DRMS (m) | t<sub>1</sub> / t<sub>2</sub> (s) | Feasible within 30 s |
|---|---|---|---|---|---|---|
| V1+V2 | 5.8188 / 11.2688 | 90.000 | 8.9678 | 0.1565 | 19.19 / 30.29 | No |
| V1+V3 | 5.8188 / 5.8188 | 90.000 | 5.8188 | 0.1016 | 18.71 / 3.49 | Yes |
| V1+V4 | 5.8188 / 5.8188 | 90.000 | 5.8188 | 0.1016 | 18.29 / 27.64 | Yes |
| V1+V5 | 5.8188 / 5.8188 | 90.000 | 5.8188 | 0.1016 | 19.47 / 14.17 | Yes |
| V2+V3 | 5.8188 / 11.2688 | 90.000 | 8.9678 | 0.1565 | 34.75 / 10.08 | No |
| V2+V4 | 5.8188 / 11.2688 | 90.000 | 8.9678 | 0.1565 | 34.75 / 25.37 | No |
| V2+V5 | 5.8188 / 11.2688 | 90.000 | 8.9678 | 0.1565 | 34.75 / 16.54 | No |
| V3+V4 | 5.8188 / 5.8188 | 90.000 | 5.8188 | 0.1016 | 6.49 / 27.64 | Yes |
| **V3+V5** | **5.8188 / 5.8188** | **90.000** | **5.8188** | **0.1016** | **5.11 / 13.61** | **Yes (selected)** |
| V4+V5 | 5.8188 / 5.8188 | 90.000 | 5.8188 | 0.1016 | 28.95 / 15.42 | Yes |

Note: d<sub>1</sub>, d<sub>2</sub> are the station–target distances, G and DRMS follow Section 4.3.1 with σ = 1° = 0.017453 rad, and t<sub>1</sub>, t<sub>2</sub> are the obstacle-avoiding travel times. The four V2 pairs share the same candidate station, hence their identical G. "Feasible" means both ready times are within the 30 s limit; among the six feasible pairs, V3+V5 has the smallest total travel time (18.72 s).

**Table D-2 Stations and per-task timeline of the 10.355 s plan in 2(2)**

| Vehicle | Task | Station (x, y) (m) | τ<sub>tr</sub> (s) | τ<sub>sl</sub> (s) | Start (s) | Observation end (s) | Reset end (s) | Clearance (m) |
|---|---|---|---|---|---|---|---|---|
| V3 | T1 | (15.2004, 87.2331) | 0.57 | 1.03 | 1.607 | 6.607 | 7.641 | 5.581 |
| V5 | T1 | (49.9000, 92.8000) | 0.07 | 1.53 | 1.607 | 6.607 | 8.140 | 7.080 |
| V1 | T2 | (14.8000, 14.3000) | 0.12 | 3.12 | 6.994 | 11.994 | 15.117 | 7.295 |
| V4 | T2 | (86.9000, 70.9000) | 1.03 | 5.96 | 6.994 | 11.994 | 17.953 | 0.067 |
| V2 | T3 | (88.1000, 9.5000) | 0.17 | 5.75 | 10.355 | 15.355 | 21.100 | 10.897 |
| V3 | T3 | (16.7656, 88.6590) | 0.71 | 2.01 | 10.355 | 15.355 | 17.363 | 0.001 |

Note: the observation lasts 5 s and the reset time is the slew back to the east-facing attitude. The start time of an alert is the later of its two vehicles' ready times, so V1 waits from 3.24 s to 6.994 s for the longer slew of V4. V3 serves T1 and then T3 (the only reuse chain); T1 is already under way at t<sub>p</sub> = 5 s and is therefore locked in Problem 4. Clearance is the minimum distance from the station to the 1.5 m-expanded building footprints; the two knife-edge values (0.001 m and 0.067 m) are those discussed in Section 4.3.5.
