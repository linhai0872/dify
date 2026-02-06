'use client'
import type { Dayjs } from 'dayjs'
import type { PeriodParams } from '@/app/components/app/overview/app-chart'
import type { I18nKeysByPrefix } from '@/types/i18n'
import dayjs from 'dayjs'
import quarterOfYear from 'dayjs/plugin/quarterOfYear'
import * as React from 'react'
import { useCallback, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { TIME_PERIOD_MAPPING as LONG_TIME_PERIOD_MAPPING } from '@/app/components/app/log/filter'
import { AvgResponseTime, AvgSessionInteractions, AvgUserInteractions, ConversationsChart, CostChart, EndUsersChart, MessagesChart, TokenPerSecond, UserSatisfactionRate, WorkflowCostChart, WorkflowDailyTerminalsChart, WorkflowMessagesChart } from '@/app/components/app/overview/app-chart'
import { useStore as useAppStore } from '@/app/components/app/store'
// [CUSTOM] 二开: 日期时间范围选择器
import CustomDatetimeRangePicker from '@/app/components/custom/overview/custom-datetime-range-picker'
// [/CUSTOM]
import { IS_CLOUD_EDITION } from '@/config'
import LongTimeRangePicker from './long-time-range-picker'
import TimeRangePicker from './time-range-picker'

dayjs.extend(quarterOfYear)

const today = dayjs()

type TimePeriodName = I18nKeysByPrefix<'appLog', 'filter.period.'>

const TIME_PERIOD_MAPPING: { value: number, name: TimePeriodName }[] = [
  { value: 0, name: 'today' },
  { value: 7, name: 'last7days' },
  { value: 30, name: 'last30days' },
]

const queryDateFormat = 'YYYY-MM-DD HH:mm'

export type IChartViewProps = {
  appId: string
  headerRight: React.ReactNode
}

export default function ChartView({ appId, headerRight }: IChartViewProps) {
  const { t } = useTranslation()
  const appDetail = useAppStore(state => state.appDetail)
  const isChatApp = appDetail?.mode !== 'completion' && appDetail?.mode !== 'workflow'
  const isWorkflow = appDetail?.mode === 'workflow'
  const [period, setPeriod] = useState<PeriodParams>(IS_CLOUD_EDITION
    ? { name: t('filter.period.today', { ns: 'appLog' }), query: { start: today.startOf('day').format(queryDateFormat), end: today.endOf('day').format(queryDateFormat) } }
    : { name: t('filter.period.last7days', { ns: 'appLog' }), query: { start: today.subtract(7, 'day').startOf('day').format(queryDateFormat), end: today.endOf('day').format(queryDateFormat) } },
  )

  // [CUSTOM] 二开: 日期时间范围选择器状态和联动逻辑
  const [startDate, setStartDate] = useState<Dayjs | null>(
    () => IS_CLOUD_EDITION ? null : today.subtract(7, 'day').startOf('day'),
  )
  const [endDate, setEndDate] = useState<Dayjs | null>(
    () => IS_CLOUD_EDITION ? null : today.endOf('day'),
  )
  // 跟踪左侧下拉的受控选中值，'custom' 表示自定义范围模式
  const [presetKey, setPresetKey] = useState<string | undefined>(undefined)

  // 左驱右: 预设下拉触发时，同步更新日期时间选择器
  const handlePresetSelect = useCallback((payload: PeriodParams) => {
    setPeriod(payload)
    setPresetKey(undefined) // 恢复为预设模式
    if (payload.query) {
      setStartDate(dayjs(payload.query.start, queryDateFormat))
      setEndDate(dayjs(payload.query.end, queryDateFormat))
    }
    else {
      setStartDate(null)
      setEndDate(null)
    }
  }, [])

  // 右覆左: 日期时间选择器变更时，更新 period 为自定义范围
  const handleDateTimeChange = useCallback((start: Dayjs, end: Dayjs) => {
    setStartDate(start)
    setEndDate(end)
    setPresetKey('custom') // 切换到自定义范围模式
    setPeriod({
      name: t('overview.dateTimeRange.custom', { ns: 'custom' }),
      query: {
        start: start.format(queryDateFormat),
        end: end.format(queryDateFormat),
      },
    })
  }, [t])

  // 清除日期时间选择器时，恢复默认 7 天
  const handleDateTimeClear = useCallback(() => {
    setStartDate(null)
    setEndDate(null)
    setPresetKey(undefined) // 恢复为预设模式
    setPeriod({
      name: t('filter.period.last7days', { ns: 'appLog' }),
      query: {
        start: today.subtract(7, 'day').startOf('day').format(queryDateFormat),
        end: today.endOf('day').format(queryDateFormat),
      },
    })
  }, [t])
  // [/CUSTOM]

  if (!appDetail)
    return null

  return (
    <div>
      <div className="mb-4">
        <div className="system-xl-semibold mb-2 text-text-primary">{t('appMenus.overview', { ns: 'common' })}</div>
        <div className="flex items-center justify-between">
          {IS_CLOUD_EDITION
            ? (
                <TimeRangePicker
                  ranges={TIME_PERIOD_MAPPING}
                  onSelect={setPeriod}
                  queryDateFormat={queryDateFormat}
                />
              )
            : (
                // [CUSTOM] 二开: 增加日期时间范围选择器
                <div className="flex items-center gap-2">
                  <LongTimeRangePicker
                    periodMapping={LONG_TIME_PERIOD_MAPPING}
                    onSelect={handlePresetSelect}
                    queryDateFormat={queryDateFormat}
                    selectedValue={presetKey}
                  />
                  <CustomDatetimeRangePicker
                    startDate={startDate}
                    endDate={endDate}
                    onChange={handleDateTimeChange}
                    onClear={handleDateTimeClear}
                  />
                </div>
                // [/CUSTOM]
              )}

          {headerRight}
        </div>
      </div>
      {!isWorkflow && (
        <div className="mb-6 grid w-full grid-cols-1 gap-6 xl:grid-cols-2">
          <ConversationsChart period={period} id={appId} />
          <EndUsersChart period={period} id={appId} />
        </div>
      )}
      {!isWorkflow && (
        <div className="mb-6 grid w-full grid-cols-1 gap-6 xl:grid-cols-2">
          {isChatApp
            ? (
                <AvgSessionInteractions period={period} id={appId} />
              )
            : (
                <AvgResponseTime period={period} id={appId} />
              )}
          <TokenPerSecond period={period} id={appId} />
        </div>
      )}
      {!isWorkflow && (
        <div className="mb-6 grid w-full grid-cols-1 gap-6 xl:grid-cols-2">
          <UserSatisfactionRate period={period} id={appId} />
          <CostChart period={period} id={appId} />
        </div>
      )}
      {!isWorkflow && isChatApp && (
        <div className="mb-6 grid w-full grid-cols-1 gap-6 xl:grid-cols-2">
          <MessagesChart period={period} id={appId} />
        </div>
      )}
      {isWorkflow && (
        <div className="mb-6 grid w-full grid-cols-1 gap-6 xl:grid-cols-2">
          <WorkflowMessagesChart period={period} id={appId} />
          <WorkflowDailyTerminalsChart period={period} id={appId} />
        </div>
      )}
      {isWorkflow && (
        <div className="mb-6 grid w-full grid-cols-1 gap-6 xl:grid-cols-2">
          <WorkflowCostChart period={period} id={appId} />
          <AvgUserInteractions period={period} id={appId} />
        </div>
      )}
    </div>
  )
}
