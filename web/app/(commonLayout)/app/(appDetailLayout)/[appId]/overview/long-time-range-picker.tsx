'use client'
import type { FC } from 'react'
import type { PeriodParams } from '@/app/components/app/overview/app-chart'
import type { Item } from '@/app/components/base/select'
import type { I18nKeysByPrefix } from '@/types/i18n'
import dayjs from 'dayjs'
import * as React from 'react'
import { useTranslation } from 'react-i18next'
import { SimpleSelect } from '@/app/components/base/select'

type TimePeriodName = I18nKeysByPrefix<'appLog', 'filter.period.'>

type Props = {
  periodMapping: { [key: string]: { value: number, name: TimePeriodName } }
  onSelect: (payload: PeriodParams) => void
  queryDateFormat: string
  // [CUSTOM] 二开: 受控选中值，用于日期时间选择器联动
  selectedValue?: string
  // [/CUSTOM]
}

const today = dayjs()

// [CUSTOM] 二开: 自定义范围选项 key
const CUSTOM_VALUE = 'custom'
// [/CUSTOM]

const LongTimeRangePicker: FC<Props> = ({
  periodMapping,
  onSelect,
  queryDateFormat,
  selectedValue, // [CUSTOM]
}) => {
  const { t } = useTranslation()

  const handleSelect = React.useCallback((item: Item) => {
    // [CUSTOM] 二开: 忽略自定义范围选项的点击（它只是显示用）
    if (item.value === CUSTOM_VALUE)
      return
    // [/CUSTOM]
    const id = item.value
    const value = periodMapping[id]?.value ?? '-1'
    const name = item.name || t('filter.period.allTime', { ns: 'appLog' })
    if (value === -1) {
      onSelect({ name: t('filter.period.allTime', { ns: 'appLog' }), query: undefined })
    }
    else if (value === 0) {
      const startOfToday = today.startOf('day').format(queryDateFormat)
      const endOfToday = today.endOf('day').format(queryDateFormat)
      onSelect({
        name,
        query: {
          start: startOfToday,
          end: endOfToday,
        },
      })
    }
    else {
      onSelect({
        name,
        query: {
          start: today.subtract(value as number, 'day').startOf('day').format(queryDateFormat),
          end: today.endOf('day').format(queryDateFormat),
        },
      })
    }
  }, [onSelect, periodMapping, queryDateFormat, t])

  // [CUSTOM] 二开: 构建选项列表，当处于自定义范围模式时追加选项
  const isCustom = selectedValue === CUSTOM_VALUE
  const items = React.useMemo(() => {
    const baseItems = Object.entries(periodMapping).map(([k, v]) => ({
      value: k,
      name: t(`filter.period.${v.name}`, { ns: 'appLog' }),
    }))
    if (isCustom) {
      baseItems.push({
        value: CUSTOM_VALUE,
        name: t('overview.dateTimeRange.custom', { ns: 'custom' }),
      })
    }
    return baseItems
  }, [periodMapping, t, isCustom])

  const defaultVal = isCustom ? CUSTOM_VALUE : '2'
  // [/CUSTOM]

  return (
    <SimpleSelect
      // [CUSTOM] 二开: key 强制重置以同步受控值
      key={defaultVal}
      // [/CUSTOM]
      items={items}
      className="mt-0 !w-40"
      notClearable={true}
      onSelect={handleSelect}
      defaultValue={defaultVal}
    />
  )
}
export default React.memo(LongTimeRangePicker)
