<template>
  <div
    id="app"
    class="container"
    :class="containerClass"
    :style="
      diyContainer
        ? { width: containerWidth + 'px', height: containerHeight + 'px' }
        : ''
    "
  >
    <div>
      <div class="tab-row">
        <div
          v-for="(el, index) in indFundData"
          :draggable="isEdit"
          class="tab-col"
          :class="drag"
          :key="el.f12"
          @dragstart="handleDragStart($event, el)"
          @dragover.prevent="handleDragOver($event, el)"
          @dragenter="handleDragEnter($event, el, index)"
          @dragend="handleDragEnd($event, el)"
        >
          <h5>
            {{ el.f14 }}
            <span
              v-if="isEdit"
              @click="dltIndFund(index)"
              class="dltBtn edit red btn"
              >✖</span
            >
          </h5>
          <p :class="el.f3 >= 0 ? 'up' : 'down'">{{ el.f2 }}</p>
          <p :class="el.f3 >= 0 ? 'up' : 'down'">
            {{ el.f4 }}&nbsp;&nbsp;{{ el.f3 }}%
          </p>
        </div>
        <div v-if="isEdit && indFundData.length < 4" class="tab-col">
          <div
            v-if="!showAddSeciInput"
            class="addSeci"
            @click="() => (showAddSeciInput = true)"
          >
            添加
          </div>
          <div v-else>
            <div style="padding-top:2px">
              <el-select
                size="mini"
                :popper-append-to-body="false"
                v-model="sltSeci"
                style="width:110px"
                placeholder="请选择"
              >
                <el-option
                  v-for="item in userSeciList"
                  :key="item.value"
                  :label="item.label"
                  :value="item.value"
                ></el-option>
              </el-select>
            </div>
            <div style="margin-top:4px">
              <input
                class="btn"
                type="button"
                value="取消"
                @click="() => (showAddSeciInput = false)"
              />
              <input class="btn" type="button" value="确定" @click="saveSeci" />
            </div>
          </div>
        </div>
      </div>
      <div v-if="isEdit" class="input-row">
        <span>添加新基金:</span>
        <!-- <input v-model="fundcode" class="btn" type="text" placeholder="请输入基金代码" /> -->
        <el-select
          v-model="fundcode"
          multiple
          filterable
          :popper-append-to-body="false"
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
              >{{ item.value }}</span
            >
          </el-option>
        </el-select>
        <input @click="save" class="btn" type="button" value="确定" />
      </div>
      <p v-if="isEdit" class="tips center">
        部分新发基金或QDII基金可以搜索到，但可能无法获取估值情况
      </p>
      <table :class="tableHeight">
        <thead>
          <tr>
            <th>基金名称</th>
            <th v-if="isEdit">基金代码</th>
            <th v-if="showGSZ && !isEdit">估算净值</th>
            <th v-if="isEdit && showCost">成本价</th>
            <th @click="sortList('gszzl')" class="pointer">
              涨跌幅
              <span :class="sortType.gszzl" class="down-arrow"></span>
            </th>
            <th @click="sortList('amount')" v-if="showAmount" class="pointer">
              持有额
              <span :class="sortType.amount" class="down-arrow"></span>
            </th>
            <th v-if="showCost">持有收益</th>
            <th v-if="showCostRate">持有收益率</th>
            <th @click="sortList('gains')" v-if="showGains" class="pointer">
              估算收益
              <span :class="sortType.gains" class="down-arrow"></span>
            </th>
            <th v-if="!isEdit">更新时间</th>
            <th v-if="isEdit && (showAmount || showGains || showCost)">
              持有份额
            </th>
            <th v-if="isEdit">特别关注</th>
            <th v-if="isEdit">删除</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="(el, index) in dataList"
            :key="el.fundcode"
            :draggable="isEdit"
            :class="drag"
            @dragstart="handleDragStart($event, el)"
            @dragover.prevent="handleDragOver($event, el)"
            @dragenter="handleDragEnter($event, el, index)"
            @dragend="handleDragEnd($event, el)"
          >
            <td class="fundName" :title="el.name">{{ el.name }}</td>
            <td v-if="isEdit">{{ el.fundcode }}</td>
            <td v-if="showGSZ && !isEdit">{{ el.gsz }}</td>
            <td v-if="isEdit && showCost">
              <input
                class="btn num"
                placeholder="持仓成本价"
                v-model="el.cost"
                @input="changeCost(el, index)"
                type="text"
              />
            </td>
            <td :class="el.gszzl >= 0 ? 'up' : 'down'">{{ el.gszzl }}%</td>
            <td v-if="showAmount">{{ calculateMoney(el) }}</td>
            <td v-if="showCost" :class="calculateCost(el) >= 0 ? 'up' : 'down'">
              {{ calculateCost(el) }}
            </td>
            <td
              v-if="showCostRate"
              :class="calculateCostRate(el) >= 0 ? 'up' : 'down'"
            >
              {{ el.cost > 0 ? calculateCostRate(el) + "%" : "" }}
            </td>
            <td v-if="showGains" :class="el.gszzl >= 0 ? 'up' : 'down'">
              {{ calculate(el) }}
            </td>
            <td v-if="!isEdit">{{ el.gztime.substr(5) }}</td>
            <th v-if="isEdit && (showAmount || showGains || showCost)">
              <input
                class="btn num"
                placeholder="输入持有份额"
                v-model="el.num"
                @input="changeNum(el, index)"
                type="text"
              />
            </th>
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
              <input
                @click="dlt(el.fundcode)"
                class="btn red edit"
                value="✖"
                type="button"
              />
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <p v-if="isEdit" class="tips">
      特别关注功能介绍：可以指定一个基金，在后台自动更新估值涨跌幅，并在程序图标中以角标的形式实时更新。
    </p>

    <div v-show="isEdit" class="input-row">
      <el-switch
        v-model="darkMode"
        @change="changeDarkMode"
        active-color="#484848"
        inactive-color="#13ce66"
        inactive-text="标准模式"
        active-text="暗色模式"
      >
      </el-switch>
      <!-- <input v-model="containerWidth" type="number" />
      <input v-model="containerHeight" type="number" /> -->
    </div>

    <div class="input-row">
      <input
        class="btn"
        v-if="isDuringDate"
        type="button"
        :value="isLiveUpdate ? '暂停更新' : '实时更新'"
        :title="
          isLiveUpdate ? '正在实时更新，点击暂停' : '已暂停，点击切换为实时更新'
        "
        @click="changeLiveUpdate"
      />
      <input class="btn" v-if="!isDuringDate" type="button" value="休市中" />
      <input
        class="btn"
        type="button"
        :value="isEdit ? '完成编辑' : '编辑'"
        @click="isEdit = !isEdit"
      />
      <!-- <input class="btn" type="button" :value="isAdd ? '取消添加' : '添加'" @click="isAdd = !isAdd" /> -->
      <input class="btn" type="button" value="设置" @click="option" />
      <input
        class="btn primary"
        type="button"
        title="φ(>ω<*)"
        value="打赏"
        @click="reward"
      />
    </div>
    <div class="input-row">
      <input
        v-if="showGains"
        class="btn"
        :class="allGains >= 0 ? 'btn-up' : 'btn-down'"
        type="button"
        :title="
          allGains >= 0 ? 'd=====(￣▽￣*)b 赞一个' : '∑(っ°Д°;)っ 大事不好啦'
        "
        :value="'日估值收益：' + allGains"
      />
      <input
        v-if="showCost"
        class="btn"
        :class="allCost >= 0 ? 'btn-up' : 'btn-down'"
        type="button"
        :title="
          allCost >= 0 ? 'd=====(￣▽￣*)b 赞一个' : '∑(っ°Д°;)っ 大事不好啦'
        "
        :value="'总持有收益：' + allCost"
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
      indFundData: [],
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
      showCost: false,
      showCostRate: false,
      showGSZ: false,
      fundList: ["001618"],
      fundListM: [],
      allGains: 0,
      allCost: 0,
      sortType: {
        gszzl: "none",
        amount: "none",
        gains: "none",
      },
      searchOptions: [],
      value: [],
      list: [],
      loading: false,
      dragging: null,
      showAddSeciInput: false,
      seciList: ["1.000001", "1.000300", "0.399001", "0.399006"],
      allSeciList: [
        {
          value: "1.000001",
          label: "上证指数",
        },
        {
          value: "1.000300",
          label: "沪深300",
        },
        {
          value: "0.399001",
          label: "深证成指",
        },
        {
          value: "1.000688",
          label: "科创50",
        },
        {
          value: "0.399006",
          label: "创业板指",
        },
        {
          value: "0.399005",
          label: "中小板指",
        },
        {
          value: "100.HSI",
          label: "恒生指数",
        },
        {
          value: "100.DJIA",
          label: "道琼斯",
        },
        {
          value: "100.NDX",
          label: "纳斯达克",
        },
        {
          value: "100.SPX",
          label: "标普500",
        },
      ],
      sltSeci: "",
      darkMode: false,
      diyContainer: false,
      containerWidth: 790,
      containerHeight: 590,
    };
  },
  mounted() {
    chrome.storage.sync.get(
      [
        "RealtimeFundcode",
        "fundListM",
        "showAmount",
        "showGains",
        "fundList",
        "seciList",
        "darkMode",
        "isLiveUpdate",
        "showCost",
        "showCostRate",
        "showGSZ",
      ],
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
        this.darkMode = res.darkMode ? res.darkMode : false;
        this.seciList = res.seciList ? res.seciList : this.seciList;
        this.showAmount = res.showAmount ? res.showAmount : false;
        this.showGains = res.showGains ? res.showGains : false;
        this.RealtimeFundcode = res.RealtimeFundcode;
        this.isLiveUpdate = res.isLiveUpdate ? res.isLiveUpdate : false;
        this.showCost = res.showCost ? res.showCost : false;
        this.showCostRate = res.showCostRate ? res.showCostRate : false;
        this.showGSZ = res.showGSZ ? res.showGSZ : false;
        this.getIndFundData();
        this.getData();
        this.checkInterval(true);
      }
    );
  },
  computed: {
    containerClass() {
      let className = "";
      if (this.darkMode) {
        className += "darkMode ";
      }
      if (this.rewardShadow) {
        className += "more-height";
      } else if (this.isEdit) {
        className += "more-width";
      } else {
        let tablist = [
          this.showAmount,
          this.showGains,
          this.showGains,
          this.showCostRate,
          this.showGSZ,
        ];
        let num = 0;
        tablist.forEach((val) => {
          if (val) {
            num++;
          }
        });
        console.log(num);
        className += "num-width-" + num;
      }
      return className;
    },
    userSeciList() {
      return this.allSeciList.filter((val) => {
        return this.seciList.indexOf(val.value) == -1;
      });
    },
    tableHeight() {
      if (this.isEdit) {
        return "table-more-height";
      }
    },
    drag() {
      if (this.isEdit) {
        return "table-drag";
      }
    },
  },
  watch: {
    //编辑状态停止更新
    isEdit(val) {
      if (val) {
        clearInterval(this.myVar);
        clearInterval(this.myVar1);
      } else {
        this.checkInterval();
      }
    },
  },
  methods: {
    checkInterval(isFirst) {
      chrome.runtime.sendMessage({ type: "DuringDate" }, (response) => {
        this.isDuringDate = response.farewell;
        if (this.isLiveUpdate && this.isDuringDate) {
          if (!isFirst) {
            this.getIndFundData();
            this.getData();
          }
          this.myVar = setInterval(() => {
            this.getIndFundData();
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
      return function(obj1, obj2) {
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
    changeDarkMode() {
      chrome.storage.sync.set({
        darkMode: this.darkMode,
      });
    },
    changeLiveUpdate() {
      chrome.storage.sync.set(
        {
          isLiveUpdate: !this.isLiveUpdate,
        },
        () => {
          this.isLiveUpdate = !this.isLiveUpdate;
          this.checkInterval();
        }
      );
    },
    saveSeci() {
      this.seciList.push(this.sltSeci);
      chrome.storage.sync.set(
        {
          seciList: this.seciList,
        },
        () => {
          this.sltSeci = "";
          this.getIndFundData();
        }
      );
    },
    dltIndFund(ind) {
      this.seciList.splice(ind, 1);
      chrome.storage.sync.set(
        {
          seciList: this.seciList,
        },
        () => {
          this.getIndFundData();
        }
      );
    },
    getIndFundData() {
      let seciListStr = this.seciList.join(",");
      let url =
        "https://push2.eastmoney.com/api/qt/ulist.np/get?fltt=2&fields=f2,f3,f4,f12,f14&secids=" +
        seciListStr +
        "&_=" +
        new Date().getTime();
      this.$axios.get(url).then((res) => {
        this.indFundData = res.data.data.diff;
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

      const promisesResolved = axiosArray.map((promise) =>
        promise.catch((error) => ({ error }))
      );

      function checkFailed(then) {
        return function(responses) {
          const someFailed = responses.some((response) => response.error);
          if (someFailed) {
            throw responses;
          }
          return then(responses);
        };
      }

      const formatData = (data) => {
        this.dataList = [];
        data.forEach((res, ind) => {
          if (res.data && res.data.match(/\{(.+?)\}/)) {
            let val = res.data.match(/\{(.+?)\}/);
            if (val) {
              //判断返回数据格式是否正常
              let data = JSON.parse(val[0]);
              let slt = this.fundListM.filter(
                (item) => item.code == data.fundcode
              );
              data.num = slt[0].num;
              data.cost = slt[0].cost;
              this.dataList.push(data);
              if (data.fundcode == this.RealtimeFundcode) {
                chrome.runtime.sendMessage({
                  type: "refreshBadge",
                  data: data,
                });
              }
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
        this.getAllCost();
      };

      this.$axios
        .all(promisesResolved)
        .then(
          checkFailed((responses) => {
            formatData(responses);
          })
        )
        .catch((err) => {
          formatData(err);
        });
    },
    getAllGains() {
      let allGains = 0;
      this.dataList.forEach((val) => {
        allGains += parseFloat(this.calculate(val));
      });
      this.allGains = allGains.toFixed(1);
    },
    getAllCost() {
      let allCost = 0;
      this.dataList.forEach((val) => {
        allCost += parseFloat(this.calculateCost(val));
      });
      this.allCost = allCost.toFixed(1);
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
    changeCost(item, ind) {
      for (let fund of this.fundListM) {
        if (fund.code == item.fundcode) {
          fund.cost = item.cost;
        }
      }
      chrome.storage.sync.set({
        fundListM: this.fundListM,
      });
      // this.getAllGains();
    },
    calculateMoney(val) {
      let sum = (val.dwjz * val.num).toFixed(1);
      return sum;
    },
    calculate(val) {
      let sum = ((val.gsz - val.dwjz) * val.num).toFixed(1);
      return sum;
    },
    calculateCost(val) {
      if (val.cost) {
        let sum = ((val.dwjz - val.cost) * val.num).toFixed(1);
        return sum;
      } else {
        return 0;
      }
    },
    calculateCostRate(val) {
      if (val.cost && val.cost != 0) {
        let sum = (((val.dwjz - val.cost) / val.cost) * 100).toFixed(2);
        return sum;
      } else {
        return 0;
      }
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
      this.fundListM = this.fundListM.filter(function(ele) {
        return ele.code != id;
      });

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
      }

      chrome.storage.sync.set(
        {
          fundListM: this.fundListM,
        },
        () => {
          this.getData();
        }
      );
    },
    handleDragStart(e, item) {
      this.dragging = item;
    },
    handleDragOver(e) {
      e.dataTransfer.dropEffect = "move";
    },
    handleDragEnd(e, item) {
      this.dragging = null;
      if (item.fundcode) {
        chrome.storage.sync.set(
          {
            fundListM: this.fundListM,
          },
          () => {}
        );
      } else if (item.f12) {
        chrome.storage.sync.set(
          {
            seciList: this.seciList,
          },
          () => {}
        );
      }
    },
    handleDragEnter(e, item, index) {
      // 基金排序
      if (this.dragging && this.dragging.fundcode && item.fundcode) {
        e.dataTransfer.effectAllowed = "move";
        if (item.fundcode === this.dragging.fundcode) {
          return;
        }
        const newItems = [...this.fundListM];
        const src = newItems.findIndex((n) => n.code == this.dragging.fundcode);
        const dst = newItems.findIndex((n) => n.code == item.fundcode);
        // // 替换
        newItems.splice(dst, 0, ...newItems.splice(src, 1));

        this.fundListM = newItems;

        //数据列表也同步更新
        const newDataItems = [...this.dataList];
        const dataSrc = newDataItems.findIndex(
          (n) => n.fundcode == this.dragging.fundcode
        );
        const dataDst = newDataItems.findIndex(
          (n) => n.fundcode == item.fundcode
        );
        newDataItems.splice(dataDst, 0, ...newDataItems.splice(dataSrc, 1));
        this.dataList = newDataItems;
      } else if (this.dragging && this.dragging.f12 && item.f12) {
        e.dataTransfer.effectAllowed = "move";
        if (item.f12 === this.dragging.f12) {
          return;
        }
        const newIndItems = [...this.seciList];
        const indSrc = newIndItems.findIndex(
          (n) => n.split(".")[1] == this.dragging.f12
        );
        const indDst = newIndItems.findIndex(
          (n) => n.split(".")[1] == item.f12
        );
        console.log(newIndItems);
        newIndItems.splice(indDst, 0, ...newIndItems.splice(indSrc, 1));
        console.log(newIndItems);
        this.seciList = newIndItems;

        const newIndDataItems = [...this.indFundData];
        const indDataSrc = newIndDataItems.findIndex(
          (n) => n.f12 == this.dragging.f12
        );
        const indDataDst = newIndDataItems.findIndex((n) => n.f12 == item.f12);
        newIndDataItems.splice(
          indDataDst,
          0,
          ...newIndDataItems.splice(indDataSrc, 1)
        );
        this.indFundData = newIndDataItems;
      }
    },
  },
};
</script>

<style lang="scss" scoped>
.container {
  min-width: 400px;
  min-height: 150px;
  overflow-y: auto;
  padding: 10px 7px;
  box-sizing: border-box;
  font-size: 12px;
  font-family: "Helvetica Neue", Helvetica, Arial, "PingFang SC",
    "Hiragino Sans GB", "Heiti SC", "Microsoft YaHei", "WenQuanYi Micro Hei",
    sans-serif;
}

.more-height {
  height: 415px;
}

.more-width {
  width: 790px;
}

.table-more-height {
  min-height: 160px;
}
.table-drag {
  cursor: move;
}
.num-all-width {
  min-width: 520px;
}

.num-width-1 {
  min-width: 420px;
}
.num-width-2 {
  min-width: 470px;
}
.num-width-3 {
  min-width: 540px;
}
.num-width-4 {
  min-width: 620px;
}
.num-width-5 {
  min-width: 690px;
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
  margin: 0 3px;
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
  width: 75px;
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
  flex: 1;
  margin: 0 4px;
  text-align: center;
  h5 {
    margin: 4px 0;
    font-size: 12px;
    .dltBtn {
      margin-left: 3px;
    }
  }
  p {
    margin: 4px 0;
  }
  .addSeci {
    margin: 10px auto;
    width: 40px;
    height: 40px;
    cursor: pointer;
    line-height: 40px;
    border: 1px solid #dcdfe6;
    border-radius: 50%;
  }
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
  display: flex;
  margin: 0 -3px;
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

//暗黑主题
.container.darkMode {
  color: rgba($color: #ffffff, $alpha: 0.6);
  background-color: #121212;
  .btn {
    background-color: rgba($color: #ffffff, $alpha: 0.16);
    color: rgba($color: #ffffff, $alpha: 0.6);
    border: 1px solid rgba($color: #ffffff, $alpha: 0.6);
  }
  .primary {
    border: 1px solid rgba($color: #409eff, $alpha: 0.6);
    background-color: rgba($color: #409eff, $alpha: 0.6);
  }
  /deep/ .el-input__inner {
    background-color: rgba($color: #ffffff, $alpha: 0.16);
    color: rgba($color: #ffffff, $alpha: 0.6);
  }
  /deep/ .el-select__input {
    color: rgba($color: #ffffff, $alpha: 0.6);
  }

  /deep/ tbody tr:hover {
    background-color: rgba($color: #ffffff, $alpha: 0.08);
  }

  .slt {
    border: 1px solid rgba($color: #67c23a, $alpha: 0.6);
    background-color: rgba($color: #67c23a, $alpha: 0.6);
  }

  .btn.red {
    border: 1px solid rgba($color: #f56c6c, $alpha: 0.6);
    background-color: rgba($color: #f56c6c, $alpha: 0.6);
  }

  .btn-up {
    border: 1px solid rgba($color: #f56c6c, $alpha: 0.6);
    background-color: rgba($color: #f56c6c, $alpha: 0.6);
  }

  .btn-down {
    border: 1px solid rgba($color: #4eb61b, $alpha: 0.6);
    background-color: rgba($color: #4eb61b, $alpha: 0.6);
  }

  .tab-col {
    background-color: rgba($color: #ffffff, $alpha: 0.09);
    border-radius: 5px;
  }

  table {
    background-color: rgba($color: #ffffff, $alpha: 0.12);
    border-radius: 5px;
  }

  ::placeholder {
    color: rgba($color: #ffffff, $alpha: 0.38);
  }

  /deep/ .el-select .el-input.is-focus .el-input__inner {
    border-color: rgba($color: #409eff, $alpha: 0.6);
  }

  /deep/ .el-select .el-tag {
    background-color: rgba($color: #ffffff, $alpha: 0.14);
    color: rgba($color: #ffffff, $alpha: 0.6);
  }

  /deep/ .el-select-dropdown {
    background-color: #383838;
    border: 1px solid rgba($color: #ffffff, $alpha: 0.38);
    .popper__arrow::after {
      border-bottom-color: #383838;
    }
    .el-scrollbar {
      background-color: rgba($color: #ffffff, $alpha: 0.16);
    }
    .el-select-dropdown__item {
      color: rgba($color: #ffffff, $alpha: 0.6);
    }

    .el-select-dropdown__item.hover,
    .el-select-dropdown__item:hover {
      background-color: rgba($color: #ffffff, $alpha: 0.08);
    }
    .el-select-dropdown__item.selected {
      color: rgba($color: #409eff, $alpha: 0.6);
      background-color: rgba($color: #ffffff, $alpha: 0.08);
    }
    .el-select-dropdown__item.selected::after {
      color: rgba($color: #409eff, $alpha: 0.6);
    }
  }

  /deep/ .el-switch__label.is-active {
    color: rgba($color: #409eff, $alpha: 0.87);
  }
  /deep/ .el-switch__label {
    color: rgba($color: #ffffff, $alpha: 0.6);
  }
}
</style>
