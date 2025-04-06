<template>
  <div id="app">
    <el-container v-if="isAuthenticated">
      <el-header>
        <div class="header-container">
          <div class="logo">
            金融大数据虚拟仿真实验平台
          </div>
          <div class="nav-section">
            <main-nav />
          </div>
          <div class="user-info">
            <el-dropdown trigger="click" @command="handleCommand">
              <span class="el-dropdown-link">
                {{ user.full_name || user.username || '用户' }} <i class="el-icon-arrow-down el-icon--right"></i>
              </span>
              <el-dropdown-menu slot="dropdown">
                <el-dropdown-item command="profile">个人中心</el-dropdown-item>
                <el-dropdown-item command="logout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </el-dropdown>
          </div>
        </div>
      </el-header>
      
      <el-main>
        <router-view/>
      </el-main>
    </el-container>
    
    <router-view v-else/>
  </div>
</template>

<script>
import { mapGetters, mapActions } from 'vuex'
import MainNav from '@/components/MainNav.vue'

export default {
  components: {
    MainNav
  },
  computed: {
    ...mapGetters(['isAuthenticated', 'user'])
  },
  methods: {
    ...mapActions(['logout']),
    handleCommand(command) {
      if (command === 'logout') {
        this.logout()
        this.$router.push('/login')
        this.$message.success('已成功退出登录')
      } else if (command === 'profile') {
        this.$router.push('/user-center')
      }
    }
  }
}
</script>

<style>
body {
  margin: 0;
  padding: 0;
  font-family: "Helvetica Neue", Helvetica, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", "微软雅黑", Arial, sans-serif;
}

#app {
  height: 100vh;
}

.el-header {
  background-color: #409EFF;
  color: white;
  line-height: 60px;
  padding: 0 20px;
}

.header-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo {
  font-size: 20px;
  font-weight: bold;
  flex: 0 0 300px;
}

.nav-section {
  flex: 1;
}

.user-info {
  flex: 0 0 auto;
  cursor: pointer;
  margin-left: 20px;
}

.el-dropdown-link {
  color: white;
  cursor: pointer;
}

.el-main {
  padding: 0;
  height: calc(100vh - 60px);
  overflow-y: auto;
}
</style>
