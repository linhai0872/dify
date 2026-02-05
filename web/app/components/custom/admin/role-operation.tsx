'use client'

import { RiCheckLine, RiExpandUpDownLine } from '@remixicon/react'
import { memo, useState } from 'react'
import {
  PortalToFollowElem,
  PortalToFollowElemContent,
  PortalToFollowElemTrigger,
} from '@/app/components/base/portal-to-follow-elem'
import { cn } from '@/utils/classnames'

export type RoleOption = {
  value: string
  label: string
  description?: string
}

export type RoleOperationProps = {
  currentRole: string
  roles: RoleOption[]
  onRoleChange: (role: string) => void
  disabled?: boolean
  className?: string
  triggerClassName?: string
}

/**
 * [CUSTOM] Role operation dropdown component with role descriptions.
 * Following Dify members-page Operation component patterns.
 */
const RoleOperation = ({
  currentRole,
  roles,
  onRoleChange,
  disabled = false,
  className,
  triggerClassName,
}: RoleOperationProps) => {
  const [open, setOpen] = useState(false)

  const currentRoleOption = roles.find(r => r.value === currentRole)

  const handleRoleSelect = (role: string) => {
    if (role !== currentRole)
      onRoleChange(role)
    setOpen(false)
  }

  return (
    <PortalToFollowElem
      open={open}
      onOpenChange={setOpen}
      placement="bottom-end"
      offset={{ mainAxis: 4 }}
    >
      <PortalToFollowElemTrigger asChild onClick={() => !disabled && setOpen(prev => !prev)}>
        <div
          className={cn(
            'system-sm-regular group flex h-full w-full items-center justify-between px-3 text-text-secondary',
            !disabled && 'cursor-pointer hover:bg-state-base-hover',
            disabled && 'cursor-not-allowed opacity-60',
            open && 'bg-state-base-hover',
            triggerClassName,
          )}
        >
          <span className="truncate">{currentRoleOption?.label || currentRole}</span>
          {!disabled && (
            <RiExpandUpDownLine className={cn('ml-1 h-4 w-4 shrink-0 text-text-quaternary group-hover:block', open ? 'block' : 'hidden')} />
          )}
        </div>
      </PortalToFollowElemTrigger>
      <PortalToFollowElemContent className="z-[999]">
        <div className={cn(
          'inline-flex min-w-[200px] flex-col rounded-xl border-[0.5px] border-components-panel-border',
          'bg-components-panel-bg-blur p-1 shadow-lg backdrop-blur-sm',
          className,
        )}
        >
          {roles.map(role => (
            <div
              key={role.value}
              className="flex cursor-pointer items-start rounded-lg px-3 py-2 hover:bg-state-base-hover"
              onClick={() => handleRoleSelect(role.value)}
            >
              {role.value === currentRole
                ? <RiCheckLine className="mr-2 mt-[2px] h-4 w-4 shrink-0 text-text-accent" />
                : <div className="mr-2 mt-[2px] h-4 w-4 shrink-0" />}
              <div className="min-w-0 flex-1">
                <div className="system-sm-semibold whitespace-nowrap text-text-secondary">
                  {role.label}
                </div>
                {role.description && (
                  <div className="system-xs-regular text-text-tertiary">
                    {role.description}
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </PortalToFollowElemContent>
    </PortalToFollowElem>
  )
}

export default memo(RoleOperation)
