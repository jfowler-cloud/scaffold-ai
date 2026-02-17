"use client";

import { useState, useEffect } from "react";
import { Canvas } from "@/components/Canvas";
import { Chat } from "@/components/Chat";
import { GeneratedCodeModal } from "@/components/GeneratedCodeModal";
import AppLayout from "@cloudscape-design/components/app-layout";
import SideNavigation from "@cloudscape-design/components/side-navigation";
import TopNavigation from "@cloudscape-design/components/top-navigation";
import SplitPanel from "@cloudscape-design/components/split-panel";
import HelpPanel from "@cloudscape-design/components/help-panel";
import Box from "@cloudscape-design/components/box";
import Link from "@cloudscape-design/components/link";
import SpaceBetween from "@cloudscape-design/components/space-between";

export default function Home() {
  const [navigationOpen, setNavigationOpen] = useState(false);
  const [toolsOpen, setToolsOpen] = useState(false);
  const [splitPanelOpen, setSplitPanelOpen] = useState(true);
  const [splitPanelSize, setSplitPanelSize] = useState(420);
  const [mounted, setMounted] = useState(false);
  const [codeModalVisible, setCodeModalVisible] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) return null;

  return (
    <>
      {/* Top Navigation */}
      <div id="top-nav" style={{ position: "sticky", top: 0, zIndex: 1002 }}>
        <TopNavigation
          identity={{
            href: "/",
            title: "Scaffold AI",
            logo: {
              src: "/logo.svg",
              alt: "Scaffold AI",
            },
          }}
          utilities={[
            {
              type: "button",
              text: "Documentation",
              href: "https://github.com/jfowler-cloud/scaffold-ai",
              external: true,
              externalIconAriaLabel: "(opens in new tab)",
            },
            {
              type: "button",
              iconName: "settings",
              ariaLabel: "Settings",
              onClick: () => {},
            },
            {
              type: "button",
              iconName: "status-info",
              ariaLabel: "Help",
              onClick: () => setToolsOpen(!toolsOpen),
            },
          ]}
        />
      </div>

      {/* App Layout */}
      <AppLayout
        headerSelector="#top-nav"
        navigation={
          <SideNavigation
            header={{ text: "Scaffold AI", href: "/" }}
            activeHref="/"
            onFollow={(e) => {
              e.preventDefault();
              if (e.detail.href === "#/generated") {
                setCodeModalVisible(true);
              }
            }}
            items={[
              { type: "link", text: "Canvas", href: "/" },
              { type: "divider" },
              {
                type: "section",
                text: "Resources",
                items: [
                  { type: "link", text: "Generated Code", href: "#/generated" },
                ],
              },
              { type: "divider" },
              {
                type: "link",
                text: "Documentation",
                href: "https://github.com/jfowler-cloud/scaffold-ai",
                external: true,
              },
            ]}
          />
        }
        navigationOpen={navigationOpen}
        onNavigationChange={({ detail }) => setNavigationOpen(detail.open)}
        navigationWidth={240}
        tools={
          <HelpPanel header={<h2>Getting Started</h2>}>
            <SpaceBetween size="m">
              <Box variant="p">
                Scaffold AI helps you design AWS serverless architectures using natural language and visual node graphs.
              </Box>
              <Box variant="h4">How to use</Box>
              <Box variant="p">
                1. Describe your application in the chat panel
              </Box>
              <Box variant="p">
                2. The AI will generate architecture nodes on the canvas
              </Box>
              <Box variant="p">
                3. Drag and connect nodes to refine your design
              </Box>
              <Box variant="p">
                4. Ask the AI to generate CDK code when ready
              </Box>
              <Box variant="h4">Supported Services</Box>
              <Box variant="p">
                Lambda, API Gateway, DynamoDB, Cognito, S3, SQS, SNS, EventBridge, Step Functions, CloudFront, Kinesis
              </Box>
              <Box variant="h4">Learn more</Box>
              <Link
                href="https://github.com/jfowler-cloud/scaffold-ai"
                external
              >
                View on GitHub
              </Link>
            </SpaceBetween>
          </HelpPanel>
        }
        toolsOpen={toolsOpen}
        onToolsChange={({ detail }) => setToolsOpen(detail.open)}
        toolsWidth={320}
        splitPanel={
          <SplitPanel
            header="AI Assistant"
            hidePreferencesButton
            closeBehavior="hide"
          >
            <Chat />
          </SplitPanel>
        }
        splitPanelOpen={splitPanelOpen}
        onSplitPanelToggle={({ detail }) => setSplitPanelOpen(detail.open)}
        splitPanelSize={splitPanelSize}
        onSplitPanelResize={({ detail }) => setSplitPanelSize(detail.size)}
        splitPanelPreferences={{ position: "side" }}
        content={
          <div style={{ height: "100%", minHeight: "calc(100vh - 56px)" }}>
            <Canvas />
          </div>
        }
        contentType="default"
        disableContentPaddings
        ariaLabels={{
          navigation: "Side navigation",
          navigationClose: "Close navigation",
          navigationToggle: "Open navigation",
          tools: "Help panel",
          toolsClose: "Close help",
          toolsToggle: "Open help",
          splitPanelToggle: "Toggle AI assistant",
          splitPanelClose: "Close AI assistant",
        }}
      />
      <GeneratedCodeModal
        visible={codeModalVisible}
        onDismiss={() => setCodeModalVisible(false)}
      />
    </>
  );
}
