

def suffix(d):
    return 'th' if 11<=d<=13 else {1:'st',2:'nd',3:'rd'}.get(d%10, 'th')


def suffix_strftime(fst, t):
    """adds {S} format specifier to get day with suffix, e.g. 31st"""
    return t.strftime(fst).replace('{S}', str(t.day) + suffix(t.day))
