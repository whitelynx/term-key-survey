<template>
  <table>
    <tbody>
      <tr>
        <th rowspan="2" class="bottomLine">Modifiers</th>
        <th rowspan="2" class="bottomLine">Key</th>
        <th v-for="result in keyedResults" :key="`${result.key}-term`">{{ result.environment['terminal program'] }}</th>
      </tr>

      <tr class="bottomLine">
        <th v-for="result in keyedResults" :key="`${result.key}-sys`">{{ result.environment['platform system'] }}</th>
      </tr>

      <tr v-for="key in keys" :key="key.key" :class="{ bottomLine: !/\+/.test(key.key) }">
        <th class="modifiers">{{ key.modifiers }}</th>
        <th class="key">{{ key.name }}</th>
        <td v-for="result in keyedResults"
          :key="`${key.key}/${result.key}`"
          class="chars" :class="{ empty: isEmpty(result.results[key.key]) }"
          >
          <span v-if="isEmpty(result.results[key.key])">none</span>
          <Char v-if="!isEmpty(result.results[key.key])"
            v-for="char in result.results[key.key]"
            :key="`${key.key}/${result.key}/${char}`"
            :char="char"
            />
        </td>
      </tr>
    </tbody>
  </table>
</template>

<script>
import _ from 'lodash';

import Char from './Char';
import { displayableKey, fishDisplayableChar } from '../displayableKey';

const keyWithModifiersRE = /^(.+\+)(\w+)$/;

export default {
  name: 'ResultsViewer',
  props: {
    results: {
      type: Array,
      default: () => {},
    },
  },
  components: {
    Char,
  },
  methods: {
    isEmpty(chars) {
      return !chars || chars.length === 0;
    },
    displayableKey,
    fishDisplayableChar,
  },
  computed: {
    keyedResults() {
      return this.results.map(result => ({
        ...result,
        key: `${result.environment['terminal program']}/${result.environment['platform system']}`,
      }));
    },
    keys() {
      return _(this.results)
        .flatMap(({ results }) => _.keys(results))
        .uniq()
        .map((key) => {
          const match = keyWithModifiersRE.exec(key);
          if (!match) {
            return {
              key,
              name: key,
              modifiers: null,
            };
          }
          return {
            key,
            name: match[2],
            modifiers: match[1],
          };
        })
        .sortBy(({ name, modifiers }) => `${name}/${modifiers}`)
        .value();
    },
  },
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
table {
  border-collapse: collapse;
}
tr.bottomLine th, tr.bottomLine td, th.bottomLine, td.bottomLine {
  border-bottom: 1px solid #bbb;
}
th, td {
  padding: 0.3ex 0.3em;
}
th {
  background-color: #eee;
}
th.modifiers {
  text-align: right;
  padding-right: 0;
}
th.key {
  text-align: left;
  padding-left: 0;
}
td.chars {
  text-align: left;
  font-family: 'Input Mono', monospace;
}
td.chars.empty {
  color: #bbb;
}
</style>
