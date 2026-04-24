<template>
  <div v-if="boxShadow" class="shadow" :class="darkMode ? 'darkMode' : ''">
    <div class="content-box">
      <h5>基金对比分析</h5>
      <el-tabs v-model="activeName" type="border-card">
        <el-tab-pane label="对比概览" name="overview">
          <div class="overview-container">
            <div class="time-range-selector">
              <span class="label">选择对比周期：</span>
              <el-radio-group v-model="selectedPeriod" @change="changePeriod">
                <el-radio-button label="week">近一周</el-radio-button>
                <el-radio-button label="month">近一月</el-radio-button>
                <el-radio-button label="3month">近三月</el-radio-button>
                <el-radio-button label="year">近一年</el-radio-button>
                <el-radio-button label="3year">近三年</el-radio-button>
              </el-radio-group>
            </div>
            
            <div class="compare-table-container" v-loading="loading">
              <table class="compare-table">
                <thead>
                  <tr>
                    <th class="align-left">对比项目</th>
                    <th v-for="fund in compareData" :key="fund.fundcode">
                      {{ fund.name }}<br/>
                      <span class="fund-code">{{ fund.fundcode }}</span>
                    </th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td class="align-left">成立时间</td>
                    <td v-for="fund in compareData" :key="fund.fundcode + '_estab'">
                      {{ fund.establishDate || '--' }}
                    </td>
                  </tr>
                  <tr>
                    <td class="align-left">基金类型</td>
                    <td v-for="fund in compareData" :key="fund.fundcode + '_type'">
                      {{ fund.fundType || '--' }}
                    </td>
                  </tr>
                  <tr>
                    <td class="align-left">最新净值</td>
                    <td v-for="fund in compareData" :key="fund.fundcode + '_nav'">
                      {{ fund.latestNav || '--' }}
                      <span class="nav-date" v-if="fund.navDate">({{ fund.navDate }})</span>
                    </td>
                  </tr>
                  <tr>
                    <td class="align-left">基金规模</td>
                    <td v-for="fund in compareData" :key="fund.fundcode + '_scale'">
                      {{ fund.scale || '--' }}
                    </td>
                  </tr>
                  <tr>
                    <td class="align-left">基金公司</td>
                    <td v-for="fund in compareData" :key="fund.fundcode + '_company'">
                      {{ fund.company || '--' }}
                    </td>
                  </tr>
                  <tr>
                    <td class="align-left">基金经理</td>
                    <td v-for="fund in compareData" :key="fund.fundcode + '_manager'">
                      {{ fund.manager || '--' }}
                    </td>
                  </tr>
                  <tr class="highlight-row">
                    <td class="align-left">
                      {{ periodLabels[selectedPeriod] }}收益率
                      <span v-if="hasMissingData" class="warning-tip" title="部分基金成立时间较晚，数据可能不完整">⚠</span>
                    </td>
                    <td 
                      v-for="fund in compareData" 
                      :key="fund.fundcode + '_yield'"
                      :class="getYieldClass(fund.periodYield)"
                    >
                      <span v-if="fund.periodYield !== null && fund.periodYield !== undefined">
                        {{ formatYield(fund.periodYield) }}%
                        <span 
                          v-if="fund.isPartialData" 
                          class="partial-tip" 
                          title="该基金成立时间较晚，仅显示成立后数据"
                        >(部分)</span>
                      </span>
                      <span v-else>--</span>
                    </td>
                  </tr>
                  <tr>
                    <td class="align-left">近一月收益率</td>
                    <td 
                      v-for="fund in compareData" 
                      :key="fund.fundcode + '_1m'"
                      :class="getYieldClass(fund.yield1Month)"
                    >
                      {{ formatYield(fund.yield1Month) }}%
                    </td>
                  </tr>
                  <tr>
                    <td class="align-left">近三月收益率</td>
                    <td 
                      v-for="fund in compareData" 
                      :key="fund.fundcode + '_3m'"
                      :class="getYieldClass(fund.yield3Month)"
                    >
                      {{ formatYield(fund.yield3Month) }}%
                    </td>
                  </tr>
                  <tr>
                    <td class="align-left">近六月收益率</td>
                    <td 
                      v-for="fund in compareData" 
                      :key="fund.fundcode + '_6m'"
                      :class="getYieldClass(fund.yield6Month)"
                    >
                      {{ formatYield(fund.yield6Month) }}%
                    </td>
                  </tr>
                  <tr>
                    <td class="align-left">近一年收益率</td>
                    <td 
                      v-for="fund in compareData" 
                      :key="fund.fundcode + '_1y'"
                      :class="getYieldClass(fund.yield1Year)"
                    >
                      {{ formatYield(fund.yield1Year) }}%
                    </td>
                  </tr>
                  <tr>
                    <td class="align-left">近三年收益率</td>
                    <td 
                      v-for="fund in compareData" 
                      :key="fund.fundcode + '_3y'"
                      :class="getYieldClass(fund.yield3Year)"
                    >
                      {{ formatYield(fund.yield3Year) }}%
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </el-tab-pane>
        
        <el-tab-pane label="收益走势对比" name="chart">
          <div class="chart-container">
            <div class="time-range-selector">
              <span class="label">选择对比周期：</span>
              <el-radio-group v-model="selectedPeriod" @change="changePeriod">
                <el-radio-button label="week">近一周</el-radio-button>
                <el-radio-button label="month">近一月</el-radio-button>
                <el-radio-button label="3month">近三月</el-radio-button>
                <el-radio-button label="year">近一年</el-radio-button>
                <el-radio-button label="3year">近三年</el-radio-button>
              </el-radio-group>
            </div>
            <div class="main-echarts" ref="mainCharts" v-loading="loading"></div>
            <div class="chart-note" v-if="hasMissingData">
              <span class="warning-icon">⚠</span>
              注：部分基金成立时间较晚，图表中仅显示其成立后的走势数据
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>

      <div class="tab-row">
        <input class="btn" type="button" value="返回列表" @click="close" />
      </div>
    </div>
  </div>
</template>

<script>
let echarts = require("echarts/lib/echarts");
import "./js/customed.js";
import "./js/dark.js";
require("echarts/lib/chart/line");
require("echarts/lib/component/tooltip");
require("echarts/lib/component/legend");

export default {
  name: "fundCompareResult",
  props: {
    darkMode: {
      type: Boolean,
      default: false,
    },
    selectedFunds: {
      type: Array,
      default: () => [],
    },
  },
  data() {
    return {
      activeName: "overview",
      boxShadow: false,
      loading: false,
      selectedPeriod: "month",
      compareData: [],
      chartData: {},
      myChart: null,
      hasMissingData: false,
      periodLabels: {
        week: "近一周",
        month: "近一月",
        "3month": "近三月",
        year: "近一年",
        "3year": "近三年",
      },
      periodMap: {
        week: "y",
        month: "y",
        "3month": "3y",
        year: "n",
        "3year": "3n",
      },
      colors: ["#409eff", "#f56c6c", "#67c23a"],
    };
  },
  methods: {
    init() {
      this.boxShadow = true;
      this.activeName = "overview";
      this.selectedPeriod = "month";
      this.compareData = [];
      this.hasMissingData = false;
      this.loadAllData();
    },
    close() {
      this.boxShadow = false;
      if (this.myChart) {
        this.myChart.dispose();
        this.myChart = null;
      }
      this.$emit("close", false);
    },
    loadAllData() {
      this.loading = true;
      this.compareData = this.selectedFunds.map((fund) => ({
        fundcode: fund.fundcode,
        name: fund.name,
      }));
      
      const promises = this.selectedFunds.map((fund, index) =>
        this.loadFundData(fund.fundcode, index)
      );
      
      Promise.all(promises)
        .then(() => {
          this.loading = false;
          this.checkMissingData();
          this.initChart();
        })
        .catch(() => {
          this.loading = false;
        });
    },
    async loadFundData(fundcode, index) {
      try {
        const infoData = await this.loadFundInfo(fundcode);
        const yieldData = await this.loadFundYield(fundcode);
        
        this.$set(this.compareData, index, {
          ...this.compareData[index],
          ...infoData,
          ...yieldData,
        });
        
        await this.loadChartData(fundcode, index);
      } catch (error) {
        console.error(`加载基金 ${fundcode} 数据失败:`, error);
      }
    },
    loadFundInfo(fundcode) {
      return new Promise((resolve) => {
        let url = `/api/fundmobapi/FundMApi/FundBaseTypeInformation.ashx?FCODE=${fundcode}&deviceid=Wap&plat=Wap&product=EFund&version=2.0.0&_=${new Date().getTime()}`;
        this.$axios.get(url).then((res) => {
          const data = res.data.Datas;
          resolve({
            establishDate: data.ESTABDATE || "--",
            fundType: data.FTYPE || "--",
            latestNav: data.DWJZ || "--",
            navDate: data.FSRQ || "",
            scale: this.numberFormat(data.ENDNAV),
            company: data.JJGS || "--",
            manager: data.JJJL || "--",
          });
        }).catch(() => {
          resolve({
            establishDate: "--",
            fundType: "--",
            latestNav: "--",
            navDate: "",
            scale: "--",
            company: "--",
            manager: "--",
          });
        });
      });
    },
    loadFundYield(fundcode) {
      return new Promise((resolve) => {
        let url = `/api/fundmobapi/FundMApi/FundBaseTypeInformation.ashx?FCODE=${fundcode}&deviceid=Wap&plat=Wap&product=EFund&version=2.0.0&_=${new Date().getTime()}`;
        this.$axios.get(url).then((res) => {
          const data = res.data.Datas;
          resolve({
            yield1Month: data.SYL_Y,
            yield3Month: data.SYL_3Y,
            yield6Month: data.SYL_6Y,
            yield1Year: data.SYL_1N,
            yield3Year: data.SYL_3N,
          });
        }).catch(() => {
          resolve({
            yield1Month: null,
            yield3Month: null,
            yield6Month: null,
            yield1Year: null,
            yield3Year: null,
          });
        });
      });
    },
    loadChartData(fundcode, index) {
      return new Promise((resolve) => {
        const range = this.periodMap[this.selectedPeriod];
        let url = `/api/fundmobapi/FundMApi/FundYieldDiagramNew.ashx?FCODE=${fundcode}&RANGE=${range}&deviceid=Wap&plat=Wap&product=EFund&version=2.0.0&_=${new Date().getTime()}`;
        this.$axios.get(url).then((res) => {
          let dataList = res.data.Datas;
          if (dataList && dataList.length > 0) {
            let dates = dataList.map((item) => item.PDATE);
            let yields = dataList.map((item) => +item.YIELD);
            
            if (this.selectedPeriod === "week" && dataList.length > 7) {
              const startIndex = dataList.length - 7;
              dates = dates.slice(startIndex);
              yields = yields.slice(startIndex);
            }
            
            const firstYield = yields[0];
            const lastYield = yields[yields.length - 1];
            const periodYield = lastYield - firstYield;
            
            this.$set(this.compareData, index, {
              ...this.compareData[index],
              periodYield: periodYield,
              isPartialData: false,
            });
            
            this.$set(this.chartData, index, {
              dates: dates,
              yields: yields,
            });
          } else {
            this.$set(this.compareData, index, {
              ...this.compareData[index],
              periodYield: null,
              isPartialData: true,
            });
          }
          resolve();
        }).catch(() => {
          this.$set(this.compareData, index, {
            ...this.compareData[index],
            periodYield: null,
            isPartialData: false,
          });
          resolve();
        });
      });
    },
    checkMissingData() {
      this.hasMissingData = this.compareData.some((fund) => fund.isPartialData);
    },
    changePeriod() {
      this.loading = true;
      const promises = this.selectedFunds.map((fund, index) =>
        this.loadChartData(fund.fundcode, index)
      );
      
      Promise.all(promises)
        .then(() => {
          this.loading = false;
          this.checkMissingData();
          this.updateChart();
        })
        .catch(() => {
          this.loading = false;
        });
    },
    initChart() {
      if (!this.$refs.mainCharts) return;
      
      this.myChart = echarts.init(
        this.$refs.mainCharts,
        this.darkMode ? "dark" : "customed"
      );
      this.updateChart();
    },
    updateChart() {
      if (!this.myChart) return;
      
      const allDates = new Set();
      this.chartData && Object.values(this.chartData).forEach((data) => {
        data.dates && data.dates.forEach((date) => allDates.add(date));
      });
      
      const sortedDates = Array.from(allDates).sort();
      
      const series = this.compareData.map((fund, index) => {
        const data = this.chartData[index];
        const values = [];
        
        sortedDates.forEach((date) => {
          if (data && data.dates) {
            const dateIndex = data.dates.indexOf(date);
            if (dateIndex !== -1) {
              values.push(data.yields[dateIndex]);
            } else {
              values.push(null);
            }
          } else {
            values.push(null);
          }
        });
        
        return {
          name: `${fund.name}(${fund.fundcode})`,
          type: "line",
          data: values,
          smooth: true,
          itemStyle: {
            color: this.colors[index % this.colors.length],
          },
          lineStyle: {
            color: this.colors[index % this.colors.length],
          },
        };
      });
      
      const option = {
        tooltip: {
          trigger: "axis",
          formatter: (params) => {
            let result = `时间：${params[0].name}<br/>`;
            params.forEach((p) => {
              if (p.value !== null && p.value !== undefined) {
                result += `${p.seriesName}: ${p.value.toFixed(2)}%<br/>`;
              }
            });
            return result;
          },
        },
        legend: {
          show: true,
          type: "scroll",
          orient: "horizontal",
          top: 10,
          left: "center",
          width: "80%",
          data: this.compareData.map((fund) => `${fund.name}(${fund.fundcode})`),
          tooltip: {
            show: true,
          },
          itemWidth: 10,
          itemHeight: 10,
          textStyle: {
            fontSize: 12,
          },
          pageButtonItemGap: 5,
          pageButtonGap: 5,
          pageIconColor: "#333",
          pageIconInactiveColor: "#aaa",
          pageTextStyle: {
            color: "#333",
          },
        },
        grid: {
          top: 60,
          bottom: 50,
          left: 60,
          right: 30,
        },
        xAxis: {
          type: "category",
          data: sortedDates,
          axisLabel: {
            rotate: 45,
            interval: Math.floor(sortedDates.length / 10),
          },
        },
        yAxis: {
          type: "value",
          scale: true,
          axisLabel: {
            formatter: (val) => val.toFixed(1) + "%",
          },
          splitLine: {
            lineStyle: {
              type: "dashed",
            },
          },
        },
        series: series,
      };
      
      this.myChart.setOption(option, true);
    },
    getYieldClass(value) {
      if (value === null || value === undefined || value === "--") return "";
      const num = parseFloat(value);
      if (isNaN(num)) return "";
      return num >= 0 ? "up" : "down";
    },
    formatYield(value) {
      if (value === null || value === undefined || value === "--") return "--";
      const num = parseFloat(value);
      if (isNaN(num)) return "--";
      return num >= 0 ? "+" + num.toFixed(2) : num.toFixed(2);
    },
    numberFormat(value) {
      if (!value) return "--";
      var k = 10000,
        sizes = ["", "万", "亿", "万亿"],
        i;
      if (value < k) {
        return value + "元";
      } else {
        i = Math.floor(Math.log(value) / Math.log(k));
        return (value / Math.pow(k, i)).toFixed(2) + sizes[i];
      }
    },
  },
  beforeDestroy() {
    if (this.myChart) {
      this.myChart.dispose();
    }
  },
};
</script>

<style lang="scss" scoped>
.shadow {
  position: absolute;
  width: 100%;
  height: 100%;
  padding: 20px;
  box-sizing: border-box;
  z-index: 1001;
  top: 0;
  left: 0;
  background-color: rgba(0, 0, 0, 0.7);
}

.content-box {
  background: #ffffff;
  border-radius: 15px;
  padding: 0 10px;
  margin: 0 auto;
  text-align: center;
  line-height: 1;
  vertical-align: middle;
  position: relative;
  h5 {
    margin: 0;
    padding: 13px;
  }

  :deep(.el-tabs__item) {
    padding: 0 15px;
    height: 34px;
    line-height: 34px;
  }
}

.overview-container {
  padding: 10px;
}

.time-range-selector {
  margin-bottom: 15px;
  text-align: left;
  
  .label {
    margin-right: 10px;
    font-weight: bold;
  }
}

.compare-table-container {
  max-height: 400px;
  overflow-y: auto;
}

.compare-table {
  width: 100%;
  border-collapse: collapse;
  text-align: center;
  
  th, td {
    padding: 10px 8px;
    border: 1px solid #ebeef5;
  }
  
  th {
    background-color: #f5f7fa;
    font-weight: bold;
    color: #606266;
  }
  
  .align-left {
    text-align: left;
    padding-left: 15px;
    font-weight: bold;
    background-color: #fafafa;
  }
  
  .fund-code {
    font-size: 12px;
    color: #909399;
    font-weight: normal;
  }
  
  .nav-date {
    font-size: 12px;
    color: #909399;
    margin-left: 5px;
  }
  
  .highlight-row {
    background-color: #ecf5ff;
    font-weight: bold;
  }
  
  .warning-tip {
    margin-left: 5px;
    cursor: help;
  }
  
  .partial-tip {
    font-size: 11px;
    color: #e6a23c;
    cursor: help;
  }
  
  .up {
    color: #f56c6c;
    font-weight: bold;
  }
  
  .down {
    color: #4eb61b;
    font-weight: bold;
  }
}

.chart-container {
  padding: 10px;
}

.main-echarts {
  width: 100%;
  height: 350px;
}

.chart-note {
  margin-top: 10px;
  padding: 8px 15px;
  background-color: #fdf6ec;
  border: 1px solid #faecd8;
  border-radius: 4px;
  color: #e6a23c;
  font-size: 12px;
  text-align: left;
  
  .warning-icon {
    margin-right: 5px;
  }
}

.btn {
  display: inline-block;
  line-height: 1;
  cursor: pointer;
  background: #fff;
  padding: 8px 15px;
  border-radius: 3px;
  font-size: 12px;
  color: #000000;
  margin: 0 5px;
  outline: none;
  border: 1px solid #dcdfe6;
}

.tab-row {
  padding: 12px 0;
}

.shadow.darkMode {
  .content-box {
    background-color: #373737;
  }
  .btn {
    background-color: rgba($color: #ffffff, $alpha: 0.16);
    color: rgba($color: #ffffff, $alpha: 0.6);
    border: 1px solid rgba($color: #ffffff, $alpha: 0.6);
  }

  :deep(.el-tabs--border-card) {
    background-color: #373737;
    border: 1px solid rgba($color: #ffffff, $alpha: 0.37);
    .el-tabs__header {
      background-color: rgba($color: #ffffff, $alpha: 0.16);
      border-bottom: 1px solid rgba($color: #ffffff, $alpha: 0.37);

      .el-tabs__item.is-active {
        background-color: rgba($color: #409eff, $alpha: 0.6);
        color: rgba($color: #ffffff, $alpha: 0.6);
        border-right-color: rgba($color: #ffffff, $alpha: 0.37);
        border-left-color: rgba($color: #ffffff, $alpha: 0.37);
      }
    }
  }

  :deep(.el-radio-button--mini .el-radio-button__inner) {
    background-color: rgba($color: #ffffff, $alpha: 0.16);
    color: rgba($color: #ffffff, $alpha: 0.6);
    border: 1px solid rgba($color: #ffffff, $alpha: 0.37);
  }

  :deep(.el-radio-button__orig-radio:checked + .el-radio-button__inner) {
    background-color: rgba($color: #409eff, $alpha: 0.6);
    color: rgba($color: #ffffff, $alpha: 0.6);
    border-color: rgba($color: #409eff, $alpha: 0.37);
  }

  .time-range-selector {
    .label {
      color: rgba($color: #ffffff, $alpha: 0.8);
    }
  }

  .compare-table {
    th, td {
      border-color: rgba($color: #ffffff, $alpha: 0.2);
    }
    
    th {
      background-color: rgba($color: #ffffff, $alpha: 0.1);
      color: rgba($color: #ffffff, $alpha: 0.8);
    }
    
    .align-left {
      background-color: rgba($color: #ffffff, $alpha: 0.08);
      color: rgba($color: #ffffff, $alpha: 0.8);
    }
    
    .fund-code, .nav-date {
      color: rgba($color: #ffffff, $alpha: 0.5);
    }
    
    .highlight-row {
      background-color: rgba($color: #409eff, $alpha: 0.15);
    }
    
    .chart-note {
      background-color: rgba($color: #e6a23c, $alpha: 0.1);
      border-color: rgba($color: #e6a23c, $alpha: 0.3);
      color: rgba($color: #e6a23c, $alpha: 0.8);
    }
  }
}
</style>
