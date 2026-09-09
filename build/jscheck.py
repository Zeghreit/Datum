"""Structural check for the engine's JavaScript, without needing node.

A naive brace count lies: braces live inside strings, template literals,
regexes and comments too. This walks the source as a tiny state machine and
only counts delimiters that are actually code. It is not a parser and will not
catch every mistake — but it reliably catches the ones that have actually bitten
this project: a block pasted twice, a slice that cut a function in half, an
edit that left a string or template unterminated.
"""

# a '/' starts a regex when the previous meaningful token cannot end an
# expression; after an identifier, number or ')' it is division instead
_REGEX_OK_AFTER = set('(,=:[!&|?{};+-*%~^<>')
_REGEX_OK_WORDS = {'return', 'typeof', 'instanceof', 'in', 'of', 'new',
                   'delete', 'void', 'do', 'else', 'case', 'yield', 'await'}


def scan(js):
    """Return (errors, counts). errors is a list of human-readable strings."""
    depth = {'{': 0, '(': 0, '[': 0}
    pairs = {'}': '{', ')': '(', ']': '['}
    errors = []
    line = 1
    i, n = 0, len(js)
    prev_sig = ''          # last significant character
    prev_word = ''         # last identifier-ish word
    word = ''
    stack = []             # (char, line) for helpful messages

    while i < n:
        c = js[i]

        if c == '\n':
            line += 1; i += 1; continue

        # comments
        if c == '/' and i + 1 < n:
            if js[i + 1] == '/':
                while i < n and js[i] != '\n':
                    i += 1
                continue
            if js[i + 1] == '*':
                j = js.find('*/', i + 2)
                if j < 0:
                    errors.append('unterminated /* comment opened on line %d' % line)
                    break
                line += js.count('\n', i, j)
                i = j + 2
                continue

        # strings and template literals
        if c in '"\'`':
            quote, start_line = c, line
            i += 1
            closed = False
            while i < n:
                if js[i] == '\\':
                    i += 2; continue
                if js[i] == '\n':
                    line += 1
                    if quote != '`':
                        errors.append('unterminated %s string on line %d' % (quote, start_line))
                        closed = True
                        break
                if js[i] == quote:
                    i += 1; closed = True; break
                i += 1
            if not closed and i >= n:
                errors.append('unterminated %s literal opened on line %d' % (quote, start_line))
                break
            prev_sig, prev_word, word = quote, '', ''
            continue

        # regex literal
        if c == '/':
            is_regex = (prev_sig == '' or prev_sig in _REGEX_OK_AFTER
                        or prev_word in _REGEX_OK_WORDS)
            if is_regex:
                start_line = i_line = line
                i += 1
                in_class = False
                closed = False
                while i < n:
                    ch = js[i]
                    if ch == '\\':
                        i += 2; continue
                    if ch == '\n':
                        break                      # regexes cannot span lines
                    if ch == '[':
                        in_class = True
                    elif ch == ']':
                        in_class = False
                    elif ch == '/' and not in_class:
                        i += 1; closed = True; break
                    i += 1
                if not closed:
                    errors.append('unterminated regex on line %d' % start_line)
                    break
                prev_sig, prev_word, word = '/', '', ''
                continue

        # delimiters
        if c in '{([':
            depth[c] += 1
            stack.append((c, line))
        elif c in '})]':
            open_c = pairs[c]
            depth[open_c] -= 1
            if depth[open_c] < 0:
                errors.append("extra '%s' on line %d" % (c, line))
                depth[open_c] = 0
            elif stack:
                stack.pop()

        # track the last significant char / word for regex detection
        if c.isspace():
            if word:
                prev_word, word = word, ''
        elif c.isalnum() or c in '_$':
            word += c
            prev_sig = c
        else:
            if word:
                prev_word, word = word, ''
            prev_sig = c
        i += 1

    for ch, cnt in depth.items():
        if cnt > 0:
            where = ''
            for s_ch, s_line in reversed(stack):
                if s_ch == ch:
                    where = ' (earliest unclosed near line %d)' % s_line
                    break
            errors.append("%d unclosed '%s'%s" % (cnt, ch, where))

    return errors, depth


if __name__ == '__main__':
    import sys, re
    path = sys.argv[1]
    html = open(path, encoding='utf-8').read()
    m = re.search(r'<script>([\s\S]*?)</script>\s*</body>', html)
    if not m:
        print('no script block'); sys.exit(2)
    errs, depth = scan(m.group(1))
    if errs:
        for e in errs:
            print('  !', e)
        sys.exit(3)
    print('structure ok', depth)
