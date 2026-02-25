"use client";

import { useState, useRef, useEffect } from "react";
import { useChatStore, useGraphStore } from "@/lib/store";
import Container from "@cloudscape-design/components/container";
import Header from "@cloudscape-design/components/header";
import SpaceBetween from "@cloudscape-design/components/space-between";
import Box from "@cloudscape-design/components/box";
import Button from "@cloudscape-design/components/button";
import Textarea from "@cloudscape-design/components/textarea";
import Spinner from "@cloudscape-design/components/spinner";
import Icon from "@cloudscape-design/components/icon";
import Select from "@cloudscape-design/components/select";
import Modal from "@cloudscape-design/components/modal";
import Alert from "@cloudscape-design/components/alert";

interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
}

function ChatBubble({ message }: { message: ChatMessage }) {
  const isUser = message.role === "user";

  return (
    <div
      style={{
        display: "flex",
        justifyContent: isUser ? "flex-end" : "flex-start",
        marginBottom: "12px",
      }}
    >
      <div
        style={{
          maxWidth: "85%",
          padding: "12px 16px",
          borderRadius: "12px",
          backgroundColor: isUser ? "#0972d3" : "#f2f3f3",
          color: isUser ? "#ffffff" : "#000716",
        }}
      >
        <SpaceBetween direction="horizontal" size="xs">
          {!isUser && <Icon name="contact" />}
          <Box variant="p">
            {message.content}
          </Box>
          {isUser && <Icon name="user-profile" />}
        </SpaceBetween>
      </div>
    </div>
  );
}

function LoadingBubble() {
  return (
    <div style={{ display: "flex", justifyContent: "flex-start", marginBottom: "12px" }}>
      <div
        style={{
          padding: "12px 16px",
          borderRadius: "12px",
          backgroundColor: "#f2f3f3",
        }}
      >
        <SpaceBetween direction="horizontal" size="xs">
          <Icon name="contact" />
          <Spinner size="normal" />
          <Box variant="small" color="text-body-secondary">
            Generating response...
          </Box>
        </SpaceBetween>
      </div>
    </div>
  );
}

function WelcomeMessage() {
  return (
    <Box textAlign="center" padding={{ vertical: "xl" }}>
      <SpaceBetween size="m">
        <Box variant="h2">Welcome to Scaffold AI</Box>
        <Box variant="p" color="text-body-secondary">
          Describe what you want to build and I&apos;ll create the architecture for you.
        </Box>
        <SpaceBetween size="xs">
          <Box variant="small" fontWeight="bold">
            Try:
          </Box>
          <Box variant="small" color="text-body-secondary">
            &quot;Build a todo app with user authentication&quot;
          </Box>
          <Box variant="small" color="text-body-secondary">
            &quot;Create a file upload service with S3&quot;
          </Box>
          <Box variant="small" color="text-body-secondary">
            &quot;Design a REST API with a database&quot;
          </Box>
        </SpaceBetween>
      </SpaceBetween>
    </Box>
  );
}

export function Chat({ plannerData }: { plannerData?: any }) {
  const [input, setInput] = useState("");
  const [iacFormat, setIacFormat] = useState({ label: "CDK (TypeScript)", value: "cdk" });
  const [deployModalVisible, setDeployModalVisible] = useState(false);
  const [securityFailed, setSecurityFailed] = useState(false);
  const [lastGenerateInput, setLastGenerateInput] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const { messages, isLoading, addMessage, setLoading, setGeneratedFiles, generatedFiles } = useChatStore();
  const { getGraphJSON, setGraph, nodes } = useGraphStore();

  // Auto-populate with planner data if available
  useEffect(() => {
    if (plannerData && plannerData.description) {
      console.log("Planner data received, populating input");
      // Use the description directly (it's already formatted)
      setInput(plannerData.description);
      console.log("✅ Input populated with planner data");
    }
  }, [plannerData]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleDeploy = () => setDeployModalVisible(true);

  const handleDownloadZip = async () => {
    if (generatedFiles.length === 0) return;

    try {
      // Dynamically import JSZip
      const JSZip = (await import('jszip')).default;
      const zip = new JSZip();

      // Add all files to zip with proper folder structure
      generatedFiles.forEach(file => {
        zip.file(file.path, file.content);
      });

      // Generate zip file
      const blob = await zip.generateAsync({ type: 'blob' });

      // Create download link
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `scaffold-ai-${iacFormat.value}-${Date.now()}.zip`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);

      addMessage({
        id: `system-${Date.now()}`,
        role: "assistant",
        content: `✅ Downloaded ${generatedFiles.length} files as ZIP with proper folder structure.`,
      });
    } catch (error) {
      addMessage({
        id: `error-${Date.now()}`,
        role: "assistant",
        content: `❌ Download failed: ${error instanceof Error ? error.message : "Unknown error"}`,
      });
    }
  };

  const handleSecurityFix = async () => {
    if (isLoading || nodes.length === 0) return;

    setLoading(true);
    addMessage({
      id: `system-${Date.now()}`,
      role: "assistant",
      content: "Analyzing security and applying fixes...",
    });

    try {
      const graphJSON = getGraphJSON();
      const response = await fetch("/api/security", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ graph: graphJSON }),
      });

      const data = await response.json();

      if (data.updated_graph) {
        // Normalize nodes: ensure node.type is set at top level for React Flow
        const normalizedNodes = (data.updated_graph.nodes || []).map((n: any) => ({
          ...n,
          type: n.type || n.data?.type || "lambda",
        }));
        setGraph(normalizedNodes, data.updated_graph.edges || []);
      }

      if (data.changes && data.changes.length > 0) {
        addMessage({
          id: `assistant-${Date.now()}`,
          role: "assistant",
          content: `Security improvements applied:\n${data.changes.join("\n")}\n\nSecurity score: ${data.security_score?.percentage ?? "N/A"}%`,
        });
        setLoading(false);
      } else {
        addMessage({
          id: `assistant-${Date.now()}`,
          role: "assistant",
          content: "✅ No security issues found. Your architecture looks good!",
        });
        setLoading(false);
      }
    } catch (error) {
      addMessage({
        id: `error-${Date.now()}`,
        role: "assistant",
        content: `❌ Security fix error: ${error instanceof Error ? error.message : "Unknown error"}`,
      });
      setLoading(false);
    }
  };

  const handleGenerateCode = async (skipSecurityCheck = false) => {
    if (isLoading || nodes.length === 0) return;

    setLoading(true);
    setSecurityFailed(false);

    try {
      const graphJSON = getGraphJSON();

      const response = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: skipSecurityCheck ? "generate code skip_security_check" : "generate code",
          graph: graphJSON,
          iac_format: iacFormat.value,
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to generate code");
      }

      const data = await response.json();

      if (data.generated_files && data.generated_files.length > 0) {
        setGeneratedFiles(data.generated_files);
      }

      // Check if security review failed
      if (data.message && data.message.includes("Security Review: FAILED")) {
        setSecurityFailed(true);
      }

      addMessage({
        id: `assistant-${Date.now()}`,
        role: "assistant",
        content: data.message,
      });
    } catch (error) {
      console.error("Generate code error:", error);
      addMessage({
        id: `error-${Date.now()}`,
        role: "assistant",
        content: "Sorry, I encountered an error generating code. Please try again.",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: ChatMessage = {
      id: `user-${Date.now()}`,
      role: "user",
      content: input,
    };

    addMessage(userMessage);
    setInput("");
    setLoading(true);

    try {
      const graphJSON = getGraphJSON();

      const response = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: input,
          graph: graphJSON,
          iac_format: iacFormat.value,
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to get response");
      }

      const data = await response.json();

      // Update the graph if the backend returned new nodes/edges
      if (data.updated_graph?.nodes?.length > 0 || data.updated_graph?.edges?.length > 0) {
        setGraph(data.updated_graph.nodes || [], data.updated_graph.edges || []);
      }

      // Save generated files if any
      if (data.generated_files && data.generated_files.length > 0) {
        setGeneratedFiles(data.generated_files);
      }

      addMessage({
        id: `assistant-${Date.now()}`,
        role: "assistant",
        content: data.message,
      });

      // Check if security review failed and prompt user to fix
      if (data.message && data.message.includes("Security Review: FAILED")) {
        setSecurityFailed(true);
      } else {
        setSecurityFailed(false);
      }
    } catch (error) {
      console.error("Chat error:", error);
      addMessage({
        id: `error-${Date.now()}`,
        role: "assistant",
        content: "Sorry, I encountered an error. Please try again.",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e: any) => {
    if (e.detail?.key === "Enter" && !e.detail?.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <>
    <Container
      header={
        <Header
          variant="h2"
          description="Describe your architecture in natural language"
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Icon name="gen-ai" />
            <span>AI Assistant</span>
          </div>
        </Header>
      }
      fitHeight
    >
      <div style={{ display: "flex", flexDirection: "column", height: "100%" }}>
        {/* Messages area */}
        <div
          style={{
            flex: 1,
            overflowY: "auto",
            padding: "16px 0",
            minHeight: 0,
          }}
        >
          {messages.length === 0 && <WelcomeMessage />}
          {messages.map((message) => (
            <ChatBubble key={message.id} message={message as ChatMessage} />
          ))}
          {isLoading && <LoadingBubble />}
          <div ref={messagesEndRef} />
        </div>

        {/* Security failure banner */}
        {securityFailed && (
          <div style={{
            backgroundColor: "#fff7ed",
            border: "1px solid #fed7aa",
            borderRadius: "8px",
            padding: "12px 16px",
            marginBottom: "8px",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            gap: "12px",
          }}>
            <span style={{ fontSize: "13px", color: "#9a3412" }}>
              ⚠️ Security review failed. Fix issues or mark as resolved to proceed.
            </span>
            <SpaceBetween direction="horizontal" size="xs">
              <Button
                variant="primary"
                onClick={handleSecurityFix}
                disabled={isLoading}
                iconName="security"
              >
                Auto-Fix
              </Button>
              <Button
                onClick={() => {
                  setSecurityFailed(false);
                  handleGenerateCode(true);
                }}
                disabled={isLoading}
              >
                Mark Resolved
              </Button>
            </SpaceBetween>
          </div>
        )}

        {/* Input area */}
        <div style={{ borderTop: "1px solid #e9ebed", paddingTop: "16px" }}>
          <SpaceBetween size="s">
            <SpaceBetween direction="horizontal" size="s" alignItems="center">
              <div style={{ flex: 1 }}>
                <Select
                  selectedOption={iacFormat}
                  onChange={({ detail }) => setIacFormat(detail.selectedOption as typeof iacFormat)}
                  options={[
                    { label: "CDK (TypeScript)", value: "cdk" },
                    { label: "CDK (Python)", value: "python-cdk" },
                    { label: "CloudFormation (YAML)", value: "cloudformation" },
                    { label: "Terraform (HCL)", value: "terraform" },
                  ]}
                  placeholder="Select IaC format"
                  disabled={isLoading}
                />
              </div>
              <Button
                variant="primary"
                onClick={handleGenerateCode}
                disabled={isLoading || nodes.length === 0}
                loading={isLoading}
                iconName="download"
              >
                Generate Code
              </Button>
              <Button
                onClick={handleSecurityFix}
                disabled={isLoading || nodes.length === 0}
                iconName="security"
              >
                Fix Security
              </Button>
              <Button
                onClick={handleDownloadZip}
                disabled={generatedFiles.length === 0}
                iconName="download"
              >
                Download ZIP
              </Button>
              <Button
                onClick={handleDeploy}
                iconName="upload"
              >
                Deploy to AWS
              </Button>
            </SpaceBetween>
            <Textarea
              value={input}
              onChange={({ detail }) => setInput(detail.value)}
              onKeyDown={handleKeyDown}
              placeholder="Describe your application architecture..."
              rows={8}
              disabled={isLoading}
            />
            <Box float="right">
              <Button
                variant="primary"
                onClick={handleSubmit}
                disabled={isLoading || !input.trim()}
                loading={isLoading}
                iconName="send"
                iconAlign="right"
              >
                Send
              </Button>
            </Box>
          </SpaceBetween>
        </div>
      </div>
    </Container>

      <Modal
        visible={deployModalVisible}
        onDismiss={() => setDeployModalVisible(false)}
        header={
          <SpaceBetween direction="horizontal" size="s">
            <Icon name="upload" size="medium" />
            <span>Deploy to AWS</span>
          </SpaceBetween>
        }
        footer={
          <Box float="right">
            <Button variant="primary" onClick={() => setDeployModalVisible(false)}>
              Got it
            </Button>
          </Box>
        }
        size="medium"
      >
        <SpaceBetween size="l">
          <Alert type="info" header="Coming soon">
            One-click deployment to AWS is not yet available. It&apos;s on the roadmap and will support CDK, CloudFormation, and Terraform.
          </Alert>
          <Box variant="p" color="text-body-secondary">
            In the meantime, download your generated code as a ZIP and deploy manually:
          </Box>
          <SpaceBetween size="xs">
            <Box variant="p">
              <strong>CDK</strong> — run <code>cdk deploy</code> from the project root
            </Box>
            <Box variant="p">
              <strong>CloudFormation</strong> — run <code>sam deploy --guided</code> or upload via the AWS Console
            </Box>
            <Box variant="p">
              <strong>Terraform</strong> — run <code>terraform init &amp;&amp; terraform apply</code>
            </Box>
          </SpaceBetween>
        </SpaceBetween>
      </Modal>
    </>
  );
}
