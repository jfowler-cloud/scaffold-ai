import { useState, useEffect } from "react";
import { Authenticator, useTheme, View, Text, Heading } from "@aws-amplify/ui-react";
import "@aws-amplify/ui-react/styles.css";
import { Canvas } from "@/components/Canvas";
import { Chat } from "@/components/Chat";
import { GeneratedCodeModal } from "@/components/GeneratedCodeModal";
import { PlannerNotification } from "@/components/PlannerNotification";
import { usePlannerImport } from "@/lib/usePlannerImport";
import AppLayout from "@cloudscape-design/components/app-layout";
import SideNavigation from "@cloudscape-design/components/side-navigation";
import TopNavigation from "@cloudscape-design/components/top-navigation";
import SplitPanel from "@cloudscape-design/components/split-panel";
import HelpPanel from "@cloudscape-design/components/help-panel";
import Box from "@cloudscape-design/components/box";
import Link from "@cloudscape-design/components/link";
import SpaceBetween from "@cloudscape-design/components/space-between";
import { applyMode, Mode } from "@cloudscape-design/global-styles";

function AuthHeader() {
  const { tokens } = useTheme();
  return (
    <View textAlign="center" padding={tokens.space.large}>
      <Text fontSize="4xl">🏗️</Text>
      <Heading level={3} marginTop={tokens.space.small}>Scaffold AI</Heading>
      <Text fontSize="small" color={tokens.colors.font.secondary}>
        AI-powered AWS architecture design and code generation
      </Text>
    </View>
  );
}

function AuthFooter() {
  const { tokens } = useTheme();
  return (
    <View textAlign="center" padding={tokens.space.large}>
      <Text fontSize="small" color={tokens.colors.font.secondary}>
        Secure authentication powered by AWS Cognito
      </Text>
    </View>
  );
}

export default function App() {
  const [navigationOpen, setNavigationOpen] = useState(false);
  const [toolsOpen, setToolsOpen] = useState(false);
  const [splitPanelOpen, setSplitPanelOpen] = useState(true);
  const [splitPanelSize, setSplitPanelSize] = useState(420);
  const [codeModalVisible, setCodeModalVisible] = useState(false);
  const [darkMode, setDarkMode] = useState(() => {
    return localStorage.getItem("scaffold-ai-darkMode") !== "false";
  });
  const [showPlannerNotification, setShowPlannerNotification] = useState(true);

  const { plannerData, isFromPlanner } = usePlannerImport();

  useEffect(() => {
    applyMode(darkMode ? Mode.Dark : Mode.Light);
    document.documentElement.classList.toggle("dark", darkMode);
    localStorage.setItem("scaffold-ai-darkMode", String(darkMode));
  }, [darkMode]);

  const toggleTheme = () => {
    document.body.classList.add("theme-transitioning");
    setTimeout(() => document.body.classList.remove("theme-transitioning"), 300);
    setDarkMode(d => !d);
  };

  return (
    <Authenticator
      hideSignUp
      components={{ Header: AuthHeader, Footer: AuthFooter }}
      formFields={{
        signIn: {
          username: { placeholder: "Enter your email", label: "Email" },
          password: { placeholder: "Enter your password", label: "Password" },
        },
      }}
    >
      {({ signOut, user }) => (
        <>
          <div id="top-nav" style={{ position: "sticky", top: 0, zIndex: 1002 }}>
            <TopNavigation
              identity={{ href: "/", title: "Scaffold AI", logo: { src: "/logo.svg", alt: "Scaffold AI" } }}
              utilities={[
                { type: "button", text: darkMode ? "☀️ Light" : "🌙 Dark", onClick: toggleTheme },
                { type: "button", text: "Documentation", href: "https://github.com/jfowler-cloud/scaffold-ai", external: true, externalIconAriaLabel: "(opens in new tab)" },
                { type: "button", iconName: "status-info", ariaLabel: "Help", onClick: () => setToolsOpen(!toolsOpen) },
                {
                  type: "menu-dropdown",
                  text: user?.signInDetails?.loginId ?? "Account",
                  iconName: "user-profile",
                  items: [{ id: "signout", text: "Sign out" }],
                  onItemClick: ({ detail }) => { if (detail.id === "signout") signOut?.(); },
                },
              ]}
            />
          </div>

          <AppLayout
            headerSelector="#top-nav"
            navigation={
              <SideNavigation
                header={{ text: "Scaffold AI", href: "/" }}
                activeHref="/"
                onFollow={(e) => {
                  e.preventDefault();
                  if (e.detail.href === "#/generated") setCodeModalVisible(true);
                }}
                items={[
                  { type: "link", text: "Canvas", href: "/" },
                  { type: "divider" },
                  { type: "section", text: "Resources", items: [{ type: "link", text: "Generated Code", href: "#/generated" }] },
                  { type: "divider" },
                  { type: "link", text: "Documentation", href: "https://github.com/jfowler-cloud/scaffold-ai", external: true },
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
                  <Box variant="h4">How to use</Box>
                  <Box variant="p">1. Describe your application in the chat panel</Box>
                  <Box variant="p">2. The AI will generate architecture nodes on the canvas</Box>
                  <Box variant="p">3. Drag and connect nodes to refine your design</Box>
                  <Box variant="p">4. Ask the AI to generate CDK code when ready</Box>
                  <Box variant="h4">Supported Services</Box>
                  <Box variant="p">Lambda, API Gateway, DynamoDB, Cognito, S3, SQS, SNS, EventBridge, Step Functions, CloudFront, Kinesis</Box>
                  <Box variant="h4">Learn more</Box>
                  <Link href="https://github.com/jfowler-cloud/scaffold-ai" external>View on GitHub</Link>
                </SpaceBetween>
              </HelpPanel>
            }
            toolsOpen={toolsOpen}
            onToolsChange={({ detail }) => setToolsOpen(detail.open)}
            toolsWidth={320}
            splitPanel={
              <SplitPanel header="AI Assistant" hidePreferencesButton closeBehavior="hide">
                <Chat plannerData={plannerData} />
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
            }}
          />

          <GeneratedCodeModal visible={codeModalVisible} onDismiss={() => setCodeModalVisible(false)} />

          {isFromPlanner && showPlannerNotification && (
            <PlannerNotification plannerData={plannerData} onDismiss={() => setShowPlannerNotification(false)} />
          )}
        </>
      )}
    </Authenticator>
  );
}
