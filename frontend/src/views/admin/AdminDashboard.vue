<template>
  <div class="admin-dashboard">
    <el-container>
      <el-aside width="200px">
        <el-menu
          default-active="dashboard"
          class="admin-menu"
          router>
          <el-menu-item index="/admin/dashboard">
            <i class="el-icon-menu"></i>
            <span>控制面板</span>
          </el-menu-item>
          <el-menu-item index="/admin/submissions">
            <i class="el-icon-document"></i>
            <span>实验提交记录</span>
          </el-menu-item>
          <el-menu-item index="/admin/users">
            <i class="el-icon-user"></i>
            <span>用户管理</span>
          </el-menu-item>
          <el-menu-item index="/admin/experiments">
            <i class="el-icon-s-data"></i>
            <span>实验管理</span>
          </el-menu-item>
        </el-menu>
      </el-aside>
      
      <el-container>
        <el-header>
          <div class="header-title">金融大数据虚拟仿真平台管理系统</div>
        </el-header>
        
        <el-main>
          <router-view></router-view>
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script>
export default {
  name: 'AdminDashboard',
  computed: {
    isUserManagementRoute() {
      // 检查当前路由是否为用户管理页面
      return this.$route.path === '/admin/users';
    }
  },
  methods: {
    logout() {
      this.$store.dispatch('logout')
      this.$router.push('/login')
    }
  }
}
</script>

<style scoped>
.admin-dashboard {
  height: 100vh;
  overflow: hidden;
}

.el-aside {
  background-color: #304156;
  color: #fff;
  height: 100vh;
}

.admin-menu {
  background-color: #304156;
  border-right: none;
}

.el-menu-item {
  color: #bfcbd9;
}

.el-menu-item:hover, .el-menu-item:focus {
  background-color: #263445;
}

.el-menu-item.is-active {
  color: #409EFF;
}

.el-header {
  background-color: #fff;
  color: #333;
  line-height: 60px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 1px 4px rgba(0,21,41,.08);
}

.header-title {
  font-size: 18px;
  font-weight: bold;
}

.header-user {
  cursor: pointer;
}

.el-dropdown-link {
  color: #409EFF;
}

.el-main {
  background-color: #f0f2f5;
  padding: 20px;
  overflow-y: auto;
  height: calc(100vh - 60px);
}
</style> 