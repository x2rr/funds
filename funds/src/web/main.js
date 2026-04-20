import Vue from "vue";
import App from "./App";
import axios from "axios";
import {
  Select,
  Option,
  Switch,
  Slider,
  Tabs,
  TabPane,
  RadioButton,
  RadioGroup,
  Dialog,
  Button,
  Loading,
  Icon,
  Message,
  Radio,
  Input
} from 'element-ui';

import VueClipboard from "vue-clipboard2";
Vue.use(VueClipboard)

Vue.prototype.$axios = axios;
Vue.prototype.$ELEMENT = { size: 'mini' };
Vue.use(Loading.directive);
Vue.prototype.$loading = Loading.service;
Vue.prototype.$message = Message;

Vue.use(Select)
Vue.use(Option)
Vue.use(Switch)
Vue.use(Slider)
Vue.use(Tabs)
Vue.use(TabPane)
Vue.use(RadioButton)
Vue.use(RadioGroup)
Vue.use(Dialog)
Vue.use(Button)
Vue.use(Loading)
Vue.use(Icon)
Vue.use(Radio)
Vue.use(Input)

document.addEventListener('DOMContentLoaded', function() {
  const loadingMask = document.getElementById('app-loading');
  if (loadingMask) {
    loadingMask.style.display = 'none';
  }
});

new Vue({
  el: "#app",
  render: h => h(App)
});
