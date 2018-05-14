<template>
  <span
    :class="{ escapeSequence: displayableChar[0] === '\\' }"
    :title="title"
    >{{ displayableChar }}</span>
</template>

<script>
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
    title() {
      return [
        this.displayableChar, '\n',
        this.char.charCodeAt(0).toString(8), ' oct\n',
        this.char.charCodeAt(0), ' dec\n',
        this.char.charCodeAt(0).toString(16).toUpperCase(), ' hex',
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
}
.escapeSequence {
  color: #008;
}
span:hover {
  color: #000;
  background: #eee;
}
span.escapeSequence:hover {
  color: #006;
}
</style>
