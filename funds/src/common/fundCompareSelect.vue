<template>
  <div v-if="boxShadow" class="shadow" :class="darkMode ? 'darkMode' : ''">
    <div class="content-box">
      <h5>基金对比</h5>
      <el-tabs v-model="activeName" type="border-card">
        <el-tab-pane label="选择基金" name="select">
          <div class="select-container">
            <div class="section-title">自选基金列表</div>
            <div class="fund-list">
              <div
                v-for="fund in dataList"
                :key="fund.fundcode"
                :class="['fund-item', { selected: isSelected(fund.fundcode) }]"
                @click="toggleFund(fund)"
              >
                <span class="fund-name">{{ fund.name }}</span>
                <span class="fund-code">{{ fund.fundcode }}</span>
                <span class="fund-change" :class="fund.gszzl >= 0 ? 'up' : 'down'">
                  {{ fund.gszzl }}%
                </span>
                <span class="check-icon" v-if="isSelected(fund.fundcode)">✓</span>
              </div>
            </div>
            
            <div class="section-title">添加新基金（不在自选列表中）</div>
            <div class="add-fund-section">
              <el-select
                v-model="newFundCode"
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
                  >{{ item.value }}</span>
                </el-option>
              </el-select>
              <input
                class="btn"
                type="button"
                value="添加"
                @click="addNewFunds"
                :disabled="!newFundCode.length"
              />
            </div>
            
            <div class="selected-funds">
              <div class="section-title">已选择对比（最多3支）</div>
              <div class="selected-list">
                <div
                  v-for="(fund, index) in selectedFunds"
                  :key="fund.fundcode"
                  class="selected-item"
                >
                  <span class="selected-name">{{ fund.name }} ({{ fund.fundcode }})</span>
                  <span class="remove-btn" @click="removeFund(index)">✕</span>
                </div>
              </div>
              <div v-if="selectedFunds.length === 0" class="empty-tip">
                请选择至少1支基金进行对比
              </div>
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>

      <div class="tab-row">
        <input
          class="btn primary"
          type="button"
          value="开始对比"
          @click="startCompare"
          :disabled="selectedFunds.length < 1"
        />
        <input class="btn" type="button" value="返回列表" @click="close" />
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "fundCompareSelect",
  props: {
    darkMode: {
      type: Boolean,
      default: false,
    },
    dataList: {
      type: Array,
      default: () => [],
    },
    fundListM: {
      type: Array,
      default: () => [],
    },
  },
  data() {
    return {
      activeName: "select",
      boxShadow: false,
      selectedFunds: [],
      newFundCode: [],
      searchOptions: [],
      allSearchOptions: [],
      loading: false,
    };
  },
  methods: {
    init() {
      this.boxShadow = true;
      this.selectedFunds = [];
      this.newFundCode = [];
      this.searchOptions = [];
      this.allSearchOptions = [];
    },
    close() {
      this.boxShadow = false;
      this.$emit("close", false);
    },
    isSelected(fundcode) {
      return this.selectedFunds.some((f) => f.fundcode === fundcode);
    },
    toggleFund(fund) {
      const index = this.selectedFunds.findIndex((f) => f.fundcode === fund.fundcode);
      if (index > -1) {
        this.selectedFunds.splice(index, 1);
      } else {
        if (this.selectedFunds.length >= 3) {
          this.$message.warning("最多只能选择3支基金进行对比");
          return;
        }
        this.selectedFunds.push({
          fundcode: fund.fundcode,
          name: fund.name,
          isNew: false,
        });
      }
    },
    selectChange() {
      this.searchOptions = [];
    },
    remoteMethod(query) {
      if (query !== "") {
        this.loading = true;
        let url =
          "/api/fundsuggest/FundSearch/api/FundSearchAPI.ashx?&m=9&key=" +
          query +
          "&_=" +
          new Date().getTime();
        this.$axios.get(url).then((res) => {
          const filteredOptions = res.data.Datas.filter((val) => {
            let hasCode = this.selectedFunds.some((currentValue) => {
              return currentValue.fundcode == val.CODE;
            });
            return !hasCode;
          }).map((val) => {
            return {
              value: val.CODE,
              label: val.NAME,
            };
          });
          this.searchOptions = filteredOptions;
          filteredOptions.forEach((item) => {
            const existing = this.allSearchOptions.find((o) => o.value === item.value);
            if (!existing) {
              this.allSearchOptions.push(item);
            }
          });
          this.loading = false;
        });
      } else {
        this.searchOptions = [];
      }
    },
    addNewFunds() {
      if (this.selectedFunds.length + this.newFundCode.length > 3) {
        this.$message.warning("最多只能选择3支基金进行对比");
        return;
      }
      
      for (const code of this.newFundCode) {
        const option = this.allSearchOptions.find((o) => o.value === code);
        if (option) {
          const alreadySelected = this.selectedFunds.some((f) => f.fundcode === code);
          if (!alreadySelected) {
            this.selectedFunds.push({
              fundcode: code,
              name: option.label,
              isNew: true,
            });
          }
        }
      }
      this.newFundCode = [];
      this.searchOptions = [];
      this.allSearchOptions = this.allSearchOptions.filter((item) => {
        return !this.selectedFunds.some((f) => f.fundcode === item.value);
      });
    },
    removeFund(index) {
      this.selectedFunds.splice(index, 1);
    },
    startCompare() {
      if (this.selectedFunds.length < 1) {
        this.$message.warning("请至少选择1支基金进行对比");
        return;
      }
      this.boxShadow = false;
      this.$emit("startCompare", this.selectedFunds);
    },
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

  /deep/ .el-tabs__item {
    padding: 0 15px;
    height: 34px;
    line-height: 34px;
  }
}

.select-container {
  max-height: 400px;
  overflow-y: auto;
  padding: 10px;
}

.section-title {
  font-weight: bold;
  text-align: left;
  margin: 10px 0 5px 0;
  padding-left: 5px;
  color: #606266;
}

.fund-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 15px;
}

.fund-item {
  display: flex;
  align-items: center;
  padding: 8px 12px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s;
  position: relative;
  
  &:hover {
    border-color: #409eff;
  }
  
  &.selected {
    border-color: #67c23a;
    background-color: #f0f9eb;
    padding-right: 25px;
  }
}

.fund-name {
  margin-right: 8px;
  font-weight: 500;
}

.fund-code {
  color: #909399;
  font-size: 12px;
  margin-right: 8px;
}

.fund-change {
  font-size: 12px;
}

.check-icon {
  position: absolute;
  right: 5px;
  color: #67c23a;
  font-weight: bold;
}

.add-fund-section {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 15px;
}

.selected-funds {
  border-top: 1px solid #ebeef5;
  padding-top: 10px;
}

.selected-list {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 10px;
}

.selected-item {
  display: flex;
  align-items: center;
  padding: 8px 12px;
  background-color: #ecf5ff;
  border: 1px solid #b3d8ff;
  border-radius: 4px;
}

.selected-name {
  margin-right: 8px;
  color: #409eff;
}

.remove-btn {
  cursor: pointer;
  color: #909399;
  font-size: 12px;
  
  &:hover {
    color: #f56c6c;
  }
}

.empty-tip {
  color: #909399;
  font-size: 12px;
  text-align: left;
  padding-left: 5px;
}

.up {
  color: #f56c6c;
  font-weight: bold;
}

.down {
  color: #4eb61b;
  font-weight: bold;
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
  
  &:disabled {
    cursor: not-allowed;
    opacity: 0.5;
  }
}

.primary {
  color: #fff;
  background-color: #409eff;
  border-color: #409eff;
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
  .primary {
    background-color: rgba($color: #409eff, $alpha: 0.6);
    border-color: rgba($color: #409eff, $alpha: 0.6);
    color: #fff;
  }

  /deep/ .el-tabs--border-card {
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

  /deep/ .el-input__inner {
    background-color: rgba($color: #ffffff, $alpha: 0.16);
    color: rgba($color: #ffffff, $alpha: 0.6);
  }

  /deep/ .el-select__input {
    color: rgba($color: #ffffff, $alpha: 0.6);
  }

  .section-title {
    color: rgba($color: #ffffff, $alpha: 0.8);
  }

  .fund-item {
    border-color: rgba($color: #ffffff, $alpha: 0.3);
    
    &:hover {
      border-color: rgba($color: #409eff, $alpha: 0.6);
    }
    
    &.selected {
      border-color: rgba($color: #67c23a, $alpha: 0.6);
      background-color: rgba($color: #67c23a, $alpha: 0.1);
    }
  }

  .fund-name {
    color: rgba($color: #ffffff, $alpha: 0.8);
  }

  .fund-code {
    color: rgba($color: #ffffff, $alpha: 0.5);
  }

  .selected-funds {
    border-top-color: rgba($color: #ffffff, $alpha: 0.2);
  }

  .selected-item {
    background-color: rgba($color: #409eff, $alpha: 0.2);
    border-color: rgba($color: #409eff, $alpha: 0.4);
  }

  .selected-name {
    color: rgba($color: #67c23a, $alpha: 0.8);
  }

  .empty-tip {
    color: rgba($color: #ffffff, $alpha: 0.5);
  }
}
</style>
