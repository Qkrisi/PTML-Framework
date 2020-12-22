def Any(l, predictate):
    for element in l:
        if predictate(l):return True
    return False