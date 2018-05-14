<template>
  <div id="app">
    <ResultsViewer :results="results"/>
  </div>
</template>

<script>
import results from './results.json';
import ResultsViewer from './components/ResultsViewer';

export default {
  name: 'App',
  data() {
    return {
      results,
    };
  },
  components: {
    ResultsViewer,
  },
};
</script>

<style>
#app {
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}
</style>
