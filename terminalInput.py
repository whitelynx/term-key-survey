'''Handle terminal input.

'''
from contextlib import contextmanager
import os
import readline
import sys
import termios
from termios import IGNBRK, BRKINT, PARMRK, ISTRIP, INLCR, IGNCR, ICRNL, IXON, OPOST, ECHO, ECHONL, ICANON, ISIG, \
        IEXTEN, CSIZE, CS8
import time

from terminalOutput import cursor, console, colors, promptColors


defaultTimeout = 0.05
sleepTime = 0.01


CTRL_C = '\x03'

fishCharMap = {
    '\x1b': r'\e',
    '\\': '\\\\',
    '"': r'\"',
    "'": r"\'",
    '\x07': r'\a',
    '\x08': r'\b',
    '\x12': r'\f',
    '\x10': r'\n',
    '\x13': r'\r',
    '\x09': r'\t',
    '\x11': r'\v',
    ' ': "' '",
    '$': r'\$',
    '*': r'\*',
    '?': r'\?',
    '~': r'\~',
    '%': r'\%',
    '#': r'\#',
    '(': r'\(',
    ')': r'\)',
    '{': r'\{',
    '}': r'\}',
    '[': r'\[',
    ']': r'\]',
    '<': r'\<',
    '>': r'\>',
    '^': r'\^',
    '&': r'\&',
    ';': r'\;',
}

readlineCharMap = {
    '\x1b': r'\e',
    '\\': '\\\\',
    '"': r'\"',
    "'": r"\'",
    '\x07': r'\a',
    '\x08': r'\b',
    '\x12': r'\f',
    '\x10': r'\n',
    '\x13': r'\r',
    '\x09': r'\t',
    '\x11': r'\v',
}


stdinIsRaw = False

upChar = None
downChar = None
enterChar = None
escChar = None


class QuitException(BaseException):
    '''Quit the application.

    '''
    pass


class BackException(BaseException):
    '''Go back to the previous menu.

    '''
    pass


@contextmanager
def rawStdin():
    oldTermAttr = termios.tcgetattr(sys.stdin)

    iflag, oflag, cflag, lflag, ispeed, ospeed, specialChars = termios.tcgetattr(sys.stdin)
    # Pretty much set up raw mode.
    iflag &= ~(IGNBRK | BRKINT | PARMRK | ISTRIP | INLCR | IGNCR | ICRNL | IXON)
    oflag &= ~OPOST
    lflag &= ~(ECHO | ECHONL | ICANON | ISIG | IEXTEN)
    # Set 8-bit character size (probably not needed)
    cflag = (cflag & ~CSIZE) | CS8

    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, [iflag, oflag, cflag, lflag, ispeed, ospeed, specialChars])
    os.set_blocking(sys.stdin.fileno(), False)

    globals()['stdinIsRaw'] = True

    yield

    globals()['stdinIsRaw'] = False

    os.set_blocking(sys.stdin.fileno(), True)
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, oldTermAttr)
    sys.stdout.write('\n')


def readByte(timeout=None):
    if not stdinIsRaw:
        with rawStdin():
            return readByte(timeout)

    startTime = os.times().elapsed

    byte = None
    while not byte:
        if timeout is not None and os.times().elapsed - startTime > timeout:
            return None
        try:
            byte = sys.stdin.read(1)
        except BlockingIOError:
            time.sleep(sleepTime)

    return byte


def controlCode(char, prefix=r'\C-'):
    return prefix + chr(ord(char) + 96)


def hexCode(char, prefix=r'\x'):
    return prefix + hex(ord(char)).lstrip('0x').rjust(2, '0')


def unicodeCode(char, prefix=r'\u', length=4):
    return prefix + hex(ord(char)).lstrip('0x').rjust(length, '0')


def multibyteHexCode(char, prefix=r'\x'):
    return ''.join(prefix + hex(ord(byte)).lstrip('0x').rjust(2, '0') for byte in char.encode("utf-8"))


def fishDisplayableChar(char):
    if char in fishCharMap:
        return fishCharMap[char]
    elif 0x1 <= ord(char) <= 0x1a:
        return controlCode(char, r'\c')
    elif 0x0 <= ord(char) <= 0x1f or ord(char) == 127 or 0x80 <= ord(char) <= 0x9f:
        return hexCode(char, r'\x')
    elif ord(char) > 0xffff:
        return unicodeCode(char, r'\U', length=8)
    elif ord(char) > 0xff:
        return unicodeCode(char, r'\u')

    return char


def readlineDisplayableChar(char):
    if char in readlineCharMap:
        return readlineCharMap[char]
    elif 0x1 <= ord(char) <= 0x1a:
        return controlCode(char, r'\C-')
    elif 0x0 <= ord(char) <= 0x1f or ord(char) == 127 or 0x80 <= ord(char) <= 0x9f:
        return hexCode(char, r'\x')
    elif ord(char) > 0xff:
        return multibyteHexCode(char, r'\c')

    return char


def displayableKey(chars, mode='fish'):
    if chars is None:
        return None

    quoted = False
    displayableChar = None

    if mode == 'repr':
        return repr(chars)
    elif mode == 'fish':
        displayableChar = fishDisplayableChar
    elif mode == 'readline':
        quoted = True
        displayableChar = readlineDisplayableChar

    result = []

    for char in chars:
        result.append(displayableChar(char))

    if quoted:
        return '"{}"'.format(''.join(result))

    return ''.join(result)


def displayKey(chars):
    dispKey = displayableKey(chars)
    if dispKey is None:
        sys.stdout.write('{c.dark.gray}(skipped){c.reset}'.format(c=colors))
    else:
        sys.stdout.write('{c.userInput}{}{c.reset}'.format(dispKey, c=colors))
    sys.stdout.flush()


def readKey():
    if not stdinIsRaw:
        with rawStdin():
            return readKey()

    response = []

    char = readByte()
    while char:
        response.append(char)

        char = readByte(defaultTimeout)

    return ''.join(response)


def getKey(prompt, allowSkip=False):
    if not stdinIsRaw:
        with rawStdin():
            return getKey(prompt, allowSkip)

    sys.stdout.write(prompt)
    sys.stdout.flush()

    response = readKey()

    if response == ' ' and allowSkip:
        sys.stdout.write('{c.dark.gray}(skipped){c.reset}'.format(c=colors))
        sys.stdout.flush()
        response = None
    elif response == CTRL_C:
        colors.printControlChar('^C\r')
        raise QuitException()
    else:
        displayKey(response)
        if response == 'q':
            raise QuitException()
        elif response == 'b':
            raise BackException()

    sys.stdout.write('\r\n')
    sys.stdout.flush()

    return response


def getKeyWithName(keyName):
    return getKey("Please press {c.bold}{c.yellow}{}{c.reset}... ".format(keyName, c=colors), allowSkip=False)


def yesNo(default=False):
    with rawStdin():
        char = readByte()
        while char not in 'yYnN\r\n' + CTRL_C:
            char = readByte()
        if char == CTRL_C:  # Ctrl+C
            colors.printControlChar('^C\r')
            sys.exit(1)
        result = char in 'yY' or (char in '\r\n' and default)
        colors.printUserInput(char if char in 'yYnN' else '(Y)' if char in '\r\n' else '(N)')
        return result


def setReadlineText(text):
    def hook():
        readline.insert_text(text)
        readline.redisplay()

    readline.set_pre_input_hook(hook)


def readLine(prompt, initialText=None):
    if initialText is not None:
        setReadlineText(initialText)

    try:
        return input('{}{c.userInput}'.format(prompt, c=promptColors))
    except KeyboardInterrupt:
        colors.printControlChar('^C\r')
        sys.exit(1)
    finally:
        sys.stdout.write(colors.reset)
        sys.stdout.flush()
        readline.set_pre_input_hook()  # Reset the pre-input hook so it doesn't keep inserting the last value.


class MenuChoice(object):
    def __init__(self, display, **kwargs):
        super().__init__()

        self.display = display

        for key, val in kwargs.items():
            setattr(self, key, val)


def chooseOne(title, choices, handleEsc=False):
    colors.printHeading(title)

    unselectedPrefix = '{c.dark.gray} - {c.reset}'.format(c=colors)
    selectedPrefix = '{c.green}-->{c.reset}'.format(c=colors)

    try:
        cursor.hide()

        for choice in choices:
            print(unselectedPrefix + choice.display)

        cursor.up(len(choices))
        cursor.setX()
        cursor.savePos()

        selectedIndex = 0

        with rawStdin():
            def updateSelection():
                cursor.setX()
                sys.stdout.write(unselectedPrefix)

                cursor.setPos(1, 1)
                console.eraseLine()
                cursor.down(2)
                console.eraseLine()
                cursor.up()
                console.eraseLine()
                sys.stdout.write('  {c.red}{}{c.reset}'.format(selectedIndex, c=colors))

                cursor.restorePos()
                if selectedIndex > 0:
                    cursor.down(selectedIndex)
                sys.stdout.write(selectedPrefix)
                sys.stdout.flush()

            updateSelection()
            while True:
                char = readKey()
                if char == CTRL_C:  # Ctrl+C
                    colors.printControlChar('^C\r')
                    sys.exit(1)
                elif char == upChar:
                    selectedIndex = max(0, selectedIndex - 1)
                    updateSelection()
                elif char == downChar:
                    selectedIndex = min(len(choices) - 1, selectedIndex + 1)
                    updateSelection()
                elif char == enterChar:
                    return choices[selectedIndex]
                elif char == escChar and handleEsc:
                    raise BackException()

    finally:
        cursor.down(len(choices) - selectedIndex)
        cursor.show()


def queryBasicKeys():
    globals()['upChar'] = getKeyWithName('Up')
    globals()['downChar'] = getKeyWithName('Down')
    globals()['enterChar'] = getKeyWithName('Enter')
    globals()['escChar'] = getKeyWithName('Esc')
