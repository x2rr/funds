import Vue from "vue";
import App from "./App";
import axios from "axios";
import 'element-ui/lib/theme-chalk/index.css';
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
  Input,
  Checkbox,
  CheckboxGroup
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
Vue.use(Checkbox)
Vue.use(CheckboxGroup)

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
