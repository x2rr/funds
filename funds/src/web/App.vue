<template>
  <div id="app" class="web-container">
    <div class="web-header" :class="{ darkMode: darkMode }">
      <h1>自选基金助手</h1>
      <p>实时查看您关注的基金，助您快速获取实时数据</p>
    </div>
    
    <div class="web-main" :class="{ darkMode: darkMode }">
      <div class="web-nav">
        <div 
          class="web-nav-item" 
          :class="{ active: activeTab === 'main' }"
          @click="activeTab = 'main'"
        >
          基金管理
        </div>
        <div 
          class="web-nav-item" 
          :class="{ active: activeTab === 'settings' }"
          @click="activeTab = 'settings'"
        >
          设置
        </div>
      </div>
      
      <div class="web-content">
        <div v-show="activeTab === 'main'">
          <div class="container" ref="app" :class="containerClass" :style="[zoom, grayscale, opacity]">
            <div>
              <div class="tab-row" v-if="isGetStorage" v-loading="loadingInd">
                <div v-for="(el, index) in indFundData" :key="el.f12" class="tab-col indFund">
                  <h5>{{ el.f14 }}</h5>
                  <p :class="el.f3 >= 0 ? 'up' : 'down'">{{ el.f2 }}</p>
                  <p :class="el.f3 >= 0 ? 'up' : 'down'">{{ el.f4 }}&nbsp;&nbsp;{{ el.f3 }}%</p>
                </div>
              </div>
              
              <div class="table-row" v-if="isGetStorage" v-loading="loadingList">
                <table>
                  <thead>
                    <tr>
                      <th class="align-left">基金名称（{{ dataList.length }}）</th>
                      <th @click="sortList('gszzl')" class="pointer">涨跌幅</th>
                      <th v-if="!isEdit">更新时间</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="(el, index) in dataList" :key="el.fundcode">
                      <td class="fundName align-left" :title="el.name">
                        <span class="hasReplace-tip" v-if="el.hasReplace">✔</span>{{ el.name }}
                      </td>
                      <td :class="el.gszzl >= 0 ? 'up' : 'down'">{{ el.gszzl }}%</td>
                      <td v-if="!isEdit">{{ el.gztime }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
            
            <div class="input-row">
              <input class="btn" type="button" @click="market" value="行情中心" />
              <input class="btn" type="button" @click="fundCompare" value="基金对比" />
              <input class="btn" type="button" :value="isEdit ? '完成编辑' : '编辑'" @click="isEdit = !isEdit" />
              <input class="btn" type="button" value="日志" @click="changelog" />
            </div>
            
            <div class="refresh" :class="{ isRefresh: isRefresh }" @click="refresh">
              <i class="el-icon-refresh"></i>
            </div>
          </div>
        </div>
        
        <div v-show="activeTab === 'settings'" style="padding: 20px;">
          <div class="container">
            <ul class="setting-list">
              <li>
                <div class="list-title">主题与页面设置</div>
                <div class="select-row">
                  <el-switch v-model="darkMode" @change="changeDarkMode" active-color="#484848" inactive-color="#13ce66" inactive-text="标准模式" active-text="暗色模式"></el-switch>
                </div>
              </li>
              <li>
                <div class="list-title">基金配置信息导入与导出</div>
                <div style="padding:8px 0 10px">
                  <input class="btn" type="button" value="导出配置文件" @click="exportConfig" />
                  <a class="exportBtn" ref="configMsg" :href="configHref" download="自选基金助手配置文件.json"></a>
                  <a href="javascript:;" class="uploadFile btn">导入配置文件
                    <input ref="importInput" type="file" accept="application/json" @change="importInput" />
                  </a>
                </div>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
const { version } = require("../../package.json");

export default {
  data() {
    return {
      activeTab: 'main',
      isEdit: false,
      indFundData: [],
      dataList: [],
      loadingInd: false,
      loadingList: true,
      isGetStorage: false,
      darkMode: false,
      zoom: { zoom: 1 },
      grayscale: {},
      grayscaleValue: 0,
      opacity: {},
      opacityValue: 0,
      isRefresh: false,
      sortType: { gszzl: "none" },
      seciList: ["1.000001", "1.000300", "0.399001", "0.399006"],
      fundListM: [],
      userId: null,
      configHref: null,
      isLiveUpdate: false,
      isDuringDate: false,
      containerClass: '',
    };
  },
  mounted() {
    this.init();
  },
  methods: {
    setStorage(data) {
      try {
        const existing = this.getStorage();
        const merged = { ...existing, ...data };
        localStorage.setItem('funds_helper', JSON.stringify(merged));
      } catch (e) {
        console.error('保存数据失败:', e);
      }
    },
    getStorage(keys = null) {
      try {
        const stored = localStorage.getItem('funds_helper');
        if (!stored) {
          return {};
        }
        const data = JSON.parse(stored);
        if (keys === null) {
          return data;
        }
        const result = {};
        keys.forEach(key => {
          if (data.hasOwnProperty(key)) {
            result[key] = data[key];
          }
        });
        return result;
      } catch (e) {
        console.error('读取数据失败:', e);
        return {};
      }
    },
    init() {
      const res = this.getStorage();
      this.darkMode = res.darkMode ? res.darkMode : false;
      this.seciList = res.seciList ? res.seciList : this.seciList;
      this.fundListM = res.fundListM ? res.fundListM : [];
      this.userId = res.userId ? res.userId : this.getGuid();
      this.grayscaleValue = res.grayscaleValue ? res.grayscaleValue : 0;
      this.opacityValue = res.opacityValue ? res.opacityValue : 0;
      
      this.grayscale = { filter: "grayscale(" + this.grayscaleValue / 100 + ")" };
      this.opacity = { opacity: 1 - this.opacityValue / 100 };
      
      this.isGetStorage = true;
      this.getIndFundData();
      this.getData();
    },
    getGuid() {
      return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, function(c) {
        var r = (Math.random() * 16) | 0;
        var v = c == "x" ? r : (r & 0x3) | 0x8;
        return v.toString(16);
      });
    },
    refresh() {
      this.init();
      this.isRefresh = true;
      setTimeout(() => {
        this.isRefresh = false;
      }, 1500);
    },
    getIndFundData() {
      if (this.seciList.length === 0) {
        this.loadingInd = false;
        return;
      }
      this.loadingInd = true;
      let seciListStr = this.seciList.join(",");
      let url = "https://push2.eastmoney.com/api/qt/ulist.np/get?fltt=2&fields=f2,f3,f4,f12,f13,f14&secids=" + seciListStr + "&_=" + new Date().getTime();
      this.$axios.get(url).then((res) => {
        this.loadingInd = false;
        if (res.data && res.data.data && res.data.data.diff) {
          this.indFundData = res.data.data.diff;
        }
      }).catch(() => {
        this.loadingInd = false;
      });
    },
    getData() {
      if (this.fundListM.length === 0) {
        this.loadingList = false;
        return;
      }
      this.loadingList = true;
      let fundlist = this.fundListM.map((val) => val.code).join(",");
      let url = "https://fundmobapi.eastmoney.com/FundMNewApi/FundMNFInfo?pageIndex=1&pageSize=200&plat=Android&appType=ttjj&product=EFund&Version=1&deviceid=" + this.userId + "&Fcodes=" + fundlist;
      this.$axios.get(url).then((res) => {
        this.loadingList = false;
        if (res.data && res.data.Datas) {
          let dataList = res.data.Datas.map((val) => {
            let data = {
              fundcode: val.FCODE,
              name: val.SHORTNAME,
              jzrq: val.PDATE,
              dwjz: isNaN(val.NAV) ? null : val.NAV,
              gsz: isNaN(val.GSZ) ? null : val.GSZ,
              gszzl: isNaN(val.GSZZL) ? 0 : val.GSZZL,
              gztime: val.GZTIME,
            };
            if (val.PDATE != "--" && val.PDATE == val.GZTIME.substr(0, 10)) {
              data.gsz = val.NAV;
              data.gszzl = isNaN(val.NAVCHGRT) ? 0 : val.NAVCHGRT;
              data.hasReplace = true;
            }
            let slt = this.fundListM.filter((item) => item.code == data.fundcode);
            data.num = slt[0] ? slt[0].num : 0;
            data.cost = slt[0] ? slt[0].cost : 0;
            return data;
          });
          this.dataList = dataList;
        }
      }).catch(() => {
        this.loadingList = false;
      });
    },
    changeDarkMode() {
      this.setStorage({ darkMode: this.darkMode });
    },
    exportConfig() {
      const res = this.getStorage();
      this.configHref = "data:text/plain," + encodeURIComponent(JSON.stringify(res, null, 2));
      setTimeout(() => {
        this.$refs["configMsg"].click();
      }, 100);
    },
    importInput(e) {
      let files = e.target.files;
      if (!files || !files.length) return;
      
      let reader = new FileReader();
      reader.onload = (event) => {
        try {
          let config = JSON.parse(event.target.result);
          this.setStorage(config);
          this.init();
          this.$message({
            message: "恭喜,导入配置成功！",
            type: "success",
            center: true,
          });
        } catch (e) {
          this.$message({
            message: "导入失败！",
            type: "error",
            center: true,
          });
        }
      };
      reader.readAsText(files[0]);
    },
    sortList(type) {
      this.sortType[type] = this.sortType[type] == "desc" ? "asc" : this.sortType[type] == "asc" ? "none" : "desc";
      if (this.sortType[type] == "none") {
        this.getData();
      } else {
        this.dataList = this.dataList.sort(this.compare(type, this.sortType[type]));
      }
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
    market() {
      this.$message({
        message: "行情中心功能开发中...",
        type: "info",
        center: true,
      });
    },
    fundCompare() {
      this.$message({
        message: "基金对比功能开发中...",
        type: "info",
        center: true,
      });
    },
    changelog() {
      this.$message({
        message: "更新日志功能开发中...",
        type: "info",
        center: true,
      });
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
  position: relative;
  font-size: 12px;
  font-family: "Helvetica Neue", Helvetica, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", "微软雅黑", Arial, sans-serif;
}

.refresh {
  position: absolute;
  right: 10px;
  width: 18px;
  bottom: 12px;
  cursor: pointer;
  i {
    color: #409eff;
    font-size: 18px;
    font-weight: bold;
  }
}

.refresh.isRefresh {
  animation: changDeg 1.5s linear 0s infinite;
}

@keyframes changDeg {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(-360deg);
  }
}

.tab-row {
  padding: 6px 0;
  display: flex;
  margin: 0 -3px;
}

.tab-col {
  flex: 1;
  margin: 0 4px;
  text-align: center;
  h5 {
    margin: 4px 0;
    font-size: 12px;
  }
  p {
    margin: 4px 0;
  }
}

.table-row {
  max-height: 425px;
  overflow-y: auto;
}

table {
  margin: 0 auto;
  width: 100%;
  border-collapse: collapse;
  text-align: right;
}

.align-left {
  text-align: left;
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

.input-row {
  text-align: center;
  margin-top: 10px;
}

.fundName {
  max-width: 150px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  cursor: pointer;
  user-select: none;
}

.fundName:hover {
  color: #409eff;
}

.hasReplace-tip {
  display: inline-block;
  padding: 0 2px;
  margin-right: 2px;
  border-radius: 2px;
  line-height: 12px;
  color: #409eff;
  border: 1px solid #409eff;
}

.pointer {
  cursor: pointer;
  user-select: none;
}

.setting-list {
  width: 600px;
  margin: 0 auto;
  text-align: left;
  padding: 0 10px 10px;
  border-radius: 8px;
}

.setting-list li {
  list-style: none;
  font-size: 16px;
  border-bottom: 1px solid #dddddd;
  padding: 10px 0;
}

.list-title {
  min-height: 34px;
  line-height: 34px;
  font-weight: bold;
}

.select-row {
  line-height: 35px;
  padding-left: 20px;
}

.exportBtn {
  visibility: hidden;
}

.uploadFile {
  text-decoration: none;
  display: inline-flex;
  position: relative;
  overflow: hidden;
}

.uploadFile input {
  position: absolute;
  font-size: 100px;
  cursor: pointer;
  right: 0;
  top: 0;
  opacity: 0;
}

.web-header {
  background: linear-gradient(135deg, #409eff 0%, #67c23a 100%);
  padding: 15px 20px;
  color: white;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  h1 {
    margin: 0;
    font-size: 24px;
    font-weight: 500;
  }
  p {
    margin: 5px 0 0;
    font-size: 14px;
    opacity: 0.9;
  }
}

.web-main {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
  overflow: hidden;
  margin: 20px;
}

.web-nav {
  display: flex;
  background: #fafafa;
  border-bottom: 1px solid #e4e7ed;
}

.web-nav-item {
  padding: 12px 24px;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  transition: all 0.3s;
  font-size: 14px;
  color: #606266;
}

.web-nav-item:hover {
  color: #409eff;
}

.web-nav-item.active {
  color: #409eff;
  border-bottom-color: #409eff;
  font-weight: 500;
}

.darkMode .web-header {
  background: linear-gradient(135deg, #1e3a5f 0%, #2d5a3f 100%);
}

.darkMode .web-main {
  background: #1e1e1e;
}

.darkMode .web-nav {
  background: #282828;
  border-bottom-color: #383838;
}

.darkMode .web-nav-item {
  color: rgba(255, 255, 255, 0.6);
}

.darkMode .web-nav-item:hover,
.darkMode .web-nav-item.active {
  color: rgba(64, 158, 255, 0.87);
}
</style>
