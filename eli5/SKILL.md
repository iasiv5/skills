---
name: eli5
description: 把复杂概念做成「大图小字」的 HTML 图解页，像给 5 岁孩子讲解一样让零基础读者一眼看懂（ELI5 = Explain Like I'm 5）。
disable-model-invocation: true
argument-hint: "要解释的概念或主题"
---

# eli5

ELI5 = Explain Like I'm 5。把用户指定的主题讲给一个 5 岁孩子——对该话题完全不懂、只认识日常事物的人。产出是一个自包含的 HTML 图解页（内联 CSS/SVG，无外部依赖），写成单个 HTML 文件交付。

## 三个约束

- **视角**：读者零基础。每个术语出现时紧跟一个日常生活比喻，比喻先于定义。
- **形式**：单个 HTML 文件，浏览器直接打开即完整可用。
- **风格（大图小字）**：一屏一张大图（SVG 示意图或场景插画），一屏文字不超过两句。

## 页面结构

全景屏（这东西整体上怎么回事）→ 拆解屏（每屏一个子概念，后一屏建立在前一屏上）→ 收尾屏（回到全景图，读者能借它向别人复述整个话题）。

## 完成标准

- 逐屏自查：每屏恰好一图；文字 ≤ 2 句；出现的每个术语都有生活比喻。
- 只看图和这两句话，读者能按顺序讲清「是什么 → 怎么运作 → 为什么重要」。

---

## 来源

本 skill 致敬 Anthropic 内部流传的 ELI5 技巧，是其本地化改写版。原版全文只有一句话，原样留存于此：

> Explain like I'm someone who knows nothing about this topic, using a HTML artifact with big pictures and few words.

出处：[anthropics/claude-plugins-community · eli5](https://github.com/anthropics/claude-plugins-community/blob/main/eli5/skills/eli5/SKILL.md)。
