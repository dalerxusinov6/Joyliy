<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useAdminAuth } from '~/composables/useAdminAuth'

useHead({
  title: 'Admin Kirish — Joyliy.uz Boshqaruv Markazi',
})

const { login, isAuthenticated, isLoading, authError, checkAuth } = useAdminAuth()
const router = useRouter()

const username = ref('admin')
const password = ref('')
const showPassword = ref(false)

onMounted(async () => {
  const authed = await checkAuth()
  if (authed) {
    router.push('/admin')
  }
})

const handleLogin = async () => {
  if (!username.value || !password.value) return
  await login(username.value, password.value)
}
</script>

<template>
  <div class="admin-login-page">
    <div class="login-card-container">
      <!-- Brand & Header -->
      <div class="login-header">
        <div class="login-logo-mark">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" class="logo-icon">
            <path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" />
            <polyline points="9 22 9 12 15 12 15 22" />
          </svg>
        </div>
        <h1 class="login-title">Joyliy<span class="brand-accent">.uz</span></h1>
        <p class="login-subtitle">Boshqaruv markaziga xavfsiz kirish</p>
      </div>

      <!-- Login Form Card -->
      <div class="login-form-card">
        <!-- Error Alert -->
        <div v-if="authError" class="login-error-alert">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="error-icon">
            <circle cx="12" cy="12" r="10"/>
            <line x1="12" y1="8" x2="12" y2="12"/>
            <line x1="12" y1="16" x2="12.01" y2="16"/>
          </svg>
          <span>{{ authError }}</span>
        </div>

        <form @submit.prevent="handleLogin" class="login-form">
          <!-- Username field -->
          <div class="form-group">
            <label class="form-label" for="username">Foydalanuvchi nomi</label>
            <div class="input-wrapper">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="input-icon">
                <path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/>
                <circle cx="12" cy="7" r="4"/>
              </svg>
              <input
                id="username"
                v-model="username"
                type="text"
                required
                autocomplete="username"
                placeholder="admin"
                class="form-input"
              />
            </div>
          </div>

          <!-- Password field -->
          <div class="form-group">
            <div class="label-row">
              <label class="form-label" for="password">Maxfiy parol</label>
            </div>
            <div class="input-wrapper">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="input-icon">
                <rect width="18" height="11" x="3" y="11" rx="2" ry="2"/>
                <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
              </svg>
              <input
                id="password"
                v-model="password"
                :type="showPassword ? 'text' : 'password'"
                required
                autocomplete="current-password"
                placeholder="••••••••••••"
                class="form-input"
              />
              <button
                type="button"
                class="toggle-pwd-btn"
                @click="showPassword = !showPassword"
                :title="showPassword ? 'Yashirish' : 'Ko‘rsatish'"
              >
                <svg v-if="!showPassword" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z"/>
                  <circle cx="12" cy="12" r="3"/>
                </svg>
                <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M9.88 9.88a3 3 0 1 0 4.24 4.24"/>
                  <path d="M10.73 5.08A10.43 10.43 0 0 1 12 5c7 0 10 7 10 7a13.16 13.16 0 0 1-1.67 2.68"/>
                  <path d="M6.61 6.61A13.526 13.526 0 0 0 2 12s3 7 10 7a9.74 9.74 0 0 0 5.39-1.61"/>
                  <line x1="2" y1="2" x2="22" y2="22"/>
                </svg>
              </button>
            </div>
            <div class="credentials-hint">
              <span>Standart kirish: <strong>admin</strong> / <strong>Daler2026</strong></span>
            </div>
          </div>

          <!-- Submit Button -->
          <button type="submit" class="submit-btn" :disabled="isLoading">
            <span v-if="!isLoading">Tizimga kirish</span>
            <span v-else class="loading-state">
              <svg class="spin-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10" stroke-opacity="0.25"/>
                <path d="M12 2a10 10 0 0 1 10 10"/>
              </svg>
              Tekshirilmoqda...
            </span>
          </button>
        </form>

        <div class="login-footer-hint">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="shield-hint-icon">
            <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
          </svg>
          <span>Ushbu hudud faqat ruxsat etilgan ma'murlar uchun. Barcha urinishlar audit jurnaliga yoziladi.</span>
        </div>
      </div>

      <!-- Public Site Link -->
      <div class="back-to-site">
        <NuxtLink to="/" class="site-link">
          ← Joyliy.uz asosiy sahifasiga qaytish
        </NuxtLink>
      </div>
    </div>
  </div>
</template>

<style scoped>
.admin-login-page {
  min-height: 100vh;
  background: radial-gradient(circle at 50% 0%, #ffffff 0%, #f1f5f9 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
  font-family: 'Plus Jakarta Sans', -apple-system, sans-serif;
}

.login-card-container {
  width: 100%;
  max-width: 420px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.login-header {
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.login-logo-mark {
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, #2878c8 0%, #175496 100%);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  margin-bottom: 12px;
  box-shadow: 0 4px 12px rgba(40, 120, 200, 0.3);
}

.logo-icon {
  width: 26px;
  height: 26px;
}

.login-title {
  font-size: 24px;
  font-weight: 800;
  color: #0f172a;
  margin: 0;
  letter-spacing: -0.5px;
}

.brand-accent {
  color: #2878c8;
}

.login-subtitle {
  font-size: 14px;
  color: #64748b;
  margin-top: 4px;
}

.login-form-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  padding: 28px 24px;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05), 0 8px 10px -6px rgba(0, 0, 0, 0.03);
}

.login-error-alert {
  background: #fef2f2;
  border: 1px solid #fecaca;
  color: #b91c1c;
  padding: 10px 14px;
  border-radius: 8px;
  font-size: 13.5px;
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 18px;
}

.error-icon {
  width: 18px;
  height: 18px;
  flex-shrink: 0;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.label-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.form-label {
  font-size: 13px;
  font-weight: 600;
  color: #334155;
}

.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.input-icon {
  position: absolute;
  left: 12px;
  width: 17px;
  height: 17px;
  color: #94a3b8;
  pointer-events: none;
}

.form-input {
  width: 100%;
  height: 44px;
  padding: 0 40px 0 38px;
  border: 1px solid #cbd5e1;
  border-radius: 10px;
  font-size: 14px;
  color: #0f172a;
  background: #f8fafc;
  outline: none;
  transition: all 0.15s ease;
  font-family: inherit;
}

.form-input:focus {
  background: #ffffff;
  border-color: #2878c8;
  box-shadow: 0 0 0 3px rgba(40, 120, 200, 0.12);
}

.toggle-pwd-btn {
  position: absolute;
  right: 12px;
  background: none;
  border: none;
  color: #94a3b8;
  cursor: pointer;
  padding: 0;
  display: flex;
  align-items: center;
}

.toggle-pwd-btn svg {
  width: 18px;
  height: 18px;
}

.toggle-pwd-btn:hover {
  color: #475569;
}

.credentials-hint {
  font-size: 11.5px;
  color: #64748b;
  margin-top: 4px;
}

.credentials-hint strong {
  color: #2878c8;
}

.submit-btn {
  height: 44px;
  background: #2878c8;
  color: #ffffff;
  border: none;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s ease;
  box-shadow: 0 2px 6px rgba(40, 120, 200, 0.3);
  margin-top: 4px;
}

.submit-btn:hover:not(:disabled) {
  background: #1e60a5;
  box-shadow: 0 4px 12px rgba(40, 120, 200, 0.4);
}

.submit-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.loading-state {
  display: flex;
  align-items: center;
  gap: 8px;
}

.spin-svg {
  width: 16px;
  height: 16px;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.login-footer-hint {
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid #f1f5f9;
  display: flex;
  align-items: flex-start;
  gap: 8px;
  font-size: 11.5px;
  color: #94a3b8;
  line-height: 1.45;
}

.shield-hint-icon {
  width: 15px;
  height: 15px;
  color: #64748b;
  flex-shrink: 0;
  margin-top: 1px;
}

.back-to-site {
  text-align: center;
}

.site-link {
  font-size: 13px;
  color: #64748b;
  text-decoration: none;
  transition: color 0.15s;
}

.site-link:hover {
  color: #2878c8;
}
</style>

