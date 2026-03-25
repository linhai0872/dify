// [CUSTOM] 二开: 指数退避重试策略类型（const + 类型别名，满足 erasableSyntaxOnly）
export const backoffStrategies = {
  FIXED: 'fixed',
  EXPONENTIAL: 'exponential',
} as const
export type BackoffStrategy = (typeof backoffStrategies)[keyof typeof backoffStrategies]
// [/CUSTOM]

export type WorkflowRetryConfig = {
  max_retries: number
  retry_interval: number
  retry_enabled: boolean
  // [CUSTOM] 二开: 指数退避配置字段
  backoff_strategy?: BackoffStrategy
  backoff_multiplier?: number
  max_backoff_interval?: number
  // [/CUSTOM]
}
