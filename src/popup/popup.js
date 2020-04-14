import Vue from 'vue'
import App from './App'
import store from '../store'
import axios from 'axios';

Vue.prototype.$axios = axios;

/* eslint-disable no-new */
new Vue({
  el: '#app',
  store,
  
  render: h => h(App)
})
