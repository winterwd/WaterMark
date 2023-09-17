#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import os
import sys

from PIL import Image
from PIL import ImageDraw
from PIL import ImageEnhance
from PIL import ImageFont
from PIL import ImageOps
from PIL import ImageChops


def crop_image(im):
    """裁剪图片边缘空白"""

    bg = Image.new(mode="RGBA", size=im.size)
    diff = ImageChops.difference(im, bg)
    del bg
    bbox = diff.getbbox()
    if bbox:
        return im.crop(bbox)
    return im


def text2img(text, font_color, font_size=25):
    """生成内容为 TEXT 的水印"""

    font = ImageFont.truetype("PingFang.ttc", font_size)
    # font = ImageFont.load_default()
    # 多行文字处理
    text = text.split("\n")
    mark_width = 0
    height = 0
    for i in range(len(text)):
        (a, b, w, h) = font.getbbox(text[i])
        height = h
        if mark_width < w:
            mark_width = w
    mark_height = height * len(text)

    # 生成水印图片
    mark = Image.new("RGBA", (mark_width, mark_height))
    draw = ImageDraw.ImageDraw(mark, "RGBA")
    draw.font = font
    for i in range(len(text)):
        (a, b, w, h) = font.getbbox(text[i])
        draw.text((0, i * h), text[i], fill=font_color)
    return mark


def set_opacity(im, opacity):
    """设置透明度"""

    assert 0 <= opacity < 1
    if im.mode != "RGBA":
        im = im.convert("RGBA")
    else:
        im = im.copy()
    alpha = im.split()[3]
    alpha = ImageEnhance.Brightness(alpha).enhance(opacity)
    im.putalpha(alpha)
    return im


def watermark(im, mark, position, opacity=1.0):
    """添加水印"""

    try:
        if opacity < 1:
            mark = set_opacity(mark, opacity)
        if im.mode != "RGBA":
            im = im.convert("RGBA")
        if im.size[0] < mark.size[0] or im.size[1] < mark.size[1]:
            print("The mark image size is larger size than original image file.")
            return False

        # 设置水印位置
        if position == "left_top":
            x = 0
            y = 0
        elif position == "left_bottom":
            x = 0
            y = im.size[1] - mark.size[1]
        elif position == "right_top":
            x = im.size[0] - mark.size[0]
            y = 0
        elif position == "right_bottom":
            x = im.size[0] - mark.size[0]
            y = im.size[1] - mark.size[1]
        elif position == "center_bottom":
            x = (im.size[0] - mark.size[0]) / 2
            y = im.size[1] - mark.size[1]
        else:
            x = (im.size[0] - mark.size[0]) / 2
            y = (im.size[1] - mark.size[1]) / 2

        layer = Image.new("RGBA", im.size)
        layer.paste(mark, (int(x), int(y)))
        return Image.composite(layer, im, layer)
    except Exception as e:
        print("Sorry, Exception: " + str(e))
        return False


def add_mark(image_file, args, output):
    im = Image.open(image_file)
    im = ImageOps.exif_transpose(im)
    mark = text2img(args.text, args.color)
    mark = crop_image(mark)
    image = watermark(im, mark, args.position, args.opacity)
    if image:
        name = os.path.basename(image_file)
        if not os.path.exists(output):
            os.mkdir(output)

        new_name = os.path.join(output, name)
        if os.path.splitext(new_name)[1] != ".png":
            image = image.convert("RGB")
        image.save(new_name)

        if args.show:
            image.show()

        print(
            "Success add `"
            + args.text
            + "` on "
            + image_file
            + " to "
            + os.path.abspath(new_name)
        )
    else:
        print("Sorry, Failed.")


def is_image_file(file_path):
    # 常见的图片文件扩展名
    image_extensions = [".jpg", ".jpeg", ".png"]

    # 获取文件扩展名（不包括点）
    file_extension = os.path.splitext(file_path)[1].lower()

    # 检查文件扩展名是否是图片扩展名之一
    if file_extension in image_extensions:
        return True
    else:
        return False


def get_all_file_paths(directory):
    file_paths = []
    # 遍历目录及其子目录下的文件
    for root, directories, files in os.walk(directory):
        for filename in files:
            # 构建文件的完整路径
            file_path = os.path.join(root, filename)
            file_paths.append(file_path)  # 将文件路径添加到列表中

    return file_paths


def main():
    parse = argparse.ArgumentParser()
    parse.add_argument("-f", "--file", required=True, help="image path or directory")
    parse.add_argument("-t", "--text", required=True, type=str, help="water mart text")
    parse.add_argument(
        "-o",
        "--out",
        default="./",
        required=False,
        help="image output directory, default is current directory",
    )
    parse.add_argument(
        "-c", "--color", default="red", type=str, help="text color, red、blue and so on"
    )
    parse.add_argument("-s", "--size", default=20, type=float, help="text size")
    parse.add_argument(
        "-p",
        "--position",
        default="right_bottom",
        help="text position, center,left_top,left_bottom,right_top,right_bottom,center_bottom,"
        "default is right_bottom",
    )
    parse.add_argument(
        "--opacity", default=0.5, type=float, help="watermark opacity, default is 0.5"
    )
    parse.add_argument("--show", help="need show watermark image", action="store_true")

    args = parse.parse_args()
    print(args)

    if isinstance(args.text, str) and sys.version_info[0] < 3:
        args.text = args.text.decode("utf-8")

    if os.path.isdir(args.file):
        file_paths = get_all_file_paths(args.file)
        for image_file in file_paths:
            if is_image_file(image_file):
                out = os.path.join(args.out, image_file.split(args.file)[-1])
                out = os.path.dirname(out)
                add_mark(image_file, args, out)
    else:
        if is_image_file(args.file):
            add_mark(args.file, args, args.out)
        else:
            print("Sorry, " + args.file + " is not a image file.")


if __name__ == "__main__":
    main()
