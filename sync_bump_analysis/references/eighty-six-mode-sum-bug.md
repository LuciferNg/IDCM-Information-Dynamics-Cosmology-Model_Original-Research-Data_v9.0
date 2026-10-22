# 86 模式總和 Find-and-Replace Bug

**日期：** 2026-08-10
**文件：** `references/eighty-six-mode-sum-bug.md`

## 1. 問題

喺 `idcm_wfield_expansion.py` 嘅 f-string 入面，`Σ_{n=1}^{43} γ_n = 86` 因為 LaTeX 風格嘅 curly braces `{` `}` 同 Python f-string 嘅 `{` `}` 衝突，令 syntax error。

## 2. 修正

將 f-string 改為普通 string + `print(msg)`：

```python
# ❌ 錯：f-string curly braces 衝突
print(f"""總能量: Σ_{n=1}^{43} γ_n = 86""")

# ✅ 正確：普通 string
msg = """總能量: Σ γ_n (n=1..43) = 86"""
print(msg)
```

## 3. 數值

```
Σ_{n=1}^{43} γ_n = Σ_{n=1}^{43} 4 sin²(πn/88) = 86
```

呢個係 exact sum，因為 γ_n + γ_{44-n} = 4 = B（complementary pairing），而有 43 個非零模式，加埋 43×2 = 86。

## 4. 教訓

喺 Python f-string 入面用 `{` `}` 要小心 — 佢哋同 LaTeX 嘅 curly braces 衝突。解決方法：
1. 用 `{{` `}}` 喺 f-string 入面
2. 或者用普通 string（`.format()` 或 concatenation）

## 5. 參考

- `idcm_wfield_expansion.py` line 277 (已修正)