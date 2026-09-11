#!/usr/bin/env python3
"""
GT30L32S4W 字库读取参考实现 (gtfont.py)
===================================================================
输入 FONT_CONFIGS 中的字体名 + 单个字符(ASCII 或 GB2312 汉字)，
输出该字符的「字形单色位图」：有笔画的像素 = 白(255)，背景 = 黑(0)。

设计目的：为把字库读取逻辑移植到其他语言(C/C++/Rust/Go...)提供可逐行
对照的参考，因此「寻址」与「变宽」两层刻意写成语言无关的纯计算，
并在注释中标注与 gt.c(Ghidra 逆向伪代码)的对应关系。

约定与 gt.c 的对应：
  FONT_CONFIGS 中的每一项对应一个已切分好的 extracted_fonts/<key>.bin
  (由 test_fonts.py 的 split_flash_image 产生)。
  - type = "ascii"      -> ASCII_GetData 的 case 1~6 (等宽)
  - type = "ascii_prop" -> ASCII_GetData 的 case 7~14 (变宽: 2B 宽头 + 位图)
  - type = "gb"         -> gt_12/16/24/32_GetData
  - type = "gb_ext"     -> GB_EXT_612/816/1224/1632
  - type = "gb_spec"    -> GB_SPEC_816
位序: 每行按容器宽取 ceil(container_w/8) 字节、高位(MSB)在前，
与已通过的 render_dots 渲染方向完全一致。

用法示例:
  python gtfont.py ASCII_8X16 'A'                 # 打印 0/1 像素矩阵
  python gtfont.py ASCII_8X16 'A' -o a.png        # 导出单色 PNG
  python gtfont.py GT_16 '啊' -o a.png            # GB2312 汉字
  python gtfont.py ASCII_32_A 'W' -o w.png        # 变宽字形(自动读 2B 宽头)
  python gtfont.py GB_EXT_816 --code 0xABA1       # 扩展区: GB 码整数
"""
import os
import sys
import argparse
from dataclasses import dataclass

# ---------------------------------------------------------------------------
# 字体配置表 (与 test_fonts.py 中验证过的 FONT_CONFIGS 保持一致)
#   base   : 该字体在原始 GT30L32S4W.bin 中的起始偏移(仅信息用)
#   stride : 每个字符槽位占用字节数
#   w, h   : 位图容器宽度/高度(像素)；变宽字 w 为容器宽，真实宽看记录头
#   count  : 槽位总数
#   type   : 解码类型
# ---------------------------------------------------------------------------
FONT_CONFIGS = {
    # ------------------ 标准 GB2312 汉字库 (区位码) ------------------
    "GT_12":          {"base": 0x0,      "stride": 24,  "w": 12, "h": 12, "count": 7614, "type": "gb"},
    "GT_16":          {"base": 0x2C9D0,  "stride": 32,  "w": 16, "h": 16, "count": 7614, "type": "gb"},
    "GT_24":          {"base": 0x68190,  "stride": 72,  "w": 24, "h": 24, "count": 7614, "type": "gb"},
    "GT_32":          {"base": 0xEDF00,  "stride": 128, "w": 32, "h": 32, "count": 7614, "type": "gb"},

    # ------------------ 等宽 ASCII 字库 (ASCII_GetData case 1~6) ------------------
    "ASCII_5X7":       {"base": 0x1DDF80, "stride": 8,   "w": 5,  "h": 7,  "count": 96, "type": "ascii"},
    "ASCII_7X8":       {"base": 0x1DE280, "stride": 8,   "w": 7,  "h": 8,  "count": 96, "type": "ascii"},
    "ASCII_6X12":      {"base": 0x1DBE00, "stride": 12,  "w": 6,  "h": 12, "count": 96, "type": "ascii"},
    "ASCII_8X16":      {"base": 0x1DD780, "stride": 16,  "w": 8,  "h": 16, "count": 96, "type": "ascii"},
    "ASCII_12X24":     {"base": 0x1DFF00, "stride": 48,  "w": 12, "h": 24, "count": 96, "type": "ascii"},
    "ASCII_16X32":     {"base": 0x1E5A50, "stride": 64,  "w": 16, "h": 32, "count": 96, "type": "ascii"},

    # ------------------ 变宽 ASCII 字库 (ASCII_GetData case 7~14) ------------------
    # 每条记录 = BYTE0~1 真实像素宽(大端) + 位图(容器 w × h), 故 stride 比位图多 2B
    "ASCII_12_A":      {"base": 0x1DC400, "stride": 26,  "w": 12, "h": 12, "count": 96, "type": "ascii_prop"},
    "ASCII_12_T":      {"base": 0x1DCDC0, "stride": 26,  "w": 12, "h": 12, "count": 96, "type": "ascii_prop"},
    "ASCII_16_A":      {"base": 0x1DE580, "stride": 34,  "w": 16, "h": 16, "count": 96, "type": "ascii_prop"},
    "ASCII_16_T":      {"base": 0x1DF240, "stride": 34,  "w": 16, "h": 16, "count": 96, "type": "ascii_prop"},
    "ASCII_24_A":      {"base": 0x1E22D0, "stride": 74,  "w": 24, "h": 24, "count": 96, "type": "ascii_prop"},
    "ASCII_24_T":      {"base": 0x1E3E90, "stride": 74,  "w": 24, "h": 24, "count": 96, "type": "ascii_prop"},
    "ASCII_32_A":      {"base": 0x1E99D0, "stride": 130, "w": 32, "h": 32, "count": 96, "type": "ascii_prop"},
    "ASCII_32_T":      {"base": 0x1ECA90, "stride": 130, "w": 32, "h": 32, "count": 96, "type": "ascii_prop"},

    # ------------------ GB 图形扩展字符 (GB_EXT_*) ------------------
    # 码区 0xAAA1..0xAAFE => 槽 0..93; 0xAAFF 空槽; 0xABA1..0xABC0 => 槽 95..126
    "GB_EXT_6x12":     {"base": 0x1DBE0C, "stride": 12,  "w": 6,  "h": 12, "count": 127, "type": "gb_ext"},
    "GB_EXT_8x16":     {"base": 0x1DD790, "stride": 16,  "w": 8,  "h": 16, "count": 127, "type": "gb_ext"},
    "GB_EXT_12x24":    {"base": 0x1DFF30, "stride": 48,  "w": 12, "h": 24, "count": 127, "type": "gb_ext"},
    "GB_EXT_16x32":    {"base": 0x1E5A90, "stride": 64,  "w": 16, "h": 32, "count": 127, "type": "gb_ext"},

    # ------------------ GB 特殊扩展图形 (GB_SPEC_816: 0xACA1..0xACDF) ------------------
    "GB_SPEC_816":     {"base": 0x1F2880, "stride": 16,  "w": 8,  "h": 16, "count": 63,  "type": "gb_spec"},
}


# ===========================================================================
# 第一层: 字符/码点 -> 槽位索引 (寻址逻辑, 移植时重点)
# ===========================================================================
def char_to_slot(font_key, ch):
    """把『单个字符』换算为该字体 bin 文件中的槽位索引 slot_index。

    入参 ch 的约定：
      - ascii / ascii_prop : 1 个 ASCII 字符或 0x20..0x7E 的整数码
      - gb                 : 1 个 GB2312 汉字(或可编码字符)；也可传 (区, 位) 二元组
      - gb_ext / gb_spec   : 整数 GB 码 (0xAAA1/0xABA1/0xACA1...)，这些码不在标准编码集中
    返回 0..count-1 的槽位号。
    """
    try:
        cfg = FONT_CONFIGS[font_key]
    except KeyError:
        raise ValueError(f"未知字体名: {font_key!r}, 可选: {list(FONT_CONFIGS)}")

    ftype = cfg["type"]

    # ---- ascii / ascii_prop: 对应 gt.c ASCII_GetData case1~14 ----
    # 所有 ASCII 字库都是 (code - 0x20) 线性索引; case7~14 的记录里多一个 2B 宽头,
    # 但那不影响『槽位』计算, 宽头在第二层切数据时处理。
    if ftype in ("ascii", "ascii_prop"):
        code = ord(ch) if isinstance(ch, str) else int(ch)
        if not (0x20 <= code <= 0x7E):
            raise ValueError(f"{font_key}: ASCII 字符码须在 0x20..0x7E, 收到 0x{code:X}")
        return code - 0x20

    # ---- gb: 对应 gt.c gt_12/16/24/32_GetData ----
    # 区/位线性索引两分支, 符号区(A1..A9)与汉字区(B0..F7)无缝衔接(idx 0..7613)。
    if ftype == "gb":
        if isinstance(ch, str):
            raw = ch.encode("gb2312")
            if len(raw) != 2:
                raise ValueError(f"{font_key}: GB2312 需单字符(双字节), 收到 {ch!r}")
            msb, lsb = raw[0], raw[1]
        else:
            msb, lsb = int(ch[0]), int(ch[1])
        if 0xA1 <= msb <= 0xA9 and lsb >= 0xA1:               # gt.c 分支1 (符号区)
            return (lsb - 0xA1) + (msb - 0xA1) * 0x5E
        if 0xAF < msb < 0xF8 and lsb > 0xA0:                  # gt.c 分支2 (汉字区)
            return lsb + (msb - 0xB0) * 0x5E + 0x2AD
        raise ValueError(f"{font_key}: 无效 GB2312 区/位 ({msb:02X},{lsb:02X})")

    # ---- gb_ext: 对应 gt.c GB_EXT_612/816/1224/1632 ----
    # 两段码区共享同一张槽位表, 0xAAFF 空槽(槽94), 第二区 0xABA1..0xABC0 从槽95开始。
    if ftype == "gb_ext":
        code = int(ch)
        if 0xAAA1 <= code <= 0xAAFE:
            return code - 0xAAA1
        if 0xABA1 <= code <= 0xABC0:
            return code - 0xAB42                      # 0xABA1 -> 槽 95
        raise ValueError(f"{font_key}: GB 码须在 0xAAA1..0xAAFE 或 0xABA1..0xABC0, 收到 0x{code:X}")

    # ---- gb_spec: 对应 gt.c GB_SPEC_816 ----
    if ftype == "gb_spec":
        code = int(ch)
        if not (0xACA1 <= code <= 0xACDF):
            raise ValueError(f"{font_key}: GB 码须在 0xACA1..0xACDF, 收到 0x{code:X}")
        return code - 0xACA1

    raise ValueError(f"{font_key}: 未知字体类型 {ftype!r}")


# ===========================================================================
# 第二层: 槽位索引 + 原始记录 -> Glyph (数据切片 + 变宽处理)
# ===========================================================================
@dataclass
class Glyph:
    """一个字符的字形结果。

    bitmap      : 纯位图字节(变宽字已去掉记录头 2B)
    real_w      : 实际绘制宽度(像素)。变宽字来自记录头, 等宽字 = 容器宽 w
    container_w : 位图容器宽(像素), 决定每行 ceil(container_w/8) 字节
    height      : 位图高度(行数 = 字节行数)
    """
    font_key: str
    ftype: str
    slot_index: int
    code: object
    bitmap: bytes
    real_w: int
    container_w: int
    height: int

    @property
    def bytes_per_row(self):
        return (self.container_w + 7) // 8

    def rows(self):
        """返回 height 行 × real_w 列的 0/1 像素矩阵(逐行从左到右、高位在前)。"""
        bpr = self.bytes_per_row
        out = []
        for y in range(self.height):
            row = self.bitmap[y * bpr:(y + 1) * bpr]
            val = 0
            for b in row:
                val = (val << 8) | b
            total_bits = len(row) * 8
            out.append([1 if (val & (1 << (total_bits - 1 - x))) else 0
                        for x in range(self.real_w)])
        return out

    def save_png(self, path, scale=1):
        """导出单色 PNG：有笔画 = 白(255)，背景 = 黑(0)。需要 Pillow。"""
        try:
            from PIL import Image
        except ImportError:
            raise RuntimeError("导出 PNG 需要 Pillow, 请先 pip install Pillow")
        mat = self.rows()
        w, h = self.real_w, self.height
        img = Image.new("L", (w, h), 0)
        px = img.load()
        for y, row in enumerate(mat):
            for x, v in enumerate(row):
                px[x, y] = 255 if v else 0
        if scale > 1:
            img = img.resize((w * scale, h * scale), Image.NEAREST)
        img.save(path)


def load_glyph(font_key, ch, extract_dir="extracted_fonts"):
    """读取 extracted_fonts/<font_key>.bin 中字符 ch 的字形。

    返回 Glyph。若文件缺失/越界会给出带原因的异常。
    """
    cfg = FONT_CONFIGS[font_key]
    slot = char_to_slot(font_key, ch)

    path = os.path.join(extract_dir, f"{font_key}.bin")
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"缺少字体文件 {path} —— 请先用 test_fonts.py 执行切分(split_flash_image)")
    with open(path, "rb") as f:
        data = f.read()

    stride = cfg["stride"]
    offset = slot * stride
    if offset + stride > len(data):
        raise ValueError(f"{font_key}: 槽 {slot} 越界 (offset=0x{offset:X}, file={len(data)}B)")

    record = data[offset:offset + stride]
    ftype = cfg["type"]

    # ---- 变宽 ASCII (case7~14): 记录 = 2B 真实像素宽(大端) + 位图 ----
    if ftype == "ascii_prop":
        real_w = (record[0] << 8) | record[1]
        if real_w == 0 or real_w > cfg["w"]:          # 容错: 与 test_fonts 一致
            real_w = cfg["w"]
        bitmap = record[2:stride]
        return Glyph(font_key, ftype, slot, ch, bytes(bitmap),
                     real_w, cfg["w"], cfg["h"])

    # ---- 其余类型: 整条记录即纯位图, 实际宽 = 容器宽 ----
    return Glyph(font_key, ftype, slot, ch, bytes(record),
                 cfg["w"], cfg["w"], cfg["h"])


# ===========================================================================
# CLI 入口
# ===========================================================================
def _parse_args(argv):
    p = argparse.ArgumentParser(
        prog="gtfont",
        description="GT30L32S4W 字形读取参考实现: 字体名 + 字符 -> 单色位图",
        epilog="示例: python gtfont.py GT_16 啊 -o out.png ; "
               "python gtfont.py GB_EXT_8x16 --code 0xABA1")
    p.add_argument("font_key", help="FONT_CONFIGS 中的字体名, 如 GT_16 / ASCII_8X16")
    p.add_argument("char", nargs="?", default=None,
                   help="单个字符(ASCII 或 GB2312 汉字); 对 gb_ext/gb_spec 用 --code")
    p.add_argument("--code", type=lambda s: int(s, 0), default=None,
                   help="GB 码整数(十六进制 0x...), 用于 gb_ext/gb_spec")
    p.add_argument("-o", "--out", default=None, help="输出 PNG 路径(省略则只打印矩阵)")
    p.add_argument("--scale", type=int, default=1, help="PNG 放大倍数(默认1)")
    p.add_argument("--text", action="store_true",
                   help="用方块字符打印字形(替代 0/1)")
    return p.parse_args(argv)


def main(argv=None):
    args = _parse_args(argv)
    ch = args.char if args.char is not None else args.code
    if ch is None:
        raise SystemExit("请提供字符(位置参数)或 --code 十六进制 GB 码")

    glyph = load_glyph(args.font_key, ch)
    print(f"font     = {glyph.font_key} (type={glyph.ftype}, slot={glyph.slot_index})")
    print(f"char     = {ch!r}   real_w={glyph.real_w}  "
          f"container={glyph.container_w}x{glyph.height}  bitmap={len(glyph.bitmap)}B")

    if args.text:
        for row in glyph.rows():
            print("".join("██" if v else "  " for v in row))
    else:
        for row in glyph.rows():
            print("".join(str(v) for v in row))

    if args.out:
        glyph.save_png(args.out, scale=args.scale)
        print(f"[OK] 已导出单色位图: {args.out}")


if __name__ == "__main__":
    main()



