<template>
  <div class="menu-permission-container">
    <div class="permission-layout">
      <!-- 左侧角色列表 -->
      <div class="role-list-panel">
        <div class="panel-header">
          <h3>角色列表</h3>
        </div>
        <div class="role-list" v-loading="roleLoading">
          <div
            v-for="role in roleList"
            :key="role.id"
            :class="['role-item', { 
              'active': currentRoleId === role.id,
              'readonly': role.is_readonly 
            }]"
            @click="handleRoleSelect(role)"
          >
            <div class="role-info">
              <div class="role-name">{{ role.name }}</div>
              <div class="role-desc">{{ role.desc }}</div>
            </div>
            <el-icon v-if="role.is_readonly" class="readonly-icon">
              <Lock />
            </el-icon>
          </div>
        </div>
      </div>

      <!-- 右侧菜单权限配置 -->
      <div class="menu-config-panel">
        <div class="panel-header">
          <h3>菜单权限配置</h3>
          <div class="current-role" v-if="currentRole">
            <span class="label">当前角色：</span>
            <span class="value">{{ currentRole.name }} ({{ currentRole.desc }})</span>
            <el-tag v-if="currentRole.is_readonly" type="warning" size="small" style="margin-left: 8px;">
              只读
            </el-tag>
          </div>
        </div>
        
        <div class="menu-tree-container" v-loading="menuLoading">
          <el-scrollbar v-if="menuTree.length > 0">
            <el-tree
              ref="menuTreeRef"
              :data="menuTree"
              :props="treeProps"
              node-key="id"
              show-checkbox
              default-expand-all
              :check-strictly="false"
              :disabled="currentRole?.is_readonly"
              @check="handleMenuCheck"
            >
              <template #default="{ node, data }">
                <span class="custom-tree-node">
                  <el-icon v-if="data.icon" class="menu-icon">
                    <component :is="data.icon" />
                  </el-icon>
                  <span class="menu-label">{{ data.label }}</span>
                </span>
              </template>
            </el-tree>
          </el-scrollbar>
          <el-empty v-else description="暂无菜单数据" />
        </div>

        <div class="action-buttons" v-if="!currentRole?.is_readonly">
          <el-button @click="handleCancel">取消</el-button>
          <el-button 
            type="primary" 
            @click="handleSave"
            :loading="saving"
            :disabled="!hasChanges"
          >
            保存
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, getCurrentInstance, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Lock } from '@element-plus/icons-vue'

const { proxy } = getCurrentInstance()

// 数据状态
const roleList = ref([])
const menuTree = ref([])
const currentRoleId = ref(null)
const currentRole = computed(() => roleList.value.find(r => r.id === currentRoleId.value))
const originalMenuIds = ref([])
const hasChanges = ref(false)

// 加载状态
const roleLoading = ref(false)
const menuLoading = ref(false)
const saving = ref(false)

// 树组件引用
const menuTreeRef = ref(null)

// 树配置
const treeProps = {
  children: 'children',
  label: 'label'
}

// 加载角色列表
const loadRoles = async () => {
  roleLoading.value = true
  try {
    const response = await proxy.$api.getRoles()
    roleList.value = response || []
    
    // 默认选中第一个角色
    if (roleList.value.length > 0) {
      currentRoleId.value = roleList.value[0].id
      await loadRoleMenus(currentRoleId.value)
    }
  } catch (error) {
    ElMessage.error('加载角色列表失败')
  } finally {
    roleLoading.value = false
  }
}

// 加载菜单树
const loadMenuTree = async () => {
  menuLoading.value = true
  try {
    const response = await proxy.$api.getMenusTree()
    menuTree.value = response || []
  } catch (error) {
    ElMessage.error('加载菜单树失败')
  } finally {
    menuLoading.value = false
  }
}

// 加载角色菜单权限
const loadRoleMenus = async (roleId) => {
  menuLoading.value = true
  try {
    const response = await proxy.$api.getRoleMenus(roleId)
    const menuIds = response?.menu_ids || []
    originalMenuIds.value = [...menuIds]
    
    // 等待DOM更新后设置选中状态
    await nextTick()
    if (menuTreeRef.value) {
      menuTreeRef.value.setCheckedKeys(menuIds, false)
    }
    
    hasChanges.value = false
  } catch (error) {
    ElMessage.error('加载角色菜单权限失败')
  } finally {
    menuLoading.value = false
  }
}

// 处理角色选择
const handleRoleSelect = async (role) => {
  // 如果已经是当前角色，不做处理
  if (currentRoleId.value === role.id) {
    return
  }

  // 检查是否有未保存的修改
  if (hasChanges.value) {
    try {
      await ElMessageBox.confirm(
        '当前角色有未保存的修改，切换角色将丢失这些修改。确定要切换吗？',
        '提示',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        }
      )
    } catch {
      return // 用户取消
    }
  }

  // 切换角色
  currentRoleId.value = role.id
  await loadRoleMenus(role.id)
}

// 处理菜单勾选变化
const handleMenuCheck = () => {
  if (currentRole.value?.is_readonly) {
    return
  }

  // 检查是否有变化
  const currentCheckedKeys = menuTreeRef.value.getCheckedKeys(false)
  const originalSet = new Set(originalMenuIds.value)
  const currentSet = new Set(currentCheckedKeys)
  
  hasChanges.value = 
    originalSet.size !== currentSet.size ||
    [...originalSet].some(id => !currentSet.has(id))
}

// 处理保存
const handleSave = async () => {
  if (!menuTreeRef.value || !currentRoleId.value) {
    return
  }

  // 获取所有选中的菜单ID（包括半选状态的父节点）
  const checkedKeys = menuTreeRef.value.getCheckedKeys(false)
  const halfCheckedKeys = menuTreeRef.value.getHalfCheckedKeys()
  const allMenuIds = [...checkedKeys, ...halfCheckedKeys]

  // 验证至少选择一个菜单
  if (allMenuIds.length === 0) {
    ElMessage.warning('请至少选择一个菜单')
    return
  }

  saving.value = true
  try {
    await proxy.$api.updateRoleMenus(currentRoleId.value, {
      menu_ids: allMenuIds
    })
    
    ElMessage.success('菜单权限保存成功')
    originalMenuIds.value = [...allMenuIds]
    hasChanges.value = false
  } catch (error) {
    ElMessage.error(error.msg || '保存失败')
  } finally {
    saving.value = false
  }
}

// 处理取消
const handleCancel = () => {
  if (!hasChanges.value) {
    return
  }

  // 恢复到原始状态
  if (menuTreeRef.value) {
    menuTreeRef.value.setCheckedKeys(originalMenuIds.value, false)
  }
  hasChanges.value = false
  ElMessage.info('已取消修改')
}

// 初始化
onMounted(async () => {
  await Promise.all([
    loadRoles(),
    loadMenuTree()
  ])
})
</script>

<style scoped lang="less">
.menu-permission-container {
  padding: 24px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  min-height: calc(100vh - 180px);
}

.permission-layout {
  display: flex;
  gap: 24px;
  height: 100%;
}

// 左侧角色列表
.role-list-panel {
  width: 280px;
  border-right: 1px solid #e8e8e8;
  padding-right: 24px;

  .panel-header {
    margin-bottom: 16px;
    padding-bottom: 12px;
    border-bottom: 2px solid #d9232c;

    h3 {
      margin: 0;
      font-size: 16px;
      font-weight: 600;
      color: #333;
    }
  }

  .role-list {
    .role-item {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 12px 16px;
      margin-bottom: 8px;
      border-radius: 6px;
      border: 1px solid #e8e8e8;
      cursor: pointer;
      transition: all 0.3s;

      &:hover:not(.readonly) {
        background-color: #fff5f5;
        border-color: #d9232c;
      }

      &.active {
        background-color: #d9232c;
        border-color: #d9232c;
        color: #fff;

        .role-name,
        .role-desc {
          color: #fff;
        }
      }

      &.readonly {
        background-color: #f5f5f5;
        cursor: not-allowed;

        .role-name,
        .role-desc {
          color: #999;
        }
      }

      .role-info {
        flex: 1;

        .role-name {
          font-size: 14px;
          font-weight: 500;
          color: #333;
          margin-bottom: 4px;
        }

        .role-desc {
          font-size: 12px;
          color: #666;
        }
      }

      .readonly-icon {
        font-size: 16px;
        color: #999;
      }
    }
  }
}

// 右侧菜单配置
.menu-config-panel {
  flex: 1;
  display: flex;
  flex-direction: column;

  .panel-header {
    margin-bottom: 16px;
    padding-bottom: 12px;
    border-bottom: 2px solid #d9232c;

    h3 {
      margin: 0 0 8px 0;
      font-size: 16px;
      font-weight: 600;
      color: #333;
    }

    .current-role {
      font-size: 14px;
      color: #666;

      .label {
        font-weight: 500;
      }

      .value {
        color: #333;
      }
    }
  }

  .menu-tree-container {
    flex: 1;
    border: 1px solid #e8e8e8;
    border-radius: 6px;
    padding: 16px;
    background-color: #fafafa;
    min-height: 400px;

    :deep(.el-tree) {
      background-color: transparent;

      .el-tree-node__content {
        height: 36px;
        border-radius: 4px;
        margin-bottom: 4px;

        &:hover {
          background-color: #fff5f5;
        }
      }

      .custom-tree-node {
        display: flex;
        align-items: center;
        gap: 8px;

        .menu-icon {
          font-size: 16px;
          color: #d9232c;
        }

        .menu-label {
          font-size: 14px;
          color: #333;
        }
      }
    }
  }

  .action-buttons {
    margin-top: 24px;
    display: flex;
    justify-content: flex-end;
    gap: 12px;
    padding-top: 16px;
    border-top: 1px solid #e8e8e8;
  }
}
</style>
