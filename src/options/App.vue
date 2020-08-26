<template>
  <div id="app" class="container">
    <div>
      <ul class="setting-list">
        <li>
          <div class="list-title">
            节假日信息
            <button :disabled="disabled" @click="getHoliday" title="点击更新节假日信息" class="btn">更新</button>
            <span class="loading" v-if="disabled">更新中。。。</span>
          </div>
          <p>
            <span v-if="holiday">
              当前版本：v{{
              holiday.version
              }}&nbsp;&nbsp;&nbsp;&nbsp;最后节假日日期：{{
              holiday.lastDate
              }}
            </span>
          </p>
          <p>
            tips：更新节假日信息，可以在节假日暂停更新估值，节假日信息会不定时更新。
            <a href="#" @click="openHoliday">查看最新版</a>
          </p>
        </li>
        <li>
          <div class="list-title">
            显示份额与收益信息
            <div class="select-row">
              显示持有金额
              <input type="radio" id="numFalse" :value="false" v-model="showAmount" />
              <label for="numFalse">否</label>
              <input type="radio" id="numTrue" :value="true" v-model="showAmount" />
              <label for="numTrue">是</label>
            </div>
            <div class="select-row">
              显示估值收益
              <input type="radio" id="numFalse" :value="false" v-model="showGains" />
              <label for="numFalse">否</label>
              <input type="radio" id="numTrue" :value="true" v-model="showGains" />
              <label for="numTrue">是</label>
            </div>
          </div>
          <p>tips：在编辑设置里，输入基金的持有份额，即可计算出收益估值情况。</p>
        </li>
        <li>
          <div class="list-title">请作者喝杯咖啡</div>
          <p style="line-height:34px">
            如果你觉得此插件对你有所帮助，或者想要支持一下我
            <input
              class="btn primary"
              type="button"
              title="φ(>ω<*)"
              value="点击打赏"
              @click="reward"
            />
          </p>
          <p style="line-height:34px">
            或者你也可以帮忙点一个star，点击查看源码→
            <span title="点击查看项目源码" class="black icon-btn-row" @click="openGithub">
              <svg
                class="githubIcon"
                height="24"
                viewBox="0 0 16 16"
                version="1.1"
                width="24"
                aria-hidden="true"
              >
                <path
                  d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"
                />
              </svg>
              <input
                class="btn black githubText"
                type="button"
                value="源代码"
              />
            </span>
          </p>
          <reward :top="50" ref="reward"></reward>
        </li>
      </ul>
    </div>
  </div>
</template>

<script>
import reward from "../common/reward";
export default {
  components: {
    reward
  },
  data() {
    return {
      holiday: null,
      disabled: false,
      showAmount: false,
      showGains: false
    };
  },
  mounted() {
    chrome.storage.sync.get(
      ["holiday", "showNum", "showAmount", "showGains"],
      res => {
        if (res.showNum) {
          //解决版本遗留问题，拆分属性
          chrome.storage.sync.set({
            showNum: false
          });
          chrome.storage.sync.set(
            {
              showAmount: true
            },
            () => {
              this.showAmount = true;
            }
          );
          chrome.storage.sync.set(
            {
              showGains: true
            },
            () => {
              this.showGains = true;
            }
          );
        } else {
          this.showAmount = res.showAmount ? res.showAmount : false;
          this.showGains = res.showGains ? res.showGains : false;
        }

        if (res.holiday) {
          this.holiday = res.holiday;
        } else {
          this.getHoliday();
        }
      }
    );
  },
  watch: {
    showAmount(val) {
      chrome.storage.sync.set(
        {
          showAmount: val
        },
        () => {
          this.showAmount = val;
        }
      );
    },
    showGains(val) {
      chrome.storage.sync.set(
        {
          showGains: val
        },
        () => {
          this.showGains = val;
        }
      );
    }
  },
  methods: {
    getHoliday() {
      this.disabled = true;
      let url = "https://x2rr.github.io/funds/holiday.json";
      this.$axios.get(url).then(res => {
        chrome.storage.sync.set(
          {
            holiday: res.data
          },
          () => {
            this.holiday = res.data;
            this.disabled = false;
          }
        );
      });
    },
    openHoliday() {
      window.open("https://x2rr.github.io/funds/holiday.json");
    },
    openGithub() {
      window.open("https://github.com/x2rr/funds");
    },
    reward(data) {
      this.$refs.reward.init();
    }
  }
};
</script>

<style lang="scss" scoped>
.container {
  min-width: 630px;
  min-height: 520px;
  text-align: center;
  padding-top: 15px;
  font-size: 13px;
  font-family: "Helvetica Neue", Helvetica, Arial, "PingFang SC",
    "Hiragino Sans GB", "Heiti SC", "Microsoft YaHei", "WenQuanYi Micro Hei",
    sans-serif;
}

.setting-list {
  width: 600px;
  margin: 0 auto;
  text-align: left;
  padding: 0;
}

.setting-list li {
  list-style: none;
  font-size: 16px;
  border-bottom: 1px solid #dddddd;
  padding: 10px 0;
}

.setting-list li p {
  margin: 0;
  font-size: 14px;
  color: #999999;
}

.list-title {
  min-height: 34px;
  line-height: 34px;
}

.list-title .select-row {
  line-height: 30px;
  padding-left: 20px;
}

.btn {
  display: inline-block;
  line-height: 1;
  cursor: pointer;
  background: #fff;
  padding: 6px 8px;
  border-radius: 3px;
  font-size: 14px;
  color: #000000;
  margin: 0 5px;
  outline: none;
  border: 1px solid #dcdfe6;
}

.btn[disabled] {
  color: #aaaaaa;
}

.icon-btn-row {
  position: relative;
  cursor: pointer;
}

.githubIcon {
  position: absolute;
  top: -4px;
  left: 12px;
}
.githubText {
  padding-left: 30px;
  padding: 8px 8px 8px 36px;
}

.slt {
  color: #fff;
  background-color: #67c23a;
  border-color: #67c23a;
}

.input-row {
  text-align: center;
  margin-top: 10px;
}

.tips {
  font-size: 12px;
  margin: 0;
  color: #aaaaaa;
  line-height: 1.4;
  padding: 5px 15px;
}
.primary {
  color: #409eff;
  border-color: #409eff;
}

.black {
  color: #24292e;
  border-color: #24292e;
}
</style>
