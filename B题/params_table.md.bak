# 题设参数规范表（B 题）

> 数据源：`第一题/code/q1_solve.py`（AST 字面量读取，不执行求解器）与 `第二题/code/q2_lib.py`；两处 B1–B5、V1–V5、T1 已交叉校验一致。

## 全局常量

| 参数 | 数值 | 单位 | 说明 |
|---|---|---|---|
| field_size | 100 | m | [0,100] x [0,100] |
| dispatch_center_O | (50, 50) | m | alerts given in (theta,R) about O |
| equivalent_disk_radius | 1.5 | m |  |
| camera_height | 2.0 | m | above ground |
| speed | 3.0 | m/s | constant, no acceleration |
| pan_rate | 30 | deg/s |  |
| tilt_rate | 30 | deg/s | both axes move together |
| elevation_min | -10.0 | deg | closed interval |
| elevation_max | 80.0 | deg | closed interval |
| observation_duration | 5 | s | synchronized two-vehicle dwell |

## 建筑（轴对齐长方体）

| 建筑 | x 区间 (m) | y 区间 (m) | 高度 (m) |
|---|---|---|---|
| B1 | [22, 34] | [16, 26] | 20 |
| B2 | [63, 79] | [59, 71] | 28 |
| B3 | [10, 24] | [65, 76] | 12 |
| B4 | [72, 86] | [22, 34] | 24 |
| B5 | [41, 51] | [38, 46] | 32 |

## 观测车初始位置

| 车辆 | x (m) | y (m) |
|---|---|---|
| V1 | 15 | 14 |
| V2 | 88 | 10 |
| V3 | 14 | 86 |
| V4 | 88 | 68 |
| V5 | 50 | 93 |

## 告警

| 告警 | θ (°) | R (m) | H (m) | 水平投影 (x, y) (m) | r_min (m) |
|---|---|---|---|---|---|
| T1 | 30 | 40 | 45 | (84.6410, 70.0000) | 7.5821 |
| T2 | 150 | 45 | 35 | (11.0289, 72.5000) | 5.8188 |
| T3 | 285 | 38 | 55 | (59.8351, 13.2948) | 9.3453 |

注：告警水平位置 = O + R(cosθ, sinθ)，O=(50,50)；r_min=(H−h_cam)/tan(ε_max) 为俯仰上界导出的最小水平距离。
