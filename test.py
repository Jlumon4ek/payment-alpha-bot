nums = [1,2,3,1]


counts = {}

for i in nums:
    if counts.get(f'{i}'): counts[f'{i}'] += 1
    else:
        counts[f"{i}"] = 1

for i in counts.values:
    if i > 1:
        print(False)

    else:
        print(True)