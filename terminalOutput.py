'''Handle terminal output.

'''
from contextlib import contextmanager
import inspect
import sys
from test.support import captured_stdout, captured_stderr
import traceback


def csi(*values, flag='m'):
    return '\x1b[{}{}'.format(';'.join(str(x) for x in values), flag)


def instantCSI(flag, prefix=(), suffix=()):
    if isinstance(prefix, str):
        prefix = (prefix, )
    elif not isinstance(prefix, tuple):
        prefix = tuple(prefix)

    if isinstance(suffix, str):
        suffix = (suffix, )
    elif not isinstance(suffix, tuple):
        suffix = tuple(suffix)

    def doCSI(*args):
        args = prefix + args + suffix
        sys.stdout.write(csi(*args, flag=flag))
        sys.stdout.flush()

    return doCSI


class cursor:  # pylint: disable=invalid-name
    savePos = instantCSI(flag='s')
    restorePos = instantCSI(flag='u')

    setPos = instantCSI(flag='H')
    setX = instantCSI(flag='G')

    up = instantCSI(flag='A')
    down = instantCSI(flag='B')
    right = instantCSI(flag='C')
    left = instantCSI(flag='D')

    hide = instantCSI(prefix='?25', flag='l')
    show = instantCSI(prefix='?25', flag='h')


class console:  # pylint: disable=invalid-name
    eraseDisplay = instantCSI(flag='J')
    eraseLine = instantCSI(flag='K')

    scrollUp = instantCSI(flag='S')
    scrollDown = instantCSI(flag='T')


class IndexedColor(object):
    def __init__(self, *prefix):
        super().__init__()

        self.prefix = prefix

    def __getitem__(self, index):
        return csi(*self.prefix, index)


class RGBColor(object):
    def __init__(self, *parts):
        super().__init__()
        self.parts = parts

    def __getitem__(self, part):
        if len(self.parts) >= 5:  # 38;2;r;g;b (or 48;2;r;g;b)
            return csi(*self.parts, part)

        return RGBColor(*self.parts, part)


class Colors16(object):
    def __init__(self, baseCode, graySeq=None):
        super().__init__()

        self.black = csi(baseCode + 0)
        self.red = csi(baseCode + 1)
        self.green = csi(baseCode + 2)
        self.yellow = csi(baseCode + 3)
        self.blue = csi(baseCode + 4)
        self.magenta = csi(baseCode + 5)
        self.cyan = csi(baseCode + 6)
        self.white = csi(baseCode + 7)

        if graySeq is not None:
            if not isinstance(graySeq, (list, tuple)):
                graySeq = (graySeq, )
            self.gray = csi(*graySeq)
            self.grey = self.gray


class ColorsFull(Colors16):
    def __init__(self, baseCode):
        super().__init__(baseCode)

        self.reset = csi(baseCode + 9)

        self.index = IndexedColor(baseCode + 8, 5)

        self.rgb = RGBColor(baseCode + 8, 2)

        darkColors = Colors16(baseCode, graySeq=baseCode + 60)
        self.dark = darkColors
        self.dim = darkColors

        brightColors = Colors16(baseCode + 60, graySeq=baseCode + 7)
        self.light = brightColors
        self.bright = brightColors


class Colors(ColorsFull):
    normal = csi()               # Reset / Normal - all attributes off
    #reset = csi()               # / (see __init__)

    bold = csi(1)               # Bold or increased intensity
    highIntensity = csi(1)      # /
    faint = csi(2)              # Faint (decreased intensity) - Not widely supported.
    lowIntensity = csi(2)       # /
    italic = csi(3)             # Italic: on - Not widely supported. Sometimes treated as inverse.
    underline = csi(4)          # Underline: Single
    blink = csi(5)              # Blink: Slow - less than 150 per minute
    rapidBlink = csi(6)         # Blink: Rapid - MS-DOS ANSI.SYS; 150+ per minute; not widely supported.
    inverse = csi(7)            # Image: Negative - inverse or reverse; swap foreground and background (reverse video)
    reverse = csi(7)            # |
    negative = csi(7)           # /
    conceal = csi(8)            # Conceal - Not widely supported.
    strikethrough = csi(9)      # Crossed-out - Characters legible, but marked for deletion. Not widely supported.

    defaultFont = csi(10)       # Primary(default) font
    altFont1 = csi(11)          # n-th alternate font - Select the n-th alternate font.
    altFont2 = csi(12)
    altFont3 = csi(13)
    altFont4 = csi(14)
    altFont5 = csi(15)
    altFont6 = csi(16)
    altFont7 = csi(17)
    altFont8 = csi(18)
    altFont9 = csi(19)
    fraktur = csi(20)           # Fraktur - hardly ever supported

    boldOff = csi(21)           # Bold: off or Underline: Double - Bold off not widely supported; double underline
    noBold = csi(21)            # | hardly ever supported.
    doubleUnderline = csi(21)   # /
    normalColor = csi(22)       # Normal color or intensity - Neither bold nor faint
    normalIntensity = csi(22)   # |
    faintOff = csi(22)          # |
    noFaint = csi(22)           # /
    notItalic = csi(23)         # Not italic, not Fraktur
    italicOff = csi(23)         # |
    noItalic = csi(23)          # |
    notFraktur = csi(23)        # |
    frakturOff = csi(23)        # |
    noFraktur = csi(23)         # /
    underlineOff = csi(24)      # Underline: None - Not singly or doubly underlined
    noUnderline = csi(24)       # /
    blinkOff = csi(25)          # Blink: off
    noBlink = csi(25)           # /
    #reserved = csi(26)         # Reserved
    positive = csi(27)          # Image: Positive
    inverseOff = csi(27)        # |
    noInverse = csi(27)         # |
    reverseOff = csi(27)        # |
    noReverse = csi(27)         # |
    negativeOff = csi(27)       # |
    noNegative = csi(27)        # /
    reveal = csi(28)            # Reveal - conceal off
    concealOff = csi(28)        # |
    noConceal = csi(28)         # /
    strikethroughOff = csi(29)  # Not crossed out
    noStrikethrough = csi(29)   # /

    fg = ColorsFull(30)

    bg = ColorsFull(40)

    def __init__(self):
        # If neither `fg` nor `bg` is given, assume you mean foreground.
        super().__init__(30)

        # Override `reset` to be the same as `normal`
        self.reset = self.normal

        # Special styles
        self.error = self.red
        self.warning = self.yellow
        self.heading = self.underline
        self.userInput = self.index[180]
        self.controlChar = self.index[202]

    def wrapWith(self, *attribs, **kwargs):
        file = kwargs.pop('file', sys.stdout)
        if kwargs:
            raise TypeError('{!r} is an invalid keyword argument for this function'.format(kwargs.keys()[0]))

        attribs = ''.join(attribs)

        def doWrap(funcOrText, *args_, **kwargs_):
            if callable(funcOrText):
                file.write(attribs)
                try:
                    return funcOrText(*args_, **kwargs_)
                finally:
                    file.write(self.reset)
                    file.flush()
            else:
                if args_ or kwargs_:
                    funcOrText = funcOrText.format(*args_, **kwargs_)

                funcOrText.replace(str(self.reset), self.reset + attribs)
                print(funcOrText, file=file)
                return None

        return doWrap

    def printError(self, text, *args, **kwargs):
        file = kwargs.pop('file', sys.stdout)
        showTraceback = kwargs.pop('showTraceback', sys.stdout)

        wrapper = self.wrapWith(self.error, file=file)

        wrapper(text, *args, **kwargs)

        if showTraceback and sys.exc_info() is not None:
            wrapper(traceback.print_exc, file=file)

        file.write(self.reset)
        file.flush()

    def printWarning(self, text, showTraceback=False, file=sys.stderr):
        print('{c.warning}{}{c.reset}'.format(text, c=self), file=file)

        if showTraceback and sys.exc_info() is not None:
            traceback.print_exc(file=file)

        file.write(self.reset)
        file.flush()

    def printHeading(self, text, *attribs):
        print('{c.heading}{}{}{c.reset}'.format(''.join(attribs), text, c=self))

    def printUserInput(self, text):
        print('{c.userInput}{}{c.reset}'.format(text, c=self))

    def printControlChar(self, text):
        print('{c.controlChar}{}{c.reset}'.format(text, c=self))


_outputFileStack = [sys.stdout]


@contextmanager
def outputFile(file):
    _outputFileStack.append(file)
    yield
    assert _outputFileStack.pop() is file


def getOutputFile():
    return _outputFileStack[-1]


class Printer(object):
    def __init__(self, **kwargs):
        self.explicitOutputFile = kwargs.pop('file', None)
        self.explicitAttribs = kwargs.pop('attribs', None)
        self._implicitOutputFileStack = []
        self.implicitAttribs = []

        #self.__dict__.update(kwargs)
        if kwargs:
            raise TypeError('{!r} is an invalid keyword argument for this function'.format(kwargs.keys()[0]))

    def extend(self, **kwargs):
        if self.explicitOutputFile is not None:
            kwargs.setdefault('file', self.explicitOutputFile)
        if self.explicitAttribs is not None:
            kwargs.setdefault('attribs', self.explicitAttribs)
        return Printer(**kwargs)

    @property
    def outputFile(self):
        if self.explicitOutputFile is not None:
            return self.explicitOutputFile
        elif self._implicitOutputFileStack:
            return self._implicitOutputFileStack[-1]

        return getOutputFile()

    @property
    def attribs(self):
        return self.explicitAttribs or [] + self.implicitAttribs

    @contextmanager
    def implicitOutputFile(self, file):
        self._implicitOutputFileStack.append(file)
        yield
        assert self._implicitOutputFileStack.pop() is file

    def __call__(self, funcOrText, *args, **kwargs):
        if callable(funcOrText):
            with captured_stdout() as stdout, captured_stderr() as stderr:
                try:
                    result = funcOrText(*args, **kwargs)
                    outputText = result
                finally:
                    stdoutVal = stdout.getvalue()
                    stderrVal = stderr.getvalue()

                    if stdoutVal:
                        outputText = stdoutVal

                        if stderrVal:
                            sys.stderr.write(stderrVal)

                    if stderrVal:
                        outputText = stderrVal

        elif args or kwargs:
            funcOrText = funcOrText.format(*args, **kwargs)
        else:
            outputText = funcOrText

        outputText = '{attribs}{}{c.reset}'.format(
            outputText.replace(colors.reset, colors.reset + self.attribs),
            attribs=self.attribs,
            c=colors
        )

        print(outputText, file=self.outputFile)


class ReadlinePromptWrapper(object):
    startIgnore = '\x01'
    endIgnore = '\x02'

    @staticmethod
    def format(text):
        return '{rp.startIgnore}{}{rp.endIgnore}'.format(text, rp=ReadlinePromptWrapper)

    def __init__(self, wrapped):
        super().__init__()

        self.wrapped = wrapped

    def __getattr__(self, name):
        return self._handleWrappedValue(getattr(self.wrapped, name))

    def __getitem__(self, key):
        return self._handleWrappedValue(self.wrapped[key])

    def _handleWrappedValue(self, value):
        if isinstance(value, str):
            return self.format(value)
        elif inspect.isfunction(value):
            return lambda *args, **kwargs: self.format(value(*args, **kwargs))

        return ReadlinePromptWrapper(value)


colors = Colors()
promptColors = ReadlinePromptWrapper(colors)
