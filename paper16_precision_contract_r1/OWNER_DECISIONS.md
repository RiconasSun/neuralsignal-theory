# Owner decisions for prospective registration

The following two messages are transcribed from the conversation into UTF-8/LF.
No original transport timestamp or byte-identical attachment hash is asserted.
Registration time is recorded separately in PRECISION_CONTRACT.json.

## S07 — owner message

选择方案 1。

S07 采用 A-only 主模型评分窗口 [100,220) ms 的放电率：

- 使用每只鼠主模型共同有效的 A presentations 和相同 observation mask。
- Rate = 评分窗 spike 总数 / 实际有效评分曝光秒数。
- 按 Rate 升序排列，平局按 Unit ID 升序。
- 选取排序后的中间 4 个单位（zero-based positions 2–5）。
- Development 仅使用 A；未来 Final 仅使用 C。
- 禁止 B/E/D 数据参与排名，禁止改变原始 8 个单位的选择。

这是未来独立 Mission 的前瞻性协议精确定义，不追溯修改原 M1，也不解除本次 STOP。

请保留当前 STOP 及全部历史证据，在新 Mission 中正式登记该精度合同后再执行。

## N4 — owner message

选择方案 2。

N4 的 11 个错误映射按以下规则执行：

1. color flip：同时改变当前颜色对应的 12 个 color×time PSTH one-hot 列，以及 `color*r`。
2. time rotation：只循环移动 PSTH 的 6 个时间索引。
3. `previous_color`、历史重复次数、running 原始值和其他 nuisance 特征保持不变。
4. B1 已拟合系数、scaler、target、mask 均保持冻结，禁止重新拟合。
5. 使用 color flip × 6 time rotations，排除 identity，共 11 个错误映射。

将此作为新的前瞻性精度合同澄清登记，保留原 M1 与当前 STOP，不追溯修改冻结历史。
