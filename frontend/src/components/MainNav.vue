<template>
  <div class="main-nav">
    <el-menu
      :default-active="activeIndex"
      class="menu"
      mode="horizontal"
      router
      background-color="#409EFF"
      text-color="#fff"
      active-text-color="#ffd04b">
      <el-menu-item index="/">首页</el-menu-item>
      <el-menu-item index="/experiments">实验列表</el-menu-item>
      <el-menu-item index="/custom-code">自定义代码实验室</el-menu-item>
      <el-menu-item index="/user-center">个人中心</el-menu-item>
      <el-menu-item index="/admin/users" v-if="isAdmin">系统管理</el-menu-item>
    </el-menu>
  </div>
</template>

<script>
export default {
  name: 'MainNav',
  computed: {
    activeIndex() {
      return this.$route.path
    },
    isAdmin() {
      const user = this.$store.getters.user;
      return user && (user.is_superuser || user.role === 'admin');
    }
  }
}
</script>

<style scoped>
.main-nav {
  width: 100%;
}

.menu {
  border-bottom: none;
}
</style> 