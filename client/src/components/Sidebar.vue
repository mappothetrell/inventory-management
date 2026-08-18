<template>
  <div>
    <!-- Mobile hamburger toggle, only visible below the 768px breakpoint -->
    <button
      class="mobile-toggle"
      :class="{ 'is-open': isOpen }"
      @click="isOpen = !isOpen"
      :aria-label="isOpen ? 'Close navigation' : 'Open navigation'"
    >
      <svg width="22" height="22" viewBox="0 0 20 20" fill="none">
        <path v-if="!isOpen" d="M3 5H17M3 10H17M3 15H17" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" />
        <path v-else d="M5 5L15 15M15 5L5 15" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" />
      </svg>
    </button>

    <!-- Backdrop shown only on mobile while the sidebar is open -->
    <div v-if="isOpen" class="sidebar-overlay" @click="isOpen = false"></div>

    <aside class="sidebar" :class="{ open: isOpen }">
      <div class="sidebar-brand">
        <!-- Icon-only badge shown only in the tablet (769-1024px) collapsed
             tier, in place of the full h1/subtitle text -->
        <div class="brand-mark">{{ t('nav.companyName').charAt(0) }}</div>
        <h1>{{ t('nav.companyName') }}</h1>
        <span class="subtitle">{{ t('nav.subtitle') }}</span>
      </div>

      <nav class="sidebar-nav">
        <router-link
          v-for="item in navItems"
          :key="item.path"
          :to="item.path"
          :class="{ active: $route.path === item.path }"
          :title="item.label"
          @click="isOpen = false"
        >
          <svg class="nav-icon" width="18" height="18" viewBox="0 0 20 20" fill="none">
            <component
              :is="shape.tag"
              v-for="(shape, idx) in icons[item.icon]"
              :key="idx"
              v-bind="shape.attrs"
              stroke="currentColor"
              stroke-width="1.5"
              stroke-linecap="round"
              stroke-linejoin="round"
              fill="none"
            />
          </svg>
          <span class="nav-label">{{ item.label }}</span>
        </router-link>
      </nav>

      <div class="sidebar-footer">
        <LanguageSwitcher />
        <div class="sidebar-divider"></div>
        <ProfileMenu
          @show-profile-details="$emit('show-profile-details')"
          @show-tasks="$emit('show-tasks')"
        />
      </div>
    </aside>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useI18n } from '../composables/useI18n'
import LanguageSwitcher from './LanguageSwitcher.vue'
import ProfileMenu from './ProfileMenu.vue'

defineEmits(['show-profile-details', 'show-tasks'])

const { t } = useI18n()

// Off-canvas open/close state used only below the 768px breakpoint;
// the sidebar is always visible at desktop widths regardless of this flag.
const isOpen = ref(false)

// Simple line-icon shape definitions per nav item, rendered generically via
// <component :is="shape.tag"> so a single template loop can cover
// path/circle primitives without a dedicated icon component per route.
const icons = {
  home: [
    { tag: 'path', attrs: { d: 'M3 9L10 3L17 9' } },
    { tag: 'path', attrs: { d: 'M5 9V16H15V9' } }
  ],
  box: [
    { tag: 'path', attrs: { d: 'M3 7L10 3L17 7V14L10 18L3 14V7Z' } },
    { tag: 'path', attrs: { d: 'M3 7L10 11L17 7' } },
    { tag: 'path', attrs: { d: 'M10 11V18' } }
  ],
  cart: [
    { tag: 'path', attrs: { d: 'M3 4H5L6.5 13H15.5L17 6H6' } },
    { tag: 'circle', attrs: { cx: 7, cy: 16.5, r: 1.1 } },
    { tag: 'circle', attrs: { cx: 14, cy: 16.5, r: 1.1 } }
  ],
  dollar: [
    { tag: 'circle', attrs: { cx: 10, cy: 10, r: 7 } },
    { tag: 'path', attrs: { d: 'M10 6.5V13.5' } },
    { tag: 'path', attrs: { d: 'M12.3 8C12.3 6.9 11.3 6.1 10 6.1C8.7 6.1 7.6 6.9 7.6 7.9C7.6 9 8.7 9.4 10 9.8C11.3 10.2 12.4 10.7 12.4 11.9C12.4 13 11.3 13.9 10 13.9C8.7 13.9 7.6 13 7.6 12' } }
  ],
  trend: [
    { tag: 'path', attrs: { d: 'M3 14L8 9L11.5 12L17 5.5' } },
    { tag: 'path', attrs: { d: 'M13 5.5H17V9.5' } }
  ],
  refresh: [
    { tag: 'path', attrs: { d: 'M4.5 10a5.5 5.5 0 019.5-3.8' } },
    { tag: 'path', attrs: { d: 'M15.5 10a5.5 5.5 0 01-9.5 3.8' } },
    { tag: 'path', attrs: { d: 'M14 3.5V6.7H10.8' } },
    { tag: 'path', attrs: { d: 'M6 16.5V13.3H9.2' } }
  ],
  doc: [
    { tag: 'path', attrs: { d: 'M6 3H14V17H6Z' } },
    { tag: 'path', attrs: { d: 'M8 7H12' } },
    { tag: 'path', attrs: { d: 'M8 10H12' } },
    { tag: 'path', attrs: { d: 'M8 13H10.5' } }
  ]
}

const navItems = computed(() => [
  { path: '/', label: t('nav.overview'), icon: 'home' },
  { path: '/inventory', label: t('nav.inventory'), icon: 'box' },
  { path: '/orders', label: t('nav.orders'), icon: 'cart' },
  { path: '/spending', label: t('nav.finance'), icon: 'dollar' },
  { path: '/demand', label: t('nav.demandForecast'), icon: 'trend' },
  { path: '/restocking', label: t('nav.restocking'), icon: 'refresh' },
  { path: '/reports', label: t('nav.reports'), icon: 'doc' }
])
</script>

<style scoped>
.sidebar {
  position: fixed;
  top: 0;
  left: 0;
  bottom: 0;
  width: 260px;
  background: #ffffff;
  border-right: 1px solid #e2e8f0;
  display: flex;
  flex-direction: column;
  z-index: 200;
  transition: transform 0.25s ease;
}

.sidebar-brand {
  padding: 1.5rem 1.5rem 1.25rem;
  border-bottom: 1px solid #f1f5f9;
}

.sidebar-brand h1 {
  font-size: 1.25rem;
  font-weight: 700;
  color: #0f172a;
  letter-spacing: -0.025em;
  line-height: 1.3;
}

.sidebar-brand .subtitle {
  display: block;
  margin-top: 0.375rem;
  font-size: 0.75rem;
  color: #64748b;
  font-weight: 400;
}

/* Hidden by default; only shown in the tablet icons-only tier below */
.brand-mark {
  display: none;
  width: 44px;
  height: 44px;
  border-radius: 8px;
  background: #2563eb;
  color: #ffffff;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 1.125rem;
}

.sidebar-nav {
  flex: 1;
  overflow-y: auto;
  padding: 0.75rem;
  display: flex;
  flex-direction: column;
  gap: 0.125rem;
}

.sidebar-nav a {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.625rem 0.875rem;
  color: #64748b;
  text-decoration: none;
  font-weight: 500;
  font-size: 0.875rem;
  border-radius: 8px;
  transition: all 0.15s ease;
}

.nav-icon {
  flex-shrink: 0;
  color: inherit;
}

.sidebar-nav a:hover {
  color: #0f172a;
  background: #f1f5f9;
}

.sidebar-nav a.active {
  color: #2563eb;
  background: #eff6ff;
  font-weight: 600;
}

.sidebar-footer {
  padding: 1rem 0.75rem 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.sidebar-footer :deep(.language-switcher),
.sidebar-footer :deep(.profile-menu) {
  width: 100%;
}

.sidebar-footer :deep(.language-button),
.sidebar-footer :deep(.profile-button) {
  width: 100%;
  justify-content: flex-start;
}

.sidebar-footer :deep(.dropdown-menu) {
  bottom: calc(100% + 0.5rem);
  top: auto;
}

.sidebar-divider {
  height: 1px;
  background: #f1f5f9;
  margin: 0.25rem 0;
}

.mobile-toggle {
  display: none;
}

.sidebar-overlay {
  display: none;
}

/* Tablet tier: auto-collapse to an icons-only rail. Automatic only (no
   toggle/JS state) - purely a CSS media query on viewport width. */
@media (max-width: 1024px) and (min-width: 769px) {
  .sidebar {
    width: 76px;
  }

  .sidebar-brand {
    padding: 1.5rem 0.5rem 1.25rem;
    display: flex;
    justify-content: center;
  }

  .sidebar-brand h1,
  .sidebar-brand .subtitle {
    display: none;
  }

  .brand-mark {
    display: flex;
  }

  .sidebar-nav a {
    justify-content: center;
    padding: 0.625rem 0.5rem;
  }

  .nav-label {
    display: none;
  }

  .sidebar-footer :deep(.language-button),
  .sidebar-footer :deep(.profile-button) {
    justify-content: center;
    padding: 0.5rem;
  }

  .sidebar-footer :deep(.language-label),
  .sidebar-footer :deep(.profile-name),
  .sidebar-footer :deep(.chevron) {
    display: none;
  }

  /* Dropdowns are absolutely positioned with right:0 relative to the
     footer buttons; at 76px wide that clips them off the left edge of
     the viewport, so anchor them to the left edge of the button instead. */
  .sidebar-footer :deep(.dropdown-menu) {
    left: 0;
    right: auto;
  }
}

@media (max-width: 768px) {
  .sidebar {
    transform: translateX(-100%);
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
  }

  .sidebar.open {
    transform: translateX(0);
  }

  .mobile-toggle {
    display: flex;
    align-items: center;
    justify-content: center;
    position: fixed;
    top: 0.875rem;
    left: 1rem;
    width: 40px;
    height: 40px;
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    color: #0f172a;
    cursor: pointer;
    z-index: 250;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
  }

  .sidebar-overlay {
    display: block;
    position: fixed;
    inset: 0;
    background: rgba(15, 23, 42, 0.4);
    z-index: 190;
  }
}
</style>
