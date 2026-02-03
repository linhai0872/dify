import type {
  Node,
} from '@/app/components/workflow/types'
import { useTranslation } from 'react-i18next'
import Input from '@/app/components/base/input'
import Slider from '@/app/components/base/slider'
import Switch from '@/app/components/base/switch'
import Split from '@/app/components/workflow/nodes/_base/components/split'
import { useRetryConfig } from './hooks'
import s from './style.module.css'
import { BackoffStrategy } from './types'

type RetryOnPanelProps = Pick<Node, 'id' | 'data'>
const RetryOnPanel = ({
  id,
  data,
}: RetryOnPanelProps) => {
  const { t } = useTranslation()
  const { handleRetryConfigChange } = useRetryConfig(id)
  const { retry_config } = data

  // [CUSTOM] 二开: 默认值
  const currentBackoffStrategy = retry_config?.backoff_strategy || BackoffStrategy.FIXED
  const isExponentialBackoff = currentBackoffStrategy === BackoffStrategy.EXPONENTIAL
  // [/CUSTOM]

  const handleRetryEnabledChange = (value: boolean) => {
    handleRetryConfigChange({
      retry_enabled: value,
      max_retries: retry_config?.max_retries || 3,
      retry_interval: retry_config?.retry_interval || 1000,
      // [CUSTOM] 二开: 保留退避策略配置
      backoff_strategy: retry_config?.backoff_strategy || BackoffStrategy.FIXED,
      backoff_multiplier: retry_config?.backoff_multiplier || 2.0,
      max_backoff_interval: retry_config?.max_backoff_interval || 60000,
      // [/CUSTOM]
    })
  }

  const handleMaxRetriesChange = (value: number) => {
    if (value > 10)
      value = 10
    else if (value < 1)
      value = 1
    handleRetryConfigChange({
      retry_enabled: true,
      max_retries: value,
      retry_interval: retry_config?.retry_interval || 1000,
      // [CUSTOM] 二开: 保留退避策略配置
      backoff_strategy: retry_config?.backoff_strategy || BackoffStrategy.FIXED,
      backoff_multiplier: retry_config?.backoff_multiplier || 2.0,
      max_backoff_interval: retry_config?.max_backoff_interval || 60000,
      // [/CUSTOM]
    })
  }

  const handleRetryIntervalChange = (value: number) => {
    if (value > 5000)
      value = 5000
    else if (value < 100)
      value = 100
    handleRetryConfigChange({
      retry_enabled: true,
      max_retries: retry_config?.max_retries || 3,
      retry_interval: value,
      // [CUSTOM] 二开: 保留退避策略配置
      backoff_strategy: retry_config?.backoff_strategy || BackoffStrategy.FIXED,
      backoff_multiplier: retry_config?.backoff_multiplier || 2.0,
      max_backoff_interval: retry_config?.max_backoff_interval || 60000,
      // [/CUSTOM]
    })
  }

  // [CUSTOM] 二开: 退避策略变更处理
  const handleBackoffStrategyChange = (strategy: BackoffStrategy) => {
    handleRetryConfigChange({
      retry_enabled: true,
      max_retries: retry_config?.max_retries || 3,
      retry_interval: retry_config?.retry_interval || 1000,
      backoff_strategy: strategy,
      backoff_multiplier: retry_config?.backoff_multiplier || 2.0,
      max_backoff_interval: retry_config?.max_backoff_interval || 60000,
    })
  }

  const handleMaxBackoffIntervalChange = (value: number) => {
    if (value > 60000)
      value = 60000
    else if (value < 1000)
      value = 1000
    handleRetryConfigChange({
      retry_enabled: true,
      max_retries: retry_config?.max_retries || 3,
      retry_interval: retry_config?.retry_interval || 1000,
      backoff_strategy: retry_config?.backoff_strategy || BackoffStrategy.EXPONENTIAL,
      backoff_multiplier: retry_config?.backoff_multiplier || 2.0,
      max_backoff_interval: value,
    })
  }
  // [/CUSTOM]

  return (
    <>
      <div className="pt-2">
        <div className="flex h-10 items-center justify-between px-4 py-2">
          <div className="flex items-center">
            <div className="system-sm-semibold-uppercase mr-0.5 text-text-secondary">{t('nodes.common.retry.retryOnFailure', { ns: 'workflow' })}</div>
          </div>
          <Switch
            defaultValue={retry_config?.retry_enabled}
            onChange={v => handleRetryEnabledChange(v)}
          />
        </div>
        {
          retry_config?.retry_enabled && (
            <div className="px-4 pb-2">
              {/* [CUSTOM] 二开: 退避策略选择器 */}
              <div className="mb-2 flex w-full items-center">
                <div className="system-xs-medium-uppercase mr-2 grow text-text-secondary">{t('nodes.common.retry.backoffStrategy', { ns: 'workflow' })}</div>
                <div className="flex gap-1">
                  <button
                    className={`rounded-md px-3 py-1 text-xs ${currentBackoffStrategy === BackoffStrategy.FIXED ? 'bg-primary-600 text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'}`}
                    onClick={() => handleBackoffStrategyChange(BackoffStrategy.FIXED)}
                  >
                    {t('nodes.common.retry.fixed', { ns: 'workflow' })}
                  </button>
                  <button
                    className={`rounded-md px-3 py-1 text-xs ${currentBackoffStrategy === BackoffStrategy.EXPONENTIAL ? 'bg-primary-600 text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'}`}
                    onClick={() => handleBackoffStrategyChange(BackoffStrategy.EXPONENTIAL)}
                  >
                    {t('nodes.common.retry.exponential', { ns: 'workflow' })}
                  </button>
                </div>
              </div>
              {/* [/CUSTOM] */}
              <div className="mb-1 flex w-full items-center">
                <div className="system-xs-medium-uppercase mr-2 grow text-text-secondary">{t('nodes.common.retry.maxRetries', { ns: 'workflow' })}</div>
                <Slider
                  className="mr-3 w-[108px]"
                  value={retry_config?.max_retries || 3}
                  onChange={handleMaxRetriesChange}
                  min={1}
                  max={10}
                />
                <Input
                  type="number"
                  wrapperClassName="w-[100px]"
                  value={retry_config?.max_retries || 3}
                  onChange={e =>
                    handleMaxRetriesChange(Number.parseInt(e.currentTarget.value, 10) || 3)}
                  min={1}
                  max={10}
                  unit={t('nodes.common.retry.times', { ns: 'workflow' }) || ''}
                  className={s.input}
                />
              </div>
              <div className="mb-1 flex items-center">
                <div className="system-xs-medium-uppercase mr-2 grow text-text-secondary">
                  {isExponentialBackoff
                    ? t('nodes.common.retry.baseInterval', { ns: 'workflow' })
                    : t('nodes.common.retry.retryInterval', { ns: 'workflow' })}
                </div>
                <Slider
                  className="mr-3 w-[108px]"
                  value={retry_config?.retry_interval || 1000}
                  onChange={handleRetryIntervalChange}
                  min={100}
                  max={5000}
                />
                <Input
                  type="number"
                  wrapperClassName="w-[100px]"
                  value={retry_config?.retry_interval || 1000}
                  onChange={e =>
                    handleRetryIntervalChange(Number.parseInt(e.currentTarget.value, 10) || 1000)}
                  min={100}
                  max={5000}
                  unit={t('nodes.common.retry.ms', { ns: 'workflow' }) || ''}
                  className={s.input}
                />
              </div>
              {/* [CUSTOM] 二开: 指数退避最大间隔配置 */}
              {isExponentialBackoff && (
                <div className="flex items-center">
                  <div className="system-xs-medium-uppercase mr-2 grow text-text-secondary">{t('nodes.common.retry.maxBackoffInterval', { ns: 'workflow' })}</div>
                  <Slider
                    className="mr-3 w-[108px]"
                    value={retry_config?.max_backoff_interval || 60000}
                    onChange={handleMaxBackoffIntervalChange}
                    min={1000}
                    max={60000}
                  />
                  <Input
                    type="number"
                    wrapperClassName="w-[100px]"
                    value={retry_config?.max_backoff_interval || 60000}
                    onChange={e =>
                      handleMaxBackoffIntervalChange(Number.parseInt(e.currentTarget.value, 10) || 60000)}
                    min={1000}
                    max={60000}
                    unit={t('nodes.common.retry.ms', { ns: 'workflow' }) || ''}
                    className={s.input}
                  />
                </div>
              )}
              {/* [/CUSTOM] */}
            </div>
          )
        }
      </div>
      <Split className="mx-4 mt-2" />
    </>
  )
}

export default RetryOnPanel
