import Vue from "vue";
import App from "./App";
import axios from "axios";
import {
  Select,
  Option,
  Switch
} from 'element-ui';

Vue.prototype.$axios = axios;

Vue.use(Select)
Vue.use(Option)
Vue.use(Switch)

/* eslint-disable no-new */
new Vue({
  el: "#app",

  render: h => h(App)
});