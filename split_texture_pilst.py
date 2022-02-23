#coding:utf-8
#python: 2.7.18

import sys
import os
import dataparse
from PIL import Image

def lstFilesByDir(_dir, _func=None, recursion=True):
    dirs = os.listdir(_dir)
    for item in dirs:
        fullPath = os.path.join(_dir, item)
        if os.path.isdir(fullPath):
            if recursion:
                lstFilesByDir(fullPath, _func, recursion)
        else:
            if _func:
                _func(fullPath)

def get_image_ext(image_file):
    return os.path.splitext(image_file)[1]

def split_texture_plist_2_pngs(data_file):
    fileName = os.path.basename(data_file)
    fileDir = os.path.dirname(data_file)
    arr = os.path.splitext(fileName)
    if len(arr) != 2:
        return
    if arr[1] == ".plist":
        # parse plist file
        data = dataparse.parse_plist_file(data_file)
        frame_data_list = data.get("frames")
        if not data or not frame_data_list:
            print("fail: unsupport plist file: " + data_file)
            return
        # check image file exists
        file_path, _ = os.path.split(data_file)
        texture_name = data["texture"]
        image_file = os.path.join(file_path, texture_name)
        image_ext = get_image_ext(image_file)
        if not os.path.exists(image_file):
            return
        # make output dir
        output_dir, _ = os.path.splitext(data_file)
        if not os.path.isdir(output_dir):
            if os.path.exists(os.path.dirname(output_dir)):
                os.mkdir(output_dir)
            else:
                os.makedirs(output_dir)
        # load image file
        try:
            src_image = Image.open(image_file)
        except Exception:
            print("fail: can't open image %s " % image_file)
            return
        for frame_data in frame_data_list:
            temp_image = src_image.crop(frame_data["src_rect"])
            if frame_data["rotated"]:
                temp_image = temp_image.rotate(90, expand=1)
            # create dst image
            mode = "RGBA" if (src_image.mode in ("RGBA", "LA") or (src_image.mode == "P" and 'transparency' in src_image.info)) else "RGB"
            dst_image = Image.new(mode, frame_data["source_size"], (0, 0, 0, 0))
            dst_image.paste(temp_image, frame_data["offset"], mask=0)
            output_path = os.path.join(output_dir, frame_data["name"])
            _, ext = os.path.splitext(output_path)
            if not ext:
                output_path = output_path + "." + image_ext
            if not os.path.exists(os.path.dirname(output_path)):
                os.makedirs(os.path.dirname(output_path))
            dst_image.save(output_path)


if __name__ == '__main__':
    cnt = len(sys.argv)
    if cnt == 2:
        print('python ' + sys.argv[0] + ' ' + sys.argv[1])
        lstFilesByDir(sys.argv[1], split_texture_plist_2_pngs)
    else:
        print('Need 1 argv: {0}'.format("folder name"))
