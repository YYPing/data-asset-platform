/**
 * 验证工具函数
 */

/**
 * 验证邮箱
 */
export function validateEmail(email: string): boolean {
  const reg = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/
  return reg.test(email)
}

/**
 * 验证手机号（中国大陆）
 */
export function validatePhone(phone: string): boolean {
  const reg = /^1[3-9]\d{9}$/
  return reg.test(phone)
}

/**
 * 验证身份证号（中国大陆）
 */
export function validateIdCard(idCard: string): boolean {
  const reg = /(^\d{15}$)|(^\d{18}$)|(^\d{17}(\d|X|x)$)/
  return reg.test(idCard)
}

/**
 * 验证用户名（字母、数字、下划线，3-20位）
 */
export function validateUsername(username: string): boolean {
  const reg = /^[a-zA-Z0-9_]{3,20}$/
  return reg.test(username)
}

/**
 * 验证密码强度
 * @param password 密码
 * @returns 0: 弱, 1: 中, 2: 强
 */
export function validatePasswordStrength(password: string): number {
  if (password.length < 6) return 0

  let strength = 0

  // 包含小写字母
  if (/[a-z]/.test(password)) strength++
  // 包含大写字母
  if (/[A-Z]/.test(password)) strength++
  // 包含数字
  if (/\d/.test(password)) strength++
  // 包含特殊字符
  if (/[!@#$%^&*(),.?":{}|<>]/.test(password)) strength++

  if (strength <= 1) return 0 // 弱
  if (strength <= 2) return 1 // 中
  return 2 // 强
}

/**
 * 验证URL
 */
export function validateURL(url: string): boolean {
  try {
    new URL(url)
    return true
  } catch {
    return false
  }
}

/**
 * 验证IP地址
 */
export function validateIP(ip: string): boolean {
  const reg = /^((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)$/
  return reg.test(ip)
}

/**
 * 验证端口号
 */
export function validatePort(port: number | string): boolean {
  const portNum = typeof port === 'string' ? parseInt(port, 10) : port
  return !isNaN(portNum) && portNum >= 1 && portNum <= 65535
}

/**
 * 验证正整数
 */
export function validatePositiveInteger(value: number | string): boolean {
  const num = typeof value === 'string' ? parseInt(value, 10) : value
  return !isNaN(num) && num > 0 && Number.isInteger(num)
}

/**
 * 验证非负数
 */
export function validateNonNegative(value: number | string): boolean {
  const num = typeof value === 'string' ? parseFloat(value) : value
  return !isNaN(num) && num >= 0
}

/**
 * 验证中文
 */
export function validateChinese(text: string): boolean {
  const reg = /^[\u4e00-\u9fa5]+$/
  return reg.test(text)
}

/**
 * 验证统一社会信用代码
 */
export function validateCreditCode(code: string): boolean {
  const reg = /^[0-9A-HJ-NPQRTUWXY]{2}\d{6}[0-9A-HJ-NPQRTUWXY]{10}$/
  return reg.test(code)
}

/**
 * Element Plus 表单验证规则生成器
 */

// 必填验证
export const requiredRule = (message = '此项为必填项', trigger: 'blur' | 'change' = 'blur') => ({
  required: true,
  message,
  trigger,
})

// 邮箱验证
export const emailRule = (message = '请输入正确的邮箱地址', trigger: 'blur' | 'change' = 'blur') => ({
  validator: (_rule: any, value: string, callback: any) => {
    if (!value) {
      callback()
    } else if (!validateEmail(value)) {
      callback(new Error(message))
    } else {
      callback()
    }
  },
  trigger,
})

// 手机号验证
export const phoneRule = (message = '请输入正确的手机号', trigger: 'blur' | 'change' = 'blur') => ({
  validator: (_rule: any, value: string, callback: any) => {
    if (!value) {
      callback()
    } else if (!validatePhone(value)) {
      callback(new Error(message))
    } else {
      callback()
    }
  },
  trigger,
})

// 用户名验证
export const usernameRule = (message = '用户名为3-20位字母、数字或下划线', trigger: 'blur' | 'change' = 'blur') => ({
  validator: (_rule: any, value: string, callback: any) => {
    if (!value) {
      callback()
    } else if (!validateUsername(value)) {
      callback(new Error(message))
    } else {
      callback()
    }
  },
  trigger,
})

// 密码验证
export const passwordRule = (minLength = 6, maxLength = 20, trigger: 'blur' | 'change' = 'blur') => ({
  validator: (_rule: any, value: string, callback: any) => {
    if (!value) {
      callback()
    } else if (value.length < minLength) {
      callback(new Error(`密码长度不能少于${minLength}位`))
    } else if (value.length > maxLength) {
      callback(new Error(`密码长度不能超过${maxLength}位`))
    } else {
      callback()
    }
  },
  trigger,
})

// 长度验证
export const lengthRule = (min: number, max: number, message?: string, trigger: 'blur' | 'change' = 'blur') => ({
  min,
  max,
  message: message || `长度在 ${min} 到 ${max} 个字符`,
  trigger,
})

// URL验证
export const urlRule = (message = '请输入正确的URL', trigger: 'blur' | 'change' = 'blur') => ({
  validator: (_rule: any, value: string, callback: any) => {
    if (!value) {
      callback()
    } else if (!validateURL(value)) {
      callback(new Error(message))
    } else {
      callback()
    }
  },
  trigger,
})

// 正整数验证
export const positiveIntegerRule = (message = '请输入正整数', trigger: 'blur' | 'change' = 'blur') => ({
  validator: (_rule: any, value: any, callback: any) => {
    if (value === '' || value === null || value === undefined) {
      callback()
    } else if (!validatePositiveInteger(value)) {
      callback(new Error(message))
    } else {
      callback()
    }
  },
  trigger,
})

// 非负数验证
export const nonNegativeRule = (message = '请输入非负数', trigger: 'blur' | 'change' = 'blur') => ({
  validator: (_rule: any, value: any, callback: any) => {
    if (value === '' || value === null || value === undefined) {
      callback()
    } else if (!validateNonNegative(value)) {
      callback(new Error(message))
    } else {
      callback()
    }
  },
  trigger,
})
