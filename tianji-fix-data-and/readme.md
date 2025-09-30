# 《天机变》- 游戏资产 (Assets) 使用说明

**版本: 2.0**
**日期: 2025-09-27**

## 1. 简介

欢迎来到《天机变》的游戏资产库。本文件夹 (`/assets`) 包含了构建游戏所需的所有数据、图像和其他资源。

本文档旨在为所有开发者提供一个清晰的指引，说明资产的组织结构、命名规范以及如何在游戏引擎中正确地加载和使用它们。请在开始开发前仔细阅读本文档。

**核心设计哲学：单一事实来源 (Single Source of Truth)**

本项目遵循严格的数据与视图分离原则。
- **视觉表现 (View):** 所有视觉资源 (如卡牌美术) 都存储在 `.png` 文件中。
- **游戏逻辑 (Logic):** 所有卡牌的逻辑行为都统一在 **`hexagram_interpretations.md`** 文件中进行定义。该文件是人类可读的描述和机器可读的 `json` 逻辑的唯一来源。
- **游戏数据 (Data):** 位于 `assets/data/cards/` 下的 `.json` 文件是 **自动生成的产物**。

**重要：请勿直接编辑 `.json` 文件。** 要修改卡牌逻辑，请参见第4.1节。

---

## 2. 文件夹结构

所有资产都位于 `assets` 文件夹下，其结构如下：

```
assets/
├── data/                      # 存放所有游戏逻辑数据 (自动生成的JSON文件)
│   └── cards/
│       ├── basic/             # 64张基础牌
│       ├── destiny/           # 12张天命牌
│       ├── function/          # 5种功能牌
│       ├── natal/             # 8张本命卦牌
│       └── state/             # 游戏状态牌
│           ├── branches/      # 12张地支牌
│           ├── celestial/     # 7张星象牌
│           └── stems/         # 10张天干牌
│
└── images/                    # 存放所有视觉资源 (PNG文件)
    └── cards/
        ├── backs/             # 各种牌背
        ├── basic/             # 基础牌美术
        ... (结构与 data/cards/ 完全镜像)
```
    **关键规则：镜像结构**

请注意，`data/cards/` 和 `images/cards/` 文件夹的**内部结构是完全一致的**。这种设计是为了简化资源加载。程序可以通过替换路径中的 `data` 为 `images`，轻易地找到任何数据文件所对应的图像文件。

---

## 3. 核心概念与命名规范

### 3.1 卡牌ID (Card ID)

游戏中的每一张卡牌都有一个**全局唯一的ID**，这是它在代码中的“身份证”。ID遵循 `[type]_[identifier]` 的格式。

*   **文件命名:** 所有与卡牌相关的文件（`.json` 和 `.png`）都必须以其卡牌ID命名。
    *   **示例:** `basic_01_qian.json`, `basic_01_qian.png`

*   **命名范式:**
    *   **基础牌:** `basic_[01-64]_[pinyin]`
    *   **功能牌:** `function_[pinyin]`
    *   **本命卦牌:** `natal_[pinyin]`
    *   **天命牌:** `destiny_[pinyin]`
    *   **天干牌:** `stem_[pinyin]`
    *   **地支牌:** `branch_[pinyin]`
    *   **星象牌:** `celestial_[pinyin]`

### 3.2 数据文件 (`.json`)

`.json` 文件是**自动生成的**，定义了卡牌的一切**逻辑行为**。

*   **编码:** 所有 `.json` 文件使用 `UTF-8` 编码。
*   **结构:** 完整的JSON结构定义请参阅 **`card_logic_schema.md`**。

### 3.3 图像文件 (`.png`)

`.png` 文件定义了卡牌的**视觉外观**。

*   **尺寸:** 当前占位图尺寸为 `500x700` 像素。
*   **替换规则:** 你可以随时替换任何一张 `.png` 图片以更新美术，**但文件名必须与对应的 `.json` 文件保持严格一致**。

---

## 4. 工作流程与编程指南

### 4.1 修改卡牌逻辑 (核心工作流)

要修改任何卡牌的逻辑、效果或数值，请严格遵循以下步骤：

1.  **编辑源文件:** 打开 **`hexagram_interpretations.md`** 文件。
2.  **找到目标卡牌:** 定位到你想要修改的卡牌的描述部分。
3.  **修改JSON块:** 直接编辑该卡牌描述下方的 ```json ... ``` 代码块。这里是定义卡牌行为的唯一地方。
4.  **运行生成脚本:** 在终端中运行以下命令：
    ```bash
    python tools/generate_card_data.py
    ```
5.  **验证:** 脚本会自动重新生成所有位于 `assets/data/cards/` 下的 `.json` 文件，确保你的修改已应用。

### 4.2 加载卡牌 (编程指南)

在游戏中加载并创建一张卡牌的推荐流程如下。此伪代码已修正了所有已知的路径解析错误，可作为实现参考。

```javascript
// 伪代码示例 (V2.0, 已修正数据结构不匹配问题)

/**
 * 加载并准备一张卡牌以供在特定位置使用。
 * @param {string} cardId - 卡牌的唯一ID, e.g., "basic_01_qian".
 * @param {string} playerLocation - 玩家当前所在的部, e.g., "di", "ren", "tian".
 * @returns {Card} 一个包含了正确效果和图像的游戏卡牌对象。
 */
function prepareCardForUse(cardId, playerLocation) {
    // 1. 从ID中解析出主类型 (basic, stem, etc.)
    const type = cardId.split('_')[0];

    // 2. 根据类型推导正确的资产路径 (此部分逻辑保持不变)
    let categoryPath;
    const stateCardTypes = ['stem', 'branch', 'celestial'];
    if (stateCardTypes.includes(type)) {
        const subfolder = (type === 'celestial') ? 'celestial' : type + 's';
        categoryPath = `state/${subfolder}`;
    } else {
        categoryPath = type;
    }

    // 3. 构建完整的文件路径
    const filename = cardId;
    const dataPath = `assets/data/cards/${categoryPath}/${filename}.json`;
    const imagePath = `assets/images/cards/${categoryPath}/${filename}.png`;

    // 4. 加载核心资源
    const fullCardData = loadJsonFile(dataPath); // 加载包含所有变体的完整JSON
    const cardImage = loadImageFile(imagePath);

    // 5. **核心逻辑：根据玩家位置选择正确的爻辞效果**
    // 从完整数据中提取出适用于当前位置的效果
    let activeEffect;
    if (fullCardData.core_mechanism && fullCardData.core_mechanism.variants) {
        const variants = fullCardData.core_mechanism.variants;
        if (variants[playerLocation]) {
            activeEffect = variants[playerLocation].effect;
        } else {
            // 如果没有找到特定位置的变体，可以设置一个默认或错误状态
            console.warn(`Card ${cardId} has no variant for location: ${playerLocation}`);
            // 根据游戏规则，此处可能需要加载一个空效果或基础效果
            activeEffect = {};
        }
    } else {
        // 对于没有爻辞变体的卡牌（如功能牌），直接使用其顶级effect
        activeEffect = fullCardData.effect || {};
    }

    // 6. 在游戏中创建卡牌对象，注入选定的效果
    // Card构造函数现在接收一个“激活效果”而不是整个数据块
    const cardObject = new Card(fullCardData.id, fullCardData.name, cardImage, activeEffect);

    return cardObject;
}

// 使用示例
// 玩家位于【地部】，准备使用《乾》卦
let playerLocation = "di";
let qianCardForDi = prepareCardForUse("basic_01_qian", playerLocation);
// qianCardForDi.activeEffect 此时将包含《乾》卦【地部】(蓄力)的效果

// 玩家位于【天部】，准备使用《乾》卦
playerLocation = "tian";
let qianCardForTian = prepareCardForUse("basic_01_qian", playerLocation);
// qianCardForTian.activeEffect 此时将包含《乾》卦【天部】(君威)的效果
```

### 4.3 构建牌库

要构建一个完整的牌库（例如，基础牌库），程序应该：

1. 读取 `assets/data/cards/basic/` 目录下的所有文件名。
2. 从文件名中提取出卡牌ID（去除`.json`后缀）。
3. 对于每一个ID，调用 `loadCard(id)` 函数来创建卡牌对象。
4. 将所有创建的卡牌对象存入一个列表或数组中，然后进行洗牌。

---

## 5. 资产详情 (JSON Schema)

**所有卡牌的JSON结构都遵循 `card_logic_schema.md` 中定义的规范。**

该文档是定义卡牌数据结构、可用动作、触发器和参数的权威来源。在实现卡牌逻辑或扩展引擎功能时，请务必以此文件为准。

由于所有 `.json` 文件都是通过脚本生成的，此处不再提供静态示例，以避免信息过时。

---