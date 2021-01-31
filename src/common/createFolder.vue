<template>
  <el-dialog
    title="新建分组"
    :custom-class="darkMode ? 'createFolder darkMode' : 'createFolder'"
    :show-close="false"
    :close-on-click-modal="false"
    :modal-append-to-body="false"
    :close-on-press-escape="false"
    :visible.sync="centerDialogVisible"
    :top="top + 'px'"
    width="400px"
    center
  >
    <div
      class="content"
      :element-loading-background="
        darkMode ? 'rgba(0, 0, 0, 0.9)' : 'rgba(255, 255, 255, 0.9)'
      "
    >

      <el-input v-model="folder.name" autocomplete="off" placeholder="分组名称"></el-input>
      <el-input v-model="folder.desc" autocomplete="off" placeholder="分组描述"></el-input>

    </div>

    <span slot="footer" class="dialog-footer">
      <el-button type="primary" @click="close">确 定</el-button>
    </span>
  </el-dialog>
</template>

<script>
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
      folder:{},
      centerDialogVisible: false,
      formLabelWidth:'120px'
    };
  },
  mounted() {},
  methods: {
    init() {
      this.centerDialogVisible = true;
    },

    close() {
      this.centerDialogVisible = false;
      this.$emit("close", this.folder);
      this.folder.name = ''
      this.folder.desc = ''
    },
  },
};
</script>

<style lang="scss" scoped>
.createFolder {
  /deep/ &.el-dialog {
    margin-bottom: 15px;
    border-radius: 15px;
  }

  .btn-row {
    text-align: center;
    padding: 30px 0;
  }

  .content {
    height: 140px;
    p {
      text-align: center;
      margin: 0;
      padding: 2px 0;
    }

    overflow-y: auto;
    ul {
      padding-left: 22px;
      margin: 5px 0;
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

.createFolder.darkMode {
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
  .btn.red {
    border: 1px solid rgba($color: #f56c6c, $alpha: 0.6);
    background-color: rgba($color: #f56c6c, $alpha: 0.6);
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
