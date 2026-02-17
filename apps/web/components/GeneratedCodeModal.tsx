"use client";

import { useChatStore } from "@/lib/store";
import Modal from "@cloudscape-design/components/modal";
import Box from "@cloudscape-design/components/box";
import SpaceBetween from "@cloudscape-design/components/space-between";
import Tabs from "@cloudscape-design/components/tabs";

interface GeneratedCodeModalProps {
  visible: boolean;
  onDismiss: () => void;
}

export function GeneratedCodeModal({ visible, onDismiss }: GeneratedCodeModalProps) {
  const { generatedFiles } = useChatStore();

  if (generatedFiles.length === 0) {
    return (
      <Modal visible={visible} onDismiss={onDismiss} header="Generated Code">
        <Box textAlign="center" padding="l">
          <SpaceBetween size="m">
            <Box variant="p" color="text-body-secondary">
              No code generated yet.
            </Box>
            <Box variant="small">
              Click the &quot;Generate Code&quot; button to create infrastructure code.
            </Box>
          </SpaceBetween>
        </Box>
      </Modal>
    );
  }

  return (
    <Modal
      visible={visible}
      onDismiss={onDismiss}
      header="Generated Code"
      size="max"
    >
      <Tabs
        tabs={generatedFiles.map((file, index) => ({
          id: `file-${index}`,
          label: file.path.split("/").pop() || file.path,
          content: (
            <SpaceBetween size="s">
              <Box variant="small" color="text-body-secondary">
                {file.path}
              </Box>
              <pre
                style={{
                  backgroundColor: "#f2f3f3",
                  padding: "16px",
                  borderRadius: "8px",
                  overflow: "auto",
                  maxHeight: "600px",
                  fontSize: "13px",
                  lineHeight: "1.5",
                }}
              >
                <code>{file.content}</code>
              </pre>
            </SpaceBetween>
          ),
        }))}
      />
    </Modal>
  );
}
