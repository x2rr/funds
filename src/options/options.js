import Vue from "vue";
import App from "./App";
import axios from "axios";
import {
  Switch,
  Message,
  Radio,
  RadioGroup,
  Button,
  Dialog
} from 'element-ui';

Vue.prototype.$axios = axios;
Vue.prototype.$message = Message;
Vue.prototype.$ELEMENT = { size: 'mini' };

Vue.use(Switch)
Vue.use(Radio)
Vue.use(RadioGroup)
Vue.use(Button)
Vue.use(Dialog)

/* eslint-disable no-new */
new Vue({
  el: "#app",

  render: h => h(App)
});