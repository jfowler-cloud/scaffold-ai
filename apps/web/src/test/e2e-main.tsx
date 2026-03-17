/**
 * E2E test entry point — bypasses Cognito auth.
 * Renders the app layout directly without the Authenticator wrapper.
 */
import React, { useState, useEffect } from 'react'
import ReactDOM from 'react-dom/client'
import { Amplify } from 'aws-amplify'
import '@cloudscape-design/global-styles/index.css'
import '../index.css'
import { Canvas } from '@/components/Canvas'
import { Chat } from '@/components/Chat'
import { GeneratedCodeModal } from '@/components/GeneratedCodeModal'
import AppLayout from '@cloudscape-design/components/app-layout'
import SideNavigation from '@cloudscape-design/components/side-navigation'
import TopNavigation from '@cloudscape-design/components/top-navigation'
import SplitPanel from '@cloudscape-design/components/split-panel'
import HelpPanel from '@cloudscape-design/components/help-panel'
import Box from '@cloudscape-design/components/box'
import SpaceBetween from '@cloudscape-design/components/space-between'
import { applyMode, Mode } from '@cloudscape-design/global-styles'

// Configure Amplify with dummy values so SDK calls don't crash
Amplify.configure({
  Auth: {
    Cognito: {
      userPoolId: 'us-east-1_FAKE',
      userPoolClientId: 'fakeclientid',
      identityPoolId: 'us-east-1:00000000-0000-0000-0000-000000000000',
    },
  },
})

function E2EApp() {
  const [navigationOpen, setNavigationOpen] = useState(false)
  const [toolsOpen, setToolsOpen] = useState(false)
  const [splitPanelOpen, setSplitPanelOpen] = useState(true)
  const [splitPanelSize, setSplitPanelSize] = useState(420)
  const [codeModalVisible, setCodeModalVisible] = useState(false)
  const [darkMode, setDarkMode] = useState(true)

  useEffect(() => {
    applyMode(darkMode ? Mode.Dark : Mode.Light)
    document.documentElement.classList.toggle('dark', darkMode)
  }, [darkMode])

  const toggleTheme = () => {
    setDarkMode(d => !d)
  }

  return (
    <>
      <div id="top-nav" style={{ position: 'sticky', top: 0, zIndex: 1002 }}>
        <TopNavigation
          identity={{ href: '/', title: 'Scaffold AI', logo: { src: '/logo.svg', alt: 'Scaffold AI' } }}
          utilities={[
            { type: 'button', text: darkMode ? 'Light' : 'Dark', onClick: toggleTheme },
            { type: 'button', text: 'Documentation', href: 'https://github.com/jfowler-cloud/scaffold-ai', external: true, externalIconAriaLabel: '(opens in new tab)' },
            {
              type: 'menu-dropdown',
              text: 'e2e@test.com',
              iconName: 'user-profile',
              items: [{ id: 'signout', text: 'Sign out' }],
              onItemClick: () => {},
            },
          ]}
        />
      </div>

      <AppLayout
        headerSelector="#top-nav"
        navigation={
          <SideNavigation
            header={{ text: 'Scaffold AI', href: '/' }}
            activeHref="/"
            onFollow={(e) => {
              e.preventDefault()
              if (e.detail.href === '#/generated') setCodeModalVisible(true)
            }}
            items={[
              { type: 'link', text: 'Canvas', href: '/' },
              { type: 'divider' },
              { type: 'section', text: 'Resources', items: [{ type: 'link', text: 'Generated Code', href: '#/generated' }] },
              { type: 'divider' },
              { type: 'link', text: 'Documentation', href: 'https://github.com/jfowler-cloud/scaffold-ai', external: true },
            ]}
          />
        }
        navigationOpen={navigationOpen}
        onNavigationChange={({ detail }) => setNavigationOpen(detail.open)}
        navigationWidth={240}
        tools={
          <HelpPanel header={<h2>Getting Started</h2>}>
            <SpaceBetween size="m">
              <Box variant="p">Scaffold AI helps you design AWS serverless architectures using natural language and visual node graphs.</Box>
            </SpaceBetween>
          </HelpPanel>
        }
        toolsOpen={toolsOpen}
        onToolsChange={({ detail }) => setToolsOpen(detail.open)}
        toolsWidth={320}
        splitPanel={
          <SplitPanel header="AI Assistant" hidePreferencesButton closeBehavior="hide">
            <Chat />
          </SplitPanel>
        }
        splitPanelOpen={splitPanelOpen}
        onSplitPanelToggle={({ detail }) => setSplitPanelOpen(detail.open)}
        splitPanelSize={splitPanelSize}
        onSplitPanelResize={({ detail }) => setSplitPanelSize(detail.size)}
        splitPanelPreferences={{ position: 'side' }}
        content={
          <div style={{ height: '100%', minHeight: 'calc(100vh - 56px)' }}>
            <Canvas />
          </div>
        }
        contentType="default"
        disableContentPaddings
        ariaLabels={{
          navigation: 'Side navigation',
          navigationClose: 'Close navigation',
          navigationToggle: 'Open navigation',
          tools: 'Help panel',
          toolsClose: 'Close help',
          toolsToggle: 'Open help',
        }}
      />

      <GeneratedCodeModal visible={codeModalVisible} onDismiss={() => setCodeModalVisible(false)} />
    </>
  )
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <E2EApp />
  </React.StrictMode>
)
