<script setup>
import { computed, ref, useId } from 'vue'
import AppIcon from './AppIcon.vue'

defineOptions({ inheritAttrs: false })

const model = defineModel({ type: String, default: '' })

const props = defineProps({
  label: { type: String, default: '' },
  type: { type: String, default: 'text' },
  icon: { type: String, default: '' },
  prefix: { type: String, default: '' },
  required: { type: Boolean, default: false },
  error: { type: String, default: '' },
  id: { type: String, default: '' },
})

const autoId = useId()
const inputId = computed(() => props.id || autoId)
const errorId = computed(() => `${inputId.value}-error`)

const isPassword = computed(() => props.type === 'password')
const showPassword = ref(false)
const inputType = computed(() => (isPassword.value && showPassword.value ? 'text' : props.type))
</script>

<template>
  <div class="input-group">
    <div class="input-group__head">
      <label :for="inputId" class="label">
        {{ label }} <span v-if="required" class="req" aria-hidden="true">*</span>
      </label>
      <slot name="label-action" />
    </div>

    <div class="input-group__control">
      <span v-if="prefix" class="input-group__prefix">{{ prefix }}</span>
      <div class="input-group__field">
        <span v-if="icon" class="input-group__icon">
          <AppIcon :name="icon" :stroke-width="1.8" />
        </span>
        <input
          :id="inputId"
          v-model="model"
          v-bind="$attrs"
          :type="inputType"
          class="field"
          :class="{
            'field--icon': icon,
            'field--toggle': isPassword,
            'field--prefixed': prefix,
            'field--invalid': error,
          }"
          :aria-required="required || undefined"
          :aria-invalid="error ? 'true' : undefined"
          :aria-describedby="error ? errorId : undefined"
        >
        <button
          v-if="isPassword"
          type="button"
          class="input-group__toggle"
          :aria-label="showPassword ? 'Sembunyikan kata sandi' : 'Tampilkan kata sandi'"
          @click="showPassword = !showPassword"
        >
          <AppIcon :name="showPassword ? 'eye-off' : 'eye'" :stroke-width="1.8" />
        </button>
      </div>
    </div>

    <p v-if="error" :id="errorId" class="input-group__error">
      <AppIcon name="alert-circle" :size="12" />
      {{ error }}
    </p>
  </div>
</template>

<style scoped>
.input-group__head {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  margin-bottom: 6px;
}

.input-group__head .label {
  margin-bottom: 0;
}

.input-group__control {
  display: flex;
}

.input-group__prefix {
  display: inline-flex;
  align-items: center;
  padding: 0 12px;
  background: var(--mist);
  border: 1px solid var(--border);
  border-right: 0;
  border-radius: var(--radius-field) 0 0 var(--radius-field);
  font-size: 12px;
  font-weight: 500;
  color: var(--ink);
}

.input-group__field {
  position: relative;
  flex: 1;
}

.input-group__icon {
  position: absolute;
  inset: 0 auto 0 14px;
  display: flex;
  align-items: center;
  color: var(--slate);
  pointer-events: none;
}

.input-group__toggle {
  position: absolute;
  inset: 0 0 0 auto;
  display: flex;
  align-items: center;
  padding: 0 14px;
  border: 0;
  background: none;
  color: var(--slate);
}

.input-group__toggle:hover {
  color: var(--ink);
}

.field {
  width: 100%;
  padding: 14px 16px;
  background: #fff;
  border: 1px solid var(--border);
  border-radius: var(--radius-field);
  font-size: 12px;
  color: var(--ink);
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.field::placeholder {
  color: rgba(94, 81, 86, 0.5);
}

.field:focus {
  outline: none;
  border-color: var(--crimson);
  box-shadow: 0 0 0 3px rgba(112, 0, 32, 0.1);
}

.field--icon {
  padding-left: 40px;
}

.field--toggle {
  padding-right: 44px;
}

.field--prefixed {
  border-radius: 0 var(--radius-field) var(--radius-field) 0;
}

.field--invalid {
  border-color: var(--crimson);
  background: #fff7f8;
}

.input-group__error {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-top: 4px;
  font-size: 11px;
  font-weight: 500;
  color: var(--crimson);
}
</style>
