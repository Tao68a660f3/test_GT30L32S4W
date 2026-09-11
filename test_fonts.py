import os
import sys

BIN_FILE = "GT30L32S4W.bin"
EXTRACT_DIR = "extracted_fonts"

# 全量配置表 (包含 GB 汉字库、等宽 ASCII、变宽 ASCII、图形扩展及特殊图形)
# count: 该物理区实际占用的字符“槽位”数(含空槽)，split 时按 count*stride 切分。
# 槽位数依据 gt.c 逆向代码推算并经镜像实测验证:
#   - gb     : 区/位线性索引 0..7613  (符号区 846 槽 + 汉字区 6768 槽，共 7614)
#   - gb_ext : 两段码区连续排布，共 127 槽 (0xAAA1..0xAAFE => 0..93, 0xAAFF 空槽, 0xABA1..0xABC0 => 95..126)
#   - gb_spec: 0xACA1..0xACDF  => 0..62  (63 槽)
FONT_CONFIGS = {
    # ------------------ 标准 GB2312 汉字库 (区位码) ------------------
    "GT_12":          {"base": 0x0,      "stride": 24,  "w": 12, "h": 12, "count": 7614, "type": "gb"},
    "GT_16":          {"base": 0x2C9D0,  "stride": 32,  "w": 16, "h": 16, "count": 7614, "type": "gb"},
    "GT_24":          {"base": 0x68190,  "stride": 72,  "w": 24, "h": 24, "count": 7614, "type": "gb"},
    "GT_32":          {"base": 0xEDF00,  "stride": 128, "w": 32, "h": 32, "count": 7614, "type": "gb"},

    # ------------------ 等宽 ASCII 字库 (case 1~6: 0x20..0x7E) ------------------
    "ASCII_5X7":       {"base": 0x1DDF80, "stride": 8,   "w": 5,  "h": 7,  "count": 96, "type": "ascii"},
    "ASCII_7X8":       {"base": 0x1DE280, "stride": 8,   "w": 7,  "h": 8,  "count": 96, "type": "ascii"},
    "ASCII_6X12":      {"base": 0x1DBE00, "stride": 12,  "w": 6,  "h": 12, "count": 96, "type": "ascii"},
    "ASCII_8X16":      {"base": 0x1DD780, "stride": 16,  "w": 8,  "h": 16, "count": 96, "type": "ascii"},
    "ASCII_12X24":     {"base": 0x1DFF00, "stride": 48,  "w": 12, "h": 24, "count": 96, "type": "ascii"},
    "ASCII_16X32":     {"base": 0x1E5A50, "stride": 64,  "w": 16, "h": 32, "count": 96, "type": "ascii"},

    # ------------------ 不等宽/变宽 ASCII 字库 (case 7~14: 0x20..0x7E) ------------------
    # 12点变宽 (BYTE 0~1 Header + 24B 位图 = 26B 步长)
    "ASCII_12_A":      {"base": 0x1DC400, "stride": 26,  "w": 12, "h": 12, "count": 96, "type": "ascii_prop"},
    "ASCII_12_T":      {"base": 0x1DCDC0, "stride": 26,  "w": 12, "h": 12, "count": 96, "type": "ascii_prop"},

    # 16点变宽 (BYTE 0~1 Header + 32B 位图 = 34B 步长)
    "ASCII_16_A":      {"base": 0x1DE580, "stride": 34,  "w": 16, "h": 16, "count": 96, "type": "ascii_prop"},
    "ASCII_16_T":      {"base": 0x1DF240, "stride": 34,  "w": 16, "h": 16, "count": 96, "type": "ascii_prop"},

    # 24点变宽 (BYTE 0~1 Header + 72B 位图 = 74B 步长)
    "ASCII_24_A":      {"base": 0x1E22D0, "stride": 74,  "w": 24, "h": 24, "count": 96, "type": "ascii_prop"},
    "ASCII_24_T":      {"base": 0x1E3E90, "stride": 74,  "w": 24, "h": 24, "count": 96, "type": "ascii_prop"},

    # 32点变宽 (BYTE 0~1 Header + 128B 位图 = 130B 步长)
    "ASCII_32_A":      {"base": 0x1E99D0, "stride": 130, "w": 32, "h": 32, "count": 96, "type": "ascii_prop"},
    "ASCII_32_T":      {"base": 0x1ECA90, "stride": 130, "w": 32, "h": 32, "count": 96, "type": "ascii_prop"},

    # ------------------ 扩展图形字符 (0xAAA1..0xAAFE + 0xABA1..0xABC0) ------------------
    "GB_EXT_6x12":     {"base": 0x1DBE0C, "stride": 12,  "w": 6,  "h": 12, "count": 127, "type": "gb_ext"},
    "GB_EXT_8x16":     {"base": 0x1DD790, "stride": 16,  "w": 8,  "h": 16, "count": 127, "type": "gb_ext"},
    "GB_EXT_12x24":    {"base": 0x1DFF30, "stride": 48,  "w": 12, "h": 24, "count": 127, "type": "gb_ext"},
    "GB_EXT_16x32":    {"base": 0x1E5A90, "stride": 64,  "w": 16, "h": 32, "count": 127, "type": "gb_ext"},

    # ------------------ 特殊扩展图形 (GB_SPEC_816: 0xACA1..0xACDF) ------------------
    "GB_SPEC_816":     {"base": 0x1F2880, "stride": 16,  "w": 8,  "h": 16, "count": 63,  "type": "gb_spec"},
}

def split_flash_image(bin_path, out_dir):
    """从二进制镜像文件切分导出独立字库文件"""
    if not os.path.exists(bin_path):
        print(f"[!] 未找到镜像文件 {bin_path}")
        return

    os.makedirs(out_dir, exist_ok=True)
    with open(bin_path, "rb") as f:
        full_bytes = f.read()
    file_size = len(full_bytes)

    print(f"[*] 导出全量字库二进制文件到 [{out_dir}/]...")
    for name, cfg in FONT_CONFIGS.items():
        start = cfg["base"]
        # 按配置的真实槽位数切分 (gb 每档 7614 槽、gb_ext 127 槽、ASCII 96 槽...)
        length = cfg["count"] * cfg["stride"]
        if start >= file_size:
            print(f"  [X] 跳过 {name}: 起始地址 0x{start:X} 超出镜像 0x{file_size:X}")
            continue
        if start + length > file_size:
            length = file_size - start  # 只保留镜面内可用部分，避免越界
        sub_data = full_bytes[start : start + length]

        file_path = os.path.join(out_dir, f"{name}.bin")
        with open(file_path, "wb") as out_f:
            out_f.write(sub_data)
        print(f"  ├─ 导出 {name}.bin ({len(sub_data)} Bytes, 首地址 0x{start:X})")
    print("[OK] 镜像切分完毕！\n")

def render_dots(data, real_w, container_w, height, title=""):
    """
    通用横置横排点阵 ASCII 画布渲染器
    real_w: 字符真实绘制宽度 (用于截断右侧空白)
    container_w: 物理容器分配宽度 (16/24/32, 用于计算每行 Bytes 数)
    """
    if not data or container_w <= 0 or height <= 0:
        print(f"[{title}] 数据无效")
        return
    
    # 严格按照物理容器宽度计算每行的字节数！
    bytes_per_row = (container_w + 7) // 8
    
    # 容错：如果未传 real_w，默认显示全宽
    if real_w <= 0 or real_w > container_w:
        real_w = container_w

    print(f"┌─ {title} (实际宽: {real_w}px | 容器: {container_w}x{height}) " + "──" * max(0, 10 - len(title)) + "─┐")
    
    for y in range(height):
        row_str = "│"
        # 截取物理上这一行的完整字节
        row_bytes = data[y * bytes_per_row : (y + 1) * bytes_per_row]
        
        row_val = 0
        for b in row_bytes:
            row_val = (row_val << 8) | b
            
        # 容器每行的总 bit 数
        total_bits = len(row_bytes) * 8
        
        # 【关键】从最高位 (Bit 15/23/31) 开始扫描，但只渲染到 real_w 截止！
        for x in range(real_w):
            bit_idx = total_bits - 1 - x
            if row_val & (1 << bit_idx):
                row_str += "**"
            else:
                row_str += "  "
        row_str += "│"
        print(row_str)
    print(f"└─" + "──" * (real_w + 2) + "─┘")

def read_char_from_file(font_name, char_val):
    """根据类型从物理数据段提取点阵位图及真实宽度

    char_val 格式:
      - ascii / ascii_prop : str 或 int (0x20..0x7E)
      - gb                 : (区msb, 位lsb)
      - gb_ext / gb_spec   : int (GB 码)
    返回: (点阵数据 or None, 真实宽, 容器宽, 高)
    """
    cfg = FONT_CONFIGS.get(font_name)
    file_path = os.path.join(EXTRACT_DIR, f"{font_name}.bin")
    if not cfg or not os.path.exists(file_path):
        return None, 0, 0, 0

    with open(file_path, "rb") as f:
        bin_data = f.read()

    ftype = cfg["type"]
    stride = cfg["stride"]
    w, h = cfg["w"], cfg["h"]

    def slice_record(idx):
        """取出第 idx 个槽的整条记录 (含 2B width header, 若有)"""
        offset = idx * stride
        if offset < 0 or offset + stride > len(bin_data):
            return None
        return bin_data[offset : offset + stride]

    # 1. 等宽 ASCII (case 1~6)
    if ftype == "ascii":
        code = ord(char_val) if isinstance(char_val, str) else char_val
        if not (0x20 <= code <= 0x7E):
            return None, 0, 0, 0
        raw = slice_record(code - 0x20)
        if raw is None:
            return None, 0, 0, 0
        return raw, w, w, h

    # 2. 不等宽/变宽 ASCII (case 7~14: BYTE 0~1 Header + 位图)
    elif ftype == "ascii_prop":
        code = ord(char_val) if isinstance(char_val, str) else char_val
        if not (0x20 <= code <= 0x7E):
            return None, 0, 0, 0
        raw = slice_record(code - 0x20)
        if raw is None or len(raw) < 2:
            return None, 0, 0, 0

        # Header 大端 2B 记录真实像素宽 (实测 'A'=0x0008=8px, 空格=0x0003=3px)
        real_w = (raw[0] << 8) | raw[1]
        if real_w == 0 or real_w > w:
            real_w = w
        return raw[2:stride], real_w, w, h

    # 3. GB2312 中文字库 (gt_12/16/24/32_GetData)
    elif ftype == "gb":
        msb, lsb = char_val
        # 分支1: 区 A1..A9 (符号区)
        if 0xA1 <= msb <= 0xA9 and lsb >= 0xA1:
            idx = (lsb - 0xA1) + (msb - 0xA1) * 0x5E
        # 分支2: 区 B0..F7 (汉字区, 接续符号区后, 无缝衔接 idx=846 起)
        elif 0xAF < msb < 0xF8 and lsb > 0xA0:
            idx = lsb + (msb - 0xB0) * 0x5E + 0x2AD
        else:
            return None, 0, 0, 0
        raw = slice_record(idx)
        if raw is None:
            return None, 0, 0, 0
        return raw, w, w, h

    # 4. GB 图形扩展字符 (GB_EXT_612/816/1224/1632)
    elif ftype == "gb_ext":
        code = char_val
        if 0xAAA1 <= code <= 0xAAFE:          # 第一区 idx 0..93
            idx = code - 0xAAA1
        elif 0xABA1 <= code <= 0xABC0:        # 第二区接 0xAAFF 空槽之后, idx 95..126
            idx = code - 0xAB42
        else:
            return None, 0, 0, 0
        raw = slice_record(idx)
        if raw is None:
            return None, 0, 0, 0
        return raw, w, w, h

    # 5. GB 特殊扩展图形 (GB_SPEC_816)
    elif ftype == "gb_spec":
        code = char_val
        if not (0xACA1 <= code <= 0xACDF):
            return None, 0, 0, 0
        raw = slice_record(code - 0xACA1)
        if raw is None:
            return None, 0, 0, 0
        return raw, w, w, h

    return None, 0, 0, 0

def _fmt_char(char_val):
    """把测试字符格式化为可读字符串"""
    if isinstance(char_val, str):
        return f"'{char_val}'"
    if isinstance(char_val, tuple):
        try:
            return f"'{bytes(char_val).decode('gb2312')}' ({char_val[0]:02X}{char_val[1]:02X})"
        except Exception:
            return f"(区{char_val[0]:02X},位{char_val[1]:02X})"
    return f"0x{char_val:04X}"


def _check_dots(dots, need_bytes):
    """校验点阵数据可用: 非空且长度足够渲染"""
    return dots is not None and len(dots) >= need_bytes


if __name__ == "__main__":
    split_flash_image(BIN_FILE, EXTRACT_DIR)

    # 每个字体类型对应一组抽样字符, 覆盖: 区段首/中/尾、变宽真实宽、第二码区与特殊区
    SAMPLES = {
        "ascii":      [" ", "A", "0", "~", "g", "y"],                       # 0x20 / 首字母 / 数字 / 0x7E
        "ascii_prop": [" ", "A", "W", "~", "g", "y"],                       # 空格宽度≈3、字母宽字、最宽、尾字符
        "gb":         [(0xA1, 0xA1), (0xA3, 0xA1), (0xB0, 0xA1),  # 符号区首/全角字符/'啊'
                       (0xD6, 0xD0), (0xF7, 0xFE)],               # '中' / 汉字库末字
        "gb_ext":     [0xAAA1, 0xAAFE, 0xABA1, 0xABC0],           # 第一区首/尾、第二区首/尾
        "gb_spec":    [0xACA1, 0xACDF],                           # 特殊图形区首/尾
    }

    print("=" * 78)
    print(" 全字体抽取测试 (配置项数: {})".format(len(FONT_CONFIGS)))
    print("=" * 78)

    total_pass = 0
    total_fail = 0
    fail_list = []

    for font_name, cfg in FONT_CONFIGS.items():
        ftype = cfg["type"]
        container_w = cfg["w"]
        height = cfg["h"]
        bpr = (container_w + 7) // 8      # 每行字节数
        need = bpr * height

        for char_val in SAMPLES.get(ftype, []):
            dots, real_w, _, _ = read_char_from_file(font_name, char_val)
            ok = _check_dots(dots, need)
            mark = "PASS" if ok else "FAIL"
            if ok:
                total_pass += 1
            else:
                total_fail += 1
                fail_list.append(f"{font_name} | {_fmt_char(char_val)}")

            print(f"[{mark}] {font_name:12s} {_fmt_char(char_val):>12s}"
                  f"  实际宽={real_w:>2d}  容器={container_w}x{height}"
                  f"  位图={len(dots) if dots else 0}/{need}B")
            if ok:
                render_dots(dots, real_w, container_w, height,
                            title=f"{font_name} | {_fmt_char(char_val)}")
            print()

    print("=" * 78)
    print(f" 结果: PASS={total_pass}  FAIL={total_fail}")
    if fail_list:
        print(" 失败明细:")
        for item in fail_list:
            print(f"   [X] {item}")
        sys.exit(1)
    print(" [OK] 全部字体抽样测试通过！")
    print("=" * 78)