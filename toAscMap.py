#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ASCII 字体总图生成器 (16x16 槽位网格)
===================================================================
根据 gtfont.py 读取 GT30L32S4W 中的 ASCII 字体，按 ASCII 码 (0~255)
直接映射到 16 行 x 16 列的网格中，并导出正方形 PNG 渲染图。
"""

import sys
import os
from PIL import Image, ImageOps
import gtfont  # 导入同目录下的 gtfont.py


def get_ascii_fonts():
    """获取 FONT_CONFIGS 中所有 ASCII 类型的字体配置"""
    return {
        k: v for k, v in gtfont.FONT_CONFIGS.items()
        if v["type"] in ("ascii", "ascii_prop")
    }


def render_ascii_grid(font_key, out_path=None, invert=False): # scale=1
    """根据字体 key 生成 16x16 槽位的 ASCII 字体总图"""
    cfg = gtfont.FONT_CONFIGS[font_key]
    
    # 所有槽位边长取字体的高度对应的尺寸 H
    h = cfg["h"]
    cell_size = h
    grid_cols, grid_rows = 16, 16

    # 正方形总画布尺寸: (16*H) x (16*H)
    img_w = cell_size * grid_cols
    img_h = cell_size * grid_rows
    
    # 创建 L 模式单色图像，默认背景为黑 (0)
    img = Image.new("L", (img_w, img_h), 0)
    px = img.load()

    rendered_count = 0
    # 遍历 16x16 = 256 个槽位，ASCII 码直接等于 idx (0 ~ 255)
    for idx in range(256):
        row = idx // grid_cols
        col = idx % grid_cols
        code = idx

        # 仅 0x20 ~ 0x7E 包含可打印 ASCII 字形
        if 0x20 <= code <= 0x7E:
            try:
                glyph = gtfont.load_glyph(font_key, code)
            except Exception as e:
                print(f"[警告] 读取字符 0x{code:02X} 失败: {e}")
                continue

            # 槽位左上角绝对坐标
            cell_x = col * cell_size
            cell_y = row * cell_size

            # 对齐方式：水平左对齐 (off_x = 0)，垂直居中对齐
            off_x = cell_x + 0
            off_y = cell_y + (cell_size - glyph.height) // 2

            matrix = glyph.rows()
            for y, row_data in enumerate(matrix):
                for x, val in enumerate(row_data):
                    if val:
                        px[off_x + x, off_y + y] = 255
            rendered_count += 1

    # 【功能已注释】最近邻放大，避免模糊
    # if scale > 1:
    #     img = img.resize((img_w * scale, img_h * scale), Image.NEAREST)

    # 如果用户选择反色，则将黑底白字转为白底黑字
    if invert:
        img = ImageOps.invert(img)

    save_path = out_path or f"{font_key}_grid.png"
    img.save(save_path)
    print(f"[OK] 成功生成 {font_key} 字体总图:")
    print(f"     - 输出文件: {save_path}")
    print(f"     - 图像尺寸: {img_w} x {img_h} 像素")
    print(f"     - 颜色模式: {'反色 (白底黑字)' if invert else '默认 (黑底白字)'}")
    print(f"     - 绘制字符: {rendered_count} 个 (ASCII 0x20..0x7E)")


def main():
    ascii_fonts = get_ascii_fonts()
    font_keys = list(ascii_fonts.keys())

    if not font_keys:
        print("[错误] 未在 FONT_CONFIGS 中找到任何 ASCII 字体！")
        sys.exit(1)

    print("==========================================")
    print("      GT30L32S4W ASCII 字体总图生成器       ")
    print("==========================================")
    print("请选择要生成的 ASCII 字体编号：\n")
    
    for idx, key in enumerate(font_keys, 1):
        info = ascii_fonts[key]
        print(f"  [{idx:2d}] {key:<12} (尺寸: {info['w']}x{info['h']}px, 类型: {info['type']})")
    
    print("\n  [ 0] 生成所有 ASCII 字体")
    print("------------------------------------------")

    try:
        choice_str = input(f"请输入选择 (0-{len(font_keys)}): ").strip()
        if not choice_str:
            print("未输入选择，程序退出。")
            return
        
        choice = int(choice_str)
        if choice < 0 or choice > len(font_keys):
            print("[错误] 输入的序号超出范围！")
            return
    except ValueError:
        print("[错误] 请输入有效的数字序号！")
        return

    # 【功能已注释】获取放大倍数
    # scale_str = input("请输入图像放大倍数 scale (默认 1): ").strip()
    # scale = int(scale_str) if scale_str.isdigit() and int(scale_str) > 0 else 1

    # 询问是否需要反色
    invert_str = input("是否需要对生成的图像进行反色处理 (白底黑字)？(y/N): ").strip().lower()
    invert = invert_str in ("y", "yes")

    print("\n开始渲染...")
    if choice == 0:
        for key in font_keys:
            render_ascii_grid(key, invert=invert)
    else:
        selected_key = font_keys[choice - 1]
        render_ascii_grid(selected_key, invert=invert)


if __name__ == "__main__":
    main()