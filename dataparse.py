#codeing:utf-8
#python: 2.7.18

import os
import json
from plistlib import readPlist

def parse_plist_file(_filepath):
    # print("---parse plist file---- " + _filepath)
    _, name = os.path.split(_filepath)
    _, ext = os.path.splitext(name)
    if ext != ".plist":
        print("fail: not plist file >", _filepath)
        return
    try:
        data = readPlist(_filepath)
    except Exception:
        print("fail: read plist file failed >", _filepath)
        return
    return parse_plistdata(data)

def _mapping_list(_result, _name, _data):
    for i, v in enumerate(_name):
        if isinstance(v, list):
            _mapping_list(_result, v, _data[i])
        else:
            _result[v] = _data[i]

    return _result

def _parse_str(_name, _str):
    return _mapping_list({}, _name, json.loads(_str.replace("{", "[").replace("}", "]")))

def parse_plistdata(_data):
    if not _data.get("metadata"):
        return None

    fmt = _data.metadata.format
    if fmt not in (0, 1, 2, 3):
        print("fail: unsupport format" + str(fmt))
        return None
    
    data = {}
    frame_data_list = []
    for (name, config) in _data.frames.items():
        frame_data = {}
        if fmt == 0:
            source_size = {
                "w": config.get("originalWidth", 0),
                "h": config.get("originalHeight", 0),
            }
            rotated = False
            src_rect = (
                config.get("x", 0),
                config.get("y", 0),
                config.get("x", 0) + config.get("originalWidth", 0),
                config.get("y", 0) + config.get("originalHeight", 0),
            )
            offset = {
                "x": config.get("offsetX", False),
                "y": config.get("offsetY", False),
            }
        elif fmt == 1 or fmt == 2:
            frame = _parse_str([["x", "y"], ["w", "h"]], config.frame)
            center_offset = _parse_str(["x", "y"], config.offset)
            source_size = _parse_str(["w", "h"], config.sourceSize)
            rotated = config.get("rotated", False)
            src_rect = (
                frame["x"],
                frame["y"],
                frame["x"]+(frame["h"] if rotated else frame["w"]),
                frame["y"]+(frame["w"] if rotated else frame["h"])
            )
            offset = {
                "x": source_size["w"]/2 + center_offset["x"] - frame["w"]/2,
                "y": source_size["h"]/2 - center_offset["y"] - frame["h"]/2,
            }
        elif fmt == 3:
            frame = _parse_str([["x", "y"], ["w", "h"]], config.textureRect)
            center_offset = _parse_str(["x", "y"], config.spriteOffset)
            source_size = _parse_str(["w", "h"], config.spriteSourceSize)
            rotated = config.textureRotated
            src_rect = (
                frame["x"],
                frame["y"],
                frame["x"]+(frame["h"] if rotated else frame["w"]),
                frame["y"]+(frame["w"] if rotated else frame["h"])
            )
            offset = {
                "x": source_size["w"]/2 + center_offset["x"] - frame["w"]/2,
                "y": source_size["h"]/2 - center_offset["y"] - frame["h"]/2,
            }
        else:
            continue

        frame_data["name"] = name
        frame_data["source_size"] = (int(source_size["w"]), int(source_size["h"]))
        frame_data["rotated"] = rotated
        frame_data["src_rect"] = [int(x) for x in src_rect]
        frame_data["offset"] = (int(offset["x"]), int(offset["y"]))

        frame_data_list.append(frame_data)

    data["frames"] = frame_data_list
    data["texture"] = _data.metadata.textureFileName
    return data
