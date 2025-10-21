<template>
  <div class="login-container">
    <form @submit.prevent="handleSubmit" class="login-form">
      <h2 class="title">用户登录</h2>

      <!-- 用户名输入 -->
      <div class="input-group">
        <label for="username">用户名</label>
        <input
            type="text"
            id="username"
            v-model="loginForm.username"
            placeholder="请输入用户名"
            class="input-field"
        >
        <div v-if="errors.username" class="error-message">{{ errors.username }}</div>
      </div>

      <!-- 密码输入 -->
      <div class="input-group">
        <label for="password">密码</label>
        <input
            type="password"
            id="password"
            v-model="loginForm.password"
            placeholder="请输入密码"
            class="input-field"
        >
        <div v-if="errors.password" class="error-message">{{ errors.password }}</div>
      </div>

      <!-- 登录按钮 -->
      <button type="submit" class="login-button" :disabled="isSubmitting">
        {{ isSubmitting ? '登录中...' : '登录' }}
      </button>

      <!-- 错误提示 -->
      <div v-if="errorMessage" class="error-message">{{ errorMessage }}</div>
    </form>
  </div>
</template>

<script setup>
import {ref, getCurrentInstance, reactive} from 'vue';
import {useRouter} from 'vue-router'
// 请求代理
const {proxy} = getCurrentInstance()
const router = useRouter()

// 登录表单数据
const loginForm = reactive({
  username: '',
  password: ''
});

// 验证错误信息
const errors = reactive({
  username: '',
  password: ''
});

// 全局错误消息
const errorMessage = ref('');
// 提交状态
const isSubmitting = ref(false);

// 表单验证
const validateForm = () => {
  let valid = true;

  // 清空错误信息
  errors.username = '';
  errors.password = '';

  if (!loginForm.username.trim()) {
    errors.username = '请输入用户名';
    valid = false;
  }

  if (!loginForm.password) {
    errors.password = '请输入密码';
    valid = false;
  } else if (loginForm.password.length < 6) {
    errors.password = '密码长度不能少于6位';
    valid = false;
  }

  return valid;
};

// 提交请求处理
const handleSubmit = async () => {
  if (!validateForm()) return;

  isSubmitting.value = true;
  errorMessage.value = '';

  try {
    // 进行登录请求
    const loginData = await proxy.$api.login(loginForm)
    localStorage.setItem('token', loginData.access_token)
    isSubmitting.value = false;
    router.push('/');
  } catch (err) {
    errorMessage.value = '登录失败，请检查用户名和密码';
    isSubmitting.value = false;
  }
};
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #6a11cb 0%, #2575fc 100%);
}

.login-form {
  width: 100%;
  max-width: 400px;
  padding: 2rem;
  background: white;
  border-radius: 10px;
  box-shadow: 0 15px 35px rgba(50, 50, 93, 0.1), 0 5px 15px rgba(0, 0, 0, 0.07);
}

.title {
  text-align: center;
  margin-bottom: 2rem;
  color: #2c3e50;
  font-size: 1.8rem;
}

.input-group {
  margin-bottom: 1.5rem;
}

label {
  display: block;
  margin-bottom: 0.5rem;
  color: #34495e;
  font-weight: 500;
}

.input-field {
  width: 100%;
  padding: 0.8rem;
  border: 1px solid #e1e5eb;
  border-radius: 6px;
  font-size: 1rem;
  transition: border-color 0.3s;
}

.input-field:focus {
  border-color: #4d7cff;
  outline: none;
  box-shadow: 0 0 0 3px rgba(77, 124, 255, 0.15);
}

.remember-group {
  display: flex;
  align-items: center;
  margin-bottom: 1.5rem;
}

.remember-checkbox {
  margin-right: 0.5rem;
  width: 18px;
  height: 18px;
}

.remember-label {
  color: #34495e;
  font-size: 0.95rem;
  cursor: pointer;
}

.login-button {
  width: 100%;
  padding: 0.9rem;
  background: linear-gradient(to right, #6a11cb, #2575fc);
  border: none;
  border-radius: 6px;
  color: white;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 6px rgba(106, 17, 203, 0.2);
}

.login-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 7px 14px rgba(106, 17, 203, 0.25);
}

.login-button:disabled {
  background: linear-gradient(to right, #b5b5b5, #8a8a8a);
  cursor: not-allowed;
  box-shadow: none;
}

.error-message {
  color: #e74c3c;
  font-size: 0.85rem;
  margin-top: 0.3rem;
}
</style>