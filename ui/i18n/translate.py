import json
import sys
from googletrans import Translator

infile = "chinese.json"
outfile = "out.json"

if len(sys.argv) >= 2:
    infile = sys.argv[1]
if len(sys.argv) >= 3:
    outfile = sys.argv[2]

print(f"reading from {infile}")

with open(infile) as f:
    data = f.read()
jsonData = json.loads(data)

print(f"will write to {outfile}")

translator = Translator()

def getTranslation(s, src="en", dest="zh-cn"):
    """get the translation of s as a string

    :s: the string in source language
    :src: the source language
    :dest: the destination language
    :returns: the string in destination language

    """
    result = translator.translate(s, src=src, dest=dest).text
    print(f"Translating {s} into {result}")
    return result

def getEn2ZhTranslation(s):
    if not all(ord(char) < 128 for char in s):
        return s
    if translator.detect(s).lang.upper() == dest.upper():
        return s
    return getTranslation(s, "en", "zh-cn")


def walkThrough(target, func):
    if isinstance(target, str):
        result = func(target)
        return result
    elif isinstance(target, list):
        return [ walkThrough(item, func) for item in target ]
    elif isinstance(target, dict):
        return { key:walkThrough(item, func) for key,item in target.items() }
    else:
        raise Exception(f"Invalid target type in json: {target} of class {type(target)}")

outJsonData = walkThrough(jsonData, getEn2ZhTranslation)
outData = json.dumps(outJsonData, indent=2)

with open(outfile, "w") as f:
    f.write(outData)
