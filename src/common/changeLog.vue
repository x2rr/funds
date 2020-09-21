<template>
  <el-dialog
    title="更新日志"
    :custom-class="darkMode ? 'changelog darkMode' : 'changelog'"
    :show-close="false"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
    :visible.sync="centerDialogVisible"
    :top="top + 'px'"
    width="400px"
    center
  >
    <div class="content">
      <ul>
        <li v-for="el in logList" :key="el.version">
          <h5>
            v{{ el.version }}
            <span class="btn primary" v-if="el.type == 2">重要更新</span>
          </h5>
          <ul>
            <li
              :class="i.type == 2 ? 'major' : ''"
              v-for="(i, ind) in el.content"
              :key="ind"
            >
              {{ i.content }}
            </li>
          </ul>
        </li>
      </ul>
    </div>

    <span slot="footer" class="dialog-footer">
      <el-button type="primary" @click="close">确 定</el-button>
    </span>
  </el-dialog>
</template>

<script>
var json = require("./changeLog.json");
export default {
  props: {
    top: {
      type: Number,
      default: 0,
    },
    darkMode: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      centerDialogVisible: false,
      logList: json,
    };
  },
  mounted() {},
  methods: {
    init() {
      this.centerDialogVisible = true;
    },

    close() {
      this.centerDialogVisible = false;
      this.$emit("close", false);
    },
    closeDialog() {
      console.log(111);
    },
  },
};
</script>

<style lang="scss" scoped>
.changelog {
  /deep/ &.el-dialog {
    margin-bottom: 15px;
    border-radius: 15px;
  }

  .content {
    height: 340px;

    overflow-y: auto;
    ul {
      padding-left: 22px;
      li {
        padding: 3px 0;
        .major {
          font-weight: bold;
        }
        h5 {
          margin: 10px 0;
          font-size: 15px;
          font-weight: bold;
        }
      }
    }
    .btn {
      display: inline-block;
      line-height: 1;
      background: #fff;
      padding: 4px 6px;
      border-radius: 3px;
      font-size: 12px;
      color: #000000;
      margin: 0 3px;
      outline: none;
      border: 1px solid #dcdfe6;
    }
    .primary {
      color: #409eff;
      border-color: #409eff;
    }
  }
  /deep/ &.el-dialog--center .el-dialog__header {
    border-bottom: 1px solid #eee;
    padding: 15px 20px 10px;
  }
  /deep/ &.el-dialog--center .el-dialog__footer {
    border-top: 1px solid #eee;
    padding: 10px 20px 10px;
  }
  /deep/ &.el-dialog--center .el-dialog__body {
    padding: 10px 12px;
  }
}

.changelog.darkMode {
  /deep/ &.el-dialog {
    background-color: #373737;
    .el-dialog__header .el-dialog__title {
      color: rgba($color: #ffffff, $alpha: 0.6);
    }
    .el-dialog__body {
      color: rgba($color: #ffffff, $alpha: 0.6);
    }
  }
  .btn {
    background-color: rgba($color: #ffffff, $alpha: 0.16);
    color: rgba($color: #ffffff, $alpha: 0.6);
    border: 1px solid rgba($color: #ffffff, $alpha: 0.6);
  }
  .primary {
    border: 1px solid rgba($color: #409eff, $alpha: 0.6);
    background-color: rgba($color: #409eff, $alpha: 0.6);
  }

  .el-button--primary {
    border: 1px solid rgba($color: #409eff, $alpha: 0.6);
    background-color: rgba($color: #409eff, $alpha: 0.6);
    color: rgba($color: #ffffff, $alpha: 0.6);
  }
}
</style>
