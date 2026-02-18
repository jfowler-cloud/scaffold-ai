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
          <Box variant="p" color={isUser ? "inherit" : "text-body-default"}>
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

export function Chat() {
  const [input, setInput] = useState("");
  const [iacFormat, setIacFormat] = useState({ label: "CDK (TypeScript)", value: "cdk" });
  const [deploying, setDeploying] = useState(false);
  const [costEstimate, setCostEstimate] = useState<any>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const { messages, isLoading, addMessage, setLoading, setGeneratedFiles, generatedFiles } = useChatStore();
  const { getGraphJSON, setGraph, nodes } = useGraphStore();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    // Estimate cost when nodes change
    if (nodes.length > 0) {
      const graphJSON = getGraphJSON();
      fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000"}/api/cost/estimate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(graphJSON),
      })
        .then(res => res.json())
        .then(data => setCostEstimate(data))
        .catch(() => setCostEstimate(null));
    } else {
      setCostEstimate(null);
    }
  }, [nodes, getGraphJSON]);

  const handleDeploy = async () => {
    if (deploying || generatedFiles.length === 0) return;
    if (!["cdk", "cloudformation"].includes(iacFormat.value)) return;

    setDeploying(true);
    addMessage({
      id: `system-${Date.now()}`,
      role: "assistant",
      content: "Starting deployment to AWS...",
    });

    try {
      if (iacFormat.value === "cloudformation") {
        // CloudFormation deployment
        const templateFile = generatedFiles.find(f => f.path.includes("template.yaml"));
        
        if (!templateFile) {
          throw new Error("CloudFormation template not found. Generate code first.");
        }

        addMessage({
          id: `assistant-${Date.now()}`,
          role: "assistant",
          content: `⚠️ CloudFormation deployment requires AWS SAM CLI.\n\nTo deploy manually:\n\n1. Save the template to \`template.yaml\`\n2. Run: \`sam deploy --guided\`\n\nOr use AWS Console to create a stack with the generated template.`,
        });
        setDeploying(false);
        return;
      }

      // CDK deployment
      const stackFile = generatedFiles.find(f => f.path.includes("stack.ts"));
      const appFile = generatedFiles.find(f => f.path.includes("app.ts"));

      if (!stackFile || !appFile) {
        throw new Error("CDK files not found. Generate code first.");
      }

      const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000"}/api/deploy`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          stack_name: "ScaffoldAIStack",
          cdk_code: stackFile.content,
          app_code: appFile.content,
          region: "us-east-1",
        }),
      });

      const data = await response.json();

      if (data.success) {
        addMessage({
          id: `assistant-${Date.now()}`,
          role: "assistant",
          content: `✅ Deployment successful! ${data.message || ""}`,
        });
      } else {
        addMessage({
          id: `error-${Date.now()}`,
          role: "assistant",
          content: `❌ Deployment failed: ${data.error}`,
        });
      }
    } catch (error) {
      addMessage({
        id: `error-${Date.now()}`,
        role: "assistant",
        content: `❌ Deployment error: ${error instanceof Error ? error.message : "Unknown error"}`,
      });
    } finally {
      setDeploying(false);
    }
  };

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
      const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000"}/api/security/autofix`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(graphJSON),
      });

      const data = await response.json();

      if (data.updated_graph) {
        setGraph(data.updated_graph.nodes || [], data.updated_graph.edges || []);
      }

      if (data.changes && data.changes.length > 0) {
        addMessage({
          id: `assistant-${Date.now()}`,
          role: "assistant",
          content: `Security improvements applied:\n${data.changes.join("\n")}\n\nSecurity score: ${data.security_score.percentage}%`,
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

  const handleGenerateCode = async () => {
    if (isLoading || nodes.length === 0) return;

    setLoading(true);

    try {
      const graphJSON = getGraphJSON();

      const response = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: "generate code",
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

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <Container
      header={
        <Header
          variant="h2"
          description="Describe your architecture in natural language"
        >
          <SpaceBetween direction="horizontal" size="xs">
            <Icon name="gen-ai" />
            AI Assistant
            {costEstimate && (
              <Box color="text-status-info" fontSize="body-s">
                Est. ${costEstimate.total_monthly}/mo
              </Box>
            )}
          </SpaceBetween>
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
                disabled={deploying || generatedFiles.length === 0 || !["cdk", "cloudformation"].includes(iacFormat.value)}
                loading={deploying}
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
              rows={2}
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
  );
}
