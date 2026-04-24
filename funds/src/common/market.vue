<template>
  <div class="market-container" :class="darkMode ? 'darkMode' : ''">
    <div class="content-box">
      <h5>行情中心</h5>
      <el-tabs v-model="activeName" type="border-card" @tab-click="handleClick">
        <el-tab-pane label="大盘资金" name="first">
          <market-line :darkMode="darkMode" ref="first"></market-line>
        </el-tab-pane>
        <el-tab-pane label="行业板块" name="second">
          <market-bar :darkMode="darkMode" ref="second"></market-bar>
        </el-tab-pane>
        <el-tab-pane label="北向资金" name="third">
          <market-S2N :darkMode="darkMode" ref="third"></market-S2N>
        </el-tab-pane>
        <el-tab-pane label="南向资金" name="fourth">
          <market-N2S :darkMode="darkMode" ref="fourth"></market-N2S>
        </el-tab-pane>
      </el-tabs>
    </div>
  </div>
</template>

<script>
import marketLine from "./marketLine";
import marketBar from "./marketBar";
import marketS2N from "./marketS2N";
import marketN2S from "./marketN2S";

export default {
  components: {
    marketLine,
    marketBar,
    marketS2N,
    marketN2S,
  },
  name: "market",
  props: {
    darkMode: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      activeName: "first",
      boxShadow: false,
      isInitialized: false,
    };
  },
  watch: {},
  mounted() {
    this.init();
  },
  methods: {
    handleClick(tab, event) {
      this.activeName = tab.name;
      this.$nextTick(() => {
        this.initChartByTab(tab.name);
      });
    },
    initChartByTab(tabName) {
      if (tabName === 'first' && this.$refs.first && this.$refs.first.init) {
        this.$refs.first.init();
      } else if (tabName === 'second' && this.$refs.second && this.$refs.second.init) {
        this.$refs.second.init();
      } else if (tabName === 'third' && this.$refs.third && this.$refs.third.init) {
        this.$refs.third.init();
      } else if (tabName === 'fourth' && this.$refs.fourth && this.$refs.fourth.init) {
        this.$refs.fourth.init();
      }
    },
    init() {
      if (this.isInitialized) return;
      this.boxShadow = true;
      this.activeName = 'first';
      this.isInitialized = true;
      this.$nextTick(() => {
        this.initChartByTab(this.activeName);
      });
    },
    close() {
      this.boxShadow = false;
      this.$emit("close", false);
    },
  },
};
</script>

<style lang="scss" scoped>
.market-container {
  width: 100%;
  height: 100%;
}

.content-box {
  width: 100%;
  background: #ffffff;
  border-radius: 8px;
  padding: 0 10px 10px;
  text-align: center;
  line-height: 1;
  position: relative;
  h5 {
    margin: 0;
    padding: 15px 0;
    font-size: 16px;
    font-weight: 500;
    color: #303133;
    border-bottom: 1px solid #ebeef5;
    margin-bottom: 15px;
  }
  :deep(.el-tabs__item) {
    padding: 0 20px;
    height: 40px;
    line-height: 40px;
    font-size: 14px;
  }
  :deep(.el-tabs--border-card) {
    border: none;
    box-shadow: none;
  }
  :deep(.el-tabs__content) {
    padding: 15px 0;
  }
}

.market-container.darkMode {
  .content-box {
    background-color: #1e1e1e;
    h5 {
      color: rgba(255, 255, 255, 0.87);
      border-bottom-color: rgba(255, 255, 255, 0.12);
    }
  }
  :deep(.el-tabs--border-card) {
    background-color: #1e1e1e;
    border: 1px solid rgba(255, 255, 255, 0.12);
    .el-tabs__header {
      background-color: rgba(255, 255, 255, 0.05);
      border-bottom: 1px solid rgba(255, 255, 255, 0.12);
      .el-tabs__item {
        color: rgba(255, 255, 255, 0.6);
      }
      .el-tabs__item.is-active {
        background-color: rgba(64, 158, 255, 0.2);
        color: rgba(64, 158, 255, 0.87);
        border-right-color: rgba(255, 255, 255, 0.12);
        border-left-color: rgba(255, 255, 255, 0.12);
      }
    }
  }
  :deep(.el-radio-button--mini .el-radio-button__inner) {
    background-color: rgba(255, 255, 255, 0.16);
    color: rgba(255, 255, 255, 0.6);
    border: 1px solid rgba(255, 255, 255, 0.12);
  }
  :deep(.el-radio-button__orig-radio:checked + .el-radio-button__inner) {
    background-color: rgba(64, 158, 255, 0.6);
    color: rgba(255, 255, 255, 0.87);
    border-color: rgba(64, 158, 255, 0.6);
  }
}
</style>
