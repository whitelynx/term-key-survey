<template>
  <span
    :class="charClass"
    :title="title"
    >{{ displayableChar }}</span>
</template>

<script>
import _ from 'lodash';

import { fishDisplayableChar } from '../displayableKey';

export default {
  name: 'ResultsViewer',
  props: {
    char: String,
  },
  methods: {
    fishDisplayableChar,
  },
  computed: {
    displayableChar() {
      return fishDisplayableChar(this.char);
    },
    charClass() {
      return {
        escapeChar: this.displayableChar === '\\e',
        escapeSequence: this.displayableChar[0] === '\\' && this.displayableChar.length > 1,
        ctrlChar: this.displayableChar[0] === '^' && this.displayableChar.length > 1,
      };
    },
    title() {
      return [
        this.displayableChar, '\n',
        _.padStart(this.char.charCodeAt(0).toString(8), 3, '0'), ' oct\n',
        this.char.charCodeAt(0), ' dec\n',
        _.padStart(this.char.charCodeAt(0).toString(16).toUpperCase(), 2, '0'), ' hex',
      ].join('');
    },
  },
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
span {
  color: #444;
  cursor: default;
  white-space: pre;
}
span.escapeSequence {
  color: #008;
}
span.ctrlChar {
  color: #800;
}
span.escapeChar {
  color: #880;
}
span:hover {
  color: #000;
  background: #ddd;
}
span.escapeSequence:hover {
  color: #006;
}
span.ctrlChar:hover {
  color: #600;
}
span.escapeChar:hover {
  color: #660;
}
</style>
