import Vue from "vue";
import App from "./App";
import axios from "axios";
import {
  Select,
  Option
} from 'element-ui';

Vue.prototype.$axios = axios;

Vue.use(Select)
Vue.use(Option)

/* eslint-disable no-new */
new Vue({
  el: "#app",

  render: h => h(App)
});