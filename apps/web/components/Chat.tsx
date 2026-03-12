
import { useState, useRef, useEffect } from "react";
import { sendChat } from "@/lib/api";
import { analyzeAndFix, getSecurityScore } from "@/lib/security-autofix";
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
  const isDark = document.documentElement.classList.contains("dark");

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
          backgroundColor: isUser ? "#e8001c" : isDark ? "#1e2228" : "#f2f3f3",
          color: isUser ? "#ffffff" : isDark ? "#e8eaed" : "#000716",
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
  const isDark = document.documentElement.classList.contains("dark");
  return (
    <div style={{ display: "flex", justifyContent: "flex-start", marginBottom: "12px" }}>
      <div
        style={{
          padding: "12px 16px",
          borderRadius: "12px",
          backgroundColor: isDark ? "#1e2228" : "#f2f3f3",
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

  /**
   * Send a chat request via fire-and-poll using AWS SDK directly.
   */
  const sendChatRequest = async (userInput: string, format: string = iacFormat.value) => {
    const graphJSON = getGraphJSON();
    return sendChat(userInput, graphJSON, format);
  };

  /**
   * Process the result from a completed chat workflow execution.
   */
  const handleChatResult = (data: { message?: string; updated_graph?: any; generated_files?: any[] }) => {
    if (data.updated_graph?.nodes?.length > 0 || data.updated_graph?.edges?.length > 0) {
      setGraph(data.updated_graph.nodes || [], data.updated_graph.edges || []);
    }
    if (data.generated_files && data.generated_files.length > 0) {
      setGeneratedFiles(data.generated_files);
    }
    addMessage({ id: `assistant-${Date.now()}`, role: "assistant", content: data.message || "" });
    if (data.message?.includes("Security Review: FAILED")) {
      setSecurityFailed(true);
    } else {
      setSecurityFailed(false);
    }
  };

  // Auto-populate and submit with planner data if available
  useEffect(() => {
    if (plannerData && plannerData.description) {
      // Build a rich prompt with structured context from the planner
      const parts: string[] = [];
      if (plannerData.projectName && plannerData.projectName !== "Imported Project") {
        parts.push(`Project: ${plannerData.projectName}`);
      }
      if (plannerData.architecture) {
        parts.push(`Architecture: ${plannerData.architecture}`);
      }
      if (plannerData.techStack && Object.keys(plannerData.techStack).length > 0) {
        const stackStr = Object.entries(plannerData.techStack).map(([k, v]) => `${k}: ${v}`).join(", ");
        parts.push(`Tech Stack: ${stackStr}`);
      }
      if (plannerData.requirements) {
        const reqs = [
          plannerData.requirements.users && `Users: ${plannerData.requirements.users}`,
          plannerData.requirements.uptime && `Uptime: ${plannerData.requirements.uptime}`,
          plannerData.requirements.dataSize && `Data: ${plannerData.requirements.dataSize}`,
        ].filter(Boolean).join(" | ");
        if (reqs) parts.push(reqs);
      }
      parts.push("", plannerData.description);

      if (plannerData.reviewFindings?.length) {
        const critHigh = plannerData.reviewFindings.filter(
          (f: any) => f.risk_level === "critical" || f.risk_level === "high"
        );
        if (critHigh.length > 0) {
          parts.push(`\n⚠️ ${critHigh.length} critical/high findings from security review — please address in the architecture.`);
        }
      }
      if (plannerData.reviewSummary) {
        parts.push(`\nReview Summary: ${plannerData.reviewSummary}`);
      }

      const msg = parts.join("\n");

      addMessage({ id: `user-${Date.now()}`, role: "user", content: msg });
      setLoading(true);

      sendChatRequest(msg, "cdk")
        .then(handleChatResult)
        .catch(() => {
          addMessage({ id: `error-${Date.now()}`, role: "assistant", content: "Sorry, I encountered an error. Please try again." });
        })
        .finally(() => setLoading(false));
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
      const { updatedGraph, changes } = analyzeAndFix(graphJSON);

      if (updatedGraph) {
        const normalizedNodes = (updatedGraph.nodes || []).map((n: any) => ({
          ...n,
          type: n.type || n.data?.type || "lambda",
        }));
        setGraph(normalizedNodes, updatedGraph.edges || []);
      }

      if (changes.length > 0) {
        const score = getSecurityScore(updatedGraph);
        addMessage({
          id: `assistant-${Date.now()}`,
          role: "assistant",
          content: `Security improvements applied:\n${changes.map(c => `✅ ${c}`).join("\n")}\n\nSecurity score: ${score.percentage}%`,
        });
      } else {
        addMessage({
          id: `assistant-${Date.now()}`,
          role: "assistant",
          content: "✅ No security issues found. Your architecture looks good!",
        });
      }
    } catch (error) {
      addMessage({
        id: `error-${Date.now()}`,
        role: "assistant",
        content: `❌ Security fix error: ${error instanceof Error ? error.message : "Unknown error"}`,
      });
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateCode = async (skipSecurityCheck = false) => {
    if (isLoading || nodes.length === 0) return;

    setLoading(true);
    setSecurityFailed(false);

    try {
      const userInput = skipSecurityCheck ? "generate code skip_security_check" : "generate code";
      const data = await sendChatRequest(userInput);
      handleChatResult(data);
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
    const currentInput = input;
    setInput("");
    setLoading(true);

    try {
      const data = await sendChatRequest(currentInput);
      handleChatResult(data);
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
          <div className="bg-orange-50 dark:bg-orange-950 border border-orange-200 dark:border-orange-800 rounded-lg px-4 py-3 mb-2 flex items-center justify-between gap-3">
            <span className="text-sm text-orange-800 dark:text-orange-200">
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
        <div className="border-t border-gray-200 dark:border-zinc-700 pt-4">
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
                onClick={() => handleGenerateCode()}
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
