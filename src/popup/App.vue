
<template>
  <div id="app" class="container" :class="rewardShadow ? 'more-height' : ''">
    <div>
      <div class="tab-row">
        <div v-for="el in seciData" class="tab-col" :key="el.f12">
          <h5>{{ el.f14 }}</h5>
          <p :class="el.f3 > 0 ? 'up' : 'down'">{{ el.f2 }}</p>
          <p :class="el.f3 > 0 ? 'up' : 'down'">{{ el.f4 }}&nbsp;&nbsp;{{ el.f3 }}%</p>
        </div>
      </div>
      <table>
        <thead>
          <tr>
            <th>基金名称</th>
            <th v-if="isEdit">基金代码</th>
            <th v-if="!isEdit">估算净值</th>
            <th>涨跌幅</th>
            <th v-if="!isEdit">更新时间</th>
            <th v-if="isEdit">特别关注</th>
            <th v-if="isEdit">删除</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="el in dataList" :key="el.fundcode">
            <td>{{ el.name }}</td>
            <td v-if="isEdit">{{ el.fundcode }}</td>
            <td v-if="!isEdit">{{ el.gsz }}</td>
            <td :class="el.gszzl > 0 ? 'up' : 'down'">{{ el.gszzl }}%</td>
            <td v-if="!isEdit">{{ el.gztime.substr(5) }}</td>
            <td v-if="isEdit">
              <input
                @click="slt(el.fundcode)"
                :class="el.fundcode == RealtimeFundcode ? 'slt' : ''"
                class="btn edit"
                value="✔"
                type="button"
              />
            </td>
            <td v-if="isEdit">
              <input @click="dlt(el.fundcode)" class="btn red edit" value="✖" type="button" />
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <p v-if="isEdit" class="tips">特别关注功能介绍：可以指定一个基金，实现后台自动更新估值涨跌幅，并在程序图标中以角标的形式实时更新。</p>
    <div class="input-row">
      <input
        class="btn"
        v-if="isDuringDate"
        type="button"
        :value="isLiveUpdate ? '暂停实时更新' : '实时更新'"
        @click="isLiveUpdate = !isLiveUpdate"
      />
      <input class="btn" v-if="!isDuringDate" type="button" value="休市中" />
      <input class="btn" type="button" :value="isEdit ? '取消编辑' : '编辑'" @click="isEdit = !isEdit" />
      <input class="btn" type="button" :value="isAdd ? '取消添加' : '添加'" @click="isAdd = !isAdd" />
      <input class="btn primary" type="button" value="打赏" @click="reward" />
    </div>
    <div v-if="isAdd" class="input-row">
      <input v-model="fundcode" class="btn" type="text" placeholder="请输入基金代码" />
      <input @click="save" class="btn" type="button" value="确定" />
    </div>
    <div v-if="rewardShadow" class="shadow">
      <div class="reward-box">
        <div class="tab-row">
          <button @click="checked = 'wepay'" :class="checked == 'wepay' ? 'checked' : ''">微信</button>
          <button @click="checked = 'alipay'" :class="checked == 'alipay' ? 'checked' : ''">支付宝</button>
        </div>
        <div class="qrcode">
          <img
            :src="
              checked == 'wepay'
                ? './../icons/qrcode/wepay.png'
                : './../icons/qrcode/alipay.png'
            "
          />
        </div>
        <p class="tips reward-tips">感谢有您的支持，自选基金才能一直保持更新，增加更多功能。</p>
        <div class="tab-row">
          <input class="btn success" type="button" value="打赏好了" @click="rewardShadow = false" />
          <input class="btn" type="button" value="下次一定" @click="rewardShadow = false" />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      isEdit: false,
      fundcode: "",
      isAdd: false,
      seciData: [],
      isLiveUpdate: false,
      isDuringDate: false,
      RealtimeFundcode: null,
      dataList: [],
      myVar: null,
      myVar1: null,
      rewardShadow: false,
      checked: "wepay",
      fundList: ["001618"]
    };
  },
  mounted() {
    this.isLiveUpdate = true;
    this.getSeciData();
    chrome.storage.sync.get(["fundList", "RealtimeFundcode"], res => {
      this.fundList = res.fundList ? res.fundList : this.fundList;
      this.RealtimeFundcode = res.RealtimeFundcode;
      this.getData();
    });
  },
  watch: {
    isLiveUpdate(val) {
      chrome.runtime.sendMessage({ type: "DuringDate" }, response => {
        this.isDuringDate = response.farewell;
        if (val && this.isDuringDate) {
          this.myVar = setInterval(() => {
            this.getSeciData();
          }, 5 * 1000);
          this.myVar1 = setInterval(() => {
            this.getData();
          }, 60 * 1000);
        } else {
          clearInterval(this.myVar);
          clearInterval(this.myVar1);
        }
      });
    }
  },
  methods: {
    reward() {
      this.rewardShadow = true;
    },
    ajaxPromise(stock) {
      return new Promise((resovle, reject) => {
        let xhr = new XMLHttpRequest();
        let url =
          "http://fundgz.1234567.com.cn/js/" +
          stock +
          ".js?rt=" +
          new Date().getTime();
        xhr.open("GET", url, true);
        xhr.send();

        xhr.onreadystatechange = () => {
          let DONE = 4;
          let OK = 200;
          if (xhr.readyState === DONE) {
            if (xhr.status === OK) {
              let res = xhr.responseText.match(/\{(.+?)\}/);
              let ress = JSON.parse(res[0]);
              resovle(ress);
            } else {
              reject("无法获取该基金信息！");
            }
          }
        };
      });
    },
    getSeciData() {
      let url =
        "https://push2.eastmoney.com/api/qt/ulist.np/get?fltt=2&fields=f2,f3,f4,f12,f14&secids=1.000001,1.000300,0.399001,0.399006&_=" +
        new Date().getTime();
      this.$axios.get(url).then(res => {
        this.seciData = res.data.data.diff;
      });
    },
    getData() {
      // 	  ["fundcode"]=>"519983"           //基金代码
      // 	  ["name"]=>"长信量化先锋混合A"    //基金名称
      // 	  ["jzrq"]=>"2018-09-21"           //净值日期
      // 	  ["dwjz"]=>"1.2440"               //当日净值
      // 	  ["gsz"]=>"1.2388"                //估算净值
      // 	  ["gszzl"]=>"-0.42"               //估算涨跌百分比 即-0.42%
      // 	  ["gztime"]=>"2018-09-25 15:00"   //估值时间

      let axiosArray = [];
      for (const fund of this.fundList) {
        let url =
          "http://fundgz.1234567.com.cn/js/" +
          fund +
          ".js?rt=" +
          new Date().getTime();
        let newPromise = this.$axios.get(url);
        axiosArray.push(newPromise);
      }

      this.$axios
        .all(axiosArray)
        .then(
          this.$axios.spread((...responses) => {
            this.dataList = [];
            responses.forEach(res => {
              let val = res.data.match(/\{(.+?)\}/);
              let data = JSON.parse(val[0]);
              this.dataList.push(data);
              if (data.fundcode == this.RealtimeFundcode) {
                chrome.runtime.sendMessage({
                  type: "refreshBadge",
                  data: data
                });
              }
            });
          })
        )
        .catch(error => {
          this.dataList = [];
        });
    },
    save() {
      //验证
      if (this.fundList.indexOf(this.fundcode) > -1) {
        alert("该基金已添加！");
        return false;
      }
      let url =
        "http://fundgz.1234567.com.cn/js/" +
        this.fundcode +
        ".js?rt=" +
        new Date().getTime();
      this.$axios
        .get(url)
        .then(res => {
          this.fundList.push(this.fundcode);
          chrome.storage.sync.set(
            {
              fundList: this.fundList
            },
            () => {
              this.getData();
            }
          );
        })
        .catch(error => {
          alert("无法获取该基金信息！");
        });
    },
    slt(id) {
      if (id == this.RealtimeFundcode) {
        chrome.storage.sync.set(
          {
            RealtimeFundcode: null
          },
          () => {
            this.RealtimeFundcode = null;
            chrome.runtime.sendMessage({ type: "endInterval" });
          }
        );
      } else {
        chrome.storage.sync.set(
          {
            RealtimeFundcode: id
          },
          () => {
            this.RealtimeFundcode = id;
            chrome.runtime.sendMessage({ type: "startInterval", id: id });
          }
        );
      }
    },
    dlt(id) {
      this.fundList = this.fundList.filter(function(ele) {
        return ele != id;
      });

      chrome.storage.sync.set(
        {
          fundList: this.fundList
        },
        () => {
          this.getData();
        }
      );
    }
  }
};
</script>

<style lang="scss" scoped>
.container {
  min-width: 380px;
  min-height: 100px;
  max-height: 405px;
  overflow-y: auto;
  padding: 10px 5px;
}

.more-height {
  height: 405px;
}

table {
  margin: 10px auto 0;
  width: 100%;
  border-collapse: collapse;
  text-align: center;
}

table th {
  padding: 8px 7px;
}

table td {
  padding: 7px;
}

.up {
  color: #f56c6c;
  font-weight: bold;
}

.down {
  color: #4eb61b;
  font-weight: bold;
}

tbody tr:hover {
  background: #f5fafe;
}

.btn {
  display: inline-block;
  line-height: 1;
  cursor: pointer;
  background: #fff;
  padding: 5px 6px;
  border-radius: 3px;
  font-size: 12px;
  color: #000000;
  margin: 0 5px;
  border: 1px solid #dcdfe6;
}

.btn.edit {
  padding: 2px 5px;
  margin: 0;
}

.btn.red {
  color: #f56c6c;
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

.tab-col {
  float: left;
  width: 25%;
  text-align: center;
}

.tab-col h5 {
  margin: 4px 0;
}

.tab-col p {
  margin: 4px 0;
}

.tab-row:after,
.tab-row:before {
  display: table;
  content: "";
}

.tab-row:after {
  clear: both;
}

.shadow {
  position: absolute;
  width: 100%;
  height: 100%;
  padding: 20px 40px;
  box-sizing: border-box;
  top: 0;
  left: 0;
  background-color: rgba(0, 0, 0, 0.7);
}

.reward-box {
  background: #ffffff;
  border-radius: 15px;
  width: 100%;
  height: 100%;
  text-align: center;
  display: inline-block;
  line-height: 1;
  vertical-align: middle;
  font-size: 0;
}

.reward-box button {
  line-height: 1;
  white-space: nowrap;
  vertical-align: middle;
  background: #fff;
  border: 1px solid #dcdfe6;
  font-weight: 500;
  border-left: 0;
  color: #606266;
  -webkit-appearance: none;
  text-align: center;
  box-sizing: border-box;
  margin: 0;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.645, 0.045, 0.355, 1);
  padding: 12px 20px;
  font-size: 14px;
  width: 85px;
  position: relative;
  display: inline-block;
  outline: none;
}

.reward-box button:first-child {
  border-left: 1px solid #dcdfe6;
  border-radius: 4px 0 0 4px;
  box-shadow: none !important;
}

.reward-box button:last-child {
  border-radius: 0 4px 4px 0;
}

.reward-box button.checked {
  color: #fff;
  background-color: #409eff;
  border-color: #409eff;
}

.tab-row {
  padding: 12px 0;
}

.qrcode img {
  width: 256px;
}

.success {
  color: #4eb61b;
  border-color: #4eb61b;
}

.primary {
  color: #409eff;
  border-color: #409eff;
}

.tips {
  font-size: 12px;
  margin: 0;
  color: #aaaaaa;
  line-height: 1.4;
  padding: 5px 15px;
}

.reward-tips {
  padding: 0 50px;
}
</style>

