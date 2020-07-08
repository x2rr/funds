<template>
  <div id="app" class="container" :class="containerWidth">
    <div>
      <div class="tab-row">
        <div v-for="el in seciData" class="tab-col" :key="el.f12">
          <h5>{{ el.f14 }}</h5>
          <p :class="el.f3 >= 0 ? 'up' : 'down'">{{ el.f2 }}</p>
          <p :class="el.f3 >= 0 ? 'up' : 'down'">{{ el.f4 }}&nbsp;&nbsp;{{ el.f3 }}%</p>
        </div>
      </div>
      <table>
        <thead>
          <tr>
            <th>基金名称</th>
            <th v-if="isEdit">基金代码</th>
            <th v-if="!isEdit">估算净值</th>
            <th>涨跌幅</th>
            <th v-if="showAmount">持有额</th>
            <th v-if="showGains">估算收益</th>
            <th v-if="!isEdit">更新时间</th>
            <th v-if="isEdit && (showAmount || showGains)">持有份额</th>
            <th v-if="isEdit">排序</th>
            <th v-if="isEdit">特别关注</th>
            <th v-if="isEdit">删除</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(el, index) in dataList" :key="el.fundcode">
            <td>{{ el.name }}</td>
            <td v-if="isEdit">{{ el.fundcode }}</td>
            <td v-if="!isEdit">{{ el.gsz }}</td>
            <td :class="el.gszzl >= 0 ? 'up' : 'down'">{{ el.gszzl }}%</td>
            <td v-if="showAmount">{{ calculateMoney(el) }}</td>
            <td v-if="showGains" :class="el.gszzl >= 0 ? 'up' : 'down'">{{ calculate(el) }}</td>
            <td v-if="!isEdit">{{ el.gztime.substr(5) }}</td>
            <th v-if="isEdit && isEdit && (showAmount || showGains)">
              <input
                class="btn num"
                placeholder="输入持有份额"
                v-model="el.num"
                @input="changeNum(el, index)"
                type="text"
              />
            </th>
            <td v-if="isEdit">
              <input @click="sortUp(index)" class="btn edit" value="▲" type="button" />
            </td>
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
    <div v-if="isEdit" class="input-row">
      <span>添加新基金:</span>
      <input v-model="fundcode" class="btn" type="text" placeholder="请输入基金代码" />
      <input @click="save" class="btn" type="button" value="确定" />
    </div>
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
      <!-- <input class="btn" type="button" :value="isAdd ? '取消添加' : '添加'" @click="isAdd = !isAdd" /> -->
      <input class="btn" type="button" value="设置" @click="option" />
      <input class="btn primary" type="button" title="φ(>ω<*)" value="打赏" @click="reward" />
      <input
        v-if="showGains"
        class="btn"
        :class="allGains >= 0 ? 'btn-up' : 'btn-down'"
        type="button"
        :title="
          allGains >= 0 ? 'd=====(￣▽￣*)b 赞一个' : '∑(っ°Д°;)っ 大事不好啦'
        "
        :value="'总收益：' + allGains"
      />
    </div>
    <reward @close="closeReward" ref="reward"></reward>
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
      showGains: false,
      showAmount: false,
      fundList: ["001618"],
      fundListM: [],
      allGains: 0
    };
  },
  mounted() {
    this.isLiveUpdate = true;
    this.getSeciData();
    chrome.storage.sync.get(
      ["RealtimeFundcode", "fundListM", "showAmount", "showGains", "fundList"],
      res => {
        this.fundList = res.fundList ? res.fundList : this.fundList;
        if (res.fundListM) {
          this.fundListM = res.fundListM;
        } else {
          for (const fund of this.fundList) {
            let val = {
              code: fund,
              num: null
            };
            this.fundListM.push(val);
          }
        }
        this.showAmount = res.showAmount ? res.showAmount : false;
        this.showGains = res.showGains ? res.showGains : false;
        this.RealtimeFundcode = res.RealtimeFundcode;
        this.getData();
      }
    );
  },
  computed: {
    containerWidth() {
      if (this.rewardShadow) {
        return "more-height";
      } else if (this.isEdit) {
        return "more-width";
      } else if (this.showAmount && this.showGains) {
        return "num-all-width";
      } else if (this.showAmount || this.showGains) {
        return "num-one-width";
      }
    }
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
    option() {
      chrome.tabs.create({ url: "options/options.html" });
    },
    reward() {
      this.rewardShadow = true;
      this.$refs.reward.init();
    },
    closeReward() {
      this.rewardShadow = false;
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
      for (const fund of this.fundListM) {
        let url =
          "http://fundgz.1234567.com.cn/js/" +
          fund.code +
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
              if (this.showAmount || this.showGains) {
                let slt = this.fundListM.filter(
                  item => item.code == data.fundcode
                );
                data.num = slt[0].num;
              }
              this.dataList.push(data);
              if (data.fundcode == this.RealtimeFundcode) {
                chrome.runtime.sendMessage({
                  type: "refreshBadge",
                  data: data
                });
              }
            });
            this.getAllGains();
          })
        )
        .catch(error => {
          console.log("数据请求出现错误！");
        });
    },
    getAllGains() {
      let allGains = 0;
      this.dataList.forEach(val => {
        allGains += parseFloat(this.calculate(val));
      });
      this.allGains = allGains.toFixed(1);
    },
    changeNum(item, ind) {
      for (let fund of this.fundListM) {
        if (fund.code == item.fundcode) {
          fund.num = item.num;
        }
      }
      chrome.storage.sync.set({
        fundListM: this.fundListM
      });
      this.getAllGains();
    },
    calculateMoney(val) {
      let sum = (val.dwjz * val.num).toFixed(1);
      return sum;
    },
    calculate(val) {
      let sum = ((val.gsz - val.dwjz) * val.num).toFixed(1);
      return sum;
    },
    save() {
      //验证
      let hasCode = this.fundListM.some((currentValue, index, array) => {
        return currentValue.code == this.fundcode;
      });

      if (hasCode) {
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
          let val = res.data.match(/\{(.+?)\}/);
          if (val) {
            let val = {
              code: this.fundcode,
              num: null
            };
            this.fundListM.push(val);
            chrome.storage.sync.set(
              {
                fundListM: this.fundListM
              },
              () => {
                this.getData();
              }
            );
          } else {
            alert("该基金可能为新发基金，暂无详细数据！");
          }
        })
        .catch(error => {
          alert("无法获取该基金信息！");
        });
    },
    sortUp(ind) {
      if (ind == 0) {
        return false;
      }
      let val = this.dataList[ind - 1];
      this.$set(this.dataList, ind - 1, this.dataList[ind]);
      this.$set(this.dataList, ind, val);
      this.fundListM[ind] = [
        this.fundListM[ind - 1],
        (this.fundListM[ind - 1] = this.fundListM[ind])
      ][0];
      chrome.storage.sync.set({
        fundListM: this.fundListM
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
      this.fundListM = this.fundListM.filter(function(ele) {
        return ele.code != id;
      });

      chrome.storage.sync.set(
        {
          fundListM: this.fundListM
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
  min-height: 150px;
  overflow-y: auto;
  padding: 10px 5px;
}

.more-height {
  height: 405px;
}

.more-width {
  width: 600px;
}

.num-all-width {
  min-width: 500px;
}

.num-one-width {
  min-width: 420px;
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
  outline: none;
  border: 1px solid #dcdfe6;
}

.btn.edit {
  padding: 2px 5px;
  margin: 0;
}

.btn.red {
  color: #f56c6c;
}

.btn.num {
  width: 80px;
}

.btn-up {
  color: #f56c6c;
  border-color: #f56c6c;
}

.btn-down {
  color: #4eb61b;
  border-color: #4eb61b;
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


.tab-row {
  padding: 12px 0;
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
</style>
