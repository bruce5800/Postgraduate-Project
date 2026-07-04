<!-- 中文毕业论文 附录B 不可能性定理的证明细节（对应 ../en/B_proof_details.md）。诚实护栏：状态如实（B.7），剩余一步点名不隐藏。数值验证交叉引用附录 A.6。 -->

# 不可能性定理的证明细节

本附录记录第9章背后的形式化推演：模型与算法类（B.1 节）、主权衡不等式及其证明（B.2 节）、
稀缺资源 cell 构造及其闭式常数（B.3 节）、把建议误差转换为匹配比值的精确仿射律（B.4 节）、
到容差分布检验的归约与样本复杂度壁垒（B.5 节）、组装后的定理（B.6 节），以及对尚未完成部分
的如实陈述（B.7 节）。此处引用的数值验证由附录 A.6 所指的片段复现。

## 设置与算法类

**实例。** known-i.i.d. 在线二部匹配（第3章）：一个含 $r$ 个在线类型与若干离线资源的类型图；
$n$ 个到达自类型分布 $p$（支撑 $[r]$）独立同分布抽取；$\mathrm{OPT}(I)$ 为实现实例 $I$ 的最大匹配。

**建议。** 一个类型直方图 $q\in\Delta([r])$（Choo/BEM 的预测对象）。**跟随**建议——模仿策略
$\mathrm{Mimic}(q)$——在建议图上构建最大匹配，并把每个到达路由到其类型的建议伙伴（第3章）。

**基线。** 免预测的 Ranking 算法 $B$，在所研究的族上
$\mathbb E[B]/\mathbb E[\mathrm{OPT}] = \rho_{\mathrm{base}}$。

**测试-回退类 $\mathcal A_k$。** 算法 $A\in\mathcal A_k$ 观察建议 $q$ 与前缀 $X_{1:k}$（前 $k$ 个
到达的类型），**以任意可测规则**（可随机化）输出决策 $D\in\{\mathrm F,\mathrm R\}$，然后在到达
$k+1,\dots,n$ 上：若 $D=\mathrm F$ 执行 $\mathrm{Mimic}(q)$，否则执行 $B$。该类覆盖每一种决策
规则，而不仅是具体算法所用的经验 $\ell_1$ 阈值。

**一致性与鲁棒性。** 对带建议 $q$ 的实例分布 $\mathcal D$，记
$R(\mathcal D)=\mathbb E[\mathrm{ALG}]/\mathbb E[\mathrm{OPT}]$。一致性为好建议下的 $R$；鲁棒性为
坏建议下的 $R$（第3章）。

**亚线性假设（A0）。** $k=o(n)$。前缀自身对匹配的贡献至多 $k=o(n)$，使每个比值偏移
$O(k/n)=o(1)$；全文将其并入 $o(1)$ 项。

## 主权衡不等式

> **引理 B.1（主权衡）。** 设 $G$、$\mathrm{Bd}$ 为共享**同一**建议 $q$ 的两个实例分布，其在
> $X_{1:k}$ 上的前缀分布为 $\mathcal L_G,\mathcal L_{\mathrm{Bd}}$，记
> $\gamma_k := \mathrm{TV}(\mathcal L_G,\mathcal L_{\mathrm{Bd}})$。设跟随 $q$ 相对基线在 $G$ 下
> 获益 $\delta$、在 $\mathrm{Bd}$ 下受损 $\Delta$：
> $$\mathbb E_G[\mathrm{Mimic}]/\mathrm{OPT} \ge \rho_{\mathrm{base}}+\delta,
> \qquad \mathbb E_{\mathrm{Bd}}[\mathrm{Mimic}]/\mathrm{OPT} \le \rho_{\mathrm{base}}-\Delta,$$
> 而 $B$ 在两者下都达到 $\rho_{\mathrm{base}}\pm o(1)$。以 $\eta_c$（$G$ 下放弃的上升空间比例，
> 捕获的上升空间 $=(1-\eta_c)\,\delta$）与 $\eta_r$（$\mathrm{Bd}$ 下鲁棒性损失占 $\Delta$ 的比例，
> 损失 $=\eta_r\,\Delta$）参数化 $A\in\mathcal A_k$。则
> $$(1-\eta_c)\;\le\;\eta_r+\gamma_k+o(1). \tag{$\star$}$$

*证明。* 在 $G$ 下对决策 $D$ 取条件：
$$\mathbb E_G[\mathrm{ALG}]/\mathrm{OPT}
= P_G(\mathrm F)\cdot\frac{\mathbb E_G[\mathrm{Mimic}]}{\mathrm{OPT}}
+ P_G(\mathrm R)\cdot\rho_{\mathrm{base}} \pm o(1)
\;\ge\; \rho_{\mathrm{base}}+\delta\,P_G(\mathrm F)-o(1).$$
由定义捕获的上升空间为 $(1-\eta_c)\delta$，故 $P_G(\mathrm F)\ge 1-\eta_c-o(1)$。对称地，
$\mathrm{Bd}$ 下 $\mathbb E_{\mathrm{Bd}}[\mathrm{ALG}]/\mathrm{OPT}
= \rho_{\mathrm{base}}-\Delta\,P_{\mathrm{Bd}}(\mathrm F)\pm o(1)$，故鲁棒性损失为
$\Delta\,P_{\mathrm{Bd}}(\mathrm F)\pm o(1)$，即 $P_{\mathrm{Bd}}(\mathrm F)=\eta_r+o(1)$。最后，
$D$ 是 $(X_{1:k},q)$ 的（随机化）函数，而 $q$ 在 $G$ 与 $\mathrm{Bd}$ 间相同，故由全变差的耦合
刻画，$|P_G(\mathrm F)-P_{\mathrm{Bd}}(\mathrm F)|\le \gamma_k$。串联三式得
$1-\eta_c-o(1)\le P_G(\mathrm F)\le P_{\mathrm{Bd}}(\mathrm F)+\gamma_k
= \eta_r+\gamma_k+o(1)$，即 $(\star)$。 $\blacksquare$

当前缀无信息（$\gamma_k\to0$）时，$(\star)$ 禁止 $\eta_c\to0$ 与 $\eta_r\to0$ 同时成立：算法无法
既一致又鲁棒。剩下的工作是构造一个族，使 $\gamma_k=o(1)$ 与有意义的赌注
$\delta,\Delta=\Theta(1-\rho_{\mathrm{base}})$ **共存**。

**注（为何两点论证不够）。** 对单个每到达分布不同的 $(G,\mathrm{Bd})$ 对，赌注本身被可区分性
封顶：$\delta,\Delta = O(\gamma_k)$，故仅凭 $(\star)$ 只得到空洞的界。要在 $\gamma_k=o(1)$ 的
**同时**取得 $\delta,\Delta=\Theta(1)$，$G$ 与 $\mathrm{Bd}$ 的差异必须摊到 $\Theta(r)$ 个类型上、
每个的扰动都低于长度 $k$ 前缀的逐类型采样分辨率——这恰是 B.5 节所引**容差检验**困难实例的结构。
这也是低维构造失败的原因（B.7 节）。

## 稀缺资源 cell

构造由独立的 *cell* 组装而成，每个 cell 可闭式计算。

**cell。** 两个离线资源 $\{a,b\}$。到达依次为：一个**灵活**请求 $F$（邻域 $\{a,b\}$），总会到达，
且必须在见到专门请求**之前**路由；随后至多一个**专门**请求——类型 $\alpha$（邻域 $\{a\}$）以概率
$\theta s$、类型 $\beta$（邻域 $\{b\}$）以概率 $\theta(1-s)$、或无（概率 $1-\theta$）。其中
$\theta\in(0,1]$ 为**争用率**、$s\in[0,1]$ 为**偏置**。建议给出预测偏置 $\hat s$；跟随它即把 $F$
路由去保护预测的多数方专门请求（$\hat s>\tfrac12$：路由 $F\to b$，把 $a$ 留给更可能出现的
$\alpha$；反之对称）。

> **引理 B.2（单 cell 常数）。** 每个 cell 在期望意义下：
>
> | 量 | 值 |
> |---|---|
> | $\mathrm{OPT}$ | $1+\theta$ |
> | 基线（均匀路由 $F$） | $1+\theta/2$ |
> | 模仿，建议方向**正确**（$\operatorname{sign}(\hat s-\tfrac12)=\operatorname{sign}(s-\tfrac12)$） | $1+\theta\max(s,1-s)$ |
> | 模仿，建议方向**错误** | $1+\theta\min(s,1-s)$ |
>
> 故跟随相对基线的每 cell 优势为 $\pm\,\theta\,|s-\tfrac12|$（符号 $=$ 建议方向是否正确），且该
> cell 的专门请求分布 $p=(\theta s,\ \theta(1-s),\ 1-\theta)$ 与建议
> $q=(\theta\hat s,\ \theta(1-\hat s),\ 1-\theta)$ 的 $\ell_1$ 距离为
> $\ell_1(p,q)=2\theta\,|s-\hat s|$。

*证明。* 路由 $F\to a$ 时 $F$ 必被匹配，专门请求除非是 $\alpha$（其唯一邻居 $a$ 已被占）否则也被
匹配：$\theta s\cdot 1+\theta(1-s)\cdot 2+(1-\theta)\cdot 1 = 1+\theta(1-s)$。对称地 $F\to b$ 得
$1+\theta s$。基线取两者平均，$1+\theta/2$。更优的路由是 $F\to b$ 当且仅当 $s>\tfrac12$，方向
正确得 $1+\theta\max(s,1-s)$、错误得 $1+\theta\min(s,1-s)$。$\mathrm{OPT}$：专门请求到达（概率
$\theta$）时为 $2$，否则为 $1$，合计 $1+\theta$。$\ell_1$ 是三坐标求和，$(1-\theta)$ 坐标相消。
$\blacksquare$

两个量干净地分离，这正是设计的用意：优势的**幅度** $\theta|s-\tfrac12|$ 只取决于真值的信号
（cell 有多"被争用"），而其**符号**只取决于建议方向是否正确。于是"建议是否净有益"恰是恢复每个
cell 的**方向**这一问题——一个需要约 $1/|s-\tfrac12|^2$ 个**该 cell 的**样本才能分辨的 Bernoulli
判别。（数值核验，每 cell $4\times10^5$ 次试验：$\theta=0.6$、$s=0.7$ 时模拟优势 $\pm0.119$ 对
公式 $\pm0.12$；引理 B.2 的全部五个恒等式吻合到三位小数——附录 A.6。）

## 聚合构造与精确仿射律

**族。** $m=\Theta(n)$ 个独立 cell，每个用一对**互不相同**的专门类型 $(\alpha_i,\beta_i)$，故类型
支撑为 $r=\Theta(n)$，且 $n$ 个到达中每个专门类型只被看到 $O(1)$ 次。cell $i$ 有争用率 $\theta_i$
与真值偏置 $s_i$，信号 $\varepsilon_i=|s_i-\tfrac12|$；建议对每个 cell 预测一个同幅度的方向
（$\hat s_i=\tfrac12\pm\varepsilon_i$，同侧或反侧）。cell 互不相交，故逐 cell 的量可加性聚合。

> **引理 B.3（精确仿射转换律）。** 令
> $\rho_{\mathrm{perfect}}=\bigl(\sum_i(1+\theta_i\max(s_i,1-s_i))\bigr)/\mathrm{OPT}$ 为全部方向
> 正确（一致性天花板）的比值，$\mathrm{OPT}=\sum_i(1+\theta_i)$。则对任何每 cell 幅度与真值一致的
> 建议，在期望意义下
> $$\mathbb E[\text{follow-ratio}] \;=\; \rho_{\mathrm{perfect}}-\tfrac12\,\ell_1(p,q),$$
> 从而盈亏平衡的建议误差为
> $\ell_1^* = 2(\rho_{\mathrm{perfect}}-\rho_{\mathrm{base}})$，其中
> $\rho_{\mathrm{base}}=\bigl(\sum_i(1+\theta_i/2)\bigr)/\mathrm{OPT}$。

*证明。* 由引理 B.2，cell $i$ 在建议方向正确时对被跟随匹配贡献 $1+\theta_i\max(s_i,1-s_i)$、错误
时贡献 $1+\theta_i\min(s_i,1-s_i)$；差为 $2\theta_i\varepsilon_i$。令 $W$ 为方向错误的 cell 集，
$$\text{被跟随匹配}
= \sum_i\bigl(1+\theta_i\max(s_i,1-s_i)\bigr)-\sum_{i\in W}2\theta_i\varepsilon_i.$$
$\ell_1$ 方面：灵活与"无专门请求"坐标相消，cell $i$ 贡献 $2\theta_i|s_i-\hat s_i|$——正确时为
$0$、错误时（反侧同幅度，$|s_i-\hat s_i|=2\varepsilon_i$）为 $4\theta_i\varepsilon_i$。类型归一化
因子为 $N=\sum_i(1+\theta_i)=\mathrm{OPT}$，故
$\ell_1(p,q)=\bigl(\sum_{i\in W}4\theta_i\varepsilon_i\bigr)/\mathrm{OPT}
=2\bigl(\sum_{i\in W}2\theta_i\varepsilon_i\bigr)/\mathrm{OPT}$。代入即得
$$\mathbb E[\text{follow-ratio}]
=\frac{\text{被跟随匹配}}{\mathrm{OPT}}
=\rho_{\mathrm{perfect}}-\tfrac12\,\ell_1(p,q). \qquad\blacksquare$$

被跟随匹配是 $m$ 个独立有界 cell 贡献之和，以 $O(1/\sqrt m)$ 的速率向均值集中；仿射律以高概率
成立，而不仅在期望意义下。（数值核验：$\theta=0.6$、$\varepsilon=0.3$、$m=4000$——
$\rho_{\mathrm{perfect}}=0.924$、$\rho_{\mathrm{base}}=0.812$——在每个错误比例
$\varphi\in\{0,0.2,0.5,0.8,1\}$ 处与仿射律吻合到三位小数，模拟盈亏平衡点 $0.223$ 对预测的
$\ell_1^*=2(0.924-0.812)=0.224$；附录 A.6。）

**推论：赌注与间隙干净，且好建议一侧是一个球。** 定义"跟随获益 $\ge\delta$"
$\iff \ell_1\le \ell_1^*-2\delta =: a$，"跟随受损 $\ge\Delta$"
$\iff \ell_1\ge \ell_1^*+2\Delta =: b$。取例如
$\delta=\Delta=(\rho_{\mathrm{perfect}}-\rho_{\mathrm{base}})/4$，得 $a=\ell_1^*/2>0$、
$b=3\ell_1^*/2$、间隙 $b-a=\ell_1^*$——全部是与 $n$ 无关的 $\Theta(1)$ 常数（由固定的每 cell
$\theta,\varepsilon$ 决定；只有 cell 数随 $n$ 增长）。关键在 $a>0$：好建议是真值周围一个
$\Theta(1)$ 半径的**球**，而非单点 $p=q$。这正是把决策问题放入**容差**检验体制的性质（B.5 节）。

## 归约到容差恒等检验

> **引理 B.4（算法 $\Rightarrow$ 检验器）。** 在 B.4 节的族上固定建议 $q$。设 $A\in\mathcal A_k$
> 在 $\ell_1(p,q)\le a$ 时是 $(1-\eta_c)$-一致的、在 $\ell_1(p,q)\ge b$ 时损失至多 $\eta_r\Delta$。
> 则把 $A$ 的决策 $D$ 视为 $k$ 个独立同分布样本 $X_{1:k}\sim p$ 的函数，它以至多
> $\eta_c+\eta_r+o(1)$ 的错误率区分 $\{\ell_1(p,q)\le a\}$ 与 $\{\ell_1(p,q)\ge b\}$。

*证明概要。* 一致性迫使 $\ell_1\le a$ 时高概率 $D=\mathrm F$（否则放弃 $\delta$ 收益，与
$(1-\eta_c)$-一致矛盾）；鲁棒性迫使 $\ell_1\ge b$ 时高概率 $D=\mathrm R$（否则吃下 $\Delta$
损失）。故 $D$ 本身就是检验器，其错误概率经引理 B.1 中相同的条件化论证由一致性与鲁棒性的松弛量
所界。 $\blacksquare$

要点在于：前缀 $X_{1:k}$ **就是** $k$ 个来自类型分布 $p$ 的独立同分布样本（known-i.i.d. 模型），
且 $D$ 是它们的任意函数——因此该检验问题的样本复杂度下界排除 $\mathcal A_k$ 中的**每一种**规则，
而不仅是经验 $\ell_1$ 阈值。正是这一步使结果与算法无关，并将其与 Choo 等人算法内部构造性的基线
耦合区分开来（第9章）。

> **定理 B.5（容差恒等检验；引用）。** 对已知的 $q$（支撑规模 $r$），以错误率 $\le 1/3$ 区分
> $\ell_1(p,q)\le\varepsilon_1$ 与 $\ell_1(p,q)\ge\varepsilon_2$ 需要
> $$k \;=\; \tilde\Theta\!\Bigl(\frac{\sqrt r}{\varepsilon_2^2}
> \;+\; \frac{r}{\log r}\cdot\max\Bigl\{\frac{\varepsilon_1}{\varepsilon_2^2},
> \Bigl(\frac{\varepsilon_1}{\varepsilon_2^2}\Bigr)^2\Bigr\}\Bigr)$$
> 个样本 [@canonne2022tolerance]。特别地，常数容差 $0<\varepsilon_1<\varepsilon_2$ 时复杂度为
> $\tilde\Theta(r/\log r)$——近线性——而非容差情形 $\varepsilon_1=0$ 只需
> $\Theta(\sqrt r/\varepsilon_2^2)$ [@paninski2008coincidence; @valiant2017automatic]。常数容差下的
> $\Omega(r/\log r)$ 下界与 $\ell_1$ 估计常数另见 [@valiant2011unseen; @jiao2018l1]。

由于 B.4 节给出 $a>0$（一个 $\Theta(1)$ 球而非单点），我们的检验问题具有常数容差
$\varepsilon_1=a$、$\varepsilon_2=b$，落入**容差**体制：在 $r=\Theta(n)$ 个类型下，任何检验器都
需要 $\tilde\Theta(n/\log n)$ 个样本。$\Theta(\sqrt r)$ 的非容差逃逸不适用——且这并非巧合而是
设计所需：若只在建议恰好正确（$a=0$）时要求一致性，一致性保证本身就空洞了。

## 组装定理

在 B.4 节的族上（常数 $\theta,\varepsilon$，故 $\rho_{\mathrm{base}}=1-\Theta(1)$、赌注
$\delta,\Delta=\Theta(1)$、容差 $a,b=\Theta(1)$、支撑 $r=\Theta(n)$）串联 B.2–B.5 节：

1. 设 $A\in\mathcal A_k$（$k=o(n/\log n)$）在该族上 $(1-o(1))$-一致且
   $(\rho_{\mathrm{base}}-o(1))$-鲁棒。
2. 由引理 B.4，其决策以 $o(1)$ 错误率、从 $k$ 个样本解出支撑 $\Theta(n)$ 上的 $(a,b)$-容差恒等
   检验问题。
3. 由定理 B.5，任何这样的检验器需要 $\tilde\Theta(n/\log n)$ 个样本——多于 $k$ 所能提供。下界所
   保证的见证对由两个类型分布 $p_G$（$\ell_1(p_G,q)\le a$）与 $p_{\mathrm{Bd}}$
   （$\ell_1(p_{\mathrm{Bd}},q)\ge b$）组成，其长度 $k$ 前缀分布满足 $\gamma_k=o(1)$；由仿射律
   （引理 B.3），位于这两个距离上的**任何**一对都分别实现收益 $\delta$ 与损失 $\Delta$。
4. 对 $(p_G,p_{\mathrm{Bd}})$ 应用引理 B.1（$\gamma_k=o(1)$）迫使
   $\eta_c+\eta_r\ge 1-o(1)$——与第 1 步矛盾。

> **定理 B.6（不可能性；即第9章的定理）。** 对每个检验预算 $k=o(n/\log n)$，存在一个含
> $r=\Theta(n)$ 个类型、基线强度 $\rho_{\mathrm{base}}=1-\Theta(1)$ 的 known-i.i.d. 匹配族，在其上
> 没有任何测试-回退算法 $A\in\mathcal A_k$——以前缀上的任意规则决策——能同时 $(1-o(1))$-一致且
> $(\rho_{\mathrm{base}}-o(1))$-鲁棒。可达的（一致性，鲁棒性）区域塌缩到基线点
> $(\rho_{\mathrm{base}},\rho_{\mathrm{base}})$。

连同容易的强基线一侧——少类型 $\Rightarrow$ 匹配近乎完美 $\Rightarrow$ 上升空间 $\delta\to0$、
无可捕获——这正是图 9.1 的剪刀：上升空间只存在于容差检验不可行之处。

## 状态、剩余一步与一个负发现

**本附录已证。** 引理 B.1（完整证明，B.2 节）；引理 B.2（完整证明加三位小数数值核验，B.3 节）；
引理 B.3（完整证明加核验，B.4 节）；引理 B.4（证明概要，其补全是对引理 B.1 两个条件化展开式的
簿记工作）。定理 B.5 是被引用的、精确的现代结果——承重的外部原料——且 B.4 节确立了我们的问题
位于其容差（保定理）一侧。

**剩余一步（如实陈述）。** B.6 节第 3 步要求**给出**容差检验下界构造中的见证对
$(p_G,p_{\mathrm{Bd}})$，并核对它在 B.4 节的 cell 参数化下确实落在 $\ell_1\le a$ 与 $\ell_1\ge b$。
由于仿射律使位于这两个距离上的任何一对都实现赌注，这是一步常规核对而非新数学；它连同一次端到端
的最终审阅，在写作本文时尚未完成（见 9.5 节）。在其闭合之前，定理 B.6 应按第9章所述的状态来读。

**一个值得记录的负发现。** 构造的**低维**版本——所有 cell 共享一个全局偏置参数、好/坏两情景仅差
一个全局平移——可证失败：长度 $k$ 的前缀能把这一个共享参数估到 $\pm1/\sqrt{\theta k}$，故任何
$\delta=\omega(\sqrt{\theta/k})$ 都会使两情景可区分，只剩一个空洞的不可能性。定理的强度确实需要
把建议误差摊到 $\Theta(n)$ 个独立 cell 上、每个的扰动都低于逐类型采样分辨率——维度是本质性的，
这也是定理的强形式针对 $r=\Theta(n)$ 体制陈述、常数 $r$ 版本留作开放的原因（9.5 节）。
