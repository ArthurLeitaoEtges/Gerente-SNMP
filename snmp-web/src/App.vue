<template>
  <SnmpInfo />
</template>

<script>
import SnmpInfo from './SnmpInfo.vue'

export default {
  name: 'App',
  components: {
    SnmpInfo
  }
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body, #app {
  width: 100%;
  height: 100%;
}

::-webkit-scrollbar {
  display: none;
}

* {
  scrollbar-width: none;      /* Firefox */
}
</style>
