module.exports = {
  root: true,
  env: {
    node: true
  },
  extends: [
    'plugin:vue/vue3-essential',
    'eslint:recommended'
  ],
  rules: {
    'vue/no-unused-components': 'warn' // Change from 'error' to 'warn'
    // Or completely disable it with:
    // 'vue/no-unused-components': 'off'
  }
}