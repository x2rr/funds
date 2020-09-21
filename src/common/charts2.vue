<template>
  <div class="box">
    <div class="main-echarts" ref="mainCharts"></div>
    <div>
      <el-radio-group v-model="sltTimeRange" @change="changeTimeRange">
        <el-radio-button label="y">月</el-radio-button>
        <el-radio-button label="3y">季</el-radio-button>
        <el-radio-button label="6y">半年</el-radio-button>
        <el-radio-button label="n">一年</el-radio-button>
      </el-radio-group>
    </div>
  </div>
</template>

<script>
let echarts = require("echarts/lib/echarts");

import "./js/customed.js";
import "./js/dark.js"

require("echarts/lib/chart/line");

require("echarts/lib/component/tooltip");
require("echarts/lib/component/legend");

export default {
  name: "chatrs",
  props: {
    darkMode: {
      type: Boolean,
      default: false,
    },
    fund: {
      type: Object,
      required: true,
    },
    chartType: {
      type: String,
      required: true,
    },
  },
  data() {
    return {
      chartEL: null,
      myChart: null,
      minVal: null,
      maxVal: null,
      interVal: null,
      sltTimeRange: "y",
      chartTypeList: {
        DWJZ: {
          name: "单位净值",
        },
        LJJZ: {
          name: "累计净值",
        },
      },
      option: {},
    };
  },
  
  watch: {},
  computed: {
    defaultColor() {
      return this.darkMode ? "rgba(255,255,255,0.6)" : "#ccc";
    },
  },
  mounted() {
    this.init();
  },
  methods: {
    init() {
      this.chartEL = this.$refs.mainCharts;
      this.myChart = echarts.init(this.chartEL, this.darkMode?"dark":"customed");
      this.option = {
        tooltip: {
          trigger: "axis",
          formatter: (p) => {
            return `时间：${p[0].name}<br />${
              this.chartTypeList[this.chartType].name
            }：${p[0].value}`;
          },
        },
        grid: {
          top: 30,
          bottom: 30,
        },
        xAxis: {
          type: "category",
          data: [],
          axisLabel: {},
        },
        yAxis: {
          type: "value",
          scale: true,
          splitLine: {
            show: true,
            lineStyle: {
              type: "dashed",
              color: this.defaultColor
            },
          },
          data: [],
        },
        series: [
          {
            type: "line",
            data: [],
          },
        ],
      };
      this.getData();
    },
    changeTimeRange(val) {
      this.getData();
    },
    handle_num_range(data) {
      var _aa = Math.max.apply(null, data);
      var _bb = Math.min.apply(null, data);
      return [_aa, _bb];
    },
    getData() {
      if (this.chartType == "LJSY") {
        let url = `https://fundmobapi.eastmoney.com/FundMApi/FundYieldDiagramNew.ashx?FCODE=${
          this.fund.fundcode
        }&RANGE=${
          this.sltTimeRange
        }&deviceid=Wap&plat=Wap&product=EFund&version=2.0.0&_=${new Date().getTime()}`;
        this.$axios.get(url).then((res) => {
          let dataList = res.data.Datas;
          this.option.legend = {
            show: true,
          };
          this.option.tooltip.formatter = (p) => {
            return `时间：${p[0].name}<br />${p[0].seriesName}：${p[0].value}%<br />${p[1].seriesName}：${p[1].value}%`;
          };
          this.option.series = [
            {
              type: "line",
              name: "涨幅",
              data: dataList.map((item) => +item.YIELD),
            },
            {
              type: "line",
              name: res.data.Expansion.INDEXNAME,
              data: dataList.map((item) => +item.INDEXYIED),
            },
          ];
          this.option.xAxis.data = dataList.map((item) => item.PDATE);
          this.myChart.setOption(this.option);
        });
      } else {
        let url = `https://fundmobapi.eastmoney.com/FundMApi/FundNetDiagram.ashx?FCODE=${
          this.fund.fundcode
        }&RANGE=${
          this.sltTimeRange
        }&deviceid=Wap&plat=Wap&product=EFund&version=2.0.0&_=${new Date().getTime()}`;
        this.$axios.get(url).then((res) => {
          let dataList = res.data.Datas;
          this.option.series[0].data = dataList.map(
            (item) => +item[this.chartType]
          );
          this.option.tooltip.formatter = (p) => {
            return `时间：${p[0].name}<br />${
              this.chartTypeList[this.chartType].name
            }：${p[0].value}`;
          };
          this.option.legend = {
            show: false,
          };
          this.option.series[0].name = this.chartTypeList[this.chartType].name;
          this.option.xAxis.data = dataList.map((item) => item.FSRQ);
          this.myChart.setOption(this.option);
        });
      }
    },
  },
};
</script>

<style lang="scss" scoped>
.box {
  width: 100%;
  height: 100%;
}
.main-echarts {
  width: 100%;
  height: 240px;
}
</style>
