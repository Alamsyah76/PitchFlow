'use client'
import { useState } from 'react'
import StudioSidebar from '../components/content-studio/StudioSidebar'
import StudioHeader from '../components/content-studio/StudioHeader'
import SenderSettings from '../components/SenderSettings'
import CampaignSettings from '../components/email-campaign/CampaignSettings'
import ApiKeySettings from '../components/settings/ApiKeySettings'

const TABS = [
  { id: 'profile', label: 'Profile' },
  { id: 'apikey', label: 'API Key' },
  { id: 'email', label: 'Email Campaign' },
]

export default function SettingsRoute() {
  const [activeTab, setActiveTab] = useState('profile')

  return (
    <div className="min-h-screen bg-[linear-gradient(180deg,#FAFBFF_0%,#F7F8FB_42%,#F5F6FA_100%)] text-slate-950">
      <StudioSidebar activeRoute="/settings" />
      <StudioHeader title="Settings" />
      <main className="px-4 py-4 md:px-8 md:py-6 lg:ml-[260px] xl:px-10">
        <div className="mx-auto max-w-screen-2xl pb-28">

          {/* Tab Navigation */}
          <div className="mb-6 flex gap-1 rounded-xl bg-slate-100 p-1 w-fit">
            {TABS.map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`rounded-lg px-5 py-2 text-sm font-medium transition-all ${
                  activeTab === tab.id
                    ? 'bg-white text-slate-900 shadow-sm'
                    : 'text-slate-500 hover:text-slate-700'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>

          {/* Tab Content */}
          {activeTab === 'profile' && <SenderSettings />}
          {activeTab === 'apikey' && <ApiKeySettings />}
          {activeTab === 'email' && <CampaignSettings />}

        </div>
      </main>
    </div>
  )
}
