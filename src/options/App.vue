
<template>
  <div id="app" class="container">
    <div>
      <ul class="setting-list">
        <li>
          <div class="list-title">
            节假日信息
            <button :disabled="disabled" @click="getHoliday" class="btn">更新</button>
            <span class="loading" v-if="disabled">更新中。。。</span>
          </div>
          <p>
            <span
              v-if="holiday"
            >当前版本：v{{holiday.version}}&nbsp;&nbsp;&nbsp;&nbsp;最后节假日日期：{{holiday.lastDate}}</span>
          </p>
          <p>
            tips：更新节假日信息，可以在节假日暂停更新估值，节假日信息会不定时更新。
            <a
              href="https://x2rr.github.io/funds/holiday.json"
            >查看最新版</a>
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
      </ul>
    </div>
  </div>
</template>

<script>
export default {
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
        if (res.showNum) { //解决版本遗留问题，拆分属性
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
    }
  }
};
</script>

<style lang="scss" scoped>
.container {
  min-width: 700px;
  min-height: 400px;
  text-align: center;
  padding-top: 15px;
}

.setting-list {
  width: 600px;
  margin: 0 auto;
  text-align: left;
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
  border: 1px solid #dcdfe6;
}

.btn[disabled] {
  color: #aaaaaa;
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
</style>

