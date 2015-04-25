# -*- coding: utf-8 -*-
'''
Extra filters for Blog app.
'''

from django import template


register = template.Library()


def isCJKChar(c):
    x = ord (c)
    # Punct & Radicals
    if x >= 0x2e80 and x <= 0x33ff:
        return True

    # Fullwidth Latin Characters
    elif x >= 0xff00 and x <= 0xffef:
        return True

    # CJK Unified Ideographs &
    # CJK Unified Ideographs Extension A
    elif x >= 0x4e00 and x <= 0x9fbb:
        return True
    # CJK Compatibility Ideographs
    elif x >= 0xf900 and x <= 0xfad9:
        return True

    # CJK Unified Ideographs Extension B
    elif x >= 0x20000 and x <= 0x2a6d6:
        return True

    # CJK Compatibility Supplement
    elif x >= 0x2f800 and x <= 0x2fa1d:
        return True

    else:
        return False


@register.filter(name = 'cut')
def cut(text, length):
    '''
    Cut string with given length.
    '''
    length = int(length)
    if len(text) < length:
        return text
    else:
        widthcount = 0
        result = []
        for char in text:
            if isCJKChar(char):
                widthcount += 2
            else:
                widthcount += 1
            result.append(char)
            if widthcount >= length * 2:
                return ''.join(result)


