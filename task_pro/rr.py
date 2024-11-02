def get_index(s,d):
    for i in range(len(s)):
        if s[i] == d:
            return i
    return 'no '

print(get_index([1,2,4,5,6,7],5))