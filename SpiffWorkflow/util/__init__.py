

def merge_dictionary(dst, src, extend_lists=False):
    """Recursive merge two dicts (vs .update which overwrites the hashes at the
    root level)

    Note: This updates dst.
    Copied from checkmate.utils
    """
    stack = [(dst, src)]
    while stack:
        current_dst, current_src = stack.pop()
        for key in current_src:
            source = current_src[key]
            if key not in current_dst:
                current_dst[key] = source
            else:
                dest = current_dst[key]
                if isinstance(source, dict) and isinstance(dest, dict):
                    stack.append((dest, source))
                elif isinstance(source, list) and isinstance(dest, list):
                    if not extend_lists:
                        # Make them the same size
                        r = dest[:]
                        s = source[:]
                        if len(dest) > len(source):
                            s.extend([None for i in range(len(dest) -
                                    len(source))])
                        elif len(dest) < len(source):
                            r.extend([None for i in range(len(source) -
                                    len(dest))])
                        # Merge lists
                        for index, value in enumerate(r):
                            if (not value) and s[index]:
                                r[index] = s[index]
                            elif isinstance(value, dict) and \
                                    isinstance(s[index], dict):
                                stack.append((dest[index], source[index]))
                            else:
                                dest[index] = s[index]
                        current_dst[key] = r
                    else:
                        dest.extend([s for s in source if s not in dest])
                else:
                    current_dst[key] = source
    return dst
