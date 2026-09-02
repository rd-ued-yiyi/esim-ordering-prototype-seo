#!/usr/bin/env python3
"""把 assets/hero/ 的矢量图层合成成一个 viewBox=0 0 375 300 的 hero SVG（矢量、任意 DPI 清晰），
并按 Figma 动效规格注入两条 SMIL 循环动画：地球大陆横向滚动（自转）、小圆点椭圆轨迹绕行+淡出。
产出 assets/hero/hero-scene.svg。"""
import re, pathlib

HERO = pathlib.Path(__file__).parent / "assets" / "hero"

def load(name):
    txt = (HERO / f"{name}.svg").read_text(encoding="utf-8")
    m = re.search(r'<svg[^>]*?\bwidth="([\d.]+)"\s+height="([\d.]+)"', txt)
    nw, nh = float(m.group(1)), float(m.group(2))
    inner = re.sub(r'^.*?<svg[^>]*?>', '', txt, count=1, flags=re.S)
    inner = re.sub(r'</svg>\s*$', '', inner, flags=re.S)
    return inner.strip(), nw, nh

def namespace(inner, prefix):
    """给该图层内所有 id 及 url(#..)/href=#.. 引用加前缀，避免多图层 id 冲突（渐变/遮罩/裁剪）。"""
    inner = re.sub(r'\bid="([^"]+)"', lambda m: f'id="{prefix}__{m.group(1)}"', inner)
    inner = re.sub(r'url\(#([^)]+)\)', lambda m: f'url(#{prefix}__{m.group(1)})', inner)
    inner = re.sub(r'\b(xlink:href|href)="#([^"]+)"',
                   lambda m: f'{m.group(1)}="#{prefix}__{m.group(2)}"', inner)
    return inner

# 裁掉顶部状态栏高度(59px)：这段是纯 cyan 渐变，插画内容(地球/气泡/星星)在 y≈85 以下，裁切不影响。
STATUS_CROP = 59
CONT_DUR = "8s"   # 地球大陆自转周期（原 Figma 2s 太快，放慢）
DOT_DUR = "6s"    # 小圆点绕行周期

# 大陆自转：SMIL 注入到 continents strip 组（0 → 一个地球宽度 -134.733，线性无限循环，无缝）
CONTINENTS_ANIM = ('<animateTransform attributeName="transform" type="translate" '
                   f'from="0 0" to="-134.733 0" dur="{CONT_DUR}" repeatCount="indefinite" '
                   'additive="sum"/>')

def load_earth():
    inner, nw, nh = load("earth")
    inner = inner.replace('<g id="continents strip">',
                          '<g id="continents strip">' + CONTINENTS_ANIM, 1)
    return namespace(inner, "earth"), nw, nh

# 图层：name, 外框 L,T,W,H(取自 Figma), SVG 变换(围绕中心), 是否 earth
LAYERS = [
    # blob 方向=scaleX(-1)（Figma: rotate180+scaleY(-1) 等效）。此方向下曲线回环藏在地球/手机后面，
    # 可见的是左侧平缓弧线+左上角弧弯——与 Figma 视觉一致（增强对比度核实过，勿再改方向）。
    # 下移 25px：让左上角弧弯在裁掉 59px 后仍可见。
    ("blob",   -14.07,  26.14, 442.147, 171.458, "scale(-1 1)"),
    ("phone1", 175.77, 107.81, 187.76,  139.245, "rotate(-158) skewX(-24) scale(1 -0.91)"),
    ("phone2", 221.95, 179.31,  30.593,  17.619, "rotate(-158) skewX(-24) scale(1 -0.91)"),
    ("phone3", 197.97, 192.59,  65.375,  36.797, "rotate(-158) skewX(-24) scale(1 -0.91)"),
    # 注意变换顺序：CSS 是 rotate 在前 scale 在后（顺序反了线的斜向会镜像成「\」）
    ("line5",  308.01, 124.26,  16.546,   7.091, "rotate(-156.8) scale(1 -1)"),
    ("line6",  208.58, 222.64,  16.546,   7.091, "rotate(-156.8) scale(1 -1)"),
    ("ring",   233.73, 151.73,  81.643,  48.717, ""),
    ("earth",  218.28,  81.96, 156.244, 132.287, "rotate(15)"),
    ("subtract",222.09, 120.0, 105.263,  52.39,  ""),
    # dot 单独处理（动画）
    ("signal", 209.98,  93.7,   42.39,   37.896, "rotate(-15)"),
    ("wifi",   325.52,  97.78,  28.015,  26.552, "rotate(30)"),
    ("star1",  304.8,   97.74,  11.7,    11.7,   "rotate(68.05)"),
    ("star2",  346.28, 169.89,  11.6,    11.6,   "rotate(68.05)"),
    ("star3",  283.95,  84.47,  18.85,   18.85,  "rotate(11.11)"),
]

def place(name, L, T, W, H, transform):
    if name == "earth":
        inner, nw, nh = load_earth()
    else:
        inner, nw, nh = load(name)
        inner = namespace(inner, name)
    cx, cy = L + W / 2, T + H / 2
    x, y = cx - nw / 2, cy - nh / 2
    nested = (f'<svg x="{x:.3f}" y="{y:.3f}" width="{nw:.3f}" height="{nh:.3f}" '
              f'viewBox="0 0 {nw} {nh}" overflow="visible" fill="none">{inner}</svg>')
    if transform:
        return (f'<g transform="translate({cx:.3f} {cy:.3f}) {transform} '
                f'translate({-cx:.3f} {-cy:.3f})">{nested}</g>')
    return nested

# 小圆点：椭圆轨迹绕行（取动效 values，均匀 keyTimes 平滑循环）+ 淡出（绕到远侧隐藏）
DOT_X = [-0.607,-2.245,-0.296,5.107,13.594,24.589,37.341,50.981,64.581,77.212,83.694,
         88.015,96.254,101.365,103.003,101.054,95.651,87.164,76.169,63.417,49.777,
         36.177,23.546,12.743,4.504,-0.607]
DOT_Y = [-0.061,-6.556,-12.256,-16.772,-19.796,-21.123,-20.662,-18.444,-14.621,-9.452,
         -5.756,-3.291,3.443,10.291,16.786,22.486,27.002,30.026,31.353,30.892,28.674,
         24.851,19.682,13.521,6.787,-0.061]

def dot_layer():
    inner, nw, nh = load("dot")
    inner = namespace(inner, "dot")
    L, T = 220.84, 137.49
    n = len(DOT_X)
    vals = ";".join(f"{DOT_X[i]:.3f} {DOT_Y[i]:.3f}" for i in range(n))
    kt = ";".join(f"{i/(n-1):.4f}" for i in range(n))
    move = (f'<animateTransform attributeName="transform" type="translate" '
            f'values="{vals}" keyTimes="{kt}" dur="{DOT_DUR}" repeatCount="indefinite" '
            f'calcMode="linear" additive="sum"/>')
    # 淡出时机按"圆点是否真被地球盘挡住"计算（球心≈(274.8,144.8) r≈37.8，轨迹点全局=(224.3+x,141+y)）：
    # 上弧 index0~4 在球盘左外侧→可见；index5~10.9 进入球盘且在背面→隐藏；index11 从右缘钻出→可见；
    # 下弧全程在地球前面→可见。即只在 t≈0.18~0.43 隐藏，其余时间都可见。
    fade = (f'<animate attributeName="opacity" values="1;1;0;0;1;1" '
            f'keyTimes="0;0.17;0.21;0.43;0.47;1" dur="{DOT_DUR}" repeatCount="indefinite"/>')
    nested = (f'<svg x="{L:.3f}" y="{T:.3f}" width="{nw:.3f}" height="{nh:.3f}" '
              f'viewBox="0 0 {nw} {nh}" overflow="visible" fill="none">{inner}</svg>')
    return f'<g id="hero-dot">{move}{fade}{nested}</g>'

parts = [f'<rect width="375" height="300" fill="#26BEC9"/>']
for spec in LAYERS[:9]:               # blob..subtract
    parts.append(place(*spec))
parts.append(dot_layer())             # dot（在 subtract 之后、signal 之前）
for spec in LAYERS[9:]:               # signal..star3
    parts.append(place(*spec))

# 底部两层渐变：先淡入 cyan，再淡入页面底色 #F1F4F8，让下方卡片自然衔接
parts.append('<rect x="0" y="72.309" width="375" height="227.691" fill="url(#heroCyanFade)"/>')
parts.append('<rect x="0" y="140" width="375" height="160" fill="url(#heroPageFade)"/>')

defs = ('<defs>'
        '<linearGradient id="heroCyanFade" x1="0" y1="0" x2="0" y2="1">'
        '<stop offset="0" stop-color="#26BEC9" stop-opacity="0"/>'
        '<stop offset="1" stop-color="#26BEC9"/></linearGradient>'
        '<linearGradient id="heroPageFade" x1="0" y1="0" x2="0" y2="1">'
        '<stop offset="0" stop-color="#F1F4F8" stop-opacity="0"/>'
        '<stop offset="1" stop-color="#F1F4F8"/></linearGradient>'
        '</defs>')

svg = (f'<svg class="hero-svg" viewBox="0 {STATUS_CROP} 375 {300 - STATUS_CROP}" width="100%" '
       'preserveAspectRatio="xMidYMid meet" xmlns="http://www.w3.org/2000/svg" '
       'style="display:block" aria-hidden="true">'
       + defs + "".join(parts) + '</svg>')

(HERO / "hero-scene.svg").write_text(svg, encoding="utf-8")
print(f"hero-scene.svg 生成完成 ({len(svg):,} 字符)")
