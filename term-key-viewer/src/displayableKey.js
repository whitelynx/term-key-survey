import _ from 'lodash';

const useCharMap = false;

const fishCharMap = {
  '\x1B': '\\e',
  '\x07': '\\a',
  '\x08': '\\b',
  '\x12': '\\f',
  '\x10': '\\n',
  '\x13': '\\r',
  '\x09': '\\t',
  '\x11': '\\v',
  ' ': "' '",
  '\\': '\\\\',
  '"': '\\"',
  "'": "\\'",
  $: '\\$',
  '*': '\\*',
  '?': '\\?',
  '~': '\\~',
  '%': '\\%',
  '#': '\\#',
  '(': '\\(',
  ')': '\\)',
  '{': '\\{',
  '}': '\\}',
  '[': '\\[',
  ']': '\\]',
  '<': '\\<',
  '>': '\\>',
  '^': '\\^',
  '&': '\\&',
  ';': '\\;',
};

const readlineCharMap = {
  '\x1B': '\\e',
  '\\': '\\\\',
  '"': '\\"',
  "'": "\\'",
  '\x07': '\\a',
  '\x08': '\\b',
  '\x12': '\\f',
  '\x10': '\\n',
  '\x13': '\\r',
  '\x09': '\\t',
  '\x11': '\\v',
};

function hex(num) {
  return num.toString(16).toUpperCase();
}

function controlCode(char, prefix = '\\C-') {
  const charCode = char.charCodeAt(0);
  return prefix + String.fromCharCode(charCode + 96);
}

function hexCode(char, prefix = '\\x') {
  const charCode = char.charCodeAt(0);
  return prefix + _.padStart(hex(charCode), 2, '0');
}

function unicodeCode(char, prefix = '\\u', length = 4) {
  const charCode = char.charCodeAt(0);
  return prefix + _.padStart(hex(charCode), length, '0');
}

function multibyteHexCode(char, prefix = '\\x') {
  return _.map(char, byte => prefix + _.padStart(hex(byte.charCodeAt(0)), 2, '0')).join('');
}

export function fishDisplayableChar(char) {
  const charCode = char.charCodeAt(0);
  if (useCharMap && char in fishCharMap) {
    return fishCharMap[char];
  } else if (charCode >= 0x1 && charCode <= 0x1a) {
    return controlCode(char, '\\c');
  } else if ((charCode >= 0x0 && charCode <= 0x1f) || charCode === 0x7f || (charCode >= 0x80 && charCode <= 0x9f)) {
    return hexCode(char, '\\x');
  } else if (charCode > 0xffff) {
    return unicodeCode(char, '\\U', 8);
  } else if (charCode > 0xff) {
    return unicodeCode(char, '\\u');
  }

  return char;
}

function readlineDisplayableChar(char) {
  const charCode = char.charCodeAt(0);
  if (char in readlineCharMap) {
    return readlineCharMap[char];
  } else if (charCode >= 0x1 && charCode <= 0x1a) {
    return controlCode(char, '\\C-');
  } else if ((charCode >= 0x0 && charCode <= 0x1f) || charCode === 0x7f || (charCode >= 0x80 && charCode <= 0x9f)) {
    return hexCode(char, '\\x');
  } else if (charCode > 0xff) {
    return multibyteHexCode(char, '\\c');
  }

  return char;
}

export function displayableKey(chars, mode = 'fish') {
  if (chars === null || chars === undefined) {
    return null;
  }

  let quoted = false;
  let displayableChar = null;

  if (mode === 'repr') {
    return JSON.stringify(chars).slice(1, -1);
  } else if (mode === 'fish') {
    displayableChar = fishDisplayableChar;
  } else if (mode === 'readline') {
    quoted = true;
    displayableChar = readlineDisplayableChar;
  }

  const result = _.map(chars, displayableChar).join('');

  return quoted ? `"${result}"` : result;
}
