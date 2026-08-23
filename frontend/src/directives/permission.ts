import type { Directive, DirectiveBinding } from 'vue'
import { useUserStore } from '@/stores/user'

/**
 * v-permission 指令
 * 用法: v-permission="'system:user:add'" 或 v-permission="['system:user:add', 'system:user:edit']"
 * 超管 permissions 为 ["*"]，自动放行
 */
function checkPermission(el: HTMLElement, binding: DirectiveBinding) {
  const { value } = binding
  if (!value) return

  const userStore = useUserStore()
  const perms = userStore.permissions

  // 超管通配
  if (perms.includes('*')) return

  const required = Array.isArray(value) ? value : [value]
  const hasPerm = required.some((p: string) => perms.includes(p))

  if (!hasPerm) {
    el.parentNode?.removeChild(el)
  }
}

export const permissionDirective: Directive = {
  mounted: checkPermission,
  updated: checkPermission,
}
