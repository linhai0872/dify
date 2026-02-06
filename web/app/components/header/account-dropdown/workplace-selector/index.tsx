import type { Plan } from '@/app/components/billing/type'
import { Menu, MenuButton, MenuItems, Transition } from '@headlessui/react'
import { RiArrowDownSLine } from '@remixicon/react'
import { Fragment } from 'react'
import { useTranslation } from 'react-i18next'
import { useContext } from 'use-context-selector'
import { ToastContext } from '@/app/components/base/toast'
import PlanBadge from '@/app/components/header/plan-badge'
import { useWorkspacesContext } from '@/context/workspace-context'
import { useIsSuperAdmin } from '@/hooks/custom/use-custom-system-role'
import { switchWorkspace } from '@/service/common'
import { cn } from '@/utils/classnames'
import { basePath } from '@/utils/var'

// [CUSTOM] Workspace role colors with semantic design system colors
const workspaceRoleColors: Record<string, { bg: string, text: string }> = {
  owner: { bg: 'bg-util-colors-violet-violet-50', text: 'text-util-colors-violet-violet-600' },
  admin: { bg: 'bg-util-colors-blue-light-blue-50', text: 'text-util-colors-blue-light-blue-600' },
  editor: { bg: 'bg-util-colors-green-green-50', text: 'text-util-colors-green-green-600' },
  normal: { bg: 'bg-components-badge-bg-gray', text: 'text-text-tertiary' },
  dataset_operator: { bg: 'bg-util-colors-warning-warning-50', text: 'text-util-colors-warning-warning-600' },
}

// [CUSTOM] Role badge component for workspace role display
const RoleBadge = ({ role }: { role?: string | null }) => {
  const { t } = useTranslation()

  if (role === null || role === undefined) {
    // Super admin viewing unjoined workspace - show read-only badge
    return (
      <span className="system-2xs-medium shrink-0 rounded bg-components-badge-bg-dimm px-1 py-0.5 text-text-quaternary">
        {t('admin.readOnly', { ns: 'custom' })}
      </span>
    )
  }

  // Map role to display text
  const roleMap: Record<string, string> = {
    owner: t('admin.workspaceRole.owner', { ns: 'custom' }),
    admin: t('admin.workspaceRole.admin', { ns: 'custom' }),
    editor: t('admin.workspaceRole.editor', { ns: 'custom' }),
    normal: t('admin.workspaceRole.normal', { ns: 'custom' }),
    dataset_operator: t('admin.workspaceRole.datasetOperator', { ns: 'custom' }),
  }

  const displayRole = roleMap[role] || role
  const colors = workspaceRoleColors[role] || workspaceRoleColors.normal

  return (
    <span className={cn(
      'system-2xs-medium shrink-0 rounded px-1 py-0.5',
      colors.bg,
      colors.text,
    )}
    >
      {displayRole}
    </span>
  )
}

const WorkplaceSelector = () => {
  const { t } = useTranslation()
  const { notify } = useContext(ToastContext)
  const { workspaces } = useWorkspacesContext()
  const currentWorkspace = workspaces.find(v => v.current)
  // [CUSTOM] Check if multi-workspace permission feature is enabled
  const { isFeatureEnabled } = useIsSuperAdmin()

  const handleSwitchWorkspace = async (tenant_id: string) => {
    try {
      if (currentWorkspace?.id === tenant_id)
        return
      await switchWorkspace({ url: '/workspaces/switch', body: { tenant_id } })
      notify({ type: 'success', message: t('actionMsg.modifiedSuccessfully', { ns: 'common' }) })
      location.assign(`${location.origin}${basePath}`)
    }
    catch {
      notify({ type: 'error', message: t('provider.saveFailed', { ns: 'common' }) })
    }
  }

  return (
    <Menu as="div" className="min-w-0">
      {
        ({ open }) => (
          <>
            <MenuButton className={cn(
              `
                group flex w-full cursor-pointer items-center
                p-0.5 hover:bg-state-base-hover ${open && 'bg-state-base-hover'} rounded-[10px]
              `,
            )}
            >
              <div className="mr-1.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-md bg-components-icon-bg-blue-solid text-[13px] max-[800px]:mr-0">
                <span className="h-6 bg-gradient-to-r from-components-avatar-shape-fill-stop-0 to-components-avatar-shape-fill-stop-100 bg-clip-text align-middle font-semibold uppercase leading-6 text-shadow-shadow-1 opacity-90">{currentWorkspace?.name[0]?.toLocaleUpperCase()}</span>
              </div>
              <div className="flex min-w-0 items-center">
                <div className="system-sm-medium min-w-0  max-w-[149px] truncate text-text-secondary max-[800px]:hidden">{currentWorkspace?.name}</div>
                <RiArrowDownSLine className="h-4 w-4 shrink-0 text-text-secondary" />
              </div>
            </MenuButton>
            <Transition
              as={Fragment}
              enter="transition ease-out duration-100"
              enterFrom="transform opacity-0 scale-95"
              enterTo="transform opacity-100 scale-100"
              leave="transition ease-in duration-75"
              leaveFrom="transform opacity-100 scale-100"
              leaveTo="transform opacity-0 scale-95"
            >
              <MenuItems
                anchor="bottom start"
                className={cn(
                  `
                    shadows-shadow-lg absolute left-[-15px] z-[1000] mt-1 flex max-h-[400px] w-[280px] flex-col items-start overflow-y-auto
                    rounded-xl bg-components-panel-bg-blur backdrop-blur-[5px]
                  `,
                )}
              >
                <div className="flex w-full flex-col items-start self-stretch rounded-xl border-[0.5px] border-components-panel-border p-1 pb-2 shadow-lg ">
                  <div className="flex items-start self-stretch px-3 pb-0.5 pt-1">
                    <span className="system-xs-medium-uppercase flex-1 text-text-tertiary">{t('userProfile.workspace', { ns: 'common' })}</span>
                  </div>
                  {
                    workspaces.map(workspace => (
                      <div className="flex items-center gap-2 self-stretch rounded-lg py-1 pl-3 pr-2 hover:bg-state-base-hover" key={workspace.id} onClick={() => handleSwitchWorkspace(workspace.id)}>
                        <div className="flex h-6 w-6 shrink-0 items-center justify-center rounded-md bg-components-icon-bg-blue-solid text-[13px]">
                          <span className="h-6 bg-gradient-to-r from-components-avatar-shape-fill-stop-0 to-components-avatar-shape-fill-stop-100 bg-clip-text align-middle font-semibold uppercase leading-6 text-shadow-shadow-1 opacity-90">{workspace?.name[0]?.toLocaleUpperCase()}</span>
                        </div>
                        <div className="system-md-regular line-clamp-1 grow cursor-pointer overflow-hidden text-ellipsis text-text-secondary">{workspace.name}</div>
                        {/* [CUSTOM] Show role badge when multi-workspace permission feature is enabled */}
                        {isFeatureEnabled && <RoleBadge role={workspace.role} />}
                        <PlanBadge plan={workspace.plan as Plan} />
                      </div>
                    ))
                  }
                </div>
              </MenuItems>
            </Transition>
          </>
        )
      }
    </Menu>
  )
}

export default WorkplaceSelector
