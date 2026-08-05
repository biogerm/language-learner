import re

def is_inside_target(idx, intervals):
    for start, end in intervals:
        if start < idx < end:
            return True
    return False

text = '"–Hej! Det var länge sedan!" sa jag'
intervals = [(1, 27)] # –Hej! Det var länge sedan!

boundaries = [0]
for match in re.finditer(r'[.!?]”?"?\s+(?=["”A-ZÅÄÖ])', text):
    idx = match.end()
    print(f"Match found ending at {idx}, inside? {is_inside_target(idx, intervals)}")
    if not is_inside_target(idx, intervals):
        boundaries.append(idx)
print(boundaries)
