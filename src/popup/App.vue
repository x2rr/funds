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
      <div v-if="isEdit" class="input-row">
        <span>添加新基金:</span>
        <!-- <input v-model="fundcode" class="btn" type="text" placeholder="请输入基金代码" /> -->
        <el-select
          v-model="fundcode"
          multiple
          filterable
          remote
          size="mini"
          reserve-keyword
          @visible-change="selectChange"
          placeholder="请输入基金编码，支持按名称或编码搜索"
          :remote-method="remoteMethod"
          :loading="loading"
          style="width:300px"
        >
          <el-option
            v-for="item in searchOptions"
            :key="item.value"
            :label="item.label"
            :value="item.value"
          >
            <span style="float: left">{{ item.label }}</span>
            <span
              style="float: right; color: #8492a6; font-size: 13px;margim-right:20px;padding-right:15px"
            >{{ item.value }}</span>
          </el-option>
        </el-select>
        <input @click="save" class="btn" type="button" value="确定" />
      </div>
      <p v-if="isEdit" class="tips center">部分新发基金或QDII基金可以搜索到，但可能无法获取估值情况</p>
      <table :class="tableHeight">
        <thead>
          <tr>
            <th>基金名称</th>
            <th v-if="isEdit">基金代码</th>
            <th v-if="!isEdit">估算净值</th>
            <th @click="sortList('gszzl')" class="pointer">
              涨跌幅
              <span :class="sortType.gszzl" class="down-arrow"></span>
            </th>
            <th @click="sortList('amount')" v-if="showAmount" class="pointer">
              持有额
              <span :class="sortType.amount" class="down-arrow"></span>
            </th>
            <th @click="sortList('gains')" v-if="showGains" class="pointer">
              估算收益
              <span :class="sortType.gains" class="down-arrow"></span>
            </th>
            <th v-if="!isEdit">更新时间</th>
            <th v-if="isEdit && (showAmount || showGains)">持有份额</th>
            <th v-if="isEdit">排序</th>
            <th v-if="isEdit">特别关注</th>
            <th v-if="isEdit">删除</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(el, index) in dataList" :key="el.fundcode">
            <td class="fundName" :title="el.name">{{ el.name }}</td>
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

    <div class="input-row">
      <input
        class="btn"
        v-if="isDuringDate"
        type="button"
        :value="isLiveUpdate ? '暂停实时更新' : '实时更新'"
        @click="isLiveUpdate = !isLiveUpdate"
      />
      <input class="btn" v-if="!isDuringDate" type="button" value="休市中" />
      <input class="btn" type="button" :value="isEdit ? '完成编辑' : '编辑'" @click="isEdit = !isEdit" />
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
    reward,
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
      allGains: 0,
      sortType: {
        gszzl: "none",
        amount: "none",
        gains: "none",
      },
      searchOptions: [],
      value: [],
      list: [],
      loading: false,
    };
  },
  mounted() {
    this.isLiveUpdate = true;
    this.getSeciData();
    chrome.storage.sync.get(
      ["RealtimeFundcode", "fundListM", "showAmount", "showGains", "fundList"],
      (res) => {
        this.fundList = res.fundList ? res.fundList : this.fundList;
        if (res.fundListM) {
          this.fundListM = res.fundListM;
        } else {
          for (const fund of this.fundList) {
            let val = {
              code: fund,
              num: null,
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
    },
    tableHeight() {
      if (this.isEdit) {
        return "table-more-height";
      }
    },
  },
  watch: {
    isLiveUpdate(val) {
      chrome.runtime.sendMessage({ type: "DuringDate" }, (response) => {
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
    },
  },
  methods: {
    selectChange() {
      this.searchOptions = [];
    },
    remoteMethod(query) {
      if (query !== "") {
        this.loading = true;
        let url =
          "https://fundsuggest.eastmoney.com/FundSearch/api/FundSearchAPI.ashx?&m=9&key=" +
          query +
          "&_=" +
          new Date().getTime();
        this.$axios.get(url).then((res) => {

          this.searchOptions = res.data.Datas.filter((val) => {
            let hasCode = this.fundListM.some((currentValue, index, array) => {
              return currentValue.code == val.CODE;
            });
            return !hasCode;
          }).map((val) => {
            return {
              value: val.CODE,
              label: val.NAME,
            };
          });
          this.loading = false;
        });
      } else {
        this.searchOptions = [];
      }
    },
    option() {
      chrome.tabs.create({ url: "/options/options.html" });
    },
    reward() {
      this.rewardShadow = true;
      this.$refs.reward.init();
    },
    sortList(type) {
      for (const key in this.sortType) {
        if (this.sortType.hasOwnProperty(key)) {
          if (key != type) {
            this.sortType[key] = "none";
          }
        }
      }
      this.sortType[type] = this.sortType[type] == "desc" ? "asc" : "desc";
      this.dataList = this.dataList.sort(
        this.compare(type, this.sortType[type])
      );
    },
    compare(property, type) {
      return function (obj1, obj2) {
        var val1 = obj1[property];
        var val2 = obj2[property];
        if (type == "asc") {
          return val1 - val2;
        } else {
          return val2 - val1;
        }
      };
    },
    closeReward() {
      this.rewardShadow = false;
    },
    getSeciData() {
      let url =
        "https://push2.eastmoney.com/api/qt/ulist.np/get?fltt=2&fields=f2,f3,f4,f12,f14&secids=1.000001,1.000300,0.399001,0.399006&_=" +
        new Date().getTime();
      this.$axios.get(url).then((res) => {
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
            responses.forEach((res, ind) => {
              let val = res.data.match(/\{(.+?)\}/);
              if (val) {
                //判读返回数据格式是否正常
                let data = JSON.parse(val[0]);
                if (this.showAmount || this.showGains) {
                  let slt = this.fundListM.filter(
                    (item) => item.code == data.fundcode
                  );
                  data.num = slt[0].num;
                }
                this.dataList.push(data);
                if (data.fundcode == this.RealtimeFundcode) {
                  chrome.runtime.sendMessage({
                    type: "refreshBadge",
                    data: data,
                  });
                }
              } else {
                //不支持的基金特殊处理
                let data = {
                  fundcode: this.fundListM[ind].code,
                  name: this.fundListM[ind].code + "无法获取详情",
                  jzrq: "",
                  dwjz: "0",
                  gsz: "0",
                  gszzl: "0",
                  gztime: "0",
                  num: "0",
                  amount: "0",
                  gains: "0",
                };

                this.dataList.push(data);
              }
            });
            this.getAllGains();
          })
        )
        .catch((error) => {
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
        fundListM: this.fundListM,
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
      this.fundcode.forEach((code) => {
        let val = {
          code: code,
          num: null,
        };
        this.fundListM.push(val);
      });
      chrome.storage.sync.set(
        {
          fundListM: this.fundListM,
        },
        () => {
          this.fundcode = [];
          this.getData();
        }
      );
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
        (this.fundListM[ind - 1] = this.fundListM[ind]),
      ][0];
      chrome.storage.sync.set({
        fundListM: this.fundListM,
      });
    },
    slt(id) {
      if (id == this.RealtimeFundcode) {
        chrome.storage.sync.set(
          {
            RealtimeFundcode: null,
          },
          () => {
            this.RealtimeFundcode = null;
            chrome.runtime.sendMessage({ type: "endInterval" });
          }
        );
      } else {
        chrome.storage.sync.set(
          {
            RealtimeFundcode: id,
          },
          () => {
            this.RealtimeFundcode = id;
            chrome.runtime.sendMessage({ type: "startInterval", id: id });
          }
        );
      }
    },
    dlt(id) {
      this.fundListM = this.fundListM.filter(function (ele) {
        return ele.code != id;
      });

      chrome.storage.sync.set(
        {
          fundListM: this.fundListM,
        },
        () => {
          this.getData();
        }
      );
    },
  },
};
</script>

<style lang="scss" scoped>
.container {
  min-width: 400px;
  min-height: 150px;
  overflow-y: auto;
  padding: 8px 2px;
  font-size: 12px;
  font-family: "Helvetica Neue", Helvetica, Arial, "PingFang SC",
    "Hiragino Sans GB", "Heiti SC", "Microsoft YaHei", "WenQuanYi Micro Hei",
    sans-serif;
}

.more-height {
  height: 405px;
}

.more-width {
  width: 620px;
}

.table-more-height {
  min-height: 160px;
}

.num-all-width {
  min-width: 520px;
}

.num-one-width {
  min-width: 440px;
}

table {
  margin: 10px auto 0;
  width: 100%;
  border-collapse: collapse;
  text-align: center;
}

.center {
  text-align: center;
}

table th {
  padding: 8px 6px;
}

table td {
  padding: 6px 6px 5px;
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
  font-size: 12px;
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
  padding: 6px 0;
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

.fundName {
  max-width: 140px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
  background-color: rgba(240, 240, 240, 1);
}

::-webkit-scrollbar-track {
  box-shadow: inset 0 0 0px rgba(240, 240, 240, 0.5);
  border-radius: 10px;
  background-color: rgba(240, 240, 240, 0.5);
}

::-webkit-scrollbar-thumb {
  border-radius: 10px;
  box-shadow: inset 0 0 0px rgba(240, 240, 240, 0.5);
  background-color: #cccccc;
}

.down-arrow {
  display: inline-block;
  position: relative;
  width: 8px;
  height: 0;
}

.down-arrow::after {
  display: inline-block;
  content: " ";
  height: 6px;
  width: 6px;
  border-width: 0 1px 1px 0;
  border-color: #666;
  border-style: solid;
  transform-origin: center;
  transition: all 0.3s;
  position: absolute;
  right: 0;
}
.down-arrow.desc::after {
  transform-origin: center;
  transform: rotate(45deg);
  top: -10px;
}
.down-arrow.asc::after {
  transform-origin: center;
  transform: rotate(-135deg);
  top: -6px;
}

.down-arrow.none {
  display: none;
}

.pointer {
  cursor: pointer;
}
</style>
