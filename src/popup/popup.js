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
  Button
} from 'element-ui';

Vue.prototype.$axios = axios;
Vue.prototype.$ELEMENT = { size: 'mini' };

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

/* eslint-disable no-new */
new Vue({
  el: "#app",

  render: h => h(App)
});