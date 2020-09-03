import Vue from "vue";
import App from "./App";
import axios from "axios";
import {
  Switch
} from 'element-ui';

Vue.prototype.$axios = axios;

Vue.use(Switch)

/* eslint-disable no-new */
new Vue({
  el: "#app",

  render: h => h(App)
});